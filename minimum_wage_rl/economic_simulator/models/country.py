import uuid
import numpy as np
from numpy import random

from economic_simulator.models.game import Game
from .market import Market
from .bank import Bank
from django.contrib.auth.models import User
from django.db import models

from ..utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser

class Country(models.Model):

    class Meta:
        db_table = "country"

    # Constants
    INITIAL_NUM_SMALL_COMPANIES = int(config_parser.get("market","num_small_business"))
    INITIAL_NUM_MEDIUM_COMPANIES = int(config_parser.get("market","num_medium_business"))
    INITIAL_NUM_LARGE_COMPANIES = int(config_parser.get("market","num_large_business"))
    INITIAL_NUM_OF_CITIZENS = int(config_parser.get("country","citizens"))
    INITIAL_MIN_WAGE = float(config_parser.get("market","initial_minimum_wage"))
    CORPORATE_TAX = float(config_parser.get("country","corporate_tax"))
    INCOME_TAX = float(config_parser.get("country","income_tax"))

    # Magic Numbers (Bank) weight_mb
    WEIGTH_LARGE_COMPANY = 2
    WEIGTH_MEDIUM_COMPANY = 1.5
    WEIGTH_SMALL_COMPANY = 1
    WAGE_THRESHOLD = 50
    NEGATIVE_REWARD = -1 

    country_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    policyCode = 0 # The minimum wage policy/strategy followed 
    companies =  dict() # new Dictionary<int, MWCompany>() = None
    workers = dict() # new Dictionary<int, MWEmployee>() = None

    # The current minimum wage of this country
    minimum_wage = models.FloatField(default=float(config_parser.get("market","initial_minimum_wage")))
    product_price = models.FloatField(default=float(config_parser.get("market","initial_product_price")))
    quantity = models.IntegerField(default=0)
    inflation = models.IntegerField(default=0)

    # Statistics
    yearly_produced_value = models.FloatField(default=0.0) # Something like GDP
    num_small_companies = models.IntegerField(default=INITIAL_NUM_SMALL_COMPANIES)
    num_medium_company = models.IntegerField(default=INITIAL_NUM_MEDIUM_COMPANIES)
    num_large_company = models.IntegerField(default=INITIAL_NUM_LARGE_COMPANIES)

    # Initialize all this
    unemployment_rate = models.FloatField(default=100.0)
    total_unemployed = models.IntegerField(default=0)
    average_income = models.FloatField(default=0.0) 
    average_skill_level = models.FloatField(default=1.0) 
    average_balance = models.FloatField(default=0.0)

    # Percentage of people living bellow poverty levels
    poverty_rate = models.FloatField(default=0.0) 
    total_jun_jobs = models.FloatField(default=0.0)
    total_senior_jobs = models.FloatField(default=0.0)
    total_executive_jobs = models.FloatField(default=0.0)
    fixed_cash_printing = models.FloatField(default=float(config_parser.get("country","initial_printed_cash")))
    total_money_printed = models.FloatField(default=0.0)
    population = models.IntegerField(default=0)
    # number_of_banks = models.IntegerField(default=1)

    market = models.ForeignKey(to=Market, unique=True, on_delete=models.CASCADE)
    
    # dictionary<int, Bank>
    bank = models.ForeignKey(to=Bank, unique=True, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.OneToOneField(Game, on_delete=models.CASCADE)

    temp_worker_list = []
    temp_company_list = []

    def ResetCountry(self):
        self.companies = dict()
        self.workers = dict()
        self.minimum_wage = Country.INITIAL_MIN_WAGE
        self.num_small_companies = Country.INITIAL_NUM_SMALL_COMPANIES
        self.num_medium_company = Country.INITIAL_NUM_MEDIUM_COMPANIES
        self.num_large_company = Country.INITIAL_NUM_LARGE_COMPANIES
        
    # utility
    def calculate_statistics(self):

        # Calculate statistics here     
        self.num_small_companies = self.num_medium_company = self.num_large_company = 0
        self.total_jun_jobs = self.total_senior_jobs = self.total_executive_jobs = 0

        # Iterating through all active companies
        # self.companies = self.company_set
        
        for each_company in self.temp_company_list:
        
            # do something with entry.Value or entry.Key
            # each_company = val

            # of small,med,large companies
            if each_company.company_size_type == 0:
                self.num_small_companies = self.num_small_companies + 1

            elif each_company.company_size_type == 1:            
                self.num_medium_company = self.num_medium_company + 1
            
            else:
                self.num_large_company = self.num_large_company + 1
            
            self.total_jun_jobs += each_company.num_junior_openings
            self.total_senior_jobs += each_company.num_senior_openings
            self.total_executive_jobs += each_company.num_executive_openings

            self.yearly_produced_value += each_company.year_income # Adding company's yearly income to the GDP
        

        # Iterating through all alive citizens
        totalSkillLevel = 0
        totalSalary = 0
        totalPovertyCnt = 0
        totalAccountBalance = 0
        totalEmployed = 0
        totalUnemployed = 0

        for each_worker in self.temp_worker_list:
            # citizen = val
            
            if each_worker.salary < self.market.product_price*30: # Can't afford to buy necessary product (e.g. food)
                totalPovertyCnt = totalPovertyCnt + 1

            if not(each_worker.is_employed):            
                totalUnemployed = totalUnemployed + 1
            
            else:
                # print("===========================AM HERE========================")
                totalSalary += each_worker.salary
                totalSkillLevel += each_worker.skill_level
                totalEmployed = totalEmployed + 1
            
            totalAccountBalance += each_worker.worker_account_balance
        

        citizensCount = len(self.temp_worker_list)
        self.unemployment_rate = round((totalUnemployed / citizensCount * 100.0), 1)
        self.poverty_rate = round((totalPovertyCnt / citizensCount * 100.0), 1)
        
        if totalEmployed > 0:
            self.average_income = round((totalSalary / (totalEmployed * 1.0)), 1)
            self.average_skill_level = round((totalSkillLevel / (totalEmployed * 1.0)), 1)
        
        self.average_balance = round((totalAccountBalance / (citizensCount * 1.0)), 1)

        statisticsString = "GDP(comp): " + str(self.yearly_produced_value) + " #SB " + str(self.num_small_companies) + " #MB " + str(self.num_medium_company) +" #LB " + str(self.num_large_company) + " Unemployment " + str(self.unemployment_rate) + " AvSalary " + str(self.average_income) + " AvSkill " + str(self.average_skill_level) + " Poverty " + str(self.poverty_rate) + "% AvBalance: " + str(self.average_balance)

        self.yearly_produced_value = 0

        return statisticsString

    def UpdateMinimumWage(self):

        if self.policyCode == 0:
            # No minimum wage regulation
            self.minimum_wage = 2
        
        elif self.policyCode == 1:        
            self.minimum_wage += self.minimum_wage * self.market.inflation_rate # CHANGE FOR YEAR??? DAYS TO MATCH PRODUCT SHIT
        
        elif self.policyCode == 2:
            # Dramatic increases every X(random) years (America model) 5%
            changeProba = round(np.random.uniform(0.0,1.0) ,2)
            if changeProba <= 0.15: # 10% chance            
                self.minimum_wage += self.minimum_wage * 0.05
        else:
            pass

        # This is case it reaches the maximum possible MW for this simulations settings
        if self.minimum_wage > 90:
            self.minimum_wage = 90

        # ELSE policy is decided by the AI
    
    def get_current_state_reward(self):
        
        state_values = []

        state_values.append(self.unemployment_rate)
        state_values.append(self.poverty_rate)
        state_values.append(self.minimum_wage)
        state_values.append(self.average_income - 30 * self.market.product_price)

        reward = self.calculate_reward()

        state_reward = dict()
        state_reward["state"] = state_values
        state_reward["reward"] = reward

        return state_reward

    def calculate_reward(self):
        # 3. Companies

        r1 = Country.WEIGTH_LARGE_COMPANY * np.log10(self.num_large_company/self.minimum_wage + 1)
        r2 = Country.WEIGTH_MEDIUM_COMPANY * np.log10(self.num_medium_company / self.minimum_wage + 1)
        r3 = Country.WEIGTH_SMALL_COMPANY * np.log10(self.num_small_companies / self.minimum_wage + 1)
        r4 = 0.0

        # r1 = 1/self.povertyRate
        # r2 = 1/self.unemploymentRate

        if self.minimum_wage > Country.WAGE_THRESHOLD:
            r4 = Country.NEGATIVE_REWARD

        # return torch.tensor([r1 + r2 + r3 + r4])
        return r1 + r2 + r3 + r4
        # return r1 + r2        

    def print_money(self, bank):
        self.total_money_printed = self.total_money_printed + self.fixed_cash_printing
        bank.deposit_money(self.fixed_cash_printing)


    def add_new_citizens(country, amount):
        from .worker import Worker
        all_citizens_list = []
        for _ in range(amount):
            citizen = Worker()
            citizen.InitializeEmployee(0, country)
            all_citizens_list.append(citizen)
        
        return all_citizens_list

    def minimum_wage_action(self,action_option):

        if action_option == 0:
            pass

        elif action_option == 1:
            self.minimum_wage = self.minimum_wage + self.minimum_wage * 0.01
        
        else:
            self.minimum_wage = self.minimum_wage + self.minimum_wage * 0.05

        return self.minimum_wage
from statistics import mode
import uuid
import numpy as np
from numpy import random
# from .worker import Worker
# from .company import Company
from .market import Market
from .bank import Bank

from django.db import models

class Country(models.Model):

    __country_instance = None
    
    @staticmethod
    def get_instance():
        if Country.__country_instance == None:
            Country()
        return Country.__country_instance

    # Constants
    INITIAL_NUM_SMALL_COMPANIES = 3
    INITIAL_NUM_MEDIUM_COMPANIES = 2
    INITIAL_NUM_LARGE_COMPANIES = 1
    INITIAL_NUM_OF_CITIZENS = 10
    
    # Magic Numbers (Bank) weight_mb
    WEIGTH_LARGE_COMPANY = 2
    WEIGTH_MEDIUM_COMPANY = 1.5
    WEIGTH_SMALL_COMPANY = 1
    wAGE_THRESHOLD = 50
    NEGATIVE_REWARD = -1 

    def __init__(self) -> None:

        if Country.__country_instance !=None:
            raise Exception("Market instance already exists, USE get_instance method")
        else:
            Country.__country_instance = self


        self.country_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

        self.policyCode = 0 # The minimum wage policy/strategy followed 
        self.companies =  dict() # new Dictionary<int, MWCompany>() = None
        self.workers = dict() # new Dictionary<int, MWEmployee>() = None

        # SET LATER
        self.minimum_wage = models.FloatField(default=2.0)  # The current minimum wage of this country
        self.companyIndex = None # A unique identifer/counter for new countries
        self.citizenID = None # A unique identifier/counter for new citizens

        # Statistics
        self.yearly_produced_value = models.FloatField(default=0.0) # Something like GDP
        self.num_small_companies = models.IntegerField(default=Country.INITIAL_NUM_SMALL_COMPANIES)
        self.num_medium_company = models.IntegerField(default=Country.INITIAL_NUM_MEDIUM_COMPANIES)
        self.num_large_company = models.IntegerField(default=Country.INITIAL_NUM_LARGE_COMPANIES)

        # Initialize all this
        self.unemployment_rate = models.FloatField(default=100.0)
        self.total_unemployed = models.IntegerField(default=0)
        self.average_income = models.FloatField(default=0.0) # The average income of all citizens
        self.average_skill_level = models.FloatField(default=1.0) # The average skill level of all citizens
        self.average_balance = models.FloatField(default=1.0)
        self.poverty_rate = models.FloatField(default=0.0) # Percentage of people living bellow poverty levels
        self.total_jun_jobs = models.FloatField(default=0.0)
        self.total_senior_jobs = models.FloatField(default=0.0)
        self.total_executive_jobs = models.FloatField(default=0.0)
        self.fixed_cash_printing = models.FloatField(default=500.0)
        self.total_money_printed = models.FloatField(default=0.0)
        self.number_of_banks = models.IntegerField(default=1)

        self.market = models.ForeignKey(to=Market, unique=True, on_delete=models.CASCADE)
        
        # dictionary<int, Bank>
        self.bank = models.ForeignKey(to=Bank, unique=True, on_delete=models.CASCADE)

    
    # def EstablishCountry(self):

    #     self.yearly_produced_value = 0
    #     self.unemployment_rate = 100
    #     self.average_skill_level = self.average_income = 1
    #     self.poverty_rate = 0
    #     self.average_balance = 0
    #     # self.companyIndex = 0
    #     # self.citizenID = 0
    #     self.total_unemployed = 0
    #     self.bank_index = 0
    #     self.total_jun_jobs = self.total_senior_jobs = self.total_executive_jobs = 0
    #     # self.num_small_companies = Country.INITIAL_NUM_SMALL_COMPANIES
    #     # self.num_medium_company = Country.INITIAL_NUM_MEDIUM_COMPANIES
    #     # self.num_large_company = Country.INITIAL_NUM_LARGE_COMPANIES

    #     # Magic Numbers
    #     # self.fixed_cash_printing = 500
    #     # self.total_money_printed = 0
    #     # self.number_of_banks = 1

    #     # Connecting to global market
    #     # marketObject = GameObject.Find("Market");
    #     from .market import Market
    #     self.market = Market.get_instance() #marketObject.GetComponent<Market>();

    #     # startup
    #     # Creating Initial companies
    #     for _ in range(self.num_small_companies): # small
    #         company = Company()
    #         company.InitializeCompany(1000, 0, self.companyIndex,self)
    #         self.companies[self.companyIndex] =  company
    #         self.companyIndex = self.companyIndex + 1
        
    #     for _ in range(self.num_medium_company): # medium
    #         company = Company()
    #         company.InitializeCompany(5000, 1, self.companyIndex,self)
    #         self.companies[self.companyIndex] =  company
    #         self.companyIndex = self.companyIndex + 1 

    #     for _ in range(self.num_large_company): # large
    #         company = Company()
    #         company.InitializeCompany(25000, 2, self.companyIndex,self)
    #         self.companies[self.companyIndex] =  company
    #         self.companyIndex = self.companyIndex + 1

    #     # Adding first citizens
    #     self.add_new_citizens(Country.INITIAL_NUM_OF_CITIZENS)

    #     # startup Create banks        
    #     for index in range(self.number_of_banks):
    #         self.bank_index += 1
    #         bank = Bank(self.bank_index)            
    #         self.bank[self.bank_index] = bank

    #     # Initialize banks
    #     self.print_money(self.bank)

    def ResetCountry(self):
        self.companies = dict()
        self.workers = dict()
        self.minimum_wage = 2
        self.num_small_companies = Country.INITIAL_NUM_SMALL_COMPANIES
        self.num_medium_company = Country.INITIAL_NUM_MEDIUM_COMPANIES
        self.num_large_company = Country.INITIAL_NUM_LARGE_COMPANIES

    # startup
    # def add_new_citizens(self, amount):
    #     for _ in range(amount):
    #         citizen = Worker()
    #         citizen.InitializeEmployee(0, self.citizenID, self)
    #         self.workers[self.citizenID] =  citizen
    #         self.citizenID = self.citizenID + 1
        
    # utility
    def calculate_statistics(self):
    # Calculate the yearly statistics for all active Companies and Citizens in this country

        # print("================Am here===============")
        # Calculate statistics here     
        self.num_small_companies = self.num_medium_company = self.num_large_company = 0
        self.total_jun_jobs = self.total_senior_jobs = self.total_executive_jobs = 0

        # Iterating through all active companies
        # self.companies = self.company_set
        for _,val in self.companies.items():
        
            # do something with entry.Value or entry.Key
            company = val

            # of small,med,large companies
            if company.companyType == 0:
                self.num_small_companies = self.num_small_companies + 1

            elif company.companyType == 1:            
                self.num_medium_company = self.num_medium_company + 1
            
            else:
                self.num_large_company = self.num_large_company + 1
            
            self.total_jun_jobs += company.junior_positions
            self.total_senior_jobs += company.senior_positions
            self.total_executive_jobs += company.executive_positions

            self.yearly_produced_value += company.year_income # Adding company's yearly income to the GDP
        

        # Iterating through all alive citizens
        totalSkillLevel = 0
        totalSalary = 0
        totalPovertyCnt = 0
        totalAccountBalance = 0
        totalEmployed = 0
        totalUnemployed = 0

        for _,val in self.workers.items():
            citizen = val
            
            if citizen.salary < self.market.product_price*30: # Can't afford to buy necessary product (e.g. food)
                totalPovertyCnt = totalPovertyCnt + 1

            if not(citizen.is_employed):            
                totalUnemployed = totalUnemployed + 1
            
            else:
                # print("===========================AM HERE========================")
                totalSalary += citizen.salary
                totalSkillLevel += citizen.skill_level
                totalEmployed = totalEmployed + 1
            
            totalAccountBalance += citizen.worker_account_balance
        

        citizensCount = len(self.workers.keys())
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
            # Adjusted yearly based on inflation (France model)
            # print("In MWCountry - line 196")
            # print(self.minimum_wage)
            # print(self.market.inflation_rate)
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

    def print_money(self, banks):
        
        print("=========================================================")
        print(self.fixed_cash_printing)
        print(self.total_money_printed)
        print("=========================================================")

        tm = getattr(self, "total_money_printed")
        fc = getattr(self, "fixed_cash_printing")

        # setattr(self, "total_money_printed", tm + fc)

        print(tm)
        print(fc)

        print("=========================================================")

        self.total_money_printed = self.total_money_printed + self.fixed_cash_printing

        # each_cash_infusion = self.fixed_cash_printing / len(banks.keys())
        banks.deposit_money(self.total_money_printed)
        # for _, each_bank in banks.items():
        #     each_bank.deposit_money(each_cash_infusion)


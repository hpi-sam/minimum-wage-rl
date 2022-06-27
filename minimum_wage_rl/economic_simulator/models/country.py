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
    INITIAL_MIN_WAGE = float(config_parser.get("minwage","initial_minimum_wage"))
    CORPORATE_TAX = float(config_parser.get("country","corporate_tax"))
    INCOME_TAX = float(config_parser.get("country","income_tax"))

    INITIAL_BANK_BALANCE = float(config_parser.get("bank","initial_bank_balance"))

    # Magic Numbers (Bank) weight_mb
    # WEIGTH_LARGE_COMPANY = 2
    # WEIGTH_MEDIUM_COMPANY = 1.5
    # WEIGTH_SMALL_COMPANY = 1
    # WAGE_THRESHOLD = 50
    # NEGATIVE_REWARD = -1 

    country_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    policyCode = 0 # The minimum wage policy/strategy followed 
    companies =  dict() # new Dictionary<int, MWCompany>() = None
    workers = dict() # new Dictionary<int, MWEmployee>() = None

    # The current minimum wage of this country
    minimum_wage = models.FloatField(default=float(config_parser.get("minwage","initial_minimum_wage")))
    product_price = models.FloatField(default=float(config_parser.get("market","initial_product_price")))
    quantity = models.IntegerField(default=0)
    inflation = models.IntegerField(default=0.0)
    year = models.IntegerField(default=1)

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
    money_circulation = models.FloatField(default=0.0)

    market = models.ForeignKey(to=Market, unique=True, on_delete=models.CASCADE)
    
    # dictionary<int, Bank>
    bank = models.ForeignKey(to=Bank, unique=True, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.OneToOneField(Game, on_delete=models.CASCADE)

    temp_worker_list = []
    temp_company_list = []

    # def ResetCountry(self):
    #     self.companies = dict()
    #     self.workers = dict()
    #     self.minimum_wage = Country.INITIAL_MIN_WAGE
    #     self.num_small_companies = Country.INITIAL_NUM_SMALL_COMPANIES
    #     self.num_medium_company = Country.INITIAL_NUM_MEDIUM_COMPANIES
    #     self.num_large_company = Country.INITIAL_NUM_LARGE_COMPANIES
        
    # def print_money(self, bank):
    #     self.total_money_printed = self.total_money_printed + self.fixed_cash_printing
    #     bank.deposit_money(self.fixed_cash_printing)


    def add_new_citizens(country, amount):
        from .worker import Worker
        all_citizens_list = []
        for _ in range(amount):
            citizen = Worker()
            citizen.InitializeEmployee(0, country)
            all_citizens_list.append(citizen)
        
        return all_citizens_list
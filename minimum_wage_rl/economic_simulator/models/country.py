import uuid

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
    
    # each_level_population
    # def __init__(self):
    #     super().__init__()
        # self.INITIAL_EACH_LEVEL_POPULATION = each_level_population
        # self.ai_flag = ai_flag

    # 1: Constants
    INITIAL_EACH_LEVEL_POPULATION = models.IntegerField(default=500)
    INITIAL_NUM_SMALL_COMPANIES = int(config_parser.get("market","num_small_business"))
    INITIAL_NUM_MEDIUM_COMPANIES = int(config_parser.get("market","num_medium_business"))
    INITIAL_NUM_LARGE_COMPANIES = int(config_parser.get("market","num_large_business"))
    # INITIAL_POPULATION = int(config_parser.get("country","initial_population"))
    INITIAL_COST_OF_OPERATION = float(config_parser.get("company","cost_of_operation"))
    INITIAL_MIN_WAGE = float(config_parser.get("minwage","initial_minimum_wage"))
    CORPORATE_TAX = float(config_parser.get("country","corporate_tax"))
    INCOME_TAX = float(config_parser.get("country","income_tax"))
    INITIAL_BANK_BALANCE = float(config_parser.get("bank","initial_bank_balance"))
    OIL_PER_UNIT_QUANTITY = float(config_parser.get("country","oil_per_unit_quantity"))
    INITIAL_OIL_COST = float(config_parser.get("country","oil_cost_per_litre"))
    POPULATION_GROWTH = int(config_parser.get("country","population_growth"))    

    # 1.1  STAGFLATION PARAMETERS
    STAGFLATION_DURATION = int(config_parser.get("stagflation","stagflation_duration"))
    OIL_RATE_INCREASE = float(config_parser.get("stagflation","oil_rate_increase"))
    COST_OF_OPERATION_INCREASE = float(config_parser.get("stagflation","cost_of_operation_increase"))
    REVENUE_DECREASE_RATE = float(config_parser.get("stagflation","revenue_decrease_rate"))    
    SUBSIDY = float(config_parser.get("country","product_subsidy"))

    # 2: Components


    country_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    market = models.ForeignKey(to=Market, unique=True, on_delete=models.CASCADE)
    bank = models.ForeignKey(to=Bank, unique=True, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.OneToOneField(Game, on_delete=models.CASCADE)
    # companies =  dict() # new Dictionary<int, MWCompany>() = None
    # workers = dict() # new Dictionary<int, MWEmployee>() = None

    # 3: High level Metrics and Stats
    money_circulation = models.FloatField(default=0.0)    
    minimum_wage = models.FloatField(default=float(config_parser.get("minwage","initial_minimum_wage")))
    product_price = models.FloatField(default=float(config_parser.get("market","initial_product_price")))
    quantity = models.IntegerField(default=0)
    inflation = models.IntegerField(default=0.0)
    year = models.IntegerField(default=1)
    population = models.IntegerField(default=0)    
    unemployment_rate = models.FloatField(default=100.0)
    poverty_rate = models.FloatField(default=0.0)

    # 4: Low level Metrics and Stats
    yearly_produced_value = models.FloatField(default=0.0) # Something like GDP
    num_small_companies = models.IntegerField(default=INITIAL_NUM_SMALL_COMPANIES)
    num_medium_company = models.IntegerField(default=INITIAL_NUM_MEDIUM_COMPANIES)
    num_large_company = models.IntegerField(default=INITIAL_NUM_LARGE_COMPANIES)

    total_unemployed = models.IntegerField(default=0)
    average_income = models.FloatField(default=0.0) 
    average_skill_level = models.FloatField(default=1.0) 
    average_balance = models.FloatField(default=0.0)

    total_jun_jobs = models.FloatField(default=0.0)
    total_senior_jobs = models.FloatField(default=0.0)
    total_executive_jobs = models.FloatField(default=0.0)
    # temp_worker_list = []
    # temp_company_list = []     

    ai_flag = models.BooleanField(False)

    # STAGFLATION PARAMETERS
    stagflation_flag = models.BooleanField(default=False)
    stagflation_start = models.FloatField(default=0.0)
    stagflation_end = models.FloatField(default=0.0)

    COMPANY_REVENUE_PERCENTAGE = models.FloatField(default=1.0)
    OIL_COST_PER_LITRE = models.FloatField(default=INITIAL_OIL_COST)  
    COST_OF_OPERATION = models.FloatField(default=INITIAL_COST_OF_OPERATION)
    population_increase = models.FloatField(default=0.01)

    # only for cached version - start
    def __init__(self, *args, **kwargs):
        super(Country, self).__init__(*args, **kwargs)
        self.company_list =  list()
        self.employed_workers = list()
        self.unemployed_workers = list()
        self.metrics_list = list()
    # only for cached version - end

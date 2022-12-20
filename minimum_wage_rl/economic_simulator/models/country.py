from utility.config import ConfigurationParser

file_name = "config_file.txt"
config_parser = ConfigurationParser.get_instance(file_name).parser

class Country():

    INITIAL_NUM_SMALL_COMPANIES = int(config_parser.get("market","num_small_business"))
    INITIAL_NUM_MEDIUM_COMPANIES = int(config_parser.get("market","num_medium_business"))
    INITIAL_NUM_LARGE_COMPANIES = int(config_parser.get("market","num_large_business"))
    INITIAL_COST_OF_OPERATION = float(config_parser.get("company","cost_of_operation"))
    INITIAL_MIN_WAGE = float(config_parser.get("minwage","initial_minimum_wage"))
    CORPORATE_TAX = float(config_parser.get("country","corporate_tax"))
    INCOME_TAX = float(config_parser.get("country","income_tax"))
    # float(config_parser.get("bank","initial_bank_balance"))
    OIL_PER_UNIT_QUANTITY = float(config_parser.get("country","oil_per_unit_quantity"))
    INITIAL_OIL_COST = float(config_parser.get("country","oil_cost_per_litre"))
    POPULATION_GROWTH = int(config_parser.get("country","population_growth"))

    # add-to-web
    # STAGFLATION PARAMETERS
    STAGFLATION_DURATION = int(config_parser.get("stagflation","stagflation_duration"))
    OIL_RATE_INCREASE = float(config_parser.get("stagflation","oil_rate_increase"))
    COST_OF_OPERATION_INCREASE = float(config_parser.get("stagflation","cost_of_operation_increase"))
    REVENUE_DECREASE_RATE = float(config_parser.get("stagflation","revenue_decrease_rate"))
    SUBSIDY = float(config_parser.get("country","product_subsidy"))
    
    def __init__(self, each_level_population) -> None:

        # 2: Components
        self.company_list =  list()
        self.employed_workers = list()
        self.unemployed_workers = list()
        self.market = None    
        self.bank = None

        # 3: High level Metrics and Stats
        self.metrics_list = list()
        self.money_circulation = 0
        self.minimum_wage = float(config_parser.get("minwage","initial_minimum_wage"))
        self.product_price = float(config_parser.get("market","initial_product_price"))
        self.quantity = 0
        self.inflation = 0.0
        self.year = 1
        self.population = each_level_population * 3
        self.unemployment_rate = 100.0
        self.poverty_rate = 0.0

        # 4: Low level Metrics and Stats
        self.yearly_produced_value = 0.0
        self.num_small_companies = Country.INITIAL_NUM_SMALL_COMPANIES
        self.num_medium_company = Country.INITIAL_NUM_MEDIUM_COMPANIES
        self.num_large_company = Country.INITIAL_NUM_LARGE_COMPANIES

        self.total_unemployed = 0
        self.average_income = 0.0
        self.average_skill_level = 1.0
        self.average_balance = 0.0

        self.total_jun_jobs = 0
        self.total_senior_jobs = 0
        self.total_executive_jobs = 0
        # total_money_printed = 0.0

        self.temp_worker_list = []
        self.temp_company_list = []

        self.INITIAL_EACH_LEVEL_POPULATION = each_level_population
        self.INITIAL_BANK_BALANCE = 0
        # int(config_parser.get("country","initial_each_level_population"))

        # add-to-web
        # STAGFLATION PARAMETERS
        self.stagflation_flag = False
        self.stagflation_start = 0
        self.stagflation_end = 0

        self.COMPANY_REVENUE_PERCENTAGE = 1.0
        self.OIL_COST_PER_LITRE = Country.INITIAL_OIL_COST
        self.COST_OF_OPERATION = Country.INITIAL_COST_OF_OPERATION
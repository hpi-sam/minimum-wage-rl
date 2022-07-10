from utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser

class Country():

    INITIAL_NUM_SMALL_COMPANIES = int(config_parser.get("market","num_small_business"))
    INITIAL_NUM_MEDIUM_COMPANIES = int(config_parser.get("market","num_medium_business"))
    INITIAL_NUM_LARGE_COMPANIES = int(config_parser.get("market","num_large_business"))
    INITIAL_NUM_OF_CITIZENS = int(config_parser.get("country","citizens"))
    INITIAL_MIN_WAGE = float(config_parser.get("minwage","initial_minimum_wage"))
    CORPORATE_TAX = float(config_parser.get("country","corporate_tax"))
    INCOME_TAX = float(config_parser.get("country","income_tax"))
    INITIAL_BANK_BALANCE = float(config_parser.get("bank","initial_bank_balance"))      

    def __init__(self) -> None:

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
        self.population = 0
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

    


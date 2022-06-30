from utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser

class Country():

    # 1: Constants
    INITIAL_NUM_SMALL_COMPANIES = int(config_parser.get("market","num_small_business"))
    INITIAL_NUM_MEDIUM_COMPANIES = int(config_parser.get("market","num_medium_business"))
    INITIAL_NUM_LARGE_COMPANIES = int(config_parser.get("market","num_large_business"))
    INITIAL_NUM_OF_CITIZENS = int(config_parser.get("country","citizens"))
    INITIAL_MIN_WAGE = float(config_parser.get("minwage","initial_minimum_wage"))
    CORPORATE_TAX = float(config_parser.get("country","corporate_tax"))
    INCOME_TAX = float(config_parser.get("country","income_tax"))

    INITIAL_BANK_BALANCE = float(config_parser.get("bank","initial_bank_balance"))

    # 2: Components
    company_list =  list()
    employed_workers = list()
    unemployed_workers = list()
    market = None    
    bank = None

    # 3: High level Metrics and Stats
    metrics_list = list()
    money_circulation = 0
    minimum_wage = float(config_parser.get("minwage","initial_minimum_wage"))
    product_price = float(config_parser.get("market","initial_product_price"))
    quantity = 0
    inflation = 0.0
    year = 1
    population = 0
    unemployment_rate = 100.0
    poverty_rate = 0.0     

    # 4: Low level Metrics and Stats
    yearly_produced_value = 0.0
    num_small_companies = INITIAL_NUM_SMALL_COMPANIES
    num_medium_company = INITIAL_NUM_MEDIUM_COMPANIES
    num_large_company = INITIAL_NUM_LARGE_COMPANIES

    total_unemployed = 0
    average_income = 0.0
    average_skill_level = 1.0
    average_balance = 0.0

    total_jun_jobs = 0
    total_senior_jobs = 0
    total_executive_jobs = 0
    # total_money_printed = 0.0

    temp_worker_list = []
    temp_company_list = []


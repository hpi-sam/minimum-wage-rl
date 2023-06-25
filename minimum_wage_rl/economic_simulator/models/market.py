from django.db import models
from ..utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser

class Market(models.Model):
    
    class Meta:
        db_table = "market"

    # Magic
    # NUM_CITIZENS_LIMIT = 100
    # CITIZEN_MAX_AGE = 100
    INITIAL_PRODUCT_PRICE = float(config_parser.get("market","initial_product_price"))
    PRODUCT_PRICE_THRESHOLD = float(config_parser.get("market","product_price_threshold")) 
    
    SENIOR_SALARY_PERCENTAGE = float(config_parser.get("minwage","senior_salary_percent"))
    EXEC_SALARY_PERCENTAGE = float(config_parser.get("minwage","exec_salary_percent"))

    MINIMUM_COMPANY_BALANCE = float(config_parser.get("market","min_company_balance"))

    REQUIRED_JUN_JOB_PERCENT = float(config_parser.get("market","required_jun_job_percent"))
    REQUIRED_SEN_JOB_PERCENT = float(config_parser.get("market","required_sen_job_percent"))
    REQUIRED_EXEC_JOB_PERCENT = float(config_parser.get("market","required_exec_job_percent"))

    SMALL_CMP_INIT_BALANCE = float(config_parser.get("market","small_company_init_balance"))
    MEDIUM_CMP_INIT_BALANCE = float(config_parser.get("market","medium_company_init_balance"))
    LARGE_CMP_INIT_BALANCE = float(config_parser.get("market","large_company_init_balance"))

    COMPANY_AGE_WEIGHTAGE =  float(config_parser.get("market","cmp_age_weightage"))
    COMPANY_ACCT_BALANCE_WEIGHTAGE = float(config_parser.get("market","cmp_acct_balance_weightage"))
    COMPANY_HIRING_BUDGET_PERCENT = float(config_parser.get("company","hiring_budget_percent"))

    STARTUP_ACCT_WEIGHTAGE = float(config_parser.get("startup","acct_balance_weightage"))
    STARTUP_AGE_WEIGHTAGE = float(config_parser.get("startup","age_weightage"))
    STARTUP_SKILLSET_WEIGHTAGE = float(config_parser.get("startup","skill_set_weightage"))
    START_MONEY_THERSHOLD_PERCENT = float(config_parser.get("startup","startup_money_percent"))
    STARTUP_LOAN_PERCENT = float(config_parser.get("startup","bank_loan_budget"))
    STARTUP_SKILL_IMPROVEMENT = float(config_parser.get("startup","startup_skill"))

    HIGH_THRESHOLD_INFLATION = float(config_parser.get("inflation","high_threshold_inflation"))
    LOW_THRESHOLD_INFLATION = float(config_parser.get("inflation","low_threshold_inflation"))
    THRESHOLD_QUANTITY_INCREASE = float(config_parser.get("inflation","threshold_quantity_increase"))
    POSSIBLE_QUANTITY_INCREASE = float(config_parser.get("inflation","possible_quantity_increase"))
    MIN_BALANCE_INFLATION = float(config_parser.get("inflation","bank_min_balance_inflation"))
    BANK_LOAN_INFLATION = float(config_parser.get("inflation","bank_threshold_loan_inflation"))
    EXPIRABLE_GOODS = bool(config_parser.get("market","expirable_goods"))        
    
    SMALL_COMPANY_TYPE=0
    MEDIUM_COMPANY_TYPE=1
    LARGE_COMPANY_TYPE=2

    # all_data = list()
    # out_file_name = None
    # month = models.IntegerField(default=0)
    # year = models.IntegerField(default=0)

    # unregulatedScenario = None
    # adjustedScenario = None
    # dramaticScenario = None
    # aiScenario = None
    
    # SET LATER
    # market_value_year = models.FloatField()
    # amount_of_new_citizens = models.IntegerField(default=0)    
    # inflation_rate = models.FloatField(default=config_parser.get("market","inflation"))

    # SET LATER
    # product_price = models.FloatField(default=INITIAL_PRODUCT_PRICE)
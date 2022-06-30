# from MWCompany import MWCompany

# import numpy as np


# from .bank import Bank
# from .country import Country
# from .company import Company

from utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser


class Worker():

    BUY_EXTRA_ACCT_BALANCE = 5
    BUY_LUXURY_ACCT_BALANCE = 10
    JUNIOR_SKILL_LEVEL = int(config_parser.get("worker","junior_skill_level"))
    SENIOR_SKILL_LEVEL = int(config_parser.get("worker","senior_skill_level"))
    DELTA_JOB_CHANGE_SALARY = 10
    INIT_LARGE_COMP_BALANCE = 25000
    INIT_MEDIUM_COMP_BALANCE = 5000
    INIT_SMALL_COMP_BALANCE = 1000
    LARGE_COMPANY_TYPE = 2
    MEDIUM_COMPANY_TYPE = 1
    SMALL_COMPANY_TYPE = 0
    MAX_SKILL_LEVEL = 100
    START_COMP_ACCT_BALANCE = 1000
    ENTREPRENERSHIP_NORMALIZING_FACTOR = 300
    JOB_CHANGE_THRESHOLD = 95
    JOB_SATISFACTION_FACTOR = 100
    INITIAL_BANK_BALANCE = float(config_parser.get("worker","initial_acct_balance")) 

    SKILL_SET_WEIGHTAGE = float(config_parser.get("worker","skill_set_weightage"))
    EXPERIENCE_WEIGHTAGE = float(config_parser.get("worker","experience_weightage"))

    # country_of_residence = None
    works_for_company = None

    skill_level = 0
    worker_account_balance = 0
    salary = 0
    age = 0

    is_employed = False
    has_company = False
    retired = False

    worker_score = 0.0

    create_start_up = False
    start_up_score = 0.0

    # Based on the company size - small/medium/large
    skill_improvement_rate = 0.0

    # def InitializeEmployee(self, initialBalance, country): #MWCountry
    #     self.worker_account_balance = initialBalance

    #     self.salary = self.age = 0
    #     self.skill_level = 1
    #     self.is_employed = self.has_company = False

    #     # Moving to a country
    #     self.country_of_residence = country    
    
# from MWCompany import MWCompany

# import numpy as np


# from .bank import Bank
# from .country import Country
# from .company import Company

from utility.config import ConfigurationParser

file_name = "config_file.txt"
config_parser = ConfigurationParser.get_instance(file_name).parser


class Worker():

    BUY_EXTRA_ACCT_BALANCE = 5
    BUY_LUXURY_ACCT_BALANCE = 10
    # GENERAL_SKILL_LEVEL = int(config_parser.get("worker","general_skill_level"))
    JUNIOR_SKILL_LEVEL = int(config_parser.get("worker","junior_skill_level"))
    SENIOR_SKILL_LEVEL = int(config_parser.get("worker","senior_skill_level"))
    EXEC_SKILL_LEVEL = int(config_parser.get("worker","exec_skill_level"))    
    INITIAL_WORKER_BANK_BALANCE = float(config_parser.get("worker","initial_acct_balance")) 

    SKILL_SET_WEIGHTAGE = float(config_parser.get("worker","skill_set_weightage"))
    EXPERIENCE_WEIGHTAGE = float(config_parser.get("worker","experience_weightage"))
    SAVINGS_PERCENT = float(config_parser.get("worker","savings_percent"))


    def __init__(self) -> None:
        # country_of_residence = None
        self.works_for_company = None

        self.skill_level = 0
        self.worker_account_balance = 0
        self.salary = 0
        self.age = 0

        self.is_employed = False
        self.has_company = False
        self.retired = False

        self.worker_score = 0.0

        self.create_start_up = False
        self.start_up_score = 0.0

        # Based on the company size - small/medium/large
        self.skill_improvement_rate = 0.0 
    
# import uuid
# from django.db import models
# from .country import Country

from utility.config import ConfigurationParser

file_name = "config_file.txt"
config_parser = ConfigurationParser.get_instance(file_name).parser


class Company():

    INSTALLMENT_PERCENT = float(config_parser.get("bank","installment_percent"))
    CORPORATE_TAX = float(config_parser.get("country","corporate_tax"))
    SML_CMP_SKILL_IMPROVEMENT = float(config_parser.get("company","small_cmp_skill_improvement"))
    MEDIUM_CMP_SKILL_IMPROVEMENT = float(config_parser.get("company","medium_cmp_skill_improvement"))
    LARGE_CMP_SKILL_IMPROVEMENT = float(config_parser.get("company","large_cmp_skill_improvement"))
    COMPANY_EARNING_PERCENT = float(config_parser.get("company","company_earning_percent"))
    # Magic Numbers
    # Possible action in future


    # MAX_EXECUTIVE_SALARY = 95       
    # MAX_SENIOR_SALARY = 65          
    # MAX_JUNIOR_OFFER = 20          
    # MAX_HIRING_RATE = 0.001
    # CHANGE_COMPANY_LARGE_BALANCE = 20000
    # CHANGE_COMPANY_MEDIUM_BALANCE = 2500


    def __init__(self) -> None:
        # company_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        self.company_size_type = None # 0 - small , 1 - medium, 2 - large

        # Balance distributions
        # hiring_rate = models.FloatField(default=0.02) # What percentage of the balance does the company spend on hiring -- DEPRECATED

        # Employees & Hiring
        # junior_hiring_ratio = models.IntegerField() # How many juniors to hire before moving to next round
        # senior_hiring_ratio = models.IntegerField() # How many seniors to hire on current round before moving to juniors
        # executive_hiring_ratio = models.IntegerField() # How many executives to hire on current round before moving to senior level
        self.skill_improvement_rate = 0 # How fast does the employee skill increase each year
    
        self.num_junior_openings = 0
        self.num_senior_openings = 0
        self.num_executive_openings = 0

        # Offers for new positions to employees - Maximum based on J,S,E levels and how much the company can afford to pay
        # junior_salary_offer = 0.0
        # senior_salary_offer = 0.0
        # executive_salary_offer = 0.0

        self.company_account_balance = 0.0
        self.company_age = 0
        self.year_income = 0

        self.company_score = 0.0

        self.num_junior_workers = 0
        self.num_senior_workers = 0
        self.num_executive_workers = 0

        self.avg_junior_salary = 0.0
        self.avg_senior_salary = 0.0
        self.avg_executive_salary = 0.0

        self.open_junior_pos = 0
        self.open_senior_pos = 0
        self.open_exec_pos = 0

        self.junior_workers_list = []
        self.senior_workers_list = []
        self.exec_workers_list = []

        self.employed_workers_list = list()

        self.start_up_worker_list = list()

        # Connection to country
        # self.country = None

        self.loan_taken = False
        self.loan_amount = 0.0

        self.closed = False
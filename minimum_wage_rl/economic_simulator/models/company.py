# import uuid
# from django.db import models
# from .country import Country

from utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser


class Company():

    # Magic Numbers
    # Possible action in future
    CORPORATE_TAX = float(config_parser.get("country","corporate_tax"))
    INSTALLMENT_PERCENT = float(config_parser.get("bank","installment_percent"))

    SML_CMP_SKILL_IMPROVEMENT = float(config_parser.get("company","small_cmp_skill_improvement"))
    MEDIUM_CMP_SKILL_IMPROVEMENT = float(config_parser.get("company","medium_cmp_skill_improvement"))
    LARGE_CMP_SKILL_IMPROVEMENT = float(config_parser.get("company","large_cmp_skill_improvement"))

    # MAX_EXECUTIVE_SALARY = 95       
    # MAX_SENIOR_SALARY = 65          
    # MAX_JUNIOR_OFFER = 20          
    # MAX_HIRING_RATE = 0.001
    # CHANGE_COMPANY_LARGE_BALANCE = 20000
    # CHANGE_COMPANY_MEDIUM_BALANCE = 2500
    
    # company_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_size_type = None # 0 - small , 1 - medium, 2 - large

    # Balance distributions
    # hiring_rate = models.FloatField(default=0.02) # What percentage of the balance does the company spend on hiring -- DEPRECATED

    # Employees & Hiring
    # junior_hiring_ratio = models.IntegerField() # How many juniors to hire before moving to next round
    # senior_hiring_ratio = models.IntegerField() # How many seniors to hire on current round before moving to juniors
    # executive_hiring_ratio = models.IntegerField() # How many executives to hire on current round before moving to senior level
    skill_improvement_rate = 0 # How fast does the employee skill increase each year
    
    num_junior_openings = 0
    num_senior_openings = 0
    num_executive_openings = 0

    # Offers for new positions to employees - Maximum based on J,S,E levels and how much the company can afford to pay
    # junior_salary_offer = 0.0
    # senior_salary_offer = 0.0
    # executive_salary_offer = 0.0

    company_account_balance = 0.0
    company_age = 0
    year_income = 0

    company_score = 0.0

    num_junior_workers = 0
    num_senior_workers = 0
    num_executive_workers = 0

    avg_junior_salary = 0.0
    avg_senior_salary = 0.0
    avg_executive_salary = 0.0

    open_junior_pos = 0
    open_senior_pos = 0
    open_exec_pos = 0

    junior_workers_list = []
    senior_workers_list = []
    exec_workers_list = []

    employed_workers_list = list()

    # Connection to country
    country = None

    loan_taken = False
    loan_amount = 0.0

    closed = False
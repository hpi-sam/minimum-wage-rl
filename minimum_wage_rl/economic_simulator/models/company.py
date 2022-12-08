import uuid
from django.db import models
from .country import Country

from ..utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser


class Company(models.Model):

    class Meta:
        db_table = "company"    

    # Magic Numbers
    # Possible action in future
    CORPORATE_TAX = float(config_parser.get("country","corporate_tax"))
    INSTALLMENT_PERCENT = float(config_parser.get("bank","installment_percent"))

    SML_CMP_SKILL_IMPROVEMENT = float(config_parser.get("company","small_cmp_skill_improvement"))
    MEDIUM_CMP_SKILL_IMPROVEMENT = float(config_parser.get("company","medium_cmp_skill_improvement"))
    LARGE_CMP_SKILL_IMPROVEMENT = float(config_parser.get("company","large_cmp_skill_improvement"))
    # COST_OF_OPERATION = float(config_parser.get("company","cost_of_operation"))
    COMPANY_EARNING_PERCENT = float(config_parser.get("company","company_earning_percent"))


    # MAX_EXECUTIVE_SALARY = 95       
    # MAX_SENIOR_SALARY = 65          
    # MAX_JUNIOR_OFFER = 20          
    # MAX_HIRING_RATE = 0.001
    # CHANGE_COMPANY_LARGE_BALANCE = 20000
    # CHANGE_COMPANY_MEDIUM_BALANCE = 2500
    
    company_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_size_type = models.IntegerField() # 0 - small , 1 - medium, 2 - large

    # Balance distributions
    # hiring_rate = models.FloatField(default=0.02) # What percentage of the balance does the company spend on hiring -- DEPRECATED

    # Employees & Hiring
    # junior_hiring_ratio = models.IntegerField() # How many juniors to hire before moving to next round
    # senior_hiring_ratio = models.IntegerField() # How many seniors to hire on current round before moving to juniors
    # executive_hiring_ratio = models.IntegerField() # How many executives to hire on current round before moving to senior level
    skill_improvement_rate = models.FloatField() # How fast does the employee skill increase each year
    
    num_junior_openings = models.IntegerField()
    num_senior_openings = models.IntegerField()
    num_executive_openings = models.IntegerField()

    # Offers for new positions to employees - Maximum based on J,S,E levels and how much the company can afford to pay
    junior_salary_offer = models.FloatField()
    senior_salary_offer = models.FloatField()
    executive_salary_offer = models.FloatField()

    company_account_balance = models.FloatField(default=0.0) # The balance sheet of the company
    company_age = models.IntegerField(default=0)
    year_income = 0 # Money made/lost during each year

    company_score = models.FloatField(default=0.0)

    num_junior_workers = models.IntegerField(default=0)
    num_senior_workers = models.IntegerField(default=0)
    num_executive_workers = models.IntegerField(default=0)

    avg_junior_salary = models.FloatField(default=0.0)
    avg_senior_salary = models.FloatField(default=0.0)
    avg_executive_salary = models.FloatField(default=0.0)

    open_junior_pos = models.IntegerField(default=0)
    open_senior_pos = models.IntegerField(default=0)
    open_exec_pos = models.IntegerField(default=0)

    junior_workers_list = []
    senior_workers_list = []
    exec_workers_list = []

    # Connection to country
    country = models.ForeignKey(to=Country, null=True, blank=True, on_delete=models.CASCADE)

    loan_taken = models.BooleanField(default=False)
    loan_amount = models.FloatField(default=0.0)

    closed = models.BooleanField(default=False)
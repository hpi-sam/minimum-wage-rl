# from MWCompany import MWCompany
# from statistics import mode
# import numpy as np
from django.db import models

from .bank import Bank
from .country import Country
from .company import Company
import uuid

from ..utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser


class Worker(models.Model):

    class Meta:
        db_table = "worker"    

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
    INITIAL_WORKER_BANK_BALANCE = float(config_parser.get("worker","initial_acct_balance")) 

    SKILL_SET_WEIGHTAGE = float(config_parser.get("worker","skill_set_weightage"))
    EXPERIENCE_WEIGHTAGE = float(config_parser.get("worker","experience_weightage"))
    SAVINGS_PERCENT = float(config_parser.get("worker","savings_percent"))

    worker_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country_of_residence = models.ForeignKey(to=Country, null=True, blank=True, on_delete=models.CASCADE)
    works_for_company = models.ForeignKey(to=Company, null=True, blank=True, on_delete=models.CASCADE)

     # Current skill level of the employee. Junior: (1-25) Senior: (25.1 - 70) Executive (70.1 - 100)
    skill_level = models.FloatField(default=float(config_parser.get("market","initial_skill_level")))
    worker_account_balance = models.FloatField(default=0)
    salary = models.FloatField(default=0)
    age = models.IntegerField()

    is_employed = models.BooleanField(default=False)
    has_company = models.BooleanField(default=False)
    retired = models.BooleanField(default=False)

    worker_score = models.FloatField(default=0.0)

    create_start_up = models.BooleanField(default=False)
    start_up_score = models.FloatField(default=0.0)
    skill_improvement_rate = models.FloatField(default=0.0)

    # company_obj = models.ForeignKey(to=Company, null=True, blank=True, on_delete=models.CASCADE)
    # bought_essential_product = models.BooleanField(default=False)
    # buy_first_extra_product = models.BooleanField(default=False)
    # buy_second_extra_product = models.BooleanField(default=False)
    # def InitializeEmployee(self, initialBalance, country): #MWCountry
    #     self.worker_account_balance = initialBalance

    #     self.salary = self.age = 0
    #     self.skill_level = 1
    #     self.bought_essential_product = self.buy_first_extra_product = self.buy_second_extra_product = False
    #     self.is_employed = self.has_company = False

    #     # Moving to a country
    #     self.country_of_residence = country
    
    # def buy_products(self, speedup, market):
    # # 'Buying essential, extra and luxury products based on current account balance'

    #     # Buying essentials (food etc)
    #     print("Am here 2")
    #     if self.worker_account_balance < market.product_price * speedup:
    #         self.worker_account_balance = 0
    #         return
    #     else:
    #         self.worker_account_balance -= market.product_price * speedup
    #         market.market_value_year += market.product_price * speedup

    #     buyPossibility = 0
    #     # Buying extra
    #     if self.worker_account_balance > Worker.BUY_EXTRA_ACCT_BALANCE * market.product_price * speedup:
    #         buyPossibility = round(np.random.random(),2)
            
    #         if buyPossibility > 0.5:
    #             self.worker_account_balance -= market.product_price * speedup
    #             market.market_value_year += market.product_price * speedup

    #     # Buying luxury
    #     if self.worker_account_balance > Worker.BUY_LUXURY_ACCT_BALANCE * market.product_price * speedup:
            
    #         buyPossibility = round(np.random.random(),2)
    #         if buyPossibility > 0.75:
    #             self.worker_account_balance -= market.product_price * speedup
    #             market.market_value_year += market.product_price * speedup
    
    # def search_job(self, all_companies_list):

    #     companyWithBestOffer = None #MWCompany
    #     maxOffer = 0
    #     # For efficiency we do a round robin until we find the first company that satisfies the employees requirments

    #     # Company Iteration
    #     # Skill levels - Junior: (1-25) Senior: (25.1 - 70) Executive (70.1 - 100)
    #     # Hiring levels J(1,7,15) S(25.1,40,55) E(70.1,80,90) C is the highest
    #     # Hiring Salary J(2,5,10) S(15,20,25) E(40,50,60) - Newbies at a loss
    #     # all_companies_list = list(self.country_of_residence.company_set.all())
    #     for each_company in all_companies_list:
            
    #         # company = v # MWCompany

    #         # Looking for Junior Position
    #         if self.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
    #             if each_company.num_junior_openings > 0:

    #                 if each_company.junior_salary_offer > (self.salary + Worker.DELTA_JOB_CHANGE_SALARY) or not(self.is_employed):  
                        
    #                     self.change_company(each_company, each_company.junior_salary_offer)
    #                     each_company.num_junior_openings = each_company.num_junior_openings - 1 
    #                     return

    #                 else:
    #                     if each_company.junior_salary_offer > maxOffer:
    #                         companyWithBestOffer = each_company
                                                    
    #         elif self.skill_level <= Worker.SENIOR_SKILL_LEVEL:
            
    #             # Looking for Senior Position
    #             if each_company.num_senior_openings > 0:
                
    #                 if each_company.senior_salary_offer > (self.salary + Worker.DELTA_JOB_CHANGE_SALARY) or not(self.is_employed):
            
    #                     self.change_company(each_company, each_company.senior_salary_offer)
    #                     each_company.num_senior_openings = each_company.num_senior_openings-1
    #                     return
                    
    #                 else:
                    
    #                     if each_company.senior_salary_offer > maxOffer:
    #                         companyWithBestOffer = each_company                                                         
            
    #         else:
            
    #             # Looking for Executive position
    #             if each_company.num_executive_openings > 0:
                
    #                 if each_company.executive_salary_offer > (self.salary + Worker.DELTA_JOB_CHANGE_SALARY) or not(self.is_employed):
                    
    #                     self.change_company(each_company, each_company.executive_salary_offer)
    #                     each_company.num_executive_openings = each_company.num_executive_openings-1
    #                     return
                    
    #                 else:  
    #                     if each_company.executive_salary_offer > maxOffer:
    #                         companyWithBestOffer = each_company       
    
    # MWCompany
    # def change_company(self, newCompany, newSalary):
    
    #     self.company_obj = newCompany

    #     if newSalary < self.country_of_residence.minimum_wage:
    #         self.salary = self.country_of_residence.minimum_wage
    #     else:
    #         self.salary = newSalary
    #     self.is_employed = True
    
    # def start_a_company(self):
        
    #     from .company import Company
    #     startup = Company()

    #     #Default = Small business

    #     initialBalance = Worker.INIT_SMALL_COMP_BALANCE
    #     companyType = Worker.SMALL_COMPANY_TYPE

    #     if self.worker_account_balance >= Worker.INIT_LARGE_COMP_BALANCE:
    #         # Start a large business
    #         # initialBalance = self.worker_account_balance
    #         companyType = Worker.LARGE_COMPANY_TYPE

    #     elif self.worker_account_balance >= Worker.INIT_MEDIUM_COMP_BALANCE:
    #         # Start a medium business
    #         # initialBalance = self.worker_account_balance
    #         companyType = Worker.MEDIUM_COMPANY_TYPE
        
    #     self.remove_worker()
    #     self.has_company = True
    #     startup.InitializeCompany(self.worker_account_balance, companyType, self.country_of_residence)
    #     self.company_obj = startup
        
    #     return startup
    
    # def explore_options(self):
    #     amount = 500

    #     changed_option = False

    #     if self.worker_account_balance > 500 and self.worker_account_balance < 1000:
            
    #         # Logic to choose banks
    #         bank = self.country_of_residence.bank

    #         # get loan
    #         loan_amount = bank.lend_loan(amount)
    #         if loan_amount >= amount: 
    #             self.worker_account_balance = self.worker_account_balance + bank.lend_loan(amount)

    #             # start company
    #             self.StartACompany()
    #             changed_option = True

    #     return changed_option

    # def evaluate_worker_step(self, all_companies_list):
        
        # new_company_obj = None

        # # Employed but does not own Company
        # if self.is_employed and not(self.has_company):
        
        #     # Increase skill
        #     if self.skill_level < Worker.MAX_SKILL_LEVEL:
        #         self.skill_level += self.company_obj.skill_improvement_rate

        #     # Explore Options here
        #     # Either Change Job or Start a Company

        #     # Start a company ? 
        #     if self.worker_account_balance > Worker.START_COMP_ACCT_BALANCE:
        #         # Magic Number refactor this logic
        #         entrepreneurshipDrive = (self.salary + self.skill_level) / Worker.ENTREPRENERSHIP_NORMALIZING_FACTOR
        #         startupProbability = round(np.random.uniform(0.0,100.0),2)

        #         if startupProbability <= entrepreneurshipDrive:
        #             new_company_obj = self.start_a_company()
        #             return new_company_obj 

        #     #Look for new job ? 
        #     if self.salary < Worker.JOB_CHANGE_THRESHOLD:
            
        #         satisfactionLevel = Worker.JOB_SATISFACTION_FACTOR - (self.skill_level - self.salary)
        #         jobsearchProba = round(np.random.uniform(0.0,100.0),2)
        #         if jobsearchProba >= satisfactionLevel:
        #             self.search_job(all_companies_list)
        
        # # Unemployeed            
        # else:            
        #     self.search_job(all_companies_list)
    
    # def remove_worker(self):
    #     self.is_employed = False
    #     self.retired = True
        
    
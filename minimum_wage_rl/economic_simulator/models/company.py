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
    MAX_EXECUTIVE_SALARY = 95       # 3 * self.countryInc.minimum_wage
    MAX_SENIOR_SALARY = 65          # 1.5 * self.countryInc.minimum_wage
    MAX_JUNIOR_OFFER = 20          # self.countryInc.minimum_wage
    MAX_HIRING_RATE = 0.001
    CHANGE_COMPANY_LARGE_BALANCE = 20000
    CHANGE_COMPANY_MEDIUM_BALANCE = 2500
    
    # def __init__(self) -> None:
    # Profile

    # self.country = models.ForeignKey(to=Country, null=True, blank=True)
    company_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    companyIndex = None #The unique identifier of a company
    company_size_type = models.IntegerField() # 0 - small , 1 - medium, 2 - large

    # Balance distributions
    hiring_rate = models.FloatField(default=0.02) # What percentage of the balance does the company spend on hiring -- DEPRECATED

    # Employees & Hiring
    junior_hiring_ratio = models.IntegerField() # How many juniors to hire before moving to next round
    senior_hiring_ratio = models.IntegerField() # How many seniors to hire on current round before moving to juniors
    executive_hiring_ratio = models.IntegerField() # How many executives to hire on current round before moving to senior level
    skill_improvement_rate = models.FloatField() # How fast does the employee skill increase each year
    
    num_junior_openings = models.IntegerField()
    num_senior_openings = models.IntegerField()
    num_executive_openings = models.IntegerField()

    # Offers for new positions to employees - Maximum based on J,S,E levels and how much the company can afford to pay
    junior_salary_offer = models.FloatField()
    senior_salary_offer = models.FloatField()
    executive_salary_offer = models.FloatField()

    companyEmployees = list() #List<MWEmployee> 

    company_account_balance = models.FloatField(default=0.0) # The balance sheet of the company
    year_income = 0 # Money made/lost during each year

    # Connection to country
    country = models.ForeignKey(to=Country, null=True, blank=True, on_delete=models.CASCADE)
    
    def InitializeCompany(self, initialBalance, companyType, country): #MWCountry
    
        self.company_account_balance = initialBalance
        self.company_size_type = companyType
        self.country = country

        self.hiring_rate = 0.02

        self.num_junior_openings = self.num_senior_openings = self.num_executive_openings = 0
        self.junior_salary_offer = self.senior_salary_offer = self.executive_salary_offer = country.minimum_wage # Initializing to the bear minimum because companies are jackasses

        if companyType == 0: # Small
            self.executive_hiring_ratio = 2
            self.senior_hiring_ratio = 2
            self.junior_hiring_ratio = 6
            self.skill_improvement_rate = 1
        
        elif companyType == 1: # Medium
            self.executive_hiring_ratio = 2
            self.senior_hiring_ratio = 6
            self.junior_hiring_ratio = 6
            self.skill_improvement_rate = 1.5
        
        else: # Large
            self.executive_hiring_ratio = 6
            self.senior_hiring_ratio = 6
            self.junior_hiring_ratio = 6
            self.skill_improvement_rate = 2

    # company.companyEmployees = list()


    def open_job_positions(self):
    
        self.num_junior_openings = self.num_senior_openings = self.num_executive_openings = 0
        hrInvestment = self.hiring_rate * self.company_account_balance

        #  Executive Hiring
        for _ in  range(self.executive_hiring_ratio):
        
            if hrInvestment > self.executive_salary_offer and hrInvestment >= self.country.minimum_wage:
                self.num_executive_openings = self.num_executive_openings + 1
                hrInvestment -= self.executive_salary_offer
            
            else:
                break

        # Senior Hiring
        for _ in range(self.senior_hiring_ratio):
    
            if hrInvestment > self.senior_salary_offer and hrInvestment >= self.country.minimum_wage:
                self.num_senior_openings = self.num_senior_openings + 1
                hrInvestment -= self.senior_salary_offer
            
            else:            
                break               

        # Junior Hiring
        for _ in range(self.junior_hiring_ratio):

            if hrInvestment > self.junior_salary_offer and hrInvestment >= self.country.minimum_wage:
                self.num_junior_openings = self.num_junior_openings + 1
                hrInvestment -= self.junior_salary_offer
            
            else:
                break

        return self.num_junior_openings + self.num_senior_openings + self.num_executive_openings

    def evaluate_company_step(self):
    
        self.pay_taxes()
        self.year_income = 0        

        # =============== Adjusting hiring offers to stay competitive in the job market -- START ===============
        if self.num_executive_openings != 0:
        
            if self.executive_salary_offer < Company.MAX_EXECUTIVE_SALARY or self.executive_salary_offer < self.country.minimum_wage:            
                self.executive_salary_offer = self.executive_salary_offer + 1

                if self.executive_salary_offer < self.country.minimum_wage:                
                    self.executive_salary_offer = self.country.minimum_wage        
        
        else:        
            if self.executive_salary_offer > self.country.minimum_wage:
                self.executive_salary_offer = self.executive_salary_offer - 1
            
        if self.num_senior_openings != 0:
        
            if self.senior_salary_offer < Company.MAX_SENIOR_SALARY or self.senior_salary_offer < self.country.minimum_wage:
                self.senior_salary_offer = self.senior_salary_offer + 1
                
                if self.senior_salary_offer < self.country.minimum_wage:
                    self.senior_salary_offer = self.country.minimum_wage     

        else:
            if self.senior_salary_offer > self.country.minimum_wage:
                self.senior_salary_offer = self.senior_salary_offer - 1
        

        if self.num_junior_openings != 0:
        
            if self.junior_salary_offer < Company.MAX_JUNIOR_OFFER or self.junior_salary_offer < self.country.minimum_wage:
                self.junior_salary_offer = self.junior_salary_offer + 1

                if self.junior_salary_offer < self.country.minimum_wage:
                    self.junior_salary_offer = self.country.minimum_wage
                
        else:        
            if self.junior_salary_offer > self.country.minimum_wage:            
                self.junior_salary_offer = self.junior_salary_offer - 1
        # =============== Adjusting hiring offers to stay competitive in the job market -- END ===============



        # ========== Re-evaluating company based on current account balance - START ============
        if self.company_account_balance > Company.CHANGE_COMPANY_LARGE_BALANCE: # 5000 buffer to go down
            self.company_size_type = 2 # Scales to a large company
        
        elif self.company_account_balance > Company.CHANGE_COMPANY_MEDIUM_BALANCE: # 2500 buffer to go down
            self.company_size_type = 1 # Scales to a medium company
        
        else:
            self.company_size_type = 0 # Stays or shrinks to a small company
        # ========== Re-evaluating company based on current account balance - END ============

       
        # =========== Decreasing  hiring rate as company progresses and grows - START ===========
        if self.hiring_rate > Company.MAX_HIRING_RATE:
            self.hiring_rate -= self.hiring_rate * 0.1
        else:
            self.hiring_rate = Company.MAX_HIRING_RATE
        # =========== Decreasing  hiring rate as company progresses and grows - END ===========
        
    # def pay_loan_installment():
    #     # Get the first bank --- NEED TO CHANGE THIS LATER
    #     bank_key = self.banks.keys()[0]
    #     bank  = self.banks[bank_key]

    #     interest = self.total_loan_amount * (bank.interest/100)
    #     self.total_loan_amount = self.total_loan_amount + interest

    #     if self.total_loan_amount <= (self.company_account_balance * (0.1)):
    #         amount_to_pay = self.total_loan_amount
    #     else:
    #         amount_to_pay = self.total_loan_amount * 0.1
    #         self.total_loan_amount = self.total_loan_amount - amount_to_pay

    #     bank.deposit_money(amount_to_pay)

        # 
        # installment = 


    def pay_taxes(self):
        self.year_income -= Company.CORPORATE_TAX * self.year_income # Taxes and other expenses at 40% to limit growth speed
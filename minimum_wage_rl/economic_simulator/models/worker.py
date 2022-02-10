# from MWCompany import MWCompany
from statistics import mode
import numpy as np
from django.db import models
from .country import Country
from .company import Company

class Worker(models.Model):

    BUY_EXTRA_ACCT_BALANCE = 5
    BUY_LUXURY_ACCT_BALANCE = 10
    JUNIOR_SKILL_LEVEL = 25
    SENIOR_SKILL_LEVEL = 70
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


    def __init__(self) -> None:

        self.country_obj = models.ForeignKey(to=Country, null=True, blank=True, on_delete=models.CASCADE) # list(Workers) -> Country
        self.company_obj = models.ForeignKey(to=Company, null=True, blank=True, on_delete=models.CASCADE) # list(Workers) -> Company

        self.skill_level = models.FloatField() # Money in employees account
        self.worker_account_balance = models.FloatField() # Current salary of the employee - based of entry level
        self.salary = models.FloatField() # Current skill level of the employee. Junior: (1-25) Senior: (25.1 - 70) Executive (70.1 - 100)
        self.initial_skill_level = models.FloatField()
        self.age = models.IntegerField()
        
        # remove        
        self.companyCode = None
        # remove        
        self.citizenID = None

        self.is_employed = models.BooleanField(default=False)
        self.has_company = models.BooleanField(default=False)
        self.bought_essential_product = models.BooleanField(default=False)
        self.buy_first_extra_product = models.BooleanField(default=False)
        self.buy_second_extra_product = models.BooleanField(default=False)

        self.market = None # Market

        self.country_of_residence = models.ForeignKey(to=Country, null=True, blank=True) # list(Workers) -> Country

        # dictionary
        self.bank = dict()

        # Magic


    def InitializeEmployee(self, initialBalance, citizenID, country): #MWCountry
        
        from .market import Market
        self.worker_account_balance = initialBalance

        self.salary = self.age = 0
        self.skill_level = self.initial_skill_level = 1
        self.bought_essential_product = self.buy_first_extra_product = self.buy_second_extra_product = False
        self.companyCode = -1
        self.citizenID = citizenID
        self.is_employed = self.has_company = False
        self.market = Market.get_instance()

        # Moving to a country
        self.country_of_residence = country

        # Set all banks here
        self.bank = self.country_of_residence.bank
    
    
    def BuyProducts(self, speedup):
    # 'Buying essential, extra and luxury products based on current account balance'

        # Buying essentials (food etc)
        if self.worker_account_balance < self.market.product_price * speedup:
            self.worker_account_balance = 0
            return
        else:
            self.worker_account_balance -= self.market.product_price * speedup
            self.market.market_value_year += self.market.product_price * speedup

        buyPossibility = 0
        # Buying extra
        if self.worker_account_balance > Worker.BUY_EXTRA_ACCT_BALANCE * self.market.product_price * speedup:
            buyPossibility = round(np.random.random(),2)
            
            if buyPossibility > 0.5:
                self.worker_account_balance -= self.market.product_price * speedup
                self.market.market_value_year += self.market.product_price * speedup

        # Buying luxury
        if self.worker_account_balance > Worker.BUY_LUXURY_ACCT_BALANCE * self.market.product_price * speedup:
            
            buyPossibility = round(np.random.random(),2)
            if buyPossibility > 0.75:
                self.worker_account_balance -= self.market.product_price * speedup
                self.market.market_value_year += self.market.product_price * speedup
    
    def LookForJob(self):

        companyWithBestOffer = None #MWCompany
        maxOffer = 0
        # For efficiency we do a round robin until we find the first company that satisfies the employees requirments

        # Company Iteration
        # Skill levels - Junior: (1-25) Senior: (25.1 - 70) Executive (70.1 - 100)
        # Hiring levels J(1,7,15) S(25.1,40,55) E(70.1,80,90) C is the highest
        # Hiring Salary J(2,5,10) S(15,20,25) E(40,50,60) - Newbies at a loss
        
        for _, v in self.country_of_residence.companies.items():
            
            company = v # MWCompany

            # Looking for Junior Position
            if self.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
                if company.junior_positions > 0:
                    
                    if company.junior_salary_offer > (self.salary+ Worker.DELTA_JOB_CHANGE_SALARY) or not(self.is_employed):  # +10 for efficiency and to simulate real life (nobody goes through all the companies)
                        
                        self.SwitchCompany(company, company.junior_salary_offer, self.skill_level)
                        company.junior_positions = company.junior_positions-1 
                        return

                    else:
                        if company.junior_salary_offer > maxOffer:
                            companyWithBestOffer = company
                                                    
            elif self.skill_level <= Worker.SENIOR_SKILL_LEVEL:
            
                # Looking for Senior Position
                if company.senior_positions > 0:
                
                    if company.senior_salary_offer > (self.salary + Worker.DELTA_JOB_CHANGE_SALARY) or not(self.is_employed):
            
                        self.SwitchCompany(company, company.senior_salary_offer, self.skill_level)
                        company.senior_positions = company.senior_positions-1
                        return
                    
                    else:
                    
                        if company.senior_salary_offer > maxOffer:
                            companyWithBestOffer = company                                                         
            
            else:
            
                # Looking for Executive position
                if company.executive_positions > 0:
                
                    if company.executive_salary_offer > (self.salary + Worker.DELTA_JOB_CHANGE_SALARY) or not(self.is_employed):
                    
                        self.SwitchCompany(company, company.executive_salary_offer, self.skill_level)
                        company.executive_positions = company.executive_positions-1
                        return
                    
                    else:  
                        if company.executive_salary_offer > maxOffer:
                            companyWithBestOffer = company                                                
    
    # MWCompany
    def SwitchCompany(self, newCompany, newSalary, newEntryLevelSkill):
    
        if self.companyCode != -1: # Unemployed
            self.country_of_residence.companies[self.companyCode].companyEmployees.remove(self)  # Leaving the previous company

        newCompany.companyEmployees.append(self) # Joining the new company
        self.companyCode = newCompany.companyIndex

        if newSalary < self.country_of_residence.minimum_wage:
            self.salary = self.country_of_residence.minimum_wage
        
        else:
            self.salary = newSalary
        
        self.initial_skill_level = newEntryLevelSkill
        self.is_employed = True
    
    def StartACompany(self):
        
        from minimum_wage_rl.economic_simulator.models.company import Company
        startup = Company()

        #Default = Small business

        initialBalance = Worker.INIT_SMALL_COMP_BALANCE
        companyType = Worker.SMALL_COMPANY_TYPE

        if self.worker_account_balance >= Worker.INIT_LARGE_COMP_BALANCE:
            # Start a large business
            # initialBalance = self.worker_account_balance
            companyType = Worker.LARGE_COMPANY_TYPE

        elif self.worker_account_balance >= Worker.INIT_MEDIUM_COMP_BALANCE:
            # Start a medium business
            # initialBalance = self.worker_account_balance
            companyType = Worker.MEDIUM_COMPANY_TYPE
        
        self.element_citizens()
        self.has_company = True
        startup.InitializeCompany(self.worker_account_balance, companyType, self.country_of_residence.companyIndex,self.country_of_residence)
        self.country_of_residence.companies[self.country_of_residence.companyIndex] =  startup
        self.country_of_residence.companyIndex = self.country_of_residence.companyIndex+1
    
    def explore_options(self):
        amount = 500

        changed_option = False

        if self.worker_account_balance > 500 and self.worker_account_balance < 1000:
            
            # Logic to choose banks
            bank = self.bank

            # get loan
            loan_amount = bank.lend_loan(amount)
            if loan_amount >= amount: 
                self.worker_account_balance = self.worker_account_balance + bank.lend_loan(amount)

                # start company
                self.StartACompany()
                changed_option = True

        return changed_option

    def EvaluateAndGrow(self):
        
        self.age = self.age + 1
        if self.companyCode != -1 and not(self.has_company):
        
            # Increase skill
            if self.skill_level < Worker.MAX_SKILL_LEVEL:
                self.skill_level += self.country_of_residence.companies[self.companyCode].skill_improvement_rate

            # Explore Options here
            # Either Change Job or Start a Company

            # Start a company ? 
            if self.worker_account_balance > Worker.START_COMP_ACCT_BALANCE:
                # Magic Number refactor this logic
                entrepreneurshipDrive = (self.salary + self.skill_level) / Worker.ENTREPRENERSHIP_NORMALIZING_FACTOR
                startupProbability = round(np.random.uniform(0.0,100.0),2)

                if startupProbability <= entrepreneurshipDrive:
                    self.StartACompany()
                    return            

            #Look for new job ? 
            if self.salary < Worker.JOB_CHANGE_THRESHOLD:
            
                satisfactionLevel = Worker.JOB_SATISFACTION_FACTOR - (self.skill_level - self.salary)
                jobsearchProba = round(np.random.uniform(0.0,100.0),2)
                if jobsearchProba >= satisfactionLevel:
                    self.LookForJob()
            
        else:
            # Unemployeed
            self.LookForJob()
    
    def element_citizens(self):
        if self.companyCode != -1:
            self.is_employed = False
            self.country_of_residence.companies[self.companyCode].companyEmployees.remove(self) #Leaving the previous company
        
    
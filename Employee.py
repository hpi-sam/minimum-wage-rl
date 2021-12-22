# from MWCompany import MWCompany
import numpy as np

class Employee:

    def __init__(self) -> None:
        self.skillLevel = None #Money in employees account
        self.accountBalance = None #Current salary of the employee - based of entry level
        self.salary = None #Current skill level of the employee. Junior: (1-25) Senior: (25.1 - 70) Executive (70.1 - 100)
        self.entryLevelSkill = None
        self.satisfactionLevel = None
        self.entrepreneurshipDrive = None
        self.age = None
        self.companyCode = None
        self.citizenID = None
        self.isEmployed = None
        self.hasCompany = None
        self.boughtEssentialProduct = None
        self.buyFirstExtraProduct = None
        self.buySecondExtraProduct = None

        # private GameObject marketObject
        self.market = None # Market

        # # Connection to country
        self.countryOfResidence = None #MWCountry
        self.is_adult = False

        # dictionary
        self.banks = dict()

        # Magic
        self.buy_extra_acct_balance = 5
        self.buy_luxury_acct_balance = 10
        self.junior_skill_level = 25
        self.senior_skill_level = 70
        self.delta_job_change_salary = 10
        self.init_large_comp_balance = 25000
        self.init_medium_comp_balance = 5000
        self.init_small_comp_balance = 1000
        self.large_company_type = 2
        self.medium_company_type = 1
        self.small_company_type = 0
        self.max_skill_level = 100
        self.start_comp_acct_balance = 1000
        self.entreprenership_normalizing_factor = 300
        self.job_change_threshold = 95
        self.job_satisfaction_factor = 100

    def InitializeEmployee(self, initialBalance, citizenID, country): #MWCountry
        
        from Market import Market
        self.accountBalance = initialBalance

        self.salary = self.age = 0
        self.skillLevel = self.entryLevelSkill = self.satisfactionLevel = self.entrepreneurshipDrive = 1
        self.boughtEssentialProduct = self.buyFirstExtraProduct = self.buySecondExtraProduct = False
        self.companyCode = -1
        self.citizenID = citizenID
        self.isEmployed = self.hasCompany = False
        self.market = Market.get_instance()

        # Moving to a country
        self.countryOfResidence = country

        # Set all banks here
        self.banks = self.countryOfResidence.banks
    
    
    def BuyProducts(self, speedup):
    # 'Buying essential, extra and luxury products based on current account balance'

        # Buying essentials (food etc)
        if self.accountBalance < self.market.productPrice * speedup:
            accountBalance = 0 #Leaving in poverty and food stamps
            return
        else:
            self.accountBalance -= self.market.productPrice * speedup
            self.market.marketValueYear += self.market.productPrice * speedup

        buyPossibility = 0
        # Buying extra
        if self.accountBalance > self.buy_extra_acct_balance * self.market.productPrice * speedup:
            buyPossibility = round(np.random.random(),2)
            
            if buyPossibility > 0.5:
                self.accountBalance -= self.market.productPrice * speedup
                self.market.marketValueYear += self.market.productPrice * speedup

        # Buying luxury
        if self.accountBalance > self.buy_luxury_acct_balance * self.market.productPrice * speedup:
            
            buyPossibility = round(np.random.random(),2)
            if buyPossibility > 0.75:
                self.accountBalance -= self.market.productPrice * speedup
                self.market.marketValueYear += self.market.productPrice * speedup
    
    def LookForJob(self):

        companyWithBestOffer = None #MWCompany
        maxOffer = 0
        # For efficiency we do a round robin until we find the first company that satisfies the employees requirments

        # Company Iteration
        # Skill levels - Junior: (1-25) Senior: (25.1 - 70) Executive (70.1 - 100)
        # Hiring levels J(1,7,15) S(25.1,40,55) E(70.1,80,90) C is the highest
        # Hiring Salary J(2,5,10) S(15,20,25) E(40,50,60) - Newbies at a loss
        
        for _, v in self.countryOfResidence.companies.items():
            
            company = v # MWCompany

            # Looking for Junior Position
            if self.skillLevel <= self.junior_skill_level:
                if company.juniorPositions > 0:
                    
                    if company.juniorOffer > (self.salary+ self.delta_job_change_salary) or not(self.isEmployed):  # +10 for efficiency and to simulate real life (nobody goes through all the companies)
                        
                        self.SwitchCompany(company, company.juniorOffer, self.skillLevel)
                        company.juniorPositions = company.juniorPositions-1 
                        return

                    else:
                        if company.juniorOffer > maxOffer:
                            companyWithBestOffer = company
                                                    
            elif self.skillLevel <= self.senior_skill_level:
            
                # Looking for Senior Position
                if company.seniorPositions > 0:
                
                    if company.seniorOffer > (self.salary + self.delta_job_change_salary) or not(self.isEmployed):
            
                        self.SwitchCompany(company, company.seniorOffer, self.skillLevel)
                        company.seniorPositions = company.seniorPositions-1
                        return
                    
                    else:
                    
                        if company.seniorOffer > maxOffer:
                            companyWithBestOffer = company                                                         
            
            else:
            
                # Looking for Executive position
                if company.executivePositions > 0:
                
                    if company.executiveOffer > (self.salary + self.delta_job_change_salary) or not(self.isEmployed):
                    
                        self.SwitchCompany(company, company.executiveOffer, self.skillLevel)
                        company.executivePositions = company.executivePositions-1
                        return
                    
                    else:  
                        if company.executiveOffer > maxOffer:
                            companyWithBestOffer = company                                                
    
    # MWCompany
    def SwitchCompany(self, newCompany, newSalary, newEntryLevelSkill):
    
        if self.companyCode != -1: # Unemployed
            self.countryOfResidence.companies[self.companyCode].companyEmployees.remove(self)  # Leaving the previous company

        newCompany.companyEmployees.append(self) # Joining the new company
        self.companyCode = newCompany.companyIndex

        if newSalary < self.countryOfResidence.minimumWage:
            self.salary = self.countryOfResidence.minimumWage
        
        else:
            self.salary = newSalary
        
        self.entryLevelSkill = newEntryLevelSkill
        self.isEmployed = True
    
    def StartACompany(self):
        
        from Company import Company
        startup = Company()

        #Default = Small business

        initialBalance = self.init_small_comp_balance
        companyType = self.small_company_type

        if self.accountBalance >= self.init_large_comp_balance:
            # Start a large business
            # initialBalance = self.accountBalance
            companyType = self.large_company_type

        elif self.accountBalance >= self.init_medium_comp_balance:
            # Start a medium business
            # initialBalance = self.accountBalance
            companyType = self.medium_company_type
        
        self.element_citizens()
        self.hasCompany = True
        startup.InitializeCompany(self.accountBalance, companyType, self.countryOfResidence.companyIndex,self.countryOfResidence)
        self.countryOfResidence.companies[self.countryOfResidence.companyIndex] =  startup
        self.countryOfResidence.companyIndex = self.countryOfResidence.companyIndex+1
    
    def explore_options(self):
        amount = 500

        changed_option = False

        if self.accountBalance > 500 and self.accountBalance < 1000:
            
            # Logic to choose banks
            all_banks = self.banks.values()
            bank = all_banks[0]

            # get loan
            loan_amount = bank.lend_loan(amount)
            if loan_amount >= amount: 
                self.accountBalance = self.accountBalance + bank.lend_loan(amount)

                # start company
                self.StartACompany()
                changed_option = True

        return changed_option

    def EvaluateAndGrow(self):
        
        self.age = self.age + 1
        if self.companyCode != -1 and not(self.hasCompany):
        
            # Increase skill
            if self.skillLevel < self.max_skill_level:
                self.skillLevel += self.countryOfResidence.companies[self.companyCode].skilIncrease

            # Explore Options here
            # Either Change Job or Start a Company

            # Start a company ? 
            if self.accountBalance > self.start_comp_acct_balance:
                # Magic Number refactor this logic
                entrepreneurshipDrive = (self.salary + self.skillLevel) / self.entreprenership_normalizing_factor
                startupProbability = round(np.random.uniform(0.0,100.0),2)

                if startupProbability <= entrepreneurshipDrive:
                    self.StartACompany()
                    return            

            #Look for new job ? 
            if self.salary < self.job_change_threshold:
            
                satisfactionLevel = self.job_satisfaction_factor - (self.skillLevel - self.salary)
                jobsearchProba = round(np.random.uniform(0.0,100.0),2)
                if jobsearchProba >= satisfactionLevel:
                    self.LookForJob()
            
        else:
            # Unemployeed
            self.LookForJob()
    
    def element_citizens(self):
        if self.companyCode != -1:
            self.isEmployed = False
            self.countryOfResidence.companies[self.companyCode].companyEmployees.remove(self) #Leaving the previous company
        
    
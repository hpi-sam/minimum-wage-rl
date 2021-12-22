class Company:
    
    def __init__(self) -> None:
        # Profile
        self.companyIndex = None #The unique identifier of a company
        self.companyType = None # 0 - small , 1 - medium, 2 - large

        # Balance distributions
        self.hiringRate = None # What percentage of the balance does the company spend on hiring -- DEPRECATED

        # Employees & Hiring
        self.juniorHiringRatio = None # How many juniors to hire before moving to next round
        self.seniorHiringRatio = None # How many seniors to hire on current round before moving to juniors
        self.executiveHiringRatio = None # How many executives to hire on current round before moving to senior level
        self.skilIncrease = None # How fast does the employee skill increase each year

        # // Hiring levels J(1,7,15) S(25.1,40,55) E(70.1,80,90) -  -- DEPRECATED

        # Job positions - Junior: (1-25) Senior: (25.1 - 70) Executive (70.1 - 100)
        self.juniorPositions = None
        self.seniorPositions = None
        self.executivePositions = None

        # Offers for new positions to employees - Maximum based on J,S,E levels and how much the company can afford to pay
        self.juniorOffer = 0
        self.seniorOffer = 0
        self.executiveOffer = 0

        self.companyEmployees = list() #List<MWEmployee> 

        # Financials
        self.accountBalance = None # The balance sheet of the company
        self.yearIncome = 0 # Money made/lost during each year

        # Connection to country
        self.countryInc = None # MWCountry

        # Magic Numbers
        self.tax_percent = 0.20
        self.max_executive_salary = 95       # 3 * self.countryInc.minimumWage
        self.max_senior_salary = 65          # 1.5 * self.countryInc.minimumWage
        self.max_junior_offer = 20          # self.countryInc.minimumWage
        self.max_hiringRate = 0.001
        self.change_company_large_balance = 20000
        self.change_company_medium_balance = 2500

        # Bank
        self.has_loan = None
        self.total_loan_amount = None
        self.banks = dict()
        self.loan_to_pay_next_year = None
    
    def InitializeCompany(self, initialBalance, companyType, companyIndex, country): #MWCountry
    
        self.accountBalance = initialBalance
        self.companyType = companyType
        self.companyIndex = companyIndex
        self.countryInc = country

        self.hiringRate = 0.02 # 2% of balance per year

        self.juniorPositions = self.seniorPositions = self.executivePositions = 0
        self.juniorOffer = self.seniorOffer = self.executiveOffer = self.countryInc.minimumWage # Initializing to the bear minimum because companies are jackasses

        if companyType == 0: # Small
            self.executiveHiringRatio = 2
            self.seniorHiringRatio = 2
            self.juniorHiringRatio = 6
            self.skilIncrease = 1
        
        elif companyType == 1: # Medium
            self.executiveHiringRatio = 2
            self.seniorHiringRatio = 6
            self.juniorHiringRatio = 6
            self.skilIncrease = 1.5
        
        else: # Large
            self.executiveHiringRatio = 6
            self.seniorHiringRatio = 6
            self.juniorHiringRatio = 6
            self.skilIncrease = 2

        self.companyEmployees = list() #List<MWEmployee>()

        # Set all banks here
        self.banks = self.countryInc.banks


    def OpenJobPositions(self):
    
        self.juniorPositions = self.seniorPositions = self.executivePositions = 0
        hrInvestment = self.hiringRate * self.accountBalance

        #  Executive Hiring
        for _ in  range(self.executiveHiringRatio):
        
            if hrInvestment > self.executiveOffer and hrInvestment >= self.countryInc.minimumWage:
                self.executivePositions = self.executivePositions + 1
                hrInvestment -= self.executiveOffer
            
            else:
                break

        # Senior Hiring
        for _ in range(self.seniorHiringRatio):
    
            if hrInvestment > self.seniorOffer and hrInvestment >= self.countryInc.minimumWage:
                self.seniorPositions = self.seniorPositions + 1
                hrInvestment -= self.seniorOffer
            
            else:            
                break               

        # Junior Hiring
        for _ in range(self.juniorHiringRatio):

            if hrInvestment > self.juniorOffer and hrInvestment >= self.countryInc.minimumWage:
                self.juniorPositions = self.juniorPositions + 1
                hrInvestment -= self.juniorOffer
            
            else:
                break

        return self.juniorPositions + self.seniorPositions + self.executivePositions

    def EvaluateAndReset(self):
    
        self.PayTaxes()
        self.yearIncome = 0        

        # =============== Adjusting hiring offers to stay competitive in the job market -- START ===============
        if self.executivePositions != 0:
        
            if self.executiveOffer < self.max_executive_salary:
            
                self.executiveOffer = self.executiveOffer + 1
                if self.executiveOffer < self.countryInc.minimumWage:                
                    self.executiveOffer = self.countryInc.minimumWage        
        
        else:        
            if self.executiveOffer > self.countryInc.minimumWage:
                self.executiveOffer = self.executiveOffer - 1
            
        if self.seniorPositions != 0:
        
            if self.seniorOffer < self.max_senior_salary or self.seniorOffer < self.countryInc.minimumWage:
                self.seniorOffer = self.seniorOffer + 1
                
                if self.seniorOffer < self.countryInc.minimumWage:
                    self.seniorOffer = self.countryInc.minimumWage     

        else:
            if self.seniorOffer > self.countryInc.minimumWage:
                self.seniorOffer = self.seniorOffer - 1
        

        if self.juniorPositions != 0:
        
            if self.juniorOffer < self.max_junior_offer or self.juniorOffer < self.countryInc.minimumWage:
                self.juniorOffer = self.juniorOffer + 1
                if self.juniorOffer < self.countryInc.minimumWage:
                    self.juniorOffer = self.countryInc.minimumWage
                
        else:        
            if self.juniorOffer > self.countryInc.minimumWage:            
                self.juniorOffer = self.juniorOffer - 1
        # =============== Adjusting hiring offers to stay competitive in the job market -- END ===============



        # ========== Re-evaluating company based on current account balance - START ============
        if self.accountBalance > self.change_company_large_balance: # 5000 buffer to go down
            self.companyType = 2 # Scales to a large company
        
        elif self.accountBalance > self.change_company_medium_balance: # 2500 buffer to go down
            self.companyType = 1 # Scales to a medium company
        
        else:
            self.companyType = 0 # Stays or shrinks to a small company
        # ========== Re-evaluating company based on current account balance - END ============

       
        # =========== Decreasing  hiring rate as company progresses and grows - START ===========
        if self.hiringRate > self.max_hiringRate:
            self.hiringRate -= self.hiringRate * 0.1
        else:
            self.hiringRate = self.max_hiringRate
        # =========== Decreasing  hiring rate as company progresses and grows - END ===========
        
    def pay_loan_installment():
        # Get the first bank --- NEED TO CHANGE THIS LATER
        bank_key = self.banks.keys()[0]
        bank  = self.banks[bank_key]

        interest = self.total_loan_amount * (bank.interest/100)
        self.total_loan_amount = self.total_loan_amount + interest

        if self.total_loan_amount <= (self.accountBalance * (0.1)):
            amount_to_pay = self.total_loan_amount
        else:
            amount_to_pay = self.total_loan_amount * 0.1
            self.total_loan_amount = self.total_loan_amount - amount_to_pay

        bank.receive_money(amount_to_pay)

        # 
        # installment = 


    def PayTaxes(self):
        self.yearIncome -= self.tax_percent * self.yearIncome # Taxes and other expenses at 40% to limit growth speed
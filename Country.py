import numpy as np
from numpy import random
from Employee import Employee
from Company import Company
# from Market import Market
from Bank import Bank

class Country:

    __country_instance = None
    
    @staticmethod
    def get_instance():
        if Country.__country_instance == None:
            Country()
        return Country.__country_instance

    def __init__(self) -> None:

        if Country.__country_instance !=None:
            raise Exception("Market instance already exists, USE get_instance method")
        else:
            Country.__country_instance = self


        self.countryCode = None # The name of the country
    
        # /***
        #  * Policies:
        #  * 0 - No minimum wage regulation ($1)
        #  * 1 - Adjusted yearly based on inflation (France model)
        #  * 2 - Dramatic increases every X years (America model)
        #  * 3 - AI (Not included here)
        #  */

        self.policyCode = 0 # The minimum wage policy/strategy followed 
        self.companies = dict() # new Dictionary<int, MWCompany>() = None
        self.citizens = dict() # new Dictionary<int, MWEmployee>() = None

        # SET LATER
        self.minimumWage = 2 # The current minimum wage of this country
        self.companyIndex = None # A unique identifer/counter for new countries
        self.citizenID = None # A unique identifier/counter for new citizens

        # Statistics
        self.yearlyProducedValue = None # Something like GDP
        self.numOfSmallBusinesses = None
        self.numOfMediumBusinesses = None
        self.numOfLargeBusinesses = None
        
        # ========================== CHECK THIS ==========================
        self.initial_num_small_business = 3
        self.initialNumMB = 2
        self.initialNumLB = 1
        
        self.initialNumOfCitizens = None

        self.unemploymentRate = None
        self.totalUnemployed = None
        self.averageIncome = None # The average income of all citizens
        self.averageSkillLevel = None # The average skill level of all citizens
        self.averageBalance = None
        self.povertyRate = None # Percentage of people living bellow poverty levels
        self.totalJuniorPos = None
        self.totalSeniorPos = None
        self.totalExecutivePos = None

        # Connection to global market
        # private GameObject marketObject = None
        self.market = None # Market

        # Magic Numbers (Bank)
        self.fixed_cash_printing = None
        self.total_money_printed = None
        self.number_of_banks = 1

        self.weight_lb = 2
        self.weight_mb = 1.5
        self.weight_sb = 1

        self.wage_threshold = 50
        self.negative_reward = -1 
        
        # dictionary<int, Bank>
        self.banks = dict()

    
    def EstablishCountry(self):

        self.yearlyProducedValue = 0
        self.unemploymentRate = 100
        self.averageSkillLevel = self.averageIncome = 1
        self.povertyRate = 0
        self.averageBalance = 0
        self.companyIndex = 0
        self.citizenID = 0
        self.totalUnemployed = 0
        self.bank_index = 0
        self.totalJuniorPos = self.totalSeniorPos = self.totalExecutivePos = 0
        self.numOfSmallBusinesses = self.initial_num_small_business
        self.numOfMediumBusinesses = self.initialNumMB
        self.numOfLargeBusinesses = self.initialNumLB

        # Magic Numbers
        self.fixed_cash_printing = 500
        self.total_money_printed = 0
        self.number_of_banks = 1

        # Connecting to global market
        # marketObject = GameObject.Find("Market");
        from Market import Market
        self.market = Market.get_instance() #marketObject.GetComponent<Market>();

        # Creating Initial companies
        for _ in range(self.numOfSmallBusinesses): # small
            company = Company()
            company.InitializeCompany(1000, 0, self.companyIndex,self)
            self.companies[self.companyIndex] =  company
            self.companyIndex = self.companyIndex + 1
        

        for _ in range(self.numOfMediumBusinesses): # medium
            company = Company()
            company.InitializeCompany(5000, 1, self.companyIndex,self)
            self.companies[self.companyIndex] =  company
            self.companyIndex = self.companyIndex + 1 

        for _ in range(self.numOfLargeBusinesses): # large
            company = Company()
            company.InitializeCompany(25000, 2, self.companyIndex,self)
            self.companies[self.companyIndex] =  company
            self.companyIndex = self.companyIndex + 1

        # Adding first citizens
        self.add_new_citizens(self.initialNumOfCitizens)

        # Create banks        
        for index in range(self.number_of_banks):
            self.bank_index += 1
            bank = Bank(self.bank_index)            
            self.banks[self.bank_index] = bank
        
        print("=====================================================")
        print(type(self.banks))
        print("=====================================================")
        print(type(self.banks.keys()))
        print("=====================================================")
        print(self.banks.keys())

        # Initialize banks
        self.print_money(self.banks)

    def ResetCountry(self):
        self.companies = dict()
        self.citizens = dict()
        self.minimumWage = 2
        self.numOfSmallBusinesses = self.initial_num_small_business
        self.numOfMediumBusinesses = self.initialNumMB
        self.numOfLargeBusinesses = self.initialNumLB

    def add_new_citizens(self, amount):
        for _ in range(amount):
            citizen = Employee()
            citizen.InitializeEmployee(0, self.citizenID, self)
            self.citizens[self.citizenID] =  citizen
            self.citizenID = self.citizenID + 1
        
    def calculate_statistics(self):
    # Calculate the yearly statistics for all active Companies and Citizens in this country

        # print("================Am here===============")
        # Calculate statistics here     
        self.numOfSmallBusinesses = self.numOfMediumBusinesses = self.numOfLargeBusinesses = 0
        self.totalJuniorPos = self.totalSeniorPos = self.totalExecutivePos = 0

        # Iterating through all active companies
        for _,val in self.companies.items():
        
            # do something with entry.Value or entry.Key
            company = val

            # of small,med,large companies
            if company.companyType == 0:
                self.numOfSmallBusinesses = self.numOfSmallBusinesses + 1

            elif company.companyType == 1:            
                self.numOfMediumBusinesses = self.numOfMediumBusinesses + 1
            
            else:
                self.numOfLargeBusinesses = self.numOfLargeBusinesses + 1
            
            self.totalJuniorPos += company.juniorPositions
            self.totalSeniorPos += company.seniorPositions
            self.totalExecutivePos += company.executivePositions

            self.yearlyProducedValue += company.yearIncome # Adding company's yearly income to the GDP
        

        # Iterating through all alive citizens
        totalSkillLevel = 0
        totalSalary = 0
        totalPovertyCnt = 0
        totalAccountBalance = 0
        totalEmployed = 0
        totalUnemployed = 0

        for _,val in self.citizens.items():
            citizen = val
            
            if citizen.salary < self.market.productPrice*30: # Can't afford to buy necessary product (e.g. food)
                totalPovertyCnt = totalPovertyCnt + 1

            if not(citizen.isEmployed):            
                totalUnemployed = totalUnemployed + 1
            
            else:
                # print("===========================AM HERE========================")
                totalSalary += citizen.salary
                totalSkillLevel += citizen.skillLevel
                totalEmployed = totalEmployed + 1
            
            totalAccountBalance += citizen.accountBalance
        

        citizensCount = len(self.citizens.keys())
        self.unemploymentRate = round((totalUnemployed / citizensCount * 100.0), 1)
        self.povertyRate = round((totalPovertyCnt / citizensCount * 100.0), 1)
        
        if totalEmployed > 0:
            self.averageIncome = round((totalSalary / (totalEmployed * 1.0)), 1)
            self.averageSkillLevel = round((totalSkillLevel / (totalEmployed * 1.0)), 1)
        
        self.averageBalance = round((totalAccountBalance / (citizensCount * 1.0)), 1)

        statisticsString = "GDP(comp): " + str(self.yearlyProducedValue) + " #SB " + str(self.numOfSmallBusinesses) + " #MB " + str(self.numOfMediumBusinesses) +" #LB " + str(self.numOfLargeBusinesses) + " Unemployment " + str(self.unemploymentRate) + " AvSalary " + str(self.averageIncome) + " AvSkill " + str(self.averageSkillLevel) + " Poverty " + str(self.povertyRate) + "% AvBalance: " + str(self.averageBalance)

        self.yearlyProducedValue = 0

        return statisticsString

    def UpdateMinimumWage(self):

        if self.policyCode == 0:
            # No minimum wage regulation
            self.minimumWage = 2
        
        elif self.policyCode == 1:        
            # Adjusted yearly based on inflation (France model)
            # print("In MWCountry - line 196")
            # print(self.minimumWage)
            # print(self.market.inflationRate)
            self.minimumWage += self.minimumWage * self.market.inflationRate # CHANGE FOR YEAR??? DAYS TO MATCH PRODUCT SHIT
        
        elif self.policyCode == 2:
            # Dramatic increases every X(random) years (America model) 5%
            changeProba = round(np.random.uniform(0.0,1.0) ,2)
            if changeProba <= 0.15: # 10% chance            
                self.minimumWage += self.minimumWage * 0.05
        else:
            pass

        # This is case it reaches the maximum possible MW for this simulations settings
        if self.minimumWage > 90:
            self.minimumWage = 90

        # ELSE policy is decided by the AI
    
    def get_current_state_reward(self):
        
        state_values = []

        state_values.append(self.unemploymentRate)
        state_values.append(self.povertyRate)
        state_values.append(self.minimumWage)
        state_values.append(self.averageIncome - 30 * self.market.productPrice)

        reward = self.calculate_reward()

        state_reward = dict()
        state_reward["state"] = state_values
        state_reward["reward"] = reward

        return state_reward

    def calculate_reward(self):
        # 3. Companies
        r1 = self.weight_lb * np.log10(self.numOfLargeBusinesses/self.minimumWage + 1)
        r2 = self.weight_mb * np.log10(self.numOfMediumBusinesses / self.minimumWage + 1)
        r3 = self.weight_sb * np.log10(self.numOfSmallBusinesses / self.minimumWage + 1)
        r4 = 0.0

        # r1 = 1/self.povertyRate
        # r2 = 1/self.unemploymentRate

        if self.minimumWage > self.wage_threshold:
            r4 = self.negative_reward

        # return torch.tensor([r1 + r2 + r3 + r4])
        return r1 + r2 + r3 + r4
        # return r1 + r2

    def print_money(self, banks):
        
        self.total_money_printed += self.fixed_cash_printing
        each_cash_infusion = self.fixed_cash_printing / len(banks.keys())

        for _, each_bank in banks.items():
            each_bank.receive_money(each_cash_infusion)


# from ..models.worker import Worker

from ..models.worker import Worker
from ..models.bank import Bank
from ..models.country import Country
from ..models.market import Market
from ..models.company import Company

def Start():

    # Create Market object
    # Create Country object
    # Create Company object
    # Assign country to it
    
    # Create Worker object
    # Assign country to it
    # Assign Company to it

   
    market_obj = Market.get_instance()
    market_obj.month = market_obj.year = 0
    market_obj.initial_product_price = market_obj.product_price
    market_obj.market_value_year = 0
    market_obj.run = 0

    # self.month = self.year = 0
    # self.initial_product_price = self.product_price
    # self.market_value_year = 0
    # self.run = 0
    
    
    # em = AICountry.get_instance()        
    
    # Apply user settings from menu preferences 5000
    # ApplyUserSettings(0.01, 5000, 2, 2, 1)
    market_obj.inflation_rate = 0.01

    # self.ApplyUserSettings(inflation,int(self.parser.get("market","citizens")), 
    # int(self.parser.get("market","small_business")),  
    # int(self.parser.get("market","medium_business")), int(self.parser.get("market","large_business")))
    # testingCountry = Country.get_instance()
    country = EstablishCountry()
    country.market = market_obj

    # self.initialize_network()

    country.save()

    # if bool(int(self.parser.get("scenario","unregulated"))):
    #     self.testingCountry.policyCode = 0
    #     self.out_file_name = self.parser.get("file","unregulated_file")

    # if bool(int(self.parser.get("scenario","adjusted"))):
    #     self.testingCountry.policyCode = 1
    #     self.out_file_name = self.parser.get("file","adjusted_file")

    # if bool(int(self.parser.get("scenario","dramatic"))):
    #     self.testingCountry.policyCode = 2
    #     self.out_file_name = self.parser.get("file","dramatic_file")

    # if bool(int(self.parser.get("scenario","ai_scenario"))):
    #     self.testingCountry.policyCode = 3
    #     self.out_file_name = self.parser.get("file","ai_scenario_file")
    #     self.aiScenario = True

def EstablishCountry():
    
    country = Country.get_instance()

    country.yearly_produced_value = 0
    country.unemployment_rate = 100
    country.average_skill_level = country.average_income = 1
    country.poverty_rate = 0
    country.average_balance = 0
    country.total_unemployed = 0
    country.bank_index = 0
    country.total_jun_jobs = country.total_senior_jobs = country.total_executive_jobs = 0

    # self.yearly_produced_value = 0
    # self.unemployment_rate = 100
    # self.average_skill_level = self.average_income = 1
    # self.poverty_rate = 0
    # self.average_balance = 0
    # self.total_unemployed = 0
    # self.bank_index = 0
    # self.total_jun_jobs = self.total_senior_jobs = self.total_executive_jobs = 0
    # self.num_small_companies = Country.INITIAL_NUM_SMALL_COMPANIES
    # self.num_medium_company = Country.INITIAL_NUM_MEDIUM_COMPANIES
    # self.num_large_company = Country.INITIAL_NUM_LARGE_COMPANIES

    # Magic Numbers
    # self.fixed_cash_printing = 500
    # self.total_money_printed = 0
    # self.number_of_banks = 1

    # Connecting to global market
    # marketObject = GameObject.Find("Market");
    #marketObject.GetComponent<Market>();

    # startup
    # Creating Initial companies
    for _ in range(Country.INITIAL_NUM_SMALL_COMPANIES): # small
        company = Company()
        InitializeCompany(company, 1000, 0, country)
        # self.companies[self.companyIndex] =  company
        # self.companyIndex = self.companyIndex + 1
    
    for _ in range(Country.INITIAL_NUM_MEDIUM_COMPANIES): # medium
        company = Company()
        company.InitializeCompany(company, 5000, 1,country)
        # self.companies[self.companyIndex] =  company
        # self.companyIndex = self.companyIndex + 1 

    for _ in range(Country.INITIAL_NUM_LARGE_COMPANIES): # large
        company = Company()
        company.InitializeCompany(company, 25000, 2, country)
        # self.companies[self.companyIndex] =  company
        # self.companyIndex = self.companyIndex + 1

    bank = Bank()         
    country.bank = bank
    
    # Initialize banks
    country.print_money(country.bank)
    
    # Adding first citizens
    add_new_citizens(country, Country.INITIAL_NUM_OF_CITIZENS)

    return country

def InitializeCompany(company, initialBalance, companyType, country):

    company.company_account_balance = initialBalance
    company.company_size_type = companyType
    company.country = country

    company.hiring_rate = 0.02

    company.junior_positions = company.senior_positions = company.executive_positions = 0
    company.junior_salary_offer = company.senior_salary_offer = company.executive_salary_offer = company.country.minimum_wage # Initializing to the bear minimum because companies are jackasses

    if companyType == 0: # Small
        company.executive_hiring_ratio = 2
        company.senior_hiring_ratio = 2
        company.junior_hiring_ratio = 6
        company.skill_improvement_rate = 1
    
    elif companyType == 1: # Medium
        company.executive_hiring_ratio = 2
        company.senior_hiring_ratio = 6
        company.junior_hiring_ratio = 6
        company.skill_improvement_rate = 1.5
    
    else: # Large
        company.executive_hiring_ratio = 6
        company.senior_hiring_ratio = 6
        company.junior_hiring_ratio = 6
        company.skill_improvement_rate = 2

    company.companyEmployees = list() #List<MWEmployee>()

# startup
def add_new_citizens(country, amount):
    for _ in range(amount):
        citizen = Worker()
        InitializeEmployee(0, country, citizen)
        # self.workers[self.citizenID] =  citizen
        # self.citizenID = self.citizenID + 1

def InitializeEmployee(country, initialBalance, citizen): #MWCountry
        
    citizen.worker_account_balance = initialBalance

    citizen.salary = citizen.age = 0
    citizen.skill_level = citizen.initial_skill_level = 1
    citizen.bought_essential_product = citizen.buy_first_extra_product = citizen.buy_second_extra_product = False
    citizen.companyCode = -1
    # self.citizenID = citizenID
    citizen.is_employed = citizen.has_company = False
    # self.market = Market.get_instance()

    # Moving to a country
    citizen.country_of_residence = country

    # Set all banks here
    citizen.bank = country.bank
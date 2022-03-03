from ..models.worker import Worker
from ..models.bank import Bank
from ..models.country import Country
from ..models.market import Market
from ..models.company import Company
from .config import ConfigurationParser
from django.db import models

all_citizens_list = []
all_companies_list = []

config_parser = ConfigurationParser.get_instance().parser

def Start():

    market_obj = Market()
    market_obj.month = market_obj.year = 0
    market_obj.market_value_year = 0
    market_obj.run = 0
    # market_obj.inflation_rate = 0.01

    country = EstablishCountry()
    
    country.market = market_obj
    market_obj.save()
    country.save()

    # SAVE ALL COMPANIES
    for each_company in all_companies_list:
        each_company.save()

    # SAVE ALL COUNTRIES
    for each_citizen in all_citizens_list:
        each_citizen.save()

def EstablishCountry():
    
    country = Country()

    country.yearly_produced_value = 0

    # Calculate and remove this
    country.unemployment_rate = 100
    country.average_skill_level = country.average_income = 1
    country.poverty_rate = 0
    country.total_unemployed = 0
    country.total_jun_jobs = country.total_senior_jobs = country.total_executive_jobs = 0

    # startup
    # Creating Initial companies
    for _ in range(Country.INITIAL_NUM_SMALL_COMPANIES): # small
        company = Company()
        InitializeCompany(company, 1000, 0, country)
        all_companies_list.append(company)
    
    for _ in range(Country.INITIAL_NUM_MEDIUM_COMPANIES): # medium
        company = Company()
        InitializeCompany(company, 5000, 1,country)
        all_companies_list.append(company)

    for _ in range(Country.INITIAL_NUM_LARGE_COMPANIES): # large
        company = Company()
        InitializeCompany(company, 25000, 2, country)
        all_companies_list.append(company)

    # Adding first citizens
    add_new_citizens(country, Country.INITIAL_NUM_OF_CITIZENS)


    bank = Bank()         
    country.bank = bank
    country.total_money_printed = 500.0
    bank.initialize_bank(500.0)   
    bank.save()

    return country

def InitializeCompany(company, initialBalance, companyType, country):

    company.company_account_balance = initialBalance
    company.company_size_type = companyType
    company.country = country

    company.hiring_rate = 0.02

    company.num_junior_openings = company.num_senior_openings = company.num_executive_openings = 0
    company.junior_salary_offer = company.senior_salary_offer = company.executive_salary_offer = country.minimum_wage # Initializing to the bear minimum because companies are jackasses

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

# startup
def add_new_citizens(country, amount):
    for _ in range(amount):
        citizen = Worker()
        InitializeEmployee(0, country, citizen)
        all_citizens_list.append(citizen)

def InitializeEmployee(initialBalance, country, citizen): #MWCountry
        
    citizen.worker_account_balance = initialBalance

    citizen.salary = citizen.age = 0
    citizen.skill_level = 1
    # citizen.initial_skill_level = 1
    citizen.bought_essential_product = citizen.buy_first_extra_product = citizen.buy_second_extra_product = False
    citizen.is_employed = citizen.has_company = False

    # Moving to a country
    citizen.country_of_residence = country
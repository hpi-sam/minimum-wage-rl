import numpy as np

# from economic_simulator.models import country
from ...models.worker import Worker
from ...models.country import Country
from ...models.company import Company
from ...models.market import Market
from . import company_module

def create_country(country, all_companies_list):
    
    country.yearly_produced_value = 0

    # Calculate and remove this
    country.unemployment_rate = 100
    country.average_skill_level = country.average_income = 1
    country.poverty_rate = 0
    country.total_unemployed = 0
    country.total_jun_jobs = country.total_senior_jobs = country.total_executive_jobs = 0

    # Adding first citizens



def create_company(country):

    all_companies_list = []

    # Creating Initial companies
    for _ in range(Country.INITIAL_NUM_SMALL_COMPANIES): # small
        company = Company()
        company_module.initialize_company(company, Market.SMALL_CMP_INIT_BALANCE, country)
        all_companies_list.append(company)
    
    for _ in range(Country.INITIAL_NUM_MEDIUM_COMPANIES): # medium
        company = Company()
        company_module.initialize_company(company, Market.MEDIUM_CMP_INIT_BALANCE, country)
        all_companies_list.append(company)

    for _ in range(Country.INITIAL_NUM_LARGE_COMPANIES): # large
        company = Company()
        company_module.initialize_company(company, Market.LARGE_CMP_INIT_BALANCE, country)
        all_companies_list.append(company)
    
    return all_companies_list

def create_bank(bank, country, initial_bank_balance):
    bank.initialize_bank(initial_bank_balance)
    country.bank = bank
    


def add_new_workers(country, num_of_citizens):

    worker_list = []

    # Skill-Level and Age are chosen from uniform distribution

    # 1: Add juniors in population
    num_of_juniors = num_of_citizens
    for _ in range(num_of_juniors):
        worker = Worker()
        age = np.random.randint(18,20)
        skill_level = np.random.randint(6, Worker.JUNIOR_SKILL_LEVEL-5)
        initialize_employee(Worker.INITIAL_WORKER_BANK_BALANCE, country, worker, age, skill_level)
        worker_list.append(worker)
    
    # 2: Add seniors in population
    num_of_seniors = num_of_citizens
    for _ in range(num_of_seniors):
        worker = Worker()
        age = np.random.randint(20,23)
        skill_level = np.random.randint(Worker.JUNIOR_SKILL_LEVEL+1, Worker.SENIOR_SKILL_LEVEL-5)
        initialize_employee(Worker.INITIAL_WORKER_BANK_BALANCE, country, worker, age, skill_level)
        worker_list.append(worker)
    
    # 3: Add executives in population
    num_of_executives = num_of_citizens
    for _ in range(num_of_executives):
        worker = Worker()
        age = np.random.randint(23,25)
        skill_level = np.random.randint(Worker.SENIOR_SKILL_LEVEL+1, Worker.EXEC_SKILL_LEVEL-5)
        initialize_employee(Worker.INITIAL_WORKER_BANK_BALANCE, country, worker, age, skill_level)
        worker_list.append(worker)

    country.population = country.population + (num_of_juniors + num_of_seniors + num_of_executives)

    return worker_list, num_of_juniors, num_of_seniors, num_of_executives


def initialize_employee(initial_balance, country, worker, age, skill_level):
    
    worker.worker_account_balance = initial_balance
    worker.age = age

    worker.salary = 0
    worker.skill_level = skill_level
    # citizen.initial_skill_level = 1
    # worker.bought_essential_product = worker.buy_first_extra_product = worker.buy_second_extra_product = False
    worker.is_employed = worker.has_company = False

    # Moving to a country
    worker.country_of_residence = country
    worker.worker_score = (Worker.SKILL_SET_WEIGHTAGE * worker.skill_level) + (Worker.EXPERIENCE_WEIGHTAGE * (worker.age-18))
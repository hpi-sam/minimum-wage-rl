from math import floor
import numpy as np

# from economic_simulator.models import country
from ...models.worker import Worker
from ...models.country import Country
from ...models.company import Company
from ...models.market import Market
from . import company_module

def create_country(country, each_level_population, ai_flag):
    
    country.yearly_produced_value = 0

    # Calculate and remove this
    country.unemployment_rate = 100
    country.average_skill_level = country.average_income = 1
    country.poverty_rate = 0
    country.total_unemployed = 0
    country.total_jun_jobs = country.total_senior_jobs = country.total_executive_jobs = 0
    country.ai_flag = ai_flag
    country.INITIAL_EACH_LEVEL_POPULATION = each_level_population
    country.population = each_level_population * 3

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

def create_bank(bank, initial_bank_balance):
    bank.initialize_bank(initial_bank_balance)
    return bank
    
def increase_population(country):
    increased_population = country.population * country.population_increase

    actual_increased_population = increased_population
    # int(np.random.normal(loc=increased_population, scale=2.0))

    each_level_population = int(actual_increased_population/3)
    extra = actual_increased_population%3

    jun_worker_population = each_level_population
    sen_worker_population = each_level_population
    exec_worker_population = each_level_population

    while extra > 0:
        jun_worker_population = jun_worker_population + 1
        extra = extra - 1
        if extra>0:
            sen_worker_population = sen_worker_population + 1
            extra = extra - 1

    new_workers_list = []

    # Add Juniors
    for i in range(jun_worker_population):
        worker = Worker()
        age = 19
        # np.random.randint(18,20)
        skill_level = 8
        # np.random.randint(7, Worker.JUNIOR_SKILL_LEVEL-5)
        initialize_employee(Worker.INITIAL_WORKER_BANK_BALANCE, country, worker, age, skill_level)
        new_workers_list.append(worker)
    
    # Add Seniors
    for i in range(sen_worker_population):
        worker = Worker()
        age = 21
        # np.random.randint(20,23)
        skill_level = 16
        # np.random.randint(Worker.JUNIOR_SKILL_LEVEL+1, Worker.SENIOR_SKILL_LEVEL-5)
        initialize_employee(Worker.INITIAL_WORKER_BANK_BALANCE, country, worker, age, skill_level)
        new_workers_list.append(worker)
        
    # Add Executives
    for i in range(exec_worker_population):
        worker = Worker()
        age = 24
        # np.random.randint(23,25)
        skill_level = 26
        # np.random.randint(Worker.SENIOR_SKILL_LEVEL+1, Worker.EXEC_SKILL_LEVEL-5)
        initialize_employee(Worker.INITIAL_WORKER_BANK_BALANCE, country, worker, age, skill_level)
        new_workers_list.append(worker)

    new_workers_list = sorted(new_workers_list, key=lambda x: x.worker_score, reverse=True)
    country.population = country.population + len(new_workers_list)

    return new_workers_list

def add_new_workers(country, num_of_citizens, employed_at_startup, JUN_SKILL_LOW_LIM, JUN_SKILL_HIGH_LIM_OFFSET, SEN_SKILL_LOW_LIM_OFFSET, SEN_SKILL_HIGH_LIM_OFFSET, EXEC_SKILL_LOW_LIM_OFFSET, EXEC_SKILL_HIGH_LIM_OFFSET):

    # worker_list = []
    jun_worker_list = []
    sen_worker_list = []
    exec_worker_list = []
    # Skill-Level and Age are chosen from uniform distribution
    
    # 1: Add juniors in population
    num_of_juniors = num_of_citizens
    for _ in range(num_of_juniors):
        worker = Worker()
        age = 19
        # np.random.randint(18,20)
        skill_level = 8
        # np.random.randint(JUN_SKILL_LOW_LIM, Worker.JUNIOR_SKILL_LEVEL-JUN_SKILL_HIGH_LIM_OFFSET)
        initialize_employee(Worker.INITIAL_WORKER_BANK_BALANCE, country, worker, age, skill_level)
        jun_worker_list.append(worker)        
        # worker_list.append(worker)
    
    # 2: Add seniors in population
    num_of_seniors = num_of_citizens
    for _ in range(num_of_seniors):
        worker = Worker()
        age = 21
        # np.random.randint(20,23)
        skill_level = 16
        # np.random.randint(Worker.JUNIOR_SKILL_LEVEL+SEN_SKILL_LOW_LIM_OFFSET, Worker.SENIOR_SKILL_LEVEL-SEN_SKILL_HIGH_LIM_OFFSET)
        initialize_employee(Worker.INITIAL_WORKER_BANK_BALANCE, country, worker, age, skill_level)
        sen_worker_list.append(worker)
        # worker_list.append(worker)
    
    # 3: Add executives in population
    num_of_executives = num_of_citizens
    for _ in range(num_of_executives):
        worker = Worker()
        age = 24
        # np.random.randint(23,25)
        skill_level = 26
        # np.random.randint(Worker.SENIOR_SKILL_LEVEL+EXEC_SKILL_LOW_LIM_OFFSET, Worker.EXEC_SKILL_LEVEL-EXEC_SKILL_HIGH_LIM_OFFSET)
        initialize_employee(Worker.INITIAL_WORKER_BANK_BALANCE, country, worker, age, skill_level)
        exec_worker_list.append(worker)
        # worker_list.append(worker)
    
    employed_jun_list, employed_sen_list, employed_exec_list, unemp_workers_list = initialize_employed_population(jun_worker_list, sen_worker_list, exec_worker_list, employed_at_startup)
    # country.population = country.population + (num_of_juniors + num_of_seniors + num_of_executives)

    unemp_num_of_jun = num_of_juniors - len(employed_jun_list)
    unemp_num_of_sen = num_of_seniors - len(employed_sen_list)
    unemp_num_of_exec = num_of_executives - len(employed_exec_list)

    return unemp_workers_list, unemp_num_of_jun, unemp_num_of_sen, unemp_num_of_exec, employed_jun_list, employed_sen_list, employed_exec_list

def initialize_employed_population(jun_worker_list, sen_worker_list, exec_worker_list, employed_at_startup):

    unemp_workers_list = []
    employed_at_startup = floor(employed_at_startup/3)

    jun_worker_list = sorted(jun_worker_list, key=lambda x: x.worker_score, reverse=True)
    sen_worker_list = sorted(sen_worker_list, key=lambda x: x.worker_score, reverse=True)
    exec_worker_list = sorted(exec_worker_list, key=lambda x: x.worker_score, reverse=True)

    employed_jun_list = jun_worker_list[:employed_at_startup]
    unemp_jun_worker_list = jun_worker_list[employed_at_startup:]

    employed_sen_list = sen_worker_list[:employed_at_startup]
    unemp_sen_worker_list = sen_worker_list[employed_at_startup:]

    employed_exec_list = exec_worker_list[:employed_at_startup]
    unemp_exec_worker_list = exec_worker_list[employed_at_startup:]

    unemp_workers_list.extend(unemp_jun_worker_list)
    unemp_workers_list.extend(unemp_sen_worker_list)
    unemp_workers_list.extend(unemp_exec_worker_list)

    return employed_jun_list, employed_sen_list, employed_exec_list, unemp_workers_list


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
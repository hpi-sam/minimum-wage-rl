import numpy as np
from ...models.worker import Worker

JUNIOR_SKILL_LEVEL = 25
SENIOR_SKILL_LEVEL = 70


def add_new_workers(country):

    worker_list = []

    # 1: Add 5 - 10 juniors in population
    num_of_juniors = np.random.randint(5,11)
    for i in range(num_of_juniors):
        worker = Worker()
        age = np.random.randint(19,25)
        skill_level = np.random.randint(1, JUNIOR_SKILL_LEVEL-20)
        InitializeEmployee(0, country, worker, age, skill_level)
        worker_list.append(worker)
    
    # 2: Add 5 - 10 seniors in population
    num_of_seniors = np.random.randint(5,11)
    for i in range(num_of_seniors):
        worker = Worker()
        age = np.random.randint(30,35)
        skill_level = np.random.randint(JUNIOR_SKILL_LEVEL, JUNIOR_SKILL_LEVEL+2)
        InitializeEmployee(0, country, worker, age, skill_level)
        worker_list.append(worker)
    
    # 3: Add 5 - 10 executives in population
    num_of_executives = np.random.randint(5,11)
    for i in range(num_of_executives):
        worker = Worker()
        age = np.random.randint(40,45)
        skill_level = np.random.randint(SENIOR_SKILL_LEVEL, SENIOR_SKILL_LEVEL+2)
        InitializeEmployee(0, country, worker, age, skill_level)
        worker_list.append(worker)

    country.population = country.population + (num_of_juniors + num_of_seniors + num_of_executives)

    return worker_list



def InitializeEmployee(initialBalance, country, worker, age, skill_level): #MWCountry

#   ===================== Find the worker score here ========================================

    worker.worker_account_balance = initialBalance
    worker.age = age

    worker.salary = 0
    worker.skill_level = skill_level
    # citizen.initial_skill_level = 1
    worker.bought_essential_product = worker.buy_first_extra_product = worker.buy_second_extra_product = False
    worker.is_employed = worker.has_company = False

    # Moving to a country
    worker.country_of_residence = country
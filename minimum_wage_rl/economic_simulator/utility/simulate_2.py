from math import ceil, floor

from economic_simulator.models.metrics import Metric
from ..models.worker import Worker
from ..models.bank import Bank
from ..models.country import Country
from ..models.market import Market
from ..models.company import Company
from ..models.game import Game

from .code_files.perform_action import perform_action
from .code_files import country_module
from .code_files import company_module
from .code_files import workers_module
from .code_files import inflation_module
from .code_files import metrics_module

from .config import ConfigurationParser
from django.db import models
import numpy as np
from functools import reduce


config_parser = ConfigurationParser.get_instance().parser

discrete_action = bool(config_parser.get("game","discrete_action"))

# def minimumwage_action(minimum_wage,action_option):
    
#     if action_option == 0:
#         pass

#     elif action_option == 1:
#         minimum_wage += minimum_wage * 0.01

#     else:
#         minimum_wage += minimum_wage * 0.05

#     return minimum_wage


def step(action, user):
    
    # Get all data from DB

    game = __get_latest_game(user)

    country = Country.objects.get(player=user, game=game)

    # Increase age of all companies by 1
    # Get all companies
    country_companies_list = list(country.company_set.all())

    # Increase age of all workers by 1
    # Get all workers
    country_workers_list = list(country.worker_set.filter(retired=False))

    # Get all unemployed workers
    unemployed_workers_list = country.worker_set.filter(retired=False, is_employed=False)

    action_map = {"minimum_wage":action}
    # Step 1 - Change minimum wage - Perform action function
    perform_action(action_map,country,discrete_action)

    # *************** Increase age of all workers here ***************

    country.temp_worker_list.extend(country_workers_list)
    country.temp_company_list.extend(country_companies_list)
    # Step 2 - Change inflation rate : fixed as of now
    
    # Step 3 - run market step
    return run_market(country, country_companies_list, unemployed_workers_list)
    
    # return self.get_state_and_reward()

def __get_latest_game(user):
    
    game_obj = None
    max_game_number = None
    max_game_query = Game.objects.filter(player=user, game_ended=False).aggregate(max_game_number=models.Max("game_number"))
    
    if not max_game_query:
        pass
    else:
        max_game_number = max_game_query["max_game_number"]
        game_obj = Game.objects.filter(player=user, game_ended = False, game_number = max_game_number).first()

    return game_obj


def run_market(country, country_companies_list, unemployed_workers_list):

    metrics = {"num_small_companies":0, "num_medium_companies":0, "num_large_companies":0,
                "total_jun_pos":0, "total_sen_pos":0, "total_exec_pos":0, 
                "average_jun_sal":0, "average_sen_sal":0, "average_exec_sal":0,
                "average_sal":0, "unemployment_rate":0, "poverty_rate:":0}
    
    metrics = Metric()

    # ================ 1: COUNTRY MODULE - Increase population ================
    new_workers_list =  country_module.add_new_workers(country)
    fired_workers = []
    employed_workers_list = []
    
    # loop through unemployed_workers_list and retire them. ********************************* 


    # ================ 2: COMPANY MODULE - pay tax, pay salary, earn, hire and fire ================
    for each_company in country_companies_list:
        
        # 2.1: Increase age of company
        each_company.company_age = each_company.company_age + 1 

        # =========== PAY LOAN =================

        # 2.2: Pay taxes
        company_module.pay_tax(each_company,country.bank)

        # ******************* retire workers above 60 here ***********************
        # 2.3: Pay salary to workers and Earn money from workers
        company_module.yearly_financial_transactions(each_company,country)

        # 2.4: Create Jobs/Fire people
        operation_map = {"close":False,"fired_workers":[],"employed_workers":[]}
        company_module.hiring_and_firing(each_company, operation_map)

        # 2.5 Change company size
        company_module.set_company_size(company_item)

        # 2.6: Find Company score
        each_company.company_score = Market.COMPANY_AGE_WEIGHTAGE * each_company.company_age + \
                                    Market.COMPANY_ACCT_BALANCE_WEIGHTAGE * each_company.company_account_balance
        
        fired_workers.extend(operation_map["fired_workers"])
        employed_workers_list.extend(operation_map["employed_workers"])

        # 2.6 Close the company if no account balance
        if operation_map["close"]:
            close_company(each_company)

    # ================ 3: WORKERS MODULE ================
    all_workers_list = []
    all_workers_list.extend(unemployed_workers_list)
    all_workers_list.extend(new_workers_list)
    all_workers_list.extend(fired_workers)
    all_workers_list.extend(employed_workers_list)

    new_companies_list = []
    
    min_startup_score = 0
    max_startup_score = 0

    # Final save list
    successful_founders_list = []
    startup_workers_list = []
    unemp_jun_worker_list = []
    unemp_sen_worker_list = []
    unemp_exec_worker_list = []
    emp_worker_list = []
    unemp_worker_list = []

    # 3.1 Worker Evaluation : worker score, startup score, 
    workers_module.evaluate_worker(all_workers_list, startup_workers_list, unemp_jun_worker_list, 
                                  unemp_sen_worker_list, unemp_exec_worker_list, emp_worker_list, 
                                  min_startup_score, max_startup_score)

    # 3.2 Create Start ups
    workers_module.create_start_up(country, new_companies_list, startup_workers_list, unemp_jun_worker_list, 
                                  unemp_sen_worker_list, unemp_exec_worker_list, emp_worker_list, successful_founders_list)

    # 3.3 Getting hired
    # Input unemp_jun_worker_list, unemp_sen_worker_list, unemp_exec_worker_list, 
    # all_companies = new + old --- sorted using company score

    unemp_jun_worker_list = sorted(unemp_jun_worker_list, key=lambda x: x.worker_score, reverse=True)
    unemp_sen_worker_list = sorted(unemp_sen_worker_list, key=lambda x: x.worker_score, reverse=True)
    unemp_exec_worker_list = sorted(unemp_exec_worker_list, key=lambda x: x.worker_score, reverse=True)

    country_companies_list.extend(new_companies_list)

    country_companies_list = sorted(country_companies_list, key=lambda x: x.company_score, reverse=True)


    for company_item in country_companies_list:
        
        if company_item.open_junior_pos > 0:
            needed_positions = company_item.open_junior_pos
            jun_salary = country.minimum_wage
            available_positions  = workers_module.get_hired(needed_positions,unemp_jun_worker_list,jun_salary,
                                                            company_item,emp_worker_list)
            unemp_jun_worker_list = unemp_jun_worker_list[available_positions:]
            company_item.open_junior_pos = company_item.open_junior_pos - available_positions
        
        if company_item.open_senior_pos > 0:
            needed_positions = company_item.open_senior_pos
            senior_salary = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
            available_positions  = workers_module.get_hired(needed_positions,unemp_sen_worker_list,senior_salary,
                                                            company_item,emp_worker_list)
            unemp_sen_worker_list = unemp_sen_worker_list[available_positions:]
            company_item.open_senior_pos = company_item.open_senior_pos - available_positions
        
        if company_item.open_exec_pos > 0:
            needed_positions = company_item.open_exec_pos
            exec_salary = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE
            available_positions  = workers_module.get_hired(needed_positions,unemp_exec_worker_list,exec_salary,
                                                            company_item,emp_worker_list)
            unemp_exec_worker_list = unemp_exec_worker_list[available_positions:]
            company_item.open_exec_pos = company_item.open_exec_pos - available_positions

        company_module.set_company_size(company_item)
        metrics_module.set_company_size_metric(company_item, metrics)
        metrics_module.set_job_pos_metrics(company_item, metrics)


    # 4: INFLATION MODULE
    unemp_worker_list.extend(unemp_jun_worker_list)
    unemp_worker_list.extend(unemp_sen_worker_list)
    unemp_worker_list.extend(unemp_exec_worker_list)

    inflation_module.set_product_price_and_quantity(emp_worker_list ,unemp_worker_list, country)

    # 5 Buy products
    fin_workers_list = []
    fin_workers_list.extend(emp_worker_list)
    fin_workers_list.extend(unemp_worker_list)
    poverty_count = 0

    inflation_module.buy_products(fin_workers_list, country, poverty_count)
    
    # Set Metrics:
    


    # ================================================================================================ #
    # ----                                         HERE                                            ----
    # ================================================================================================ #
    new_workers_created_list = []
    new_companies_created_list = []

    # DELETE THIS
    country_workers_list = []

    # country_companies = self.testingCountry.companies # Dictionary<int, MWCompany> 
    # country_workers = self.testingCountry.workers # Dictionary<int, MWEmployee> 
    speedup = 30.415  # 365/12 is the speedup

    # 1. Companies must pay employees and employees must give value back to the companies        
    for each_company in country_companies_list:
    
        # company = V
        all_workers = list(each_company.worker_set.filter(retired=False))
        for each_worker in all_workers:            
            # Paying employees
            each_worker.worker_account_balance += each_worker.salary
            each_company.company_account_balance -= each_worker.salary

            # Giving value back to company
            each_company.company_account_balance += each_worker.skill_level
            each_company.year_income += (each_worker.skill_level - each_worker.salary)        

    # 2. People buy products every year
    # Employee Iteration  
    for each_worker in country_workers_list:        
        each_worker.buy_products(speedup, country.market)
    
    # 3. Check if year to be increased. Yearly 
    if country.market.month % 12 != 0:
        country.market.year = country.market.year + 1 

        # 4. Every year - Add new citizens
        new_workers_created_list = country.add_new_citizens(country.market.amount_of_new_citizens)
        country.temp_worker_list.extend(new_workers_created_list)
        if country.market.amount_of_new_citizens < Market.NUM_CITIZENS_LIMIT:
            country.market.amount_of_new_citizens += 1

        totalOpenPositions = 0
        totalUnemployed = country.total_unemployed

        # 5. Every year - Company Iteration
        for each_company in country_companies_list:            
            each_company.evaluate_company_step() # Step 1. Evaluate year and reset
            totalOpenPositions += each_company.open_job_positions() # Step 2. Open new job positions based on balance and company size
        
        # citizensToRemove = list()
        # 6. Every year - Employee Iteration
        for each_worker in country_workers_list:
            each_worker.age = each_worker.age + 1
            
            if not(each_worker.has_company) and each_worker.age > Market.CITIZEN_MAX_AGE:
                each_worker.remove_worker()
            else:
                new_company = each_worker.evaluate_worker_step(country_companies_list)
                if new_company != None:
                    new_companies_created_list.append(new_company)
            
        country.temp_company_list.extend(new_companies_created_list)  

        # 9. Every year - Updating product prices
        country.market.update_product_prices()

        # 10. Every year - Calculate Stats
        countryStatsOutput = country.calculate_statistics() # string 
        country.market.market_value_year = 0            
                    
        # SETTING EXCEL VALUES
        values_dict = dict()
        values_dict["year"] = country.market.year
        values_dict["Average Salary"] = country.average_income
        values_dict["productPrice"] = country.market.product_price
        values_dict["Poverty"] = country.poverty_rate
        values_dict["Unemployment"] = country.unemployment_rate
        values_dict["Small Company"] = country.num_small_companies
        values_dict["Medium Company"] = country.num_medium_company
        values_dict["Large Company"] = country.num_large_company
        values_dict["Junior"] = country.total_jun_jobs
        values_dict["Senior"] = country.total_senior_jobs
        values_dict["Executive"] = country.total_executive_jobs
        values_dict["Minimum Wage"] = country.minimum_wage

        country.market.all_data.append(values_dict)

        print("============ YEAR - " + str(country.market.year) + "=============")

    # print()
    country.bank.save()
    # print()
    country.market.save()
    # print()
    country.save()
    if len(new_workers_created_list) != 0:
        for each_worker in new_workers_created_list:
            each_worker.save()
        # print(new_workers_created_list)
    
    if len(country_workers_list) != 0:
        for each_worker in country_workers_list:
            each_worker.save()
        # print(country_workers_list)
    
    if len(new_companies_created_list) != 0:
        for each_company in new_companies_created_list:
            each_company.save()

        # print(new_companies_created_list)
    
    if len(country_companies_list) != 0:
        for each_company in country_companies_list:
            each_company.save()


    return get_current_state_reward(country)
        # print(country_companies_list)


    #     bank.save
    #     market.save
    #     country.save
    #     for each_company in all_companies_list:
    #     each_company.save()

    # # SAVE ALL citizens
    # for each_citizen in all_citizens_list:
    #     each_citizen.save()



def close_company(each_company):
    pass

def get_current_state_reward(country):
    
    state_values = []

    state_values.append(country.unemployment_rate)
    state_values.append(country.poverty_rate)
    state_values.append(country.minimum_wage)
    state_values.append(country.average_income - 30 * country.market.product_price)

    reward = calculate_reward(country)

    state_reward = dict()
    state_reward["state"] = state_values
    state_reward["reward"] = reward
    state_reward["done"] = False

    return state_reward

def calculate_reward(country):
    # 3. Companies

    r1 = Country.WEIGTH_LARGE_COMPANY * np.log10(country.num_large_company/country.minimum_wage + 1)
    r2 = Country.WEIGTH_MEDIUM_COMPANY * np.log10(country.num_medium_company / country.minimum_wage + 1)
    r3 = Country.WEIGTH_SMALL_COMPANY * np.log10(country.num_small_companies / country.minimum_wage + 1)
    r4 = 0.0

    # r1 = 1/self.povertyRate
    # r2 = 1/self.unemploymentRate

    if country.minimum_wage > Country.WAGE_THRESHOLD:
        r4 = Country.NEGATIVE_REWARD

    # return torch.tensor([r1 + r2 + r3 + r4])
    return r1 + r2 + r3 + r4
    # return r1 + r2

def get_state(user):
    game = __get_latest_game(user)

    country = Country.objects.get(player=user, game=game)
    country_companies_list = list(country.company_set.all())
    country_workers_list = list(country.worker_set.filter(retired=False))

    return get_current_state_reward(country)

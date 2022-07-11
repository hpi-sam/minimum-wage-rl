# from math import ceil, floor

# import numpy as np

from models.metrics import Metric
# from economic_simulator.utility.code_files.common_module import retire
# from ..models.worker import Worker
# from ..models.bank import Bank
# from ..models.country import Country
# from ..models.company import Company
# from ..models.game import Game
# from django.db.models import F

from models.market import Market
from .code_files.perform_action import perform_action
from .code_files import country_module
from .code_files import company_module
from .code_files import workers_module
from .code_files import inflation_module_2
from .code_files import metrics_module
from .code_files import hiring_module

from .config import ConfigurationParser
# from django.db import models
# import numpy as np
# from functools import reduce
# from django.db import transaction


config_parser = ConfigurationParser.get_instance().parser

discrete_action = bool(config_parser.get("game","discrete_action"))

def step(game, action_map):
    
    country = game.country

    # Get all companies with -> closed = False
    country_companies_list = country.company_list

    # Increase age of unemployed workers by 1
    
    # for each_worker in country.employed_workers:
    #     each_worker.age = each_worker.age + 1
    if len(country_companies_list) > 0:
        for each_worker in country.unemployed_workers:
            each_worker.age = each_worker.age + 1

        # Get all unemployed workers - retired=False and is_employed=False
        unemployed_workers_list = country.unemployed_workers

        # action_map = {"minimum_wage":action}
        # Step 1 - Change minimum wage - Perform action function
        discrete_action = False
        perform_action(action_map,country,discrete_action)
        
        # Step 2 - run market step
        return run_market(country, country_companies_list, unemployed_workers_list, game)
    else:
        # current_state = dict()
        # current_state["Unemployment Rate"] = float(0.0)
        # current_state["Poverty Rate"] = float(0.0)
        # current_state["Minimum wage"] = float(0.0)
        # current_state["Inflation Rate"] = float(0.0)
        # current_state["population"] = float(0.0)

        state_values = []

        reward = -10000

        message = "Game Over, all companies have shutdown"

        done = True
        
        # current_state, 
        return state_values, reward, message, done


# @transaction.atomic
def run_market(country, country_companies_list, unemployed_workers_list, game):
    
    retired_people = 0
    country.year = country.year + 1 
    metrics = Metric()
    metrics.year = country.year

    total_open_positions = 0

    # ================ 1: COUNTRY MODULE - Increase population ================
    new_workers_list, _, _, _ =  country_module.add_new_workers(country)
    fired_workers = []
    employed_workers_list = []
    retired_workers_list = []
    
    # ================ 2: Retire Unemployed workers ================
    non_retired_workers = []
    for each_unemployed_worker in unemployed_workers_list:
        # Increase age of worker here
        if each_unemployed_worker.age >= 60:
            workers_module.retire(each_unemployed_worker, country)
            retired_workers_list.append(each_unemployed_worker)
            # retired_people = retired_people + 1
        else:
            non_retired_workers.append(each_unemployed_worker)

    unemployed_workers_list = list(non_retired_workers)

    # ================ 3: COMPANY MODULE - pay tax, pay salary, earn, hire and fire ================
    open_companies_list = []
    closed_companies_list = []
    for each_company in country_companies_list:
        
        # 3.1: Increase age of company
        each_company.company_age = each_company.company_age + 1 

        # 3.2: Pay Loan
        company_module.pay_loan(each_company,country.bank)

        # 3.3: Pay taxes
        company_module.pay_tax(each_company,country.bank)

        # 3.4: Pay salary to workers and Earn money from workers
        all_emp_workers_list = company_module.yearly_financial_transactions(each_company,country, retired_workers_list)
        each_company.employed_workers_list = all_emp_workers_list

        # 3.5: 
        # Step 1: Fire people
        # Step 2: Create Open Positions - Junior, Senior and Executive
        operation_map = {"close":False,"fired_workers":[],"employed_workers":[]}
        company_module.hiring_and_firing(each_company, operation_map)

        total_open_positions = total_open_positions + each_company.open_junior_pos
        total_open_positions = total_open_positions + each_company.open_senior_pos
        total_open_positions = total_open_positions + each_company.open_exec_pos

        # 3.6: Change company size
        company_module.set_company_size(each_company)

        # 3.7: Find Company score
        each_company.company_score = Market.COMPANY_AGE_WEIGHTAGE * each_company.company_age + \
                                    Market.COMPANY_ACCT_BALANCE_WEIGHTAGE * each_company.company_account_balance
        
        fired_workers.extend(operation_map["fired_workers"])
        employed_workers_list.extend(operation_map["employed_workers"])

        # 3.8: Close the company if no account balance
        if operation_map["close"]:
            company = close_company(each_company, fired_workers)
            closed_companies_list.append(company)    
        else:
            open_companies_list.append(each_company)

    # ================ 4: WORKERS MODULE ================
    all_workers_list = []
    all_workers_list.extend(unemployed_workers_list)
    all_workers_list.extend(new_workers_list)
    all_workers_list.extend(fired_workers)
    # all_workers_list.extend(employed_workers_list)  --- for standalone

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

    # 4.1 Worker Evaluation : worker score, startup score, 
    workers_module.evaluate_worker(all_workers_list, startup_workers_list, unemp_jun_worker_list, 
                                  unemp_sen_worker_list, unemp_exec_worker_list, emp_worker_list, 
                                  min_startup_score, max_startup_score)

    # Only for standalone
    workers_module.evaluate_emp_worker(open_companies_list, emp_worker_list, min_startup_score, max_startup_score)                                  

    # 4.2 Create Start ups
    workers_module.create_start_up(country, new_companies_list, startup_workers_list, unemp_jun_worker_list, 
                                  unemp_sen_worker_list, unemp_exec_worker_list, emp_worker_list, successful_founders_list)
    
    # Only for standalone
    workers_module.create_start_up_for_employed(country, new_companies_list, startup_workers_list, open_companies_list, emp_worker_list, successful_founders_list)                                  

    retired_workers_list.extend(successful_founders_list)                                                                  

    # 4.3 Getting hired and Set metrics
    # Input unemp_jun_worker_list, unemp_sen_worker_list, unemp_exec_worker_list, 
    # all_companies = new + old --- sorted using company score
    unemp_jun_worker_list = sorted(unemp_jun_worker_list, key=lambda x: x.worker_score, reverse=True)
    unemp_sen_worker_list = sorted(unemp_sen_worker_list, key=lambda x: x.worker_score, reverse=True)
    unemp_exec_worker_list = sorted(unemp_exec_worker_list, key=lambda x: x.worker_score, reverse=True)

    open_companies_list.extend(new_companies_list)

    open_companies_list = sorted(open_companies_list, key=lambda x: x.company_score, reverse=True)

    # Hire Workers

    # LIST ONLY THE COMPANIES WHICH HAS OPENINGS
    # CHECK FOR JUNIOR, SENIOR, EXECUTIVE

    total_unemployed_workers = len(unemp_jun_worker_list) + len(unemp_sen_worker_list) + len(unemp_exec_worker_list)
    hire_loop_counter = min(total_open_positions, total_unemployed_workers)
    num_of_companies = len(open_companies_list)

    counter = 0
    company_counter = 0


    # Hire first 50% by first come first serve
    


    # Hire second 50% by equal distribution of workers among companies
    jun_salary = country.minimum_wage
    senior_salary = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
    exec_salary = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE
    
    if num_of_companies > 0:
        # 1. Junior
        level = "junior"
        unemp_jun_worker_list = hiring_module.hire_workers(open_companies_list,unemp_jun_worker_list,level, jun_salary, metrics, emp_worker_list)

        # 2. Senior
        level = "senior"
        unemp_sen_worker_list = hiring_module.hire_workers(open_companies_list,unemp_sen_worker_list,level, senior_salary,metrics, emp_worker_list)

        # 3. Executive
        level = "exec"
        unemp_exec_worker_list = hiring_module.hire_workers(open_companies_list,unemp_exec_worker_list,level, exec_salary,metrics, emp_worker_list)


    for company_item in open_companies_list:
        company_module.set_company_size(company_item)
        metrics_module.set_company_size_metrics(company_item, metrics)


    # 5: INFLATION MODULE
    metrics.unemployed_jun_pos = len(unemp_jun_worker_list)
    metrics.unemployed_sen_pos = len(unemp_sen_worker_list)
    metrics.unemployed_exec_pos = len(unemp_exec_worker_list)
    
    unemp_worker_list.extend(unemp_jun_worker_list)
    unemp_worker_list.extend(unemp_sen_worker_list)
    unemp_worker_list.extend(unemp_exec_worker_list)

    inflation_module_2.set_product_price_and_quantity(emp_worker_list ,unemp_worker_list, country, metrics)

    # 6: Buy products and Set metrics
    fin_workers_list = []
    fin_workers_list.extend(emp_worker_list)
    fin_workers_list.extend(unemp_worker_list)
    poverty_count = 0

    inflation_module_2.buy_products(fin_workers_list, country, poverty_count, metrics)

    metrics.bank_account_balance = float(country.bank.liquid_capital)
    
    
    # ============== 7: Save all data ==============
    # Try bulk update and bulk create 
    
    country.employed_workers = emp_worker_list
    country.unemployed_workers = unemp_worker_list

    # save bank
    # country.bank.save()
    
    # save market
    # country.market.save()

    # save country
    # country.save()

    # save metrics
    # metrics.country_of_residence = country
    # metrics.save()
    country.metrics_list.append(metrics)
    
    # save company list
    country.company_list = open_companies_list
    # for each_company in open_companies_list:
    #     each_company.save()
    
    # for each_company in closed_companies_list:
    #     each_company.save()

    # save workers list
    # for each_worker in fin_workers_list:
    #     each_worker.save()
    
    # for each_worker in retired_workers_list:
    #     retired_people = retired_people + 1
    #     each_worker.save()

    print_needed_data(game, metrics, country, retired_people)

    # current_state, 
    state_values, reward, message, done =  get_current_state_reward(country, metrics)

    game_metric = game.game_metric_list[-1]
    m_values = [country.year, metrics.minimum_wage, metrics.unemployment_rate, metrics.poverty_rate, metrics.inflation,
                metrics.product_price,  metrics.quantity, metrics.bank_account_balance, country.population, metrics.population]
    game_metric.metric_list.append(m_values)
    game.game_metric_list[-1] = game_metric

    # current_state, 
    return state_values, reward, message, done


def print_needed_data(game, metrics, country,retired_people):
    # metrics = Metric()
    # country = Country()
    print("====================== YEAR: ", metrics.year , " Game: ", str(game.game_number) , " Episode: ", str(len(game.game_metric_list)), "======================")
    print("Minwage - ", metrics.minimum_wage, ", Unemployment - ", metrics.unemployment_rate, ", Poverty Rate - ", metrics.poverty_rate)
    print("Product price - ", country.product_price, " , Inflation - ", metrics.inflation, ", Quantity - ", country.quantity)
    # print("Inflation - ", metrics.inflation)
    # print("Quantity - ", country.quantity)
    print("retired people - ", retired_people , " , Population - ", metrics.population,)
    print("small cmps - ", metrics.num_small_companies, ", medium cmps - ", metrics.num_medium_companies, ", large cmps - ", metrics.num_large_companies)
        
    
    # print("Unemployment - ", metrics.unemployment_rate)
    # print("Poverty Rate - ", metrics.poverty_rate)
    # print()
    # print("medium cmps - ", metrics.num_medium_companies)
    # print("large cmps - ", metrics.num_large_companies)
    print("Bank balance - ", metrics.bank_account_balance)

    print("Filled Junior Jobs - ", metrics.total_filled_jun_pos, end="")
    print(" , Filled Senior Jobs - ", metrics.total_filled_sen_pos, end="")
    print(" , Filled Executive Jobs - ", metrics.total_filled_exec_pos)

    print("Unemployed Junior Jobs - ", metrics.unemployed_jun_pos, end="")
    print(" , Unemployed Senior Jobs - ", metrics.unemployed_sen_pos, end="")
    print(" , Unemployed Executive Jobs - ", metrics.unemployed_exec_pos)
    
    print("Average Junior Salary - ", metrics.average_jun_sal, end="")
    print(" , Average Senior Salary - ", metrics.average_sen_sal, end="")
    print(" , Average Executive Salary - ", metrics.average_exec_sal)
    
    print("==============================================================")
    print("")

def close_company(each_company, fired_workers):
    fired_list = []
    fired_list.extend(each_company.junior_workers_list)
    fired_list.extend(each_company.senior_workers_list)
    fired_list.extend(each_company.exec_workers_list)

    fired_workers.extend(company_module.fire(fired_list))
    
    each_company.junior_workers_list = []
    each_company.senior_workers_list = []
    each_company.exec_workers_list = []

    each_company.closed = True

    return each_company


def get_current_state_reward(country, metrics):

    # current_state = dict()
    # current_state["Unemployment Rate"] = float("{:.2f}".format(metrics.unemployment_rate))
    # current_state["Poverty Rate"] = float("{:.2f}".format(metrics.poverty_rate))
    # current_state["Minimum wage"] = metrics.minimum_wage
    # current_state["Inflation Rate"] = float("{:.2f}".format(metrics.inflation_rate))
    # current_state["population"] = metrics.population

    # state_values.append(country.unemployment_rate)
    # state_values.append(country.poverty_rate)
    # state_values.append(country.minimum_wage)
    # state_values.append(country.average_income - 30 * country.market.product_price)

    state_values, reward = get_game_state(metrics)
    done =  False
    message = ""
    # state_reward = dict()
    # state_reward["state"] = state_values
    # state_reward["reward"] = reward
    # state_reward["done"] = False
    # current_state, 

    return state_values, reward, message, done

def calculate_reward(metrics):
    poverty_weightage = int(config_parser.get("reward","poverty_weightage"))
    unemp_weightage = int(config_parser.get("reward","unemp_weightage"))

    r1 = 1 - (metrics.unemployment_rate/100)
    #  * unemp_weightage
    # r2 =  - (metrics.poverty_rate/100)
    r2 = 1 - (metrics.poverty_rate/100)
    # r2 = 100 - (metrics.poverty_rate)
    # * poverty_weightage
    # r1 +
    
    return r2

def get_state(game):
    # game = __get_latest_game(user)
    country = game.country
    #  Country.objects.get(player=user, game=game)
    metric = country.metrics_list[-1] 
    # Metric.objects.filter(country_of_residence=country).last()
    # current_state, 
    state_values, reward, message, done = get_current_state_reward(country, metric)


    # current_state,
    return  state_values, reward, message, done

def get_game_state(metric):
    state_values = []
    state_values.append(metric.minimum_wage)
    state_values.append(metric.product_price)
    state_values.append(metric.quantity)
    # state_values.append(metric.poverty_rate)
    state_values.append(metric.unemployment_rate)
    state_values.append(metric.inflation)
    state_values.append(metric.bank_account_balance)
    state_values.append(metric.population)

    reward = calculate_reward(metric)

    return state_values, reward




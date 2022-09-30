# from math import ceil, floor

from cmath import log
from itertools import count
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
import logging
logging.basicConfig(filename="C:\\Users\\AkshayGudi\\Documents\\3_MinWage\\minimum_wage_rl\\economic_simulator\\my_log.log", level=logging.INFO)
# from django.db import models
# import numpy as np
# from functools import reduce
# from django.db import transaction


config_parser = ConfigurationParser.get_instance().parser

discrete_action = config_parser.getboolean("game","discrete_action")
max_steps = int(config_parser.get("meta","training_steps"))

def step(game, action_map):
    
    # print(" Game - ", game.game_number, " Episode - " +  str(len(game.game_metric_list)) )

    country = game.country

    # Get all companies with -> closed = False
    country_companies_list = country.company_list

    
    
    # for each_worker in country.employed_workers:
    #     each_worker.age = each_worker.age + 1


    # Increase age of unemployed workers by 1
    # 
    # 
    if len(country_companies_list) > 0 and country.bank.liquid_capital > 0:
        for each_worker in country.unemployed_workers:
            each_worker.age = each_worker.age + 1

        # Get all unemployed workers - retired=False and is_employed=False
        unemployed_workers_list = country.unemployed_workers

        # Step 1 - Change minimum wage - Perform action function
        perform_action(action_map,country,discrete_action)
        
        
        logging.info("=========== Game - " + str(game.game_number) + " Episode: " +  str(len(game.game_metric_list)) +  " Year: " + str(country.year) + " ===========")
        logging.info("Minimum wage - " + str(country.minimum_wage))
        # Step 2 - run market step
        return run_market(country, country_companies_list, unemployed_workers_list, game)
    else:
        logging.info("Game Over")
        state_values = []

        reward = -10000

        message = "Game Over, "
        if len(country_companies_list) <= 0 :
            message = message + "All companies have shutdown "
            logging.info("Companies Shut Down")

        if country.bank.liquid_capital <= 0:
            message = message + "Bank has shutdown"
            logging.info("Bank has Shutdown")

        done = True
        
        # current_state, 
        info = {"message" : message}
        return state_values, float(reward), done, info


# @transaction.atomic
def run_market(country, country_companies_list, unemployed_workers_list, game):
    
    retired_people = 0
    country.year = country.year + 1 
    metrics = Metric()
    metrics.year = country.year

    total_open_positions = 0
    total_open_junior_pos = 0
    total_open_senior_pos = 0
    total_open_exec_pos = 0

    # ================ 1: COUNTRY MODULE - Increase population ================
    # new_workers_list, _, _, _ =  country_module.add_new_workers(country)
    # new_workers_list = []
    fired_workers = []
    employed_workers_list = []
    retired_workers_list = []

    # ================ 2: Retire Unemployed workers ================
    # non_retired_workers = []
    # for each_unemployed_worker in unemployed_workers_list:
    #     # Increase age of worker here
    #     if each_unemployed_worker.age >= 60:
    #         # workers_module.retire(each_unemployed_worker, country)
    #         # retired_workers_list.append(each_unemployed_worker)
    #         # retired_people = retired_people + 1
    #         pass
    #     else:
    #         non_retired_workers.append(each_unemployed_worker)

    # unemployed_workers_list = list(non_retired_workers)

    # ================ 3: COMPANY MODULE - pay tax, pay salary, earn, hire and fire ================
    open_companies_list = []
    closed_companies_list = []
    comp_count = 0
    num_closed_comp = 0
    for each_company in country_companies_list:
        
        comp_count = comp_count + 1
        
        # 3.1: Increase age of company
        each_company.company_age = each_company.company_age + 1 

        # 3.2: Pay Loan
        company_module.pay_loan(each_company,country.bank)

        # 3.3: Pay taxes
        coo = company_module.pay_cost_of_operation(each_company, country.bank)        

        # Pay taxes
        tax = company_module.pay_tax(each_company, country.bank)        

        # 3.4: Pay salary to workers and Earn money from workers
        all_emp_workers_list = company_module.yearly_financial_transactions(each_company,country, retired_workers_list)
        each_company.employed_workers_list = all_emp_workers_list

        print("Before - Company - ", comp_count , " Employed People - ", len(all_emp_workers_list))

        # 3.5: 
        # Step 1: Fire people
        # Step 2: Create Open Positions - Junior, Senior and Executive
        operation_map = {"close":False,"fired_workers":[],"employed_workers":[]}
        company_module.hiring_and_firing(comp_count, each_company, operation_map)
        print("After - Company - ", comp_count, " Fired people - ", len(operation_map["fired_workers"]), " Employed People - ", len(operation_map["employed_workers"]))

        total_open_positions = total_open_positions + each_company.open_junior_pos
        total_open_positions = total_open_positions + each_company.open_senior_pos
        total_open_positions = total_open_positions + each_company.open_exec_pos

        total_open_junior_pos = total_open_junior_pos + each_company.open_junior_pos
        total_open_senior_pos = total_open_senior_pos  + each_company.open_senior_pos
        total_open_exec_pos = total_open_exec_pos + each_company.open_exec_pos

        # 3.6: Change company size
        company_module.set_company_size(each_company)

        # 3.7: Find Company score
        each_company.company_score = Market.COMPANY_AGE_WEIGHTAGE * each_company.company_age + \
                                    Market.COMPANY_ACCT_BALANCE_WEIGHTAGE * each_company.company_account_balance
        
        fired_workers.extend(operation_map["fired_workers"])
        employed_workers_list.extend(operation_map["employed_workers"])

        each_company.employed_workers_list = operation_map["employed_workers"]

        # 3.8: Close the company if no account balance
        if operation_map["close"]:
            company = close_company(each_company, fired_workers)
            closed_companies_list.append(company)
            num_closed_comp = num_closed_comp + 1
            logging.info("Company closed")
        else:
            open_companies_list.append(each_company)

    # ================ 4: WORKERS MODULE - create startup, hire workers ================
    all_workers_list = []

    # all_workers_list.extend(new_workers_list)
    # For standalone all_workers_list has only Uemployed and Fired Workers
    all_workers_list.extend(unemployed_workers_list)
    all_workers_list.extend(fired_workers)
    
    # Comment this For standalone: Because employed workers will be accessed through company object
    # all_workers_list.extend(employed_workers_list)

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
    # Standalone -> for standalone only unemployed, fired and new workers are sent to this method using all_workers_list
    workers_module.evaluate_worker(all_workers_list, startup_workers_list, unemp_jun_worker_list, 
                                  unemp_sen_worker_list, unemp_exec_worker_list, emp_worker_list, 
                                  min_startup_score, max_startup_score)

    # Only for standalone: Employed workers are sent to this method, which are present in open_companies_list
    workers_module.evaluate_emp_worker(open_companies_list, emp_worker_list, min_startup_score, max_startup_score)                                  

    # 4.2 Create Start ups
    workers_module.create_start_up(country, new_companies_list, startup_workers_list, unemp_jun_worker_list, 
                                  unemp_sen_worker_list, unemp_exec_worker_list, emp_worker_list, successful_founders_list)

    metrics.num_retired = len(retired_workers_list)
    metrics.startup_founders = len(successful_founders_list)
    # Only for standalone
    workers_module.create_start_up_for_employed(country, new_companies_list, startup_workers_list, open_companies_list, emp_worker_list, successful_founders_list)                                  

    # retired_workers_list.extend(successful_founders_list)                                                                  

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

    # Hire first 50% by first come first serve
    


    # Hire second 50% by equal distribution of workers among companies
    jun_salary = country.minimum_wage
    senior_salary = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
    exec_salary = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE
    
    if num_of_companies > 0:
        # 1. Junior
        level = "junior"
        # print("Junior Before - UnEmployed Junior workers", len(unemp_jun_worker_list) , " Employed Workers - ", len(emp_worker_list))
        unemp_jun_worker_list, num_jun_hired = hiring_module.hire_workers(open_companies_list,unemp_jun_worker_list,level, jun_salary, metrics, emp_worker_list)
        # print("Junior After - UnEmployed Junior workers", len(unemp_jun_worker_list) , " Employed Workers - ", len(emp_worker_list))
        # print("Juniors Hired - ", num_jun_hired)

        # 2. Senior
        level = "senior"
        # print("Senior Before - UnEmployed Senior workers", len(unemp_sen_worker_list) , " Employed Workers - ", len(emp_worker_list))
        unemp_sen_worker_list, num_sen_hired = hiring_module.hire_workers(open_companies_list,unemp_sen_worker_list,level, senior_salary,metrics, emp_worker_list)
        # print("Senior After - UnEmployed Senior workers", len(unemp_sen_worker_list) , " Employed Workers - ", len(emp_worker_list))
        # print("Seniors Hired - ", num_sen_hired)

        # 3. Executive
        level = "exec"
        # print("Exec Before - UnEmployed Exec workers", len(unemp_exec_worker_list) , " Employed Workers - ", len(emp_worker_list))
        unemp_exec_worker_list, num_of_exec_hired = hiring_module.hire_workers(open_companies_list,unemp_exec_worker_list,level, exec_salary,metrics, emp_worker_list)
        # print("Exec After - UnEmployed Exec workers", len(unemp_exec_worker_list) , " Employed Workers - ", len(emp_worker_list))
        # print("Executives Hired - ", num_of_exec_hired)


        metrics.current_year_filled_jun_pos = num_jun_hired
        metrics.current_year_filled_sen_pos = num_sen_hired
        metrics.current_year_filled_exec_pos = num_of_exec_hired

    smll_comp_acct_balance = 0.0
    medium_comp_acct_balance = 0.0
    large_comp_acct_balance = 0.0

    for company_item in open_companies_list:
        # Pay cost of operation
        coo = company_module.pay_cost_of_operation(company_item, country.bank)        

        # Pay taxes
        tax = company_module.pay_tax(company_item,country.bank)

        # print("Coo - ", coo, " Year income - ", company_item.year_income, " Tax - ", tax)

        company_module.set_company_size(company_item)
        metrics_module.set_company_size_metrics(company_item, metrics)

        company_item.year_income = 0.0

    print("")

    # 5: INFLATION MODULE - set product prices
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
    metrics.money_circulation = country.money_circulation    
    
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
    metrics.product_price = country.product_price
    metrics.quantity  = country.quantity 
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

    # print_needed_data(game, metrics, country, retired_people)
    print("Final Workers  - " , len(fin_workers_list))
    print("Fired Workers - ", len(fired_workers))

    logging.info("Total Workers - " +  str(len(fin_workers_list)))
    logging.info("Total Companies - " + str(len(country.company_list)))
    logging.info("Fired Workers - " +  str(len(fired_workers)))
    logging.info("Number of closed companies - " + str(num_closed_comp))
    logging.info("Product Price - " + str(country.product_price) + " ,Bank balance - " + str(country.bank.liquid_capital))
    logging.info("Uemployment Rate - " + str(metrics.unemployment_rate) + " ,Poverty Rate - " + str(metrics.poverty_rate))    

    # current_state, 
    state_values, reward, done, info =  get_current_state_reward(country, metrics)

    # For excel
    game_metric = game.game_metric_list[-1]
    m_values = [country.year, round(metrics.minimum_wage,2), metrics.unemployment_rate, metrics.poverty_rate, metrics.inflation,
                metrics.product_price,  metrics.quantity, round(metrics.bank_account_balance,2), country.population, 
                metrics.unemployed_junior_rate, metrics.unemployed_senior_rate, metrics.unemployed_exec_rate, 
                metrics.num_small_companies, metrics.num_medium_companies, metrics.num_large_companies]
    game_metric.metric_list.append(m_values)
    game.game_metric_list[-1] = game_metric

    logging.info(" End of Step - " + str(country.year))
    logging.info(" ===============================*********************====================================== ")
    return state_values, reward, done, info


def print_needed_data(game, metrics, country,retired_people):

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

    print("Hired Juniors (Current Year) - ", metrics.total_filled_jun_pos, end="")
    print(" , Hired Seniors (Current Year) - ", metrics.total_filled_sen_pos, end="")
    print(" , Hired Executives (Current Year) - ", metrics.total_filled_exec_pos)

    print("Unemployed Juniors - ", metrics.unemployed_jun_pos, end="")
    print(" , Unemployed Seniors - ", metrics.unemployed_sen_pos, end="")
    print(" , Unemployed Executives - ", metrics.unemployed_exec_pos)
    
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

    country_companies_list = country.company_list

    state_values, reward = get_game_state(metrics)

    message = ""
    if country.year >= max_steps:
        done =  True
        message = message + "End of Episode"
    elif len(country_companies_list) == 0:
        done = True
        message = message + "Game over, Companies are closed"
        reward = -100
    elif country.bank.liquid_capital <= 0:
        done = True        
        message = message + "Game over, Bank has shutdown"
        reward = -100        
    else:
        done = False
        message = message + "Episode - " + str(country.year)
    
    info = {"message" : message}
    return state_values, float(reward), done, info

def calculate_reward(metrics):
    poverty_weightage = int(config_parser.get("reward","poverty_weightage"))
    unemp_weightage = int(config_parser.get("reward","unemp_weightage"))

    # r1 = metrics.old_poverty_rate - metrics.poverty_rate
    # r2 = metrics.old_unemployment_rate - metrics.unemployment_rate
    
    r1 = -metrics.unemployment_rate/100
    #  * unemp_weightage
    # r2 =  - (metrics.poverty_rate/100)
    r2 = - metrics.poverty_rate/100
    # r2 = 100 - (metrics.poverty_rate)
    # * poverty_weightage
    # r1 +
    
    return r1 + r2

def get_state(game):
    # game = __get_latest_game(user)
    country = game.country
    #  Country.objects.get(player=user, game=game)
    metric = country.metrics_list[-1] 
    # Metric.objects.filter(country_of_residence=country).last()
    # current_state, 
    state_values, reward, done, info = get_current_state_reward(country, metric)


    # current_state,
    return  state_values, reward, done, info

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
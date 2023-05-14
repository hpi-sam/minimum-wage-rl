# from math import ceil, floor
import numpy as np
from models.metrics import Metric
# from economic_simulator.utility.code_files.common_module import retire
# from ..models.worker import Worker
# from ..models.bank import Bank
from models.country import Country
from models.company import Company
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
from .code_files import common_module

from .config import ConfigurationParser
import logging
logging.basicConfig(filename="C:\\Users\\AkshayGudi\\Documents\\3_MinWage\\minimum_wage_rl\\economic_simulator\\my_log.log", level=logging.INFO)
# from django.db import models
# import numpy as np
# from functools import reduce
# from django.db import transaction

file_name = "config_file.txt"
config_parser = ConfigurationParser.get_instance(file_name).parser

env_file = "env_config_file.txt"
config_parser_env = ConfigurationParser.get_instance(env_file).parser

discrete_action = config_parser.getboolean("game","discrete_action")
max_steps = int(config_parser.get("meta","training_steps"))
MAX_SKILL_LEVEL = int(config_parser.get("worker","exec_skill_level"))


max_jun_avg_bal = 260
min_jun_avg_bal = 0.64

max_sen_avg_bal = 368.55
min_sen_avg_bal = 0.77

max_product_price = 71
min_product_price = 5

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
        
        
        logging.info("=========== Game - " + str(game.game_number) + " Episode: " +  str(game.episode_number) +  " Year: " + str(country.year) + " ===========")
        # logging.info("Minimum wage - " + str(country.minimum_wage))

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
        
        info = {"message" : message, "money_circulation": country.money_circulation, "poverty_rate":country.poverty_rate}

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

    metrics.old_bank_account_balance = float(country.bank.liquid_capital)
    # ================ 1: COUNTRY MODULE - Increase population ================
    if country.year % 4 == 0:
        new_workers_list =  country_module.increase_population(country)
    else:
        new_workers_list = []

    # new_workers_list = []
    fired_workers = []
    employed_workers_list = []
    retired_workers_list = []

    # ================ 1.1: Add Stagflation settings ================
    if country.stagflation_flag:
        set_stagflation_values(country)
                

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

        # 3.3: Pay Cost of operation
        coo = company_module.pay_cost_of_operation(country, each_company, country.bank)        


        # Pay taxes
        tax = company_module.pay_tax(each_company, country.bank)        

        # 3.4: Pay salary to workers and Earn money from workers
        all_emp_workers_list = company_module.yearly_financial_transactions(each_company,country, retired_workers_list)
        
        # Only for stand-alone
        each_company.employed_workers_list = all_emp_workers_list

        # print("Before - Company - ", comp_count , " Employed People - ", len(all_emp_workers_list))

        # 3.5: 
        # Step 1: Fire people
        # Step 2: Create Open Positions - Junior, Senior and Executive
        operation_map = {"close":False,"fired_workers":[],"employed_workers":[]}            
        company_module.hiring_and_firing(comp_count, each_company, operation_map)
        # print("After - Company - ", comp_count, " Fired people - ", len(operation_map["fired_workers"]), " Employed People - ", len(operation_map["employed_workers"]))

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


        # Only for stand-alone
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

    all_workers_list.extend(new_workers_list)
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
                                  min_startup_score, max_startup_score, MAX_SKILL_LEVEL)

    # Only for standalone: Employed workers are sent to this method, which are present in open_companies_list
    workers_module.evaluate_emp_worker(open_companies_list, emp_worker_list, min_startup_score, max_startup_score, MAX_SKILL_LEVEL)                                  


    # 4.2 Create Start ups
    workers_module.create_start_up(country, new_companies_list, startup_workers_list, unemp_jun_worker_list, 
                                  unemp_sen_worker_list, unemp_exec_worker_list, emp_worker_list, successful_founders_list, open_companies_list)

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

        # 1. Executive
        level = "exec"
        # print("Exec Before - UnEmployed Exec workers", len(unemp_exec_worker_list) , " Employed Workers - ", len(emp_worker_list))
        unemp_exec_worker_list, num_of_exec_hired = hiring_module.hire_workers(country, open_companies_list,unemp_exec_worker_list,level, exec_salary,metrics, emp_worker_list)
        # print("Exec After - UnEmployed Exec workers", len(unemp_exec_worker_list) , " Employed Workers - ", len(emp_worker_list))
        # print("Executives Hired - ", num_of_exec_hired)



        # 2. Senior
        level = "senior"
        # print("Senior Before - UnEmployed Senior workers", len(unemp_sen_worker_list) , " Employed Workers - ", len(emp_worker_list))
        unemp_sen_worker_list, num_sen_hired = hiring_module.hire_workers(country, open_companies_list,unemp_sen_worker_list,level, senior_salary,metrics, emp_worker_list)
        # print("Senior After - UnEmployed Senior workers", len(unemp_sen_worker_list) , " Employed Workers - ", len(emp_worker_list))
        # print("Seniors Hired - ", num_sen_hired)

        # 3. Junior
        level = "junior"
        # print("Junior Before - UnEmployed Junior workers", len(unemp_jun_worker_list) , " Employed Workers - ", len(emp_worker_list))
        unemp_jun_worker_list, num_jun_hired = hiring_module.hire_workers(country, open_companies_list,unemp_jun_worker_list,level, jun_salary, metrics, emp_worker_list)
        # print("Junior After - UnEmployed Junior workers", len(unemp_jun_worker_list) , " Employed Workers - ", len(emp_worker_list))
        # print("Juniors Hired - ", num_jun_hired)

        metrics.current_year_filled_jun_pos = num_jun_hired
        metrics.current_year_filled_sen_pos = num_sen_hired
        metrics.current_year_filled_exec_pos = num_of_exec_hired

    smll_comp_acct_balance = 0.0
    medium_comp_acct_balance = 0.0
    large_comp_acct_balance = 0.0

    for company_item in open_companies_list:
        # Pay cost of operation
        # coo = company_module.pay_cost_of_operation(company_item, country.bank)        

        # Pay taxes
        # tax = company_module.pay_tax(company_item,country.bank)

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


    avg_jun_acct_balance, avg_sen_acct_balance, avg_exec_acct_balance =  common_module.get_avg_acct_balance(emp_worker_list, unemp_worker_list)

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
    # print("Final Workers  - " , len(fin_workers_list))
    # print("Fired Workers - ", len(fired_workers))

    # logging.info("Total Workers - " +  str(len(fin_workers_list)))
    # logging.info("Total Companies - " + str(len(country.company_list)))
    # logging.info("Fired Workers - " +  str(len(fired_workers)))
    # logging.info("Number of closed companies - " + str(num_closed_comp))
    # logging.info("Product Price - " + str(country.product_price) + " ,Bank balance - " + str(country.bank.liquid_capital))
    # logging.info("Uemployment Rate - " + str(metrics.unemployment_rate) + " ,Poverty Rate - " + str(metrics.poverty_rate))    

    # current_state, 
    current_state, state_values, reward, done, info =  get_current_state_reward(avg_jun_acct_balance, avg_sen_acct_balance, avg_exec_acct_balance,  country, metrics)

    # For excel
    # country = Country()
    
    m_avg_jun_acct_balance = info["avg_jun_acct_balance"]
    m_avg_sen_acct_balance = info["avg_senior_acct_balance"]
    m_avg_exec_acct_balance = info["avg_exec_acct_balance"]

    if game.episode_number > 0:
        game_metric = game.game_metric_list[-1]
        m_values = [country.year, round(metrics.minimum_wage,2), metrics.unemployment_rate, metrics.poverty_rate, metrics.inflation,
                    metrics.product_price,  metrics.quantity, round(metrics.bank_account_balance,2), country.population, 
                    country.OIL_COST_PER_LITRE, country.COMPANY_REVENUE_PERCENTAGE, country.COST_OF_OPERATION,                    
                    metrics.unemployed_junior_rate, metrics.unemployed_senior_rate, metrics.unemployed_exec_rate, 
                    metrics.num_small_companies, metrics.num_medium_companies, metrics.num_large_companies, 
                    metrics.money_circulation, m_avg_jun_acct_balance ,m_avg_sen_acct_balance,m_avg_exec_acct_balance, game.level]
        game_metric.metric_list.append(m_values)
        game.game_metric_list[-1] = game_metric
    
    # [0]minimum_wage, [1]product_price, [2]quantity, [3]unemployment_rate, [4]inflation, 
    # [5]bank_account_balance, [6]poverty_rate, [7]money_circulation [8] Population
    # logging.info("Observations - " + str(state_values[0]) + ", " + str(state_values[1]) + ", " + str(state_values[2]) + ", " + 
    # str(state_values[3]) + ", " + str(state_values[4]) + ", " + str(state_values[5]) + ", " + str(state_values[6]) + ", " + 
    # str(state_values[7]) + ", " + str(state_values[8]))
    # logging.info(" End of Step - " + str(country.year))
    logging.info("MC - " + str(state_values[7]) + " - " + str(country.money_circulation))
    # print(type(state_values[7]))
    logging.info(" ===============================*********************====================================== ")

    # print("Minwage - ", metrics.minimum_wage, "  Product price - ", country.product_price)        
    # print("OIL RATE - ", country.OIL_COST_PER_LITRE, ", REVENUE - ", country.COMPANY_REVENUE_PERCENTAGE)
    # print("COST OF OPERATION - ", country.COST_OF_OPERATION)

    return state_values, reward, done, info

def set_stagflation_values(country):
    if country.year > country.stagflation_end:
        country.stagflation_flag = False
    else:
        if country.year >= country.stagflation_start and country.year <= country.stagflation_start + 2:
                # increase oil price
            increased_oil_rate = country.OIL_COST_PER_LITRE * Country.OIL_RATE_INCREASE
            country.OIL_COST_PER_LITRE = country.OIL_COST_PER_LITRE + increased_oil_rate

                # increase cost of operation for company
            increased_cost_of_op = country.COST_OF_OPERATION * Country.COST_OF_OPERATION_INCREASE
            country.COST_OF_OPERATION = country.COST_OF_OPERATION + increased_cost_of_op

			    # decrease how much companies earn from each employee
            decreased_revenue_rate = country.COMPANY_REVENUE_PERCENTAGE * Country.REVENUE_DECREASE_RATE
            country.COMPANY_REVENUE_PERCENTAGE = country.COMPANY_REVENUE_PERCENTAGE - decreased_revenue_rate
                
        elif country.year > country.stagflation_start + 2 and country.year < country.stagflation_end - 2:
                # maintain same metrics
            pass
        elif country.year >= country.stagflation_end - 2 and country.year <= country.stagflation_end:
                # push oil price little towards normal                
            country.OIL_COST_PER_LITRE = round(country.OIL_COST_PER_LITRE/(1+country.OIL_RATE_INCREASE), 2)

                # push cost of operation for company little towards normal
            country.COST_OF_OPERATION = round(country.COST_OF_OPERATION/(1+country.COST_OF_OPERATION_INCREASE), 2)
                
                # increase how much companies earn from each employee towards normal
            country.COMPANY_REVENUE_PERCENTAGE = round(country.COMPANY_REVENUE_PERCENTAGE/(1-Country.REVENUE_DECREASE_RATE), 2)



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


def get_current_state_reward(avg_jun_acct_balance, avg_senior_acct_balance, avg_exec_acct_balance,country, metrics):

    country_companies_list = country.company_list

    metrics.population = country.population

    current_state = dict()
    current_state["Year"] = int(metrics.year)
    current_state["Minimum wage"] = float("{:.2f}".format(metrics.minimum_wage))
    current_state["Unemployment Rate"] = float("{:.2f}".format(metrics.unemployment_rate))
    current_state["Poverty Rate"] = float("{:.2f}".format(metrics.poverty_rate))
    current_state["Quantity"] = metrics.quantity
    current_state["Inflation"] = float("{:.2f}".format(metrics.inflation))
    current_state["Product Price"] = float("{:.2f}".format(metrics.product_price))
    current_state["Population"] = metrics.population
    current_state["Small Companies"] = metrics.num_small_companies
    current_state["Medium Companies"] = metrics.num_medium_companies
    current_state["Large Companies"] = metrics.num_large_companies
    current_state["Bank Balance"] = metrics.bank_account_balance
    current_state["Retired Current Year"] = metrics.num_retired
    current_state["Start Up Founders Current Year"] = metrics.startup_founders

    # print("--------------------------------------------------------------------------------")
    # print("=========================== Every Step State - Start ===========================")
    # for each_key in current_state.keys():
    #     print(each_key, " ---> ", current_state[each_key])
    # print("=========================== Every Step State - End ===========================")
    # print("--------------------------------------------------------------------------------")


    state_values, reward = get_game_state(avg_jun_acct_balance, avg_senior_acct_balance ,metrics)

    message = ""
    if country.year >= max_steps:
        done =  True
        message = message + "End of Episode"
    elif len(country_companies_list) == 0:
        done = True
        message = message + "Game over, Companies are closed"

        reward = -1
    elif country.bank.liquid_capital <= 0:
        done = True        
        message = message + "Game over, Bank has shutdown"
        reward = -1   

    else:
        done = False
        message = message + "Episode - " + str(country.year)
    info = dict()
    info["message"] = message
    info["money_circulation"] = country.money_circulation
    info["avg_jun_acct_balance"] = avg_jun_acct_balance
    info["avg_senior_acct_balance"] = avg_senior_acct_balance
    info["avg_exec_acct_balance"]  = avg_exec_acct_balance
    info["poverty_rate"] = metrics.poverty_rate

    return current_state, state_values, float(reward), done, info


def calculate_reward(avg_jun_acct_balance, avg_senior_acct_balance, metrics):
    poverty_weightage = int(config_parser.get("reward","poverty_weightage"))
    unemp_weightage = int(config_parser.get("reward","unemp_weightage"))

    # r1 = metrics.old_poverty_rate - metrics.poverty_rate
    # r2 = metrics.old_unemployment_rate - metrics.unemployment_rate
    # r2 = 100 - (metrics.poverty_rate)
    # * poverty_weightage
    # r1 +
    #  * unemp_weightage
    # r2 =  - (metrics.poverty_rate/100)
    max_jun_avg_bal = 260
    min_jun_avg_bal = 0.64

    max_sen_avg_bal = 368.55
    min_sen_avg_bal = 0.77

    max_product_price = 71
    min_product_price = 5

    jun_avg_bal_range = max_jun_avg_bal - min_jun_avg_bal
    sen_avg_bal_range = max_sen_avg_bal - min_sen_avg_bal
    product_price_range = max_product_price - min_product_price        

    jun_acct_bal_weight = 0.1
    sen_acct_bal_weight = 0.25
    inflation_weight = 0.25
    product_price_weight = 0.9

    # (inflation_weight * metrics.inflation) -
    # (sen_acct_bal_weight * avg_senior_acct_balance(sen_avg_bal_range)) - \

    r = (jun_acct_bal_weight * avg_jun_acct_balance/(jun_avg_bal_range)) + \
        (product_price_weight * metrics.product_price/(product_price_range))

    r1 = 1- (metrics.unemployment_rate/100)
    r2 = -metrics.poverty_rate/100
    
    # return r2
    # reward_here
    scale = 1
    return r2 * scale

def get_state(game):
    # game = __get_latest_game(user)
    country = game.country
    #  Country.objects.get(player=user, game=game)
    metric = country.metrics_list[-1] 
    # Metric.objects.filter(country_of_residence=country).last()
    # current_state,

    emp_worker_list = country.employed_workers
    unemp_worker_list = country.unemployed_workers

    avg_jun_acct_balance, avg_sen_acct_balance, avg_exec_acct_balance = common_module.get_avg_acct_balance(emp_worker_list, unemp_worker_list)

    current_state, state_values, reward, done, info = get_current_state_reward(avg_jun_acct_balance, avg_sen_acct_balance,avg_exec_acct_balance, country, metric)

    return  state_values, reward, done, info

def get_game_state(avg_jun_acct_balance, avg_senior_acct_balance, metric):
    state_values = []

    state_values.append(metric.minimum_wage)
    state_values.append(float("{:.6f}".format(np.log(metric.product_price))))
    state_values.append(float("{:.6f}".format(np.log(metric.produced_quantity))))
    state_values.append(metric.unemployment_rate/100)
    state_values.append(metric.inflation)
    state_values.append(float("{:.6f}".format(np.log(metric.bank_account_balance))))    
    state_values.append(metric.poverty_rate/100)
    state_values.append(float("{:.6f}".format(np.log(metric.money_circulation) if metric.money_circulation>0 else metric.money_circulation )))
    state_values.append(float("{:.6f}".format(np.log(metric.population))))

    reward = calculate_reward(avg_jun_acct_balance, avg_senior_acct_balance, metric)

    return state_values, reward
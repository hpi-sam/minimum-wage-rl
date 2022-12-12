# from math import ceil, floor

from math import ceil
from economic_simulator.models.metrics import Metric
from economic_simulator.utility.code_files.common_module import retire
from ..models.worker import Worker
from ..models.bank import Bank
from ..models.country import Country
from ..models.market import Market
from ..models.company import Company
from ..models.game import Game

from django.db.models import F

from .code_files.perform_action import perform_action
from .code_files import country_module
from .code_files import company_module
from .code_files import workers_module
from .code_files import inflation_module_2
from .code_files import metrics_module
from .code_files import hiring_module

from .config import ConfigurationParser
from django.db import models
import numpy as np
# from functools import reduce
from django.db import transaction


config_parser = ConfigurationParser.get_instance().parser
discrete_action = config_parser.getboolean("game","discrete_action")
max_steps = int(config_parser.get("meta","training_steps"))
MAX_SKILL_LEVEL = int(config_parser.get("worker","exec_skill_level"))

def step(action_map, user, ai_flag, player_game_number):
    
    # Get all data from DB

    game = __get_latest_game(user, player_game_number)
    country = Country.objects.get(player=user, game=game)

    # Get all "OPEN" companies 
    country_companies_list = list(country.company_set.filter(closed=False))

    if len(country_companies_list) > 0 and country.bank.liquid_capital > 0:
        # Increase age of all workers by 1
        Worker.objects.filter(country_of_residence=country).update(age=F("age") + 1)

        # Get all workers
        country_workers_list = list(country.worker_set.filter(retired=False))

        # Get all unemployed workers
        unemployed_workers_list = country.worker_set.filter(retired=False, is_employed=False)

        # action_map = {"minimum_wage":action}
        # Step 1 - Change minimum wage - Perform action function
        # discrete_action = False
        perform_action(action_map,country,discrete_action)

        country.temp_worker_list.extend(country_workers_list)
        country.temp_company_list.extend(country_companies_list)
        # Step 2 - Change inflation rate : fixed as of now
        
        # Step 3 - run market step
        return run_market(game, country, country_companies_list, unemployed_workers_list)
    
    else:
        current_state = dict()
        current_state["Unemployment Rate"] = float(0.0)
        current_state["Poverty Rate"] = float(0.0)
        current_state["Minimum wage"] = float(0.0)
        current_state["Inflation Rate"] = float(0.0)
        current_state["population"] = float(0.0)

        state_values = []

        reward = -10000

        message = "Game Over, all companies have shutdown"

        done = True
        
        return game, current_state, state_values, reward, message, done
        
    # return self.get_state_and_reward()

def __get_latest_game(user, player_game_number):
    
    game_obj = None
    max_game_number = None
    max_game_query = Game.objects.filter(player=user, game_ended=False, player_game_number=player_game_number).aggregate(max_game_number=models.Max("game_number"))
    
    if not max_game_query:
        pass
    else:
        max_game_number = max_game_query["max_game_number"]
        game_obj = Game.objects.filter(player=user, game_ended = False, game_number = max_game_number).first()

    return game_obj


@transaction.atomic
def run_market(game, country, country_companies_list, unemployed_workers_list):
    
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
    if country.year % 2 == 0:
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

    # print("Total Workers Currently - ", country.population)

    # ================ 2: Retire Unemployed workers ================
    # non_retired_workers = []
    # for each_unemployed_worker in unemployed_workers_list:
    #     if each_unemployed_worker.age >= 60:
    #         workers_module.retire(each_unemployed_worker, country)
    #         retired_workers_list.append(each_unemployed_worker)
    #         # retired_people = retired_people + 1
    #     else:
    #         non_retired_workers.append(each_unemployed_worker)

    # unemployed_workers_list = list(non_retired_workers)

    # ================ 3: COMPANY MODULE - pay tax, pay salary, earn, hire and fire ================
    open_companies_list = []
    closed_companies_list = []
    comp_count = 0    
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


        # 3.3: Pay taxes
        # company_module.pay_tax(each_company,country.bank)

        # 3.4: Pay salary to workers and Earn money from workers
        company_module.yearly_financial_transactions(each_company,country, retired_workers_list)

        # 3.5: Create Jobs/Fire people
        operation_map = {"close":False,"fired_workers":[],"employed_workers":[]}
        company_module.hiring_and_firing(each_company, operation_map, country)

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
    all_workers_list.extend(employed_workers_list)

    print("Total Open Position - ", total_open_positions)
    print("Total Unemployed Workers - ", len(all_workers_list))

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
                                  min_startup_score, max_startup_score, MAX_SKILL_LEVEL)

    # print("Open Junior Pos - ", total_open_junior_pos, " Unemployed Junior Workers - ", len(unemp_jun_worker_list))
    # print("Open Senior Pos - ", total_open_senior_pos, " Unemployed Senior Workers - ", len(unemp_sen_worker_list))
    # print("Open Exec Pos - ", total_open_exec_pos, " Unemployed Exec Workers - ", len(unemp_exec_worker_list))

    # 4.2 Create Start ups
    workers_module.create_start_up(country, new_companies_list, startup_workers_list, unemp_jun_worker_list, 
                                  unemp_sen_worker_list, unemp_exec_worker_list, emp_worker_list, successful_founders_list, MAX_SKILL_LEVEL, open_companies_list)

    metrics.num_retired = len(retired_workers_list)
    metrics.startup_founders = len(successful_founders_list)
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

    counter = 0
    company_counter = 0


    # Hire first 50% by first come first serve
    


    # Hire second 50% by equal distribution of workers among companies
    
    jun_salary = country.minimum_wage
    senior_salary = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
    exec_salary = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE

    if num_of_companies > 0:

        # 3. Executive
        level = "exec"
        unemp_exec_worker_list, num_of_exec_hired = hiring_module.hire_workers(country, open_companies_list,unemp_exec_worker_list,level, exec_salary,metrics, emp_worker_list)

        # 2. Senior        
        level = "senior"
        unemp_sen_worker_list, num_sen_hired = hiring_module.hire_workers(country, open_companies_list,unemp_sen_worker_list,level, senior_salary,metrics, emp_worker_list)

        # 1. Junior
        level = "junior"
        unemp_jun_worker_list, num_jun_hired = hiring_module.hire_workers(country, open_companies_list,unemp_jun_worker_list,level, jun_salary, metrics, emp_worker_list)


        
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
        # tax = company_module.pay_tax(company_item, country.bank)
        
        # print("Coo - ", coo, " Year income - ", company_item.year_income, " Tax - ", tax)

        company_module.set_company_size(company_item)
        metrics_module.set_company_size_metrics(company_item, metrics)

        company_item.year_income = 0.0

    print("")

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
    metrics.money_circulation = country.money_circulation
    
    # 7: Save all data
    # Try bulk update and bulk create 
    
    # save bank
    country.bank.save()
    
    # save market
    country.market.save()

    # save country
    country.save()

    # save metrics
    metrics.country_of_residence = country
    metrics.product_price = country.product_price
    metrics.quantity  = country.quantity
    metrics.num_of_open_companies = len(open_companies_list)
    metrics.save()
    
    # save company list
    for each_company in open_companies_list:
        each_company.save()
    
    for each_company in closed_companies_list:
        each_company.save()

    # save workers list
    for each_worker in fin_workers_list:
        each_worker.save()
    
    for each_worker in retired_workers_list:
        retired_people = retired_people + 1
        each_worker.save()

    cmp_metrics(metrics, country)

    print_needed_data(metrics, country, retired_people)

    return get_current_state_reward(game, country, metrics)
    

def cmp_metrics(metrics, country):
    # select num(workers) from companies inner join workers on company_id == worker.company_id where worker_skill < 10
    # Average juniors, seniors, executes in small, medium, large companies
    small_cmps = 0
    small_jun_workers = 0
    small_sen_workers = 0
    small_exec_workers = 0

    medium_cmps = 0
    medium_jun_workers = 0
    medium_sen_workers = 0
    medium_exec_workers = 0

    large_cmps = 0
    large_jun_workers = 0
    large_sen_workers = 0
    large_exec_workers = 0

    smll_acct_balance = 0.0
    medium_acct_balance = 0.0
    large_acct_balance = 0.0

    all_cmps = list(country.company_set.filter(closed=False))

    for company in all_cmps:
        #Small Company:
        if company.company_account_balance < Market.MEDIUM_CMP_INIT_BALANCE:
            small_cmps = small_cmps + 1
            smll_acct_balance = smll_acct_balance + company.company_account_balance
            # juniors
            jun_workers = list(company.worker_set.filter(retired=False).filter(skill_level__lte=10))
            small_jun_workers = small_jun_workers + len(jun_workers)

            sen_workers = list(company.worker_set.filter(retired=False).filter(skill_level__gt=10).filter(skill_level__lte=20))
            small_sen_workers = small_sen_workers + len(sen_workers)

            exec_workers = list(company.worker_set.filter(retired=False).filter(skill_level__gt=20))
            small_exec_workers = small_exec_workers + len(exec_workers)

        elif company.company_account_balance >= Market.MEDIUM_CMP_INIT_BALANCE and company.company_account_balance < Market.LARGE_CMP_INIT_BALANCE:
            medium_cmps = medium_cmps + 1
            medium_acct_balance = medium_acct_balance + company.company_account_balance
            # juniors
            jun_workers = list(company.worker_set.filter(retired=False).filter(skill_level__lte=10))
            medium_jun_workers = medium_jun_workers + len(jun_workers)

            sen_workers = list(company.worker_set.filter(retired=False).filter(skill_level__gt=10).filter(skill_level__lte=20))
            medium_sen_workers = medium_sen_workers + len(sen_workers)

            exec_workers = list(company.worker_set.filter(retired=False).filter(skill_level__gt=20))
            medium_exec_workers = medium_exec_workers + len(exec_workers)
        else:
            large_cmps = large_cmps + 1
            large_acct_balance = large_acct_balance + company.company_account_balance
            # juniors
            jun_workers = list(company.worker_set.filter(retired=False).filter(skill_level__lte=10))
            large_jun_workers = large_jun_workers + len(jun_workers)

            sen_workers = list(company.worker_set.filter(retired=False).filter(skill_level__gt=10).filter(skill_level__lte=20))
            large_sen_workers = large_sen_workers + len(sen_workers)

            exec_workers = list(company.worker_set.filter(retired=False).filter(skill_level__gt=20))
            large_exec_workers = large_exec_workers + len(exec_workers)

    jun_data = Worker.objects.filter(is_employed=False).filter(skill_level__lte=10).aggregate(jun_sum=models.Sum("worker_account_balance"), count_people=models.Count("worker_id"))
    sen_data = Worker.objects.filter(is_employed=False).filter(skill_level__gt=10).filter(skill_level__lte=20).aggregate(sen_sum=models.Sum("worker_account_balance"), count_people=models.Count("worker_id"))
    exec_data = Worker.objects.filter(is_employed=False).filter(skill_level__gt=20).aggregate(exec_sum=models.Sum("worker_account_balance"), count_people=models.Count("worker_id"))
    # jun_count = Worker.objects.filter(is_employed=False and skill_level<)

    if jun_data["jun_sum"] == None or jun_data["count_people"] <=0:
        metrics.uemp_jun_acct_balance = 0
    else:
        metrics.uemp_jun_acct_balance = jun_data["jun_sum"]/jun_data["count_people"]
    
    if sen_data["sen_sum"] == None or sen_data["count_people"] <=0:
        metrics.uemp_sen_acct_balance = 0
    else:
        metrics.uemp_sen_acct_balance = sen_data["sen_sum"]/sen_data["count_people"]
    
    if exec_data["exec_sum"] == None or exec_data["count_people"] <=0:
        metrics.uemp_exec_acct_balance = 0
    else:
        metrics.uemp_exec_acct_balance = exec_data["exec_sum"]/exec_data["count_people"]

    metrics.avg_juniors_small_cmp = ceil(small_jun_workers/small_cmps) if small_cmps>0 else 0
    metrics.avg_seniors_small_cmp = ceil(small_sen_workers/small_cmps) if small_cmps>0 else 0
    metrics.avg_execs_small_cmp = ceil(small_exec_workers/small_cmps) if small_cmps>0 else 0
    metrics.avg_juniors_medium_cmp = ceil(medium_jun_workers/medium_cmps) if medium_cmps>0 else 0
    metrics.avg_seniors_medium_cmp = ceil(medium_sen_workers/medium_cmps) if medium_cmps>0 else 0
    metrics.avg_execs_medium_cmp = ceil(medium_exec_workers/medium_cmps) if medium_cmps>0 else 0
    metrics.avg_juniors_large_cmp = ceil(large_jun_workers/large_cmps) if large_cmps>0 else 0
    metrics.avg_seniors_large_cmp = ceil(large_sen_workers/large_cmps) if large_cmps>0 else 0
    metrics.avg_execs_large_cmp = ceil(large_exec_workers/large_cmps) if large_cmps>0 else 0
    metrics.small_comp_acct_balance = smll_acct_balance/small_cmps if small_cmps>0 else 0
    metrics.medium_comp_acct_balance = medium_acct_balance/medium_cmps if medium_cmps>0 else 0
    metrics.large_comp_acct_balance = large_acct_balance/large_cmps if large_cmps>0 else 0

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


def print_needed_data(metrics, country,retired_people):
    # metrics = Metric()
    # country = Country()
    print("====================== YEAR ", metrics.year , "======================")
    print("Year - " ,metrics.year)
    print("Minwage - ", metrics.minimum_wage)
    print("Population - ", metrics.population)
    print("retired people - ", retired_people)
    print("Bank balance - ", metrics.bank_account_balance)
    print("Product price - ", country.product_price)
    print("Money Circulation - ", metrics.money_circulation)
    print("Inflation - ", metrics.inflation)
    print("Quantity - ", country.quantity)
    print("Unemployment - ", metrics.unemployment_rate)
    print("Poverty Rate - ", metrics.poverty_rate)

    print("--------------------------- Average Balance ---------------------------")
    print("Average Jun Acct balance - ", metrics.jun_worker_avg_balance)
    print("Average Sen Acct balance - ", metrics.sen_worker_avg_balance)
    print("Average Exec Acct balance - ", metrics.exec_worker_avg_balance)

    print("============== Hired Level ========================")
    print("Current year Jun hired - ", metrics.current_year_filled_jun_pos)
    print("Current year Sen hired - ", metrics.current_year_filled_sen_pos)
    print("Current year Exec hired - ", metrics.current_year_filled_exec_pos)

    print("Total Jun Hired - ", metrics.total_filled_jun_pos)
    print("Total Sen Hired - ", metrics.total_filled_sen_pos)
    print("Total Exec Hired - ", metrics.total_filled_exec_pos)

    print("UnEmployed Juniors - ", metrics.unemployed_jun_pos)
    print("UnEmployed Seniors", metrics.unemployed_sen_pos)
    print("UnEmployed Exec", metrics.unemployed_exec_pos)

    print("======================== Predict Next Employment =======================")
    print("Average Number of Juniors in Small Company", metrics.avg_juniors_small_cmp)
    print("Average Number of Seniors in Small Company", metrics.avg_seniors_small_cmp) 
    print("Average Number of Executives in Small Company", metrics.avg_execs_small_cmp)
    print("")
    print("Average Number of Juniors in Medium Company", metrics.avg_juniors_medium_cmp)
    print("Average Number of Seniors in Medium Company", metrics.avg_seniors_medium_cmp)
    print("Average Number of Executives in Medium Company", metrics.avg_execs_medium_cmp)
    print("")
    print("Average Number of Juniors in Large Company", metrics.avg_juniors_large_cmp) 
    print("Average Number of Seniors in Large Company", metrics.avg_seniors_large_cmp)
    print("Average Number of Executives in Large Company", metrics.avg_execs_large_cmp)
    print("")
    print("Average account balance in small company", metrics.small_comp_acct_balance)
    print("Average account balance in medium company", metrics.medium_comp_acct_balance)
    print("Average account balance in large company", metrics.large_comp_acct_balance)
    print("")
    print("Average Junior Skill", metrics.avg_jun_skill_level)
    print("Average Seniors Skill", metrics.avg_sen_skill_level)
    print("Average Executives Skill", metrics.avg_exec_skill_level)


    print("Num small cmp - ", metrics.num_small_companies)
    print("Num medium cmp - ", metrics.num_medium_companies)
    print("Num large cmp - ", metrics.num_large_companies)

    print("Unemployed Jun Acct balance - ", metrics.uemp_jun_acct_balance)
    print("Unemployed Sen Acct balance - ", metrics.uemp_sen_acct_balance)
    print("Unemployed Exec Acct balance - ", metrics.uemp_exec_acct_balance)
    # print("Junior Jobs - ", metrics.total_filled_jun_pos)
    # print("Senior Jobs - ", metrics.total_filled_sen_pos)
    # print("Executive Jobs - ", metrics.total_filled_exec_pos)
    # print("Unemployed Junior Jobs - ", metrics.unemployed_jun_pos)
    # print("Unemployed Senior Jobs - ", metrics.unemployed_sen_pos)
    # print("Unemployed Executive Jobs - ", metrics.unemployed_exec_pos)
    # print("Average Junior Salary - ", metrics.average_jun_sal)
    # print("Average Senior Salary - ", metrics.average_sen_sal)
    # print("Average Executive Salary - ", metrics.average_exec_sal)
    
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


def get_current_state_reward(game, country, metrics):
    
    # state_values = []

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


    # state_values.append(country.unemployment_rate)
    # state_values.append(country.poverty_rate)
    # state_values.append(country.minimum_wage)
    # state_values.append(country.average_income - 30 * country.market.product_price)

    state_values, reward = get_game_state(metrics)
    done =  False
    message = ""
    if country.year >= max_steps:
        done =  True
        message = message + "Game Ended"
    elif metrics.num_of_open_companies <= 0:
        done = True
        message = message + "Game over, Companies are closed"
        reward = -100
    elif country.bank.liquid_capital <= 0:
        done = True        
        message = message + "Game over, Bank has shutdown"
        reward = -100        
    else:
        if country.year < 4:
            message = message + "Game Started in Level-" + str(game.level)
        done = False
        message = message
    
    info = message
    # {"message" : message, "money_circulation":country.money_circulation}

    return game, current_state, state_values, reward, info, done

def calculate_reward(metrics):

    poverty_weightage = int(config_parser.get("reward","poverty_weightage"))
    unemp_weightage = int(config_parser.get("reward","unemp_weightage"))

    r1 = 1 - (metrics.unemployment_rate/100)
    #  * unemp_weightage
    r2 = 1 - (metrics.poverty_rate/100)
    # * poverty_weightage
    # r1 +
    return  r1 + r2

def get_state(user, ai_flag, player_game_number):
    game = __get_latest_game(user, player_game_number)

    country = Country.objects.get(player=user, game=game, ai_flag=ai_flag)
    max_query = Metric.objects.filter(country_of_residence=country).aggregate(max_year=models.Max("year"))
    max_metric_year = max_query["max_year"]
    metric = Metric.objects.filter(country_of_residence=country, year=max_metric_year).first()

    # country_companies_list = list(country.company_set.all())
    # country_workers_list = list(country.worker_set.filter(retired=False))

    return get_current_state_reward(game, country, metric)

# def get_game_state(metric):
#     # game = __get_latest_game(user)
#     # metric = Metric.objects.filter(player=user, game=game).last()
#     state_values = []
#     state_values.append(metric.minimum_wage)
#     state_values.append(metric.product_price)
#     state_values.append(metric.quantity)
#     state_values.append(metric.poverty_rate)
#     state_values.append(metric.unemployment_rate)

#     state_values.append(metric.inflation)
#     state_values.append(metric.bank_account_balance)

#     reward = calculate_reward(metric)

#     return state_values, reward

def get_game_state(metric):
    state_values = []
    state_values.append(metric.minimum_wage)
    state_values.append(metric.product_price)
    state_values.append(float("{:.6f}".format(np.log(metric.produced_quantity))))
    state_values.append(metric.unemployment_rate/100)
    state_values.append(metric.inflation)
    state_values.append(float("{:.6f}".format(np.log(metric.bank_account_balance))))    
    state_values.append(metric.poverty_rate/100)
    state_values.append(float("{:.6f}".format(np.log(metric.money_circulation))))
    state_values.append(float("{:.6f}".format(np.log(metric.population))))

    reward = calculate_reward(metric)

    return state_values, reward
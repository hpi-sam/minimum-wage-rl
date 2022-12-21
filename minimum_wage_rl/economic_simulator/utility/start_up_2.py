from itertools import count

from ..models.worker import Worker
from ..models.bank import Bank
from ..models.country import Country
from ..models.market import Market
from ..models.company import Company
from ..models.metrics import Metric
from ..models.game import Game
from .config import ConfigurationParser
from django.db import models
from .code_files import country_module
from django.db import transaction
import numpy as np

from economic_simulator.models import country

config_parser = ConfigurationParser.get_instance().parser

@transaction.atomic
def start(user, level, ai_flag, player_game):

    game = Game()    
    game.level = level
    if ai_flag:
        game.player_game_number = player_game.game_number


    config_level = None
    stagflation_config = False

    if game.level == 1:
        config_level = "Level_1"
    elif game.level == 2:
        level = 1
        # np.random.randint(1,4)
        config_level = "Level_" + str(level)
        stagflation_config = True
        # config_level = "Level_2"    
    elif game.level == 3:
        level = 1
        # np.random.randint(1,4)
        config_level = "Level_" + str(level)
        stagflation_config = True        
        # config_level = "Level_2"
    elif game.level == 4:
        level = 1
        # np.random.randint(1,4)
        config_level = "Level_" + str(level)
        stagflation_config = True

    RICH_JUN_PERCENT = config_parser.getfloat(config_level,"rich_jun_workers_percentage")
    RICH_SEN_PERCENT = config_parser.getfloat(config_level,"rich_sen_workers_percentage")
    RICH_EXEC_PERCENT = config_parser.getfloat(config_level,"rich_exec_workers_percentage")
    EMPLOYED_AT_STARTUP = config_parser.getfloat(config_level,"employed_at_startup")
    initial_bank_balance_percent = config_parser.getfloat(config_level,"initial_bank_balance_percent")
    each_level_population = int(config_parser.get(config_level,"initial_each_level_population"))

    min_wage_weightage = float(config_parser.get("worker","initial_balance_weightage"))

    JUN_SKILL_LOW_LIM = config_parser.getint("worker","jun_skill_low_limit")
    JUN_SKILL_HIGH_LIM_OFFSET = config_parser.getint("worker","jun_skill_high_limit_offset")
    SEN_SKILL_LOW_LIM_OFFSET = config_parser.getint("worker","sen_skill_low_limit_offset")
    SEN_SKILL_HIGH_LIM_OFFSET = config_parser.getint("worker","sen_skill_high_limit_offset")
    EXEC_SKILL_LOW_LIM_OFFSET = config_parser.getint("worker","exec_skill_low_limit_offset")
    EXEC_SKILL_HIGH_LIM_OFFSET = config_parser.getint("worker","exec_skill_high_limit_offset")

    

    # all_workers_list = []
    all_companies_list = []

    metric_obj = Metric()
    metric_obj.year = 0    

    # 1: Create Market 
    market_obj = Market()
    market_obj.month = market_obj.year = 0
    market_obj.market_value_year = 0

    # 2: Create Country
    country = Country(each_level_population)
    # country.total_money_printed = Country.INITIAL_BANK_BALANCE    
    country_module.create_country(country, each_level_population, ai_flag)

    initial_bank_balance = get_central_bank_balance(initial_bank_balance_percent, country)
    country.INITIAL_BANK_BALANCE = initial_bank_balance

    country.market = market_obj    
    country.player = user

    # 2.1 Add Stagflation settings
    if stagflation_config:
        set_stagflation_parameters(country)

    # 3: Create Company
    all_companies_list = country_module.create_company(country)
    
    metric_obj.num_small_companies = Country.INITIAL_NUM_SMALL_COMPANIES
    metric_obj.num_medium_companies = Country.INITIAL_NUM_MEDIUM_COMPANIES
    metric_obj.num_large_companies = Country.INITIAL_NUM_LARGE_COMPANIES

    metric_obj.total_filled_jun_pos = 0
    metric_obj.total_filled_sen_pos = 0
    metric_obj.total_filled_exec_pos = 0

    # 5: Number of workers to be employed at start up
    employed_at_startup = country.INITIAL_EACH_LEVEL_POPULATION * 3 * EMPLOYED_AT_STARTUP

    # 6: Create Workers
    unemp_workers_list, new_num_of_juniors, new_num_of_seniors, new_num_of_executives, employed_jun_list, employed_sen_list, employed_exec_list = country_module.add_new_workers(country, country.INITIAL_EACH_LEVEL_POPULATION, employed_at_startup, JUN_SKILL_LOW_LIM, JUN_SKILL_HIGH_LIM_OFFSET, SEN_SKILL_LOW_LIM_OFFSET, SEN_SKILL_HIGH_LIM_OFFSET, EXEC_SKILL_LOW_LIM_OFFSET, EXEC_SKILL_HIGH_LIM_OFFSET)
    # country.unemployed_workers = all_workers_list

    num_workers_hired = len(employed_jun_list) + len(employed_sen_list) + len(employed_exec_list)

    # 4: Create Bank
    bank = Bank()
    bank = country_module.create_bank(bank, country.INITIAL_BANK_BALANCE)
    country.bank = bank

    # 7: Employee workers
    wage_base = country.minimum_wage
    all_companies_list, employed_money_circulation, employed_jun_list, employed_sen_list, employed_exec_list = hire_initial_workers(all_companies_list, employed_jun_list, employed_sen_list, employed_exec_list, wage_base)

    # 5: Create Game
    game_number = get_latest_game_number(user)

    game.player = user
    game.game_number = game_number
    country.game = game

    # 6: Create Workers
    # all_workers_list, new_num_of_juniors, new_num_of_seniors, new_num_of_executives = country_module.add_new_workers(country, Country.INITIAL_POPULATION)
    
    metric_obj.unemployed_jun_pos = new_num_of_juniors
    metric_obj.unemployed_sen_pos = new_num_of_seniors
    metric_obj.unemployed_exec_pos = new_num_of_executives

    metric_obj.average_jun_sal = country.minimum_wage
    metric_obj.average_sen_sal = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
    metric_obj.average_exec_sal = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE

    metric_obj.average_sal = (metric_obj.average_jun_sal * new_num_of_juniors   + 
                            metric_obj.average_sen_sal * new_num_of_seniors + 
                            metric_obj.average_exec_sal * new_num_of_executives)/len(unemp_workers_list)

    metric_obj.unemployment_rate = 100
    metric_obj.poverty_rate = 100

    metric_obj.population = country.population
    metric_obj.minimum_wage = country.minimum_wage
    metric_obj.country_of_residence = country

    metric_obj.inflation = 0
    metric_obj.inflation_rate = 0

    metric_obj.bank_account_balance = country.INITIAL_BANK_BALANCE


    # 7: Set initial product price and quantity
    # country.product_price
    # country.quantity
    # country.minimum_wage

    # 7.1: Initial quantity    
    money_circulation = get_money_circulation(unemp_workers_list, country, min_wage_weightage, employed_money_circulation, RICH_JUN_PERCENT, RICH_SEN_PERCENT, RICH_EXEC_PERCENT)
    country.quantity = money_circulation/country.product_price
    country.money_circulation = money_circulation

    metric_obj.product_price = country.product_price
    metric_obj.quantity = country.quantity
    metric_obj.produced_quantity = country.quantity
    metric_obj.money_circulation = money_circulation

    game.save()

    country.bank.save()
    
    # save market
    country.market.save()

    # save country
    country.save()

    # SAVE ALL COMPANIES
    for each_company in all_companies_list:
        each_company.save()

    # SAVE ALL Workers
    for each_citizen in unemp_workers_list:
        each_citizen.save()

    # SAVE JUNIOR EMPLOYED WORKERS
    for each_emp in employed_jun_list:
        each_emp.save()

    # SAVE SENIOR EMPLOYED WORKERS
    for each_emp in employed_sen_list:
        each_emp.save()

    # SAVE EXEC EMPLOYED WORKERS
    for each_emp in employed_exec_list:
        each_emp.save()

    metric_obj.save()

    print_needed(metric_obj, country)

    return collect_metrics(country), game

def set_stagflation_parameters(country):
    country.stagflation_flag = True
    country.stagflation_start = 6
    # np.random.randint(5,7)
    country.stagflation_end = country.stagflation_start + Country.STAGFLATION_DURATION

def get_central_bank_balance(initial_bank_balance_percent, country):
    quant = (country.population * 12)
    needed_money = (quant * country.product_price)
    transport_cost = (quant * country.OIL_PER_UNIT_QUANTITY * country.OIL_COST_PER_LITRE)

    total_money = needed_money + transport_cost
    initial_bank_balance = total_money * initial_bank_balance_percent    
    return initial_bank_balance

def print_metrics(country):
    print("=========================== Year ", country.year, "==========================")
    print("Minimum wage - ", country.minimum_wage)
    print("Quantity - ", country.quantity)
    print("Product price - ", country.product_price)
    print("Population - ", country.population)
    print(" Bank balance - ", country.bank.liquid_capital)


def get_money_circulation(unemp_workers_list, country, min_wage_weightage, employed_money_circulation, RICH_JUN_PERCENT, RICH_SEN_PERCENT, RICH_EXEC_PERCENT):

    rich_jun_acct_bal, rich_sen_acct_bal, rich_exec_acct_bal = calculate_rich_worker_initial_balance(country)
    rich_jun, rich_sen, rich_exec = account_balance_division(RICH_JUN_PERCENT, RICH_SEN_PERCENT, RICH_EXEC_PERCENT, country.INITIAL_EACH_LEVEL_POPULATION)

    wage_base = country.minimum_wage * min_wage_weightage
    jun_sal = wage_base
    sen_sal = wage_base + wage_base * Market.SENIOR_SALARY_PERCENTAGE
    exec_sal = wage_base + wage_base * Market.EXEC_SALARY_PERCENTAGE

    money_circulation = 0
    money_circulation = money_circulation + employed_money_circulation

    for each_worker in unemp_workers_list:
        if each_worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
            if rich_jun > 0:
                each_worker.worker_account_balance += (rich_jun_acct_bal)
                money_circulation += rich_jun_acct_bal
                rich_jun = rich_jun - 1
            else:
                each_worker.worker_account_balance += (jun_sal * 12)
                money_circulation += jun_sal * 12
        
        elif (each_worker.skill_level > Worker.JUNIOR_SKILL_LEVEL) and (each_worker.skill_level <= Worker.SENIOR_SKILL_LEVEL):
            if rich_sen > 0:
                each_worker.worker_account_balance += (rich_sen_acct_bal)
                money_circulation += rich_sen_acct_bal
                rich_sen = rich_sen - 1
            else:
                each_worker.worker_account_balance += (sen_sal * 12)
                money_circulation += sen_sal * 12
        
        else:
            if rich_exec>0:
                each_worker.worker_account_balance += (rich_exec_acct_bal)
                money_circulation += rich_exec_acct_bal
                rich_exec = rich_exec - 1
            else:        
                each_worker.worker_account_balance += (exec_sal * 12)
                money_circulation += exec_sal * 12

    return money_circulation

def account_balance_division(RICH_JUN_PERCENT, RICH_SEN_PERCENT, RICH_EXEC_PERCENT, each_level_population):
    rich_jun = (RICH_JUN_PERCENT/100) * each_level_population
    rich_sen = (RICH_SEN_PERCENT/100) * each_level_population
    rich_exec = (RICH_EXEC_PERCENT/100) * each_level_population

    return rich_jun, rich_sen, rich_exec

def calculate_rich_worker_initial_balance(country):
    wage_base = country.minimum_wage
    rich_jun_sal = wage_base * 12
    rich_sen_sal = (wage_base + wage_base * Market.SENIOR_SALARY_PERCENTAGE) * 12
    rich_exec_sal = (wage_base + wage_base * Market.EXEC_SALARY_PERCENTAGE) * 12

    return rich_jun_sal, rich_sen_sal, rich_exec_sal


# def get_money_circulation(all_workers_list, country, min_wage_weightage):

#     wage_base = country.minimum_wage * min_wage_weightage
#     jun_sal = wage_base
#     sen_sal = wage_base + wage_base * Market.SENIOR_SALARY_PERCENTAGE
#     exec_sal = wage_base + wage_base * Market.EXEC_SALARY_PERCENTAGE

#     money_circulation = 0

#     for each_worker in all_workers_list:
#         if each_worker.skill_level < Worker.JUNIOR_SKILL_LEVEL:
#             each_worker.worker_account_balance += (jun_sal * 12)
#             money_circulation += jun_sal * 12
        
#         elif (each_worker.skill_level > Worker.JUNIOR_SKILL_LEVEL) and (each_worker.skill_level < Worker.SENIOR_SKILL_LEVEL):
#             each_worker.worker_account_balance += (sen_sal * 12)
#             money_circulation += sen_sal * 12
        
#         else:
#             each_worker.worker_account_balance += (exec_sal * 12)
#             money_circulation += exec_sal * 12

#     return money_circulation


def hire_initial_workers(all_companies_list, employed_jun_list, employed_sen_list, employed_exec_list, wage_base):

    money_circulation = 0
    all_companies_list = sorted(all_companies_list, key=lambda cmp:cmp.company_account_balance, reverse=True)

    # Hire Juniors
    salary = wage_base * 12    
    jun_money, employed_jun_list = hire_workers(all_companies_list, employed_jun_list, salary)

    # Hire Seniors
    salary = (wage_base + wage_base * Market.SENIOR_SALARY_PERCENTAGE) * 12
    sen_money, employed_sen_list = hire_workers(all_companies_list, employed_sen_list, salary)

    # Hire Executives
    salary = (wage_base + wage_base * Market.EXEC_SALARY_PERCENTAGE) * 12    
    exec_money, employed_exec_list = hire_workers(all_companies_list, employed_exec_list, salary)

    money_circulation = jun_money + sen_money + exec_money

    return all_companies_list, money_circulation, employed_jun_list, employed_sen_list, employed_exec_list

def hire_workers(all_companies_list, employed_worker_list, salary):
    
    i = 0    
    money_circulation = 0
    num_workers = len(employed_worker_list)
    while i < num_workers:
        for company_obj in all_companies_list:
            worker = employed_worker_list[i]
            worker.is_employed=True
            worker.salary=salary
            
            worker.worker_account_balance += worker.salary * 12
            money_circulation = money_circulation = + worker.worker_account_balance
            worker.skill_improvement_rate = company_obj.skill_improvement_rate

            # worker.works_for_company = company
            # company_obj.employed_workers_list.append(worker)
            worker.works_for_company = company_obj
            i = i +1
            if i >= num_workers:
                break        
    return money_circulation, employed_worker_list


def collect_metrics(country):
    current_state = dict()
    current_state["Unemployment Rate"] = float("{:.2f}".format(100.0))
    current_state["Poverty Rate"] = float("{:.2f}".format(0.0))
    current_state["Minimum wage"] = country.minimum_wage
    current_state["Inflation Rate"] = float("{:.2f}".format(0.0))
    current_state["population"] = country.population

    return current_state

def get_latest_game_number(user):
    max_game_query = Game.objects.filter(player=user).aggregate(max_game_number=models.Max("game_number"))
    if not max_game_query or max_game_query["max_game_number"]  == None:
        game_number = 1
    else:
        game_number = max_game_query["max_game_number"]  + 1
    return game_number

def print_needed(metrics, country):
    # metrics = Metric()
    print("====================== YEAR ", metrics.year , "======================")
    print("Year - " ,metrics.year)
    print("Minwage - ", metrics.minimum_wage)
    print("Population - ", metrics.population)
    print("retired people - ", metrics.num_retired)
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
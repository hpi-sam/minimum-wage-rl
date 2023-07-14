
from itertools import count
# from ..models.game_metric import GameMetric
from ..models.metrics import Metric
from ..models.worker import Worker
# from ..models.bank import Bank
from ..models.country import Country
from ..models.market import Market
from ..models.bank import Bank
from ..models.game import Game
# from ..models.company import Company
from ..config import ConfigurationParser
from .code_files import country_module
import numpy as np
from django.db import models
# from django.db import transaction

# from economic_simulator.models import country

file_name = "config_file.txt"
config_parser = ConfigurationParser.get_instance(file_name).parser



# @transaction.atomic
def initialize_and_start(user, level, ai_flag, player_game):

    config_level = None
    stagflation_config = False

    game = Game()
    game_number = get_latest_game_number()
    game.player = user
    game.game_number = game_number
    game.ai_flag = ai_flag
    game.level = level
    if ai_flag:
        game.player_game_number = player_game.game_number


    if game.level == 1:
        config_level = "Level_1"
    elif game.level == 2:
        config_level = "Level_2"    
    elif game.level == 3:
        config_level = "Level_1"
    elif game.level == 4:
        level = 1        
        config_level = "Level_" + str(level)
        stagflation_config = True    

    RICH_JUN_PERCENT = config_parser.getfloat(config_level,"rich_jun_workers_percentage")
    RICH_SEN_PERCENT = config_parser.getfloat(config_level,"rich_sen_workers_percentage")
    RICH_EXEC_PERCENT = config_parser.getfloat(config_level,"rich_exec_workers_percentage")
    EMPLOYED_AT_STARTUP = config_parser.getfloat(config_level,"employed_at_startup")
    initial_bank_balance_percent = config_parser.getfloat(config_level,"initial_bank_balance_percent")
    each_level_population = int(config_parser.get(config_level,"initial_each_level_population"))

    min_wage_weightage = float(config_parser.get("worker","initial_balance_weightage"))
    # Money_Circulation_MAX = config_parser.getint(config_level,"money_circulation_max")
    # Money_Circulation_MIN = config_parser.getint(config_level,"money_circulation_min")
    # Bank_Balance_MAX = config_parser.getint(config_level,"bank_balance_max")
    # Bank_Balance_MIN = config_parser.getint(config_level,"bank_balance_min")
    # Quantity_MAX = config_parser.getint(config_level,"quantity_max")
    # Quantity_MIN = config_parser.getint(config_level,"quantity_min")

    JUN_SKILL_LOW_LIM = config_parser.getint("worker","jun_skill_low_limit")
    JUN_SKILL_HIGH_LIM_OFFSET = config_parser.getint("worker","jun_skill_high_limit_offset")
    SEN_SKILL_LOW_LIM_OFFSET = config_parser.getint("worker","sen_skill_low_limit_offset")
    SEN_SKILL_HIGH_LIM_OFFSET = config_parser.getint("worker","sen_skill_high_limit_offset")
    EXEC_SKILL_LOW_LIM_OFFSET = config_parser.getint("worker","exec_skill_low_limit_offset")
    EXEC_SKILL_HIGH_LIM_OFFSET = config_parser.getint("worker","exec_skill_high_limit_offset")


    game.episode_number = 1
    # game_metric = GameMetric(1)    

    all_workers_list = []
    all_companies_list = []

    metric_obj = Metric()
    metric_obj.year = 1

    # 1: Create Market 
    market_obj = Market()
    # market_obj.month = market_obj.year = 0
    # market_obj.market_value_year = 0

    # 2: Create Country
    country = Country(each_level_population)
    # country.total_money_printed = Country.INITIAL_BANK_BALANCE
    country_module.create_country(country, each_level_population, ai_flag)
    country.population_increase = float(config_parser.get(config_level,"population_increase"))
    
    initial_bank_balance = get_central_bank_balance(initial_bank_balance_percent, country)
    country.INITIAL_BANK_BALANCE = initial_bank_balance

    country.market = market_obj

    # 2.1 Add Stagflation settings
    if stagflation_config:
        set_stagflation_parameters(country)

    # 3: Create Company
    all_companies_list = country_module.create_company(country)

    country.company_list = all_companies_list

    metric_obj.num_small_companies = Country.INITIAL_NUM_SMALL_COMPANIES
    metric_obj.num_medium_companies = Country.INITIAL_NUM_MEDIUM_COMPANIES
    metric_obj.num_large_companies = Country.INITIAL_NUM_LARGE_COMPANIES

    metric_obj.total_filled_jun_pos = 0
    metric_obj.total_filled_sen_pos = 0
    metric_obj.total_filled_exec_pos = 0

    # 5: Number of workers to be employed at start up
    employed_at_startup = country.INITIAL_EACH_LEVEL_POPULATION * 3 * EMPLOYED_AT_STARTUP

    # 6: Create Workers
    all_workers_list, new_num_of_juniors, new_num_of_seniors, new_num_of_executives, employed_jun_list, employed_sen_list, employed_exec_list = country_module.add_new_workers(country, country.INITIAL_EACH_LEVEL_POPULATION, employed_at_startup, JUN_SKILL_LOW_LIM, JUN_SKILL_HIGH_LIM_OFFSET, SEN_SKILL_LOW_LIM_OFFSET, SEN_SKILL_HIGH_LIM_OFFSET, EXEC_SKILL_LOW_LIM_OFFSET, EXEC_SKILL_HIGH_LIM_OFFSET)
    country.unemployed_workers = all_workers_list

    num_workers_hired = len(employed_jun_list) + len(employed_sen_list) + len(employed_exec_list)

    # 4: Create Bank
    bank = Bank()
    bank = country_module.create_bank(bank, country.INITIAL_BANK_BALANCE)
    country.bank = bank

    # 7: Employee workers
    wage_base = country.minimum_wage
    all_companies_list, employed_money_circulation = hire_initial_workers(all_companies_list, employed_jun_list, employed_sen_list, employed_exec_list, wage_base)

    metric_obj.unemployed_jun_pos = new_num_of_juniors
    metric_obj.unemployed_sen_pos = new_num_of_seniors
    metric_obj.unemployed_exec_pos = new_num_of_executives

    metric_obj.average_jun_sal = country.minimum_wage
    metric_obj.average_sen_sal = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
    metric_obj.average_exec_sal = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE

    metric_obj.average_sal = (metric_obj.average_jun_sal + metric_obj.average_sen_sal + metric_obj.average_exec_sal)/len(all_workers_list)

    metric_obj.unemployment_rate = 100
    metric_obj.poverty_rate = 100

    metric_obj.population = country.population
    metric_obj.minimum_wage = country.minimum_wage
    metric_obj.game = game

    metric_obj.inflation = 0
    metric_obj.inflation_rate = 0

    metric_obj.bank_account_balance = country.INITIAL_BANK_BALANCE

    # 6: Initial quantity    
    money_circulation = get_money_circulation(all_workers_list, country, min_wage_weightage, employed_money_circulation, RICH_JUN_PERCENT, RICH_SEN_PERCENT, RICH_EXEC_PERCENT)
    country.quantity = money_circulation/country.product_price
    country.money_circulation = money_circulation
    
    metric_obj.product_price = country.product_price
    metric_obj.quantity = country.quantity
    metric_obj.produced_quantity = country.quantity
    metric_obj.money_circulation = money_circulation

    # 7: Assign country
    # country.metrics_list.append(metric_obj)
    game.game_metric_list.append(metric_obj)


    game.country = country

    # print_metrics(country)

    normazlized_current_state, current_state = collect_metrics(country, num_workers_hired)

    return normazlized_current_state, current_state, game

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

# def print_metrics(country):
#     print("=========================== Year ", country.year, "==========================")
#     print("Minimum wage - ", country.minimum_wage)
#     print("Quantity - ", country.quantity)
#     print("Product price - ", country.product_price)
#     print("Population - ", country.population)
#     print(" Bank balance - ", country.bank.liquid_capital)


def get_money_circulation(all_workers_list, country, min_wage_weightage, employed_money_circulation, RICH_JUN_PERCENT, RICH_SEN_PERCENT, RICH_EXEC_PERCENT):

    rich_jun_acct_bal, rich_sen_acct_bal, rich_exec_acct_bal = calculate_rich_worker_initial_balance(country)
    rich_jun, rich_sen, rich_exec = account_balance_division(RICH_JUN_PERCENT, RICH_SEN_PERCENT, RICH_EXEC_PERCENT, country.INITIAL_EACH_LEVEL_POPULATION)

    wage_base = country.minimum_wage * min_wage_weightage
    jun_sal = wage_base
    sen_sal = wage_base + wage_base * Market.SENIOR_SALARY_PERCENTAGE
    exec_sal = wage_base + wage_base * Market.EXEC_SALARY_PERCENTAGE

    money_circulation = 0
    money_circulation = money_circulation + employed_money_circulation

    for each_worker in all_workers_list:
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
    
def hire_initial_workers(all_companies_list, employed_jun_list, employed_sen_list, employed_exec_list, wage_base):

    money_circulation = 0
    # all_companies_list = sorted(all_companies_list, key=lambda cmp:cmp.company_account_balance, reverse=True)    
    # Hire Juniors
    salary = wage_base * 12    
    jun_money = hire_workers(all_companies_list, employed_jun_list, salary)

    # Hire Seniors
    salary = (wage_base + wage_base * Market.SENIOR_SALARY_PERCENTAGE) * 12
    sen_money = hire_workers(all_companies_list, employed_sen_list, salary)

    # Hire Executives
    salary = (wage_base + wage_base * Market.EXEC_SALARY_PERCENTAGE) * 12    
    exec_money = hire_workers(all_companies_list, employed_exec_list, salary)

    money_circulation = jun_money + sen_money + exec_money

    return all_companies_list, money_circulation

def hire_workers(all_companies_list, employed_worker_list, salary):
    
    i = 0
    j = 0
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
            company_obj.employed_workers_list.append(worker)
            i = i +1
            if i >= num_workers:
                break        
            j = j + 1

    return money_circulation

def collect_metrics(country, num_workers_hired):
    normazlized_current_state = list()
    normazlized_current_state.append(country.minimum_wage)
    normazlized_current_state.append(float("{:.6f}".format(np.log(country.product_price))))
    normazlized_current_state.append(float("{:.6f}".format(np.log(country.quantity))))
    # (country.population - num_workers_hired)/country.population
    normazlized_current_state.append(float("{:.2f}".format(1.0)))
    normazlized_current_state.append(float("{:.2f}".format(0.0)))
    normazlized_current_state.append(float("{:.6f}".format(np.log(country.bank.liquid_capital))))
    # (country.population - num_workers_hired)/country.population
    normazlized_current_state.append(float("{:.2f}".format(1.0)))
    normazlized_current_state.append(float("{:.6f}".format(np.log(country.money_circulation))))
    normazlized_current_state.append(float("{:.6f}".format(np.log(country.population))))

    current_state = dict()
    current_state["Year"] = country.year
    current_state["Unemployment Rate"] = float("{:.2f}".format(100.0))
    current_state["Poverty Rate"] = float("{:.2f}".format(100.0))
    current_state["Minimum wage"] = country.minimum_wage
    current_state["Inflation Rate"] = float("{:.2f}".format(0.0))
    current_state["population"] = country.population

    return normazlized_current_state, current_state

def get_latest_game_number():
    max_game_query = Game.objects.distinct().aggregate(max_game_number=models.Max("game_number"))
    if not max_game_query or max_game_query["max_game_number"]  == None:
        game_number = 1
    else:
        game_number = max_game_query["max_game_number"]  + 1
    return game_number

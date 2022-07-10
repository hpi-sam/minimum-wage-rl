# from itertools import count
from models.game_metric import GameMetric
from models.metrics import Metric
from models.worker import Worker
# from ..models.bank import Bank
from models.country import Country
from models.market import Market
# from ..models.company import Company
from .config import ConfigurationParser
from .code_files import country_module
# from django.db import transaction

# from economic_simulator.models import country

config_parser = ConfigurationParser.get_instance().parser

# @transaction.atomic
def start(game, episode_num):

    game_metric = GameMetric(episode_num)
    game.game_metric_list.append(game_metric)

    min_wage_weightage = float(config_parser.get("worker","initial_balance_weightage"))

    all_workers_list = []
    all_companies_list = []

    metric_obj = Metric()
    metric_obj.year = 0

    # 1: Create Market 
    market_obj = Market()
    market_obj.month = market_obj.year = 0
    market_obj.market_value_year = 0

    # 2: Create Country
    country = Country()
    # country.total_money_printed = Country.INITIAL_BANK_BALANCE
    country_module.create_country(country)
    country.market = market_obj

    # 3: Create Company
    all_companies_list = country_module.create_company(country)
    country.company_list = all_companies_list

    metric_obj.num_small_companies = Country.INITIAL_NUM_SMALL_COMPANIES
    metric_obj.num_medium_companies = Country.INITIAL_NUM_MEDIUM_COMPANIES
    metric_obj.num_large_companies = Country.INITIAL_NUM_LARGE_COMPANIES

    metric_obj.total_filled_jun_pos = 0
    metric_obj.total_filled_sen_pos = 0
    metric_obj.total_filled_exec_pos = 0

    # 4: Create Bank
    bank = country_module.create_bank(Country.INITIAL_BANK_BALANCE)
    country.bank = bank

    # 5: Create Workers
    all_workers_list, new_num_of_juniors, new_num_of_seniors, new_num_of_executives = country_module.add_new_workers(country)
    country.unemployed_workers = all_workers_list

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
    # metric_obj.country_of_residence = country

    metric_obj.inflation = 0
    metric_obj.inflation_rate = 0

    metric_obj.bank_account_balance = Country.INITIAL_BANK_BALANCE

    # 6: Initial quantity    
    money_circulation = get_money_circulation(all_workers_list, country, min_wage_weightage)
    country.quantity = money_circulation/country.product_price
    country.money_circulation = money_circulation
    
    metric_obj.product_price = country.product_price
    metric_obj.quantity = country.quantity
    metric_obj.money_circulation = money_circulation

    # 7: Assign country
    country.metrics_list.append(metric_obj)
    game.country = country

    # print_metrics(country)

    return collect_metrics(country)

def print_metrics(country):
    print("=========================== Year ", country.year, "==========================")
    print("Minimum wage - ", country.minimum_wage)
    print("Quantity - ", country.quantity)
    print("Product price - ", country.product_price)
    print("Population - ", country.population)
    print(" Bank balance - ", country.bank.liquid_capital)

def get_money_circulation(all_workers_list, country, min_wage_weightage):

    wage_base = country.minimum_wage * min_wage_weightage
    jun_sal = wage_base
    sen_sal = wage_base + wage_base * Market.SENIOR_SALARY_PERCENTAGE
    exec_sal = wage_base + wage_base * Market.EXEC_SALARY_PERCENTAGE

    money_circulation = 0

    for each_worker in all_workers_list:
        if each_worker.skill_level < Worker.JUNIOR_SKILL_LEVEL:
            each_worker.worker_account_balance += (jun_sal * 12)
            money_circulation += jun_sal * 12
        
        elif (each_worker.skill_level > Worker.JUNIOR_SKILL_LEVEL) and (each_worker.skill_level < Worker.SENIOR_SKILL_LEVEL):
            each_worker.worker_account_balance += (sen_sal * 12)
            money_circulation += sen_sal * 12
        
        else:
            each_worker.worker_account_balance += (exec_sal * 12)
            money_circulation += exec_sal * 12

    return money_circulation

def collect_metrics(country):
    current_state = dict()
    current_state["Unemployment Rate"] = float("{:.2f}".format(100.0))
    current_state["Poverty Rate"] = float("{:.2f}".format(0.0))
    current_state["Minimum wage"] = country.minimum_wage
    current_state["Inflation Rate"] = float("{:.2f}".format(0.0))
    current_state["population"] = country.population

    return current_state
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

from economic_simulator.models import country

config_parser = ConfigurationParser.get_instance().parser

@transaction.atomic
def start(user):

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
    country_module.create_country(country,all_companies_list)
    country.market = market_obj    
    country.player = user

    # 3: Create Company
    all_companies_list = country_module.create_company(country)
    
    metric_obj.num_small_companies = Country.INITIAL_NUM_SMALL_COMPANIES
    metric_obj.num_medium_companies = Country.INITIAL_NUM_MEDIUM_COMPANIES
    metric_obj.num_large_companies = Country.INITIAL_NUM_LARGE_COMPANIES

    metric_obj.total_filled_jun_pos = 0
    metric_obj.total_filled_sen_pos = 0
    metric_obj.total_filled_exec_pos = 0


    # 4: Create Bank
    bank = Bank()
    country_module.create_bank(bank, country, Country.INITIAL_BANK_BALANCE)

    # 5: Create Game
    game_number = get_latest_game_number(user)
    game = Game()
    game.player = user
    game.game_number = game_number
    country.game = game

    # 6: Create Workers
    all_workers_list, new_num_of_juniors, new_num_of_seniors, new_num_of_executives = country_module.add_new_workers(country, Country.INITIAL_POPULATION)
    
    metric_obj.unemployed_jun_pos = new_num_of_juniors
    metric_obj.unemployed_sen_pos = new_num_of_seniors
    metric_obj.unemployed_exec_pos = new_num_of_executives

    metric_obj.average_jun_sal = country.minimum_wage
    metric_obj.average_sen_sal = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
    metric_obj.average_exec_sal = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE

    metric_obj.average_sal = (metric_obj.average_jun_sal * new_num_of_juniors   + 
                            metric_obj.average_sen_sal * new_num_of_seniors + 
                            metric_obj.average_exec_sal * new_num_of_executives)/len(all_workers_list)

    metric_obj.unemployment_rate = 100
    metric_obj.poverty_rate = 100

    metric_obj.population = country.population
    metric_obj.minimum_wage = country.minimum_wage
    metric_obj.country_of_residence = country

    metric_obj.inflation = 0
    metric_obj.inflation_rate = 0

    metric_obj.bank_account_balance = Country.INITIAL_BANK_BALANCE


    # 7: Set initial product price and quantity
    # country.product_price
    # country.quantity
    # country.minimum_wage

    # 7.1: Initial quantity    
    money_circulation = get_money_circulation(all_workers_list, country, min_wage_weightage)
    country.quantity = money_circulation/country.product_price
    country.money_circulation = money_circulation

    metric_obj.product_price = country.product_price
    metric_obj.quantity = country.quantity
    metric_obj.money_circulation = money_circulation

    # market_obj.save()
    # country.save()

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
    for each_citizen in all_workers_list:
        each_citizen.save()

    metric_obj.save()

    print_needed(metric_obj, country)

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
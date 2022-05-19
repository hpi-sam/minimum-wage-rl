from itertools import count
from ..models.worker import Worker
from ..models.bank import Bank
from ..models.country import Country
from ..models.market import Market
from ..models.company import Company
from ..models.game import Game
from .config import ConfigurationParser
from django.db import models
from .code_files import country_module
from django.db import transaction

from economic_simulator.models import country

config_parser = ConfigurationParser.get_instance().parser

@transaction.atomic
def start(user):

    all_workers_list = []
    all_companies_list = []

    # save bank : bank.save()
    # save game : game.save()
    # save market : market_obj.save()
    # save country : country.save()
    # save worker
    # save company

    # 1: Create Market 
    market_obj = Market()
    market_obj.month = market_obj.year = 0
    market_obj.market_value_year = 0
    market_obj.run = 0

    # 2: Create Country
    country = Country()
    country.total_money_printed = Country.INITIAL_BANK_BALANCE    
    country_module.create_country(country,all_companies_list)
    country.market = market_obj    
    country.player = user

    # 3: Create Company
    all_companies_list = country_module.create_company(country)

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
    all_workers_list = country_module.add_new_workers(country)

    # 7: Set initial product price and quantity
    country.product_price
    country.quantity
    country.minimum_wage

    # 7.1: Initial quantity
    
    jun_sal, sen_sal, exec_sal = get_money_circulation(all_workers_list, country)

    country.quantity = (jun_sal + sen_sal + exec_sal)/country.product_price

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

    print_metrics(country)

    return collect_metrics(country)

def print_metrics(country):
    print("=========================== Year ", country.year, "==========================")
    print("Minimum wage - ", country.minimum_wage)
    print("Quantity - ", country.quantity)
    print("Product price - ", country.product_price)
    print("Population - ", country.population)
    print(" Bank balance - ", country.bank.liquid_capital)

def get_money_circulation(all_workers_list, country):
    jun_pos = 0
    sen_pos = 0
    exec_pos = 0

    for each_worker in all_workers_list:
        if each_worker.skill_level < Worker.JUNIOR_SKILL_LEVEL:
            jun_pos = jun_pos + 1
        elif (each_worker.skill_level > Worker.JUNIOR_SKILL_LEVEL) and (each_worker.skill_level < Worker.SENIOR_SKILL_LEVEL):
            sen_pos = sen_pos + 1
        else:
            exec_pos = exec_pos + 1

    jun_sal = jun_pos * country.minimum_wage * 12
    sen_sal = sen_pos * (country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE) * 12
    exec_sal = exec_pos * (country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE) * 12

    return jun_sal, sen_sal, exec_sal

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



# # startup
# def add_new_citizens(country, amount):
#     for _ in range(amount):
#         citizen = Worker()
#         InitializeEmployee(0, country, citizen)
#         all_citizens_list.append(citizen)

# def InitializeEmployee(initialBalance, country, citizen): #MWCountry
        
#     citizen.worker_account_balance = initialBalance

#     citizen.salary = citizen.age = 0
#     citizen.skill_level = 1
#     # citizen.initial_skill_level = 1
#     citizen.bought_essential_product = citizen.buy_first_extra_product = citizen.buy_second_extra_product = False
#     citizen.is_employed = citizen.has_company = False

#     # Moving to a country
#     citizen.country_of_residence = country
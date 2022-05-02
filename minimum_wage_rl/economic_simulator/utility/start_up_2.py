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
    country.quantity = (len(all_workers_list) * country.minimum_wage)/country.product_price

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

    return collect_metrics(country)

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
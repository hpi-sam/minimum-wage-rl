# from models.country import Country
# from models.metrics import Metric
from models.country import Country
from models.market import Market
from models.worker import Worker
from models.country import Country
from functools import reduce
from math import ceil, floor
from utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser
import logging
logging.basicConfig(filename="C:\\Users\\AkshayGudi\\Documents\\3_MinWage\\minimum_wage_rl\\economic_simulator\\my_log.log", level=logging.INFO)


def set_product_price_and_quantity(emp_worker_list, unemp_worker_list, country, metrics):
    
    print("Money in bank - ", country.bank.liquid_capital)

    inflation_weightage = country.inflation if country.inflation > 0 else 0.0
    emp_workers_acct = reduce(lambda result, worker: result + (worker.worker_account_balance - (worker.worker_account_balance * Worker.SAVINGS_PERCENT * inflation_weightage)), emp_worker_list, 0 )
    
    unemp_workers_acct = reduce(lambda result, worker: result + (worker.worker_account_balance - (worker.worker_account_balance * Worker.SAVINGS_PERCENT * inflation_weightage)), unemp_worker_list, 0 )

    old_money_circulation = country.money_circulation
    current_money_circulation = emp_workers_acct + unemp_workers_acct
    country.money_circulation = current_money_circulation
    velocity_of_money = 1
    current_product_price = country.product_price

    if Market.EXPIRABLE_GOODS:
        old_quantity = 0.0
    else:
        old_quantity = country.quantity

    old_inflation = country.inflation
    inflation = 0.0
    inflation_rate = 0.0
    steady_product_price = False
    new_quantity = 0
    
    bank_money_spent = 0
    logging.info("old quantity - " + str(old_quantity))
    needed_quantity = country.population * 12
    produce_quantity = needed_quantity - old_quantity if needed_quantity - old_quantity > 0 else 0

    # 1. Check if latest money circulation is less than previous money circulation
    if current_money_circulation <= old_money_circulation:

        if produce_quantity > 0:
            produce_quantity = produce_extra_quantity(produce_quantity, current_product_price, country)
        else:
            print("here")
        
        if (produce_quantity + old_quantity) <= 0:
                print("here")

        new_price = round(current_money_circulation/(produce_quantity + old_quantity), 2)

        if new_price < Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD:
            new_price = Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD

        new_price, deflation = calculate_deflation(current_product_price, new_price, old_inflation, metrics, country)
        country.product_price = new_price
        country.quantity = produce_quantity + old_quantity

        metrics.product_price = new_price
        metrics.quantity = produce_quantity + old_quantity
    
    else:

        # if produce_quantity > 0:
        new_price = round(current_money_circulation/(produce_quantity + old_quantity), 2)

        if new_price < Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD:
            new_price = Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD

        inflation = calculate_inflation(current_product_price, new_price, old_inflation, metrics, country)
        
        # 1.1 Inflation below a given threshold - then - Increase Quantity (maybe price)
        if inflation <= Market.LOW_THRESHOLD_INFLATION:
            new_quantity = int(current_money_circulation/current_product_price)
            new_quantity = max(new_quantity, needed_quantity)

            produce_quantity = new_quantity - old_quantity

            produce_quantity = produce_extra_quantity(produce_quantity,current_product_price,country)
            new_price = round(current_money_circulation/(produce_quantity + old_quantity), 2)

            if new_price < Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD:
                new_price = Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD
    
            country.product_price = new_price
            country.quantity = produce_quantity + old_quantity

            metrics.product_price = new_price
            metrics.quantity = produce_quantity + old_quantity


        # 1.2 Inflation above a given threshold - then - Increase Quantity (maybe price)
        # What was removed - Upper limit for Quantity production
        elif inflation > Market.HIGH_THRESHOLD_INFLATION:
            new_quantity = int(current_money_circulation/current_product_price)
            new_quantity = max(new_quantity, needed_quantity)

            produce_quantity = new_quantity - old_quantity

            produce_quantity = produce_extra_quantity(produce_quantity,current_product_price,country)
            new_price = round(current_money_circulation/(produce_quantity + old_quantity), 2)

            if new_price < Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD:
                new_price = Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD

            country.product_price = new_price
            country.quantity = produce_quantity + old_quantity

            metrics.product_price = new_price
            metrics.quantity = produce_quantity + old_quantity

            # 1.3 Inflation in between certain limit - then - Increase Product price
        else:
            produce_quantity = produce_extra_quantity(produce_quantity,current_product_price, country)
            new_price = round(current_money_circulation/(produce_quantity + old_quantity), 2)

            if new_price < Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD:
                new_price = Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD

            country.product_price = new_price
            country.quantity = produce_quantity + old_quantity

            metrics.product_price = new_price
            metrics.quantity = produce_quantity + old_quantity
        
        calculate_inflation(current_product_price, new_price, old_inflation, metrics, country)
        # else:
        #     calculate_inflation(current_product_price, current_product_price, old_inflation, metrics)

        if country.product_price <= 0.0:
            country.product_price = 0.01
            metrics.product_price = 0.01

# Production cost and Transport Cost
def produce_extra_quantity(produce_quantity, price, country):

    money_needed = produce_quantity * price
    transport_cost = produce_quantity * Country.OIL_PER_UNIT_QUANTITY * Country.OIL_COST_PER_LITRE
    print("Needed Quantity - ", produce_quantity)


    if country.bank.liquid_capital * Market.MIN_BALANCE_INFLATION > (money_needed + transport_cost):
        print("Cost of import - ", transport_cost)
        print("Production cost - ", money_needed)
        print("Produced Quantity - ", produce_quantity)

        country.bank.liquid_capital = country.bank.liquid_capital - money_needed
        country.bank.liquid_capital = country.bank.liquid_capital - transport_cost
        logging.info("Money Spent - " + str(money_needed))
        return int(produce_quantity)
    else:

        money_available =  country.bank.liquid_capital * Market.MIN_BALANCE_INFLATION
        possible_quantity = ceil(money_available/price)
        transport_cost = possible_quantity * Country.OIL_PER_UNIT_QUANTITY * Country.OIL_COST_PER_LITRE

        print("Cost of import - ", transport_cost)
        print("Production cost - ", money_available)
        print("Possible Quantity - ", possible_quantity)

        country.bank.liquid_capital = country.bank.liquid_capital - money_available
        country.bank.liquid_capital = country.bank.liquid_capital - transport_cost
        print("Bank Balance after production - ", country.bank.liquid_capital)
        logging.info("Money Spent - " + str(money_available))
        return int(possible_quantity)

def calculate_deflation(current_product_price, new_product_price, old_inflation, metrics, country):
    
    deflation = (new_product_price - current_product_price)/current_product_price
    if abs(deflation) > 0.5:
        deflation = -0.5
        new_product_price = round(current_product_price + current_product_price * deflation, 2)

        if new_product_price < Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD:
            new_product_price = Market.INITIAL_PRODUCT_PRICE * Market.PRODUCT_PRICE_THRESHOLD
            deflation = (new_product_price - current_product_price)/current_product_price
    
    deflation_rate = (deflation - old_inflation)/old_inflation if old_inflation> 0 else (deflation - old_inflation)
    metrics.inflation = round(deflation, 2)
    country.inflation = round(deflation, 2)
    metrics.inflation_rate = round(deflation_rate, 2)

    return new_product_price, deflation

def calculate_inflation(current_product_price, new_product_price, old_inflation, metrics, country):
    inflation = (new_product_price - current_product_price)/current_product_price
    inflation_rate = (inflation - old_inflation)/old_inflation if old_inflation> 0 else (inflation - old_inflation)
    metrics.inflation = round(inflation, 2)
    country.inflation = round(inflation, 2)
    metrics.inflation_rate = round(inflation_rate, 2)

    return inflation

def buy_products(fin_workers_list, country, poverty_count, metrics):

    employee_details_map = {"jun_workers": 0, "sen_workers": 0, "exec_workers": 0, 
                            "jun_worker_sal": 0.0, "sen_worker_sal": 0.0, "exec_worker_sal": 0.0}

    unemployed = 0
    unemployed_jun = 0
    unemployed_sen = 0
    unemployed_exec = 0

    total_junior = 0
    total_senior = 0
    total_exec = 0
    
    if country.product_price < 0.0:
        print("=========================== LOW PRICE =======================")
    
    total_money_deposited = 0
    for each_worker in fin_workers_list:
    # if this condition true buy products
        worker_money_deposited = 0
        if each_worker.worker_account_balance > country.product_price * 12:
            each_worker.worker_account_balance = each_worker.worker_account_balance - country.product_price * 12
            country.bank.liquid_capital = country.bank.liquid_capital + country.product_price * 12
            country.quantity = country.quantity - 12
            salary_metrics(each_worker, employee_details_map)
            worker_money_deposited =  country.product_price * 12      

        else:
            payable_months = floor(each_worker.worker_account_balance/country.product_price)
            each_worker.worker_account_balance = each_worker.worker_account_balance - country.product_price * payable_months
            country.bank.liquid_capital = country.bank.liquid_capital + country.product_price * payable_months
            country.quantity = country.quantity - payable_months
            poverty_count = poverty_count + 1
            worker_money_deposited = country.product_price * payable_months

            salary_metrics(each_worker, employee_details_map)

        total_money_deposited = total_money_deposited + worker_money_deposited

        if each_worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
            total_junior = total_junior  + 1
        elif (each_worker.skill_level > Worker.JUNIOR_SKILL_LEVEL) and (each_worker.skill_level <= Worker.SENIOR_SKILL_LEVEL):
            total_senior = total_senior + 1
        else:
            total_exec = total_exec + 1



        if not(each_worker.is_employed):
            unemployed = unemployed + 1
            
            if each_worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
                unemployed_jun = unemployed_jun  + 1
            elif (each_worker.skill_level > Worker.JUNIOR_SKILL_LEVEL) and (each_worker.skill_level <= Worker.SENIOR_SKILL_LEVEL):
                unemployed_sen = unemployed_sen + 1
            else:
                unemployed_exec = unemployed_exec + 1

    logging.info("Total Money deposited - " + str(total_money_deposited))
    logging.info("Country Quantity - " + str(country.quantity))

    # Add mertrics
    # metrics.total_filled_jun_pos = employee_details_map["jun_workers"]
    # metrics.total_filled_sen_pos = employee_details_map["sen_workers"]
    # metrics.total_filled_exec_pos = employee_details_map["exec_workers"]

    metrics.average_jun_sal = round(employee_details_map["jun_worker_sal"]/employee_details_map["jun_workers"] if employee_details_map["jun_workers"] > 0 else 0, 1)
    metrics.average_sen_sal = round(employee_details_map["sen_worker_sal"]/employee_details_map["sen_workers"] if employee_details_map["sen_workers"] > 0 else 0, 1)
    metrics.average_exec_sal = round(employee_details_map["exec_worker_sal"]/employee_details_map["exec_workers"] if employee_details_map["exec_workers"] > 0 else 0, 1)
    metrics.average_sal = round((employee_details_map["jun_worker_sal"] + employee_details_map["sen_worker_sal"] + employee_details_map["exec_worker_sal"])/len(fin_workers_list) if len(fin_workers_list) > 0 else 0, 1)
    
    metrics.old_poverty_rate = metrics.poverty_rate
    metrics.old_unemployment_rate = metrics.unemployment_rate
    
    metrics.unemployed_junior_rate = round((unemployed_jun/total_junior) *100 , 2)
    metrics.unemployed_senior_rate = round((unemployed_sen/total_senior) *100 , 2)
    metrics.unemployed_exec_rate = round((unemployed_exec/total_exec) *100 , 2)

    metrics.unemployment_rate = round(unemployed/len(fin_workers_list) * 100, 2)
    metrics.poverty_rate = round(poverty_count/len(fin_workers_list) * 100, 2)
    metrics.population = len(fin_workers_list)
    metrics.minimum_wage = country.minimum_wage

def salary_metrics(each_worker, employee_details_map):

    if each_worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL and (each_worker.is_employed):
        employee_details_map["jun_workers"] = employee_details_map["jun_workers"] + 1
        employee_details_map["jun_worker_sal"] = employee_details_map["jun_worker_sal"] + each_worker.salary

    elif each_worker.skill_level <= Worker.SENIOR_SKILL_LEVEL and (each_worker.is_employed):
        employee_details_map["sen_workers"] = employee_details_map["sen_workers"] + 1
        employee_details_map["sen_worker_sal"] = employee_details_map["sen_worker_sal"] + each_worker.salary
    
    elif each_worker.skill_level > Worker.SENIOR_SKILL_LEVEL and (each_worker.is_employed):
        employee_details_map["exec_workers"] = employee_details_map["exec_workers"] + 1
        employee_details_map["exec_worker_sal"] = employee_details_map["exec_worker_sal"] + each_worker.salary
        

# def increase_quantity(money_circulation,velocity_of_money,delta_quantity, new_quantity, current_quantity, country, metrics, product_price):

#     money_needed = delta_quantity * product_price

#     # 4.6 Check if bank has enough money to produce more products
#     if country.bank.liquid_capital * Market.MIN_BALANCE_INFLATION > money_needed:
#         country.bank.liquid_capital = country.bank.liquid_capital - money_needed
#         new_quantity = delta_quantity + current_quantity
#         country.quantity = new_quantity
#         inflation = calculate_inflation(country.product_price,product_price, country.inflation, metrics)
#         country.product_price = product_price
#     else:
#         money_available =  country.bank.liquid_capital * Market.BANK_LOAN_INFLATION
#         delta_possible_quantity = ceil(money_available/country.product_price)
#         country.bank.liquid_capital = country.bank.liquid_capital - money_available
#         new_quantity = delta_possible_quantity + current_quantity
#         new_product_price = (money_circulation * velocity_of_money)/new_quantity if money_circulation > 0 else country.product_price

#         country.product_price = new_product_price
#         country.quantity = new_quantity

#         inflation = calculate_inflation(country.product_price,new_product_price, country.inflation, metrics)

#     country.quantity = new_quantity
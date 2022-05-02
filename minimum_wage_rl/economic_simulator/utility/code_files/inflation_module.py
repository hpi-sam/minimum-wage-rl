from ...models.market import Market
from ...models.worker import Worker
from functools import reduce
from math import ceil, floor

def set_product_price_and_quantity(emp_worker_list, unemp_worker_list, country, metrics):

    emp_workers_acct = reduce(lambda result, worker: result + worker.worker_account_balance, emp_worker_list, 0 )
    unemp_workers_acct = reduce(lambda result, worker: result + worker.worker_account_balance, unemp_worker_list, 0 )

    money_circulation = emp_workers_acct + unemp_workers_acct
    velocity_of_money = 1
    current_product_price = country.product_price
    current_quantity = country.quantity
    old_inflation = country.inflation
    inflation = 0.0
    inflation_rate = 0.0
    steady_product_price = False
    new_quantity = 0

    # 4.1 Check price change
    new_product_price = (money_circulation * velocity_of_money)/country.quantity

    if new_product_price > current_product_price:
        # inflation = (new_product_price - current_product_price)/current_product_price
        # inflation_rate = (old_inflation - inflation)/old_inflation if old_inflation> 0 else 0
        inflation = calculate_inflation(current_product_price,new_product_price, old_inflation, metrics)

        if inflation > Market.THRESHOLD_INFLATION:
            steady_product_price = True
        else:
            country.product_price = new_product_price
    else:
        inflation = calculate_inflation(current_product_price,new_product_price, old_inflation, metrics)

    # 4.2 Check quantity change : if inflation is more than threshold
    if steady_product_price:
        new_quantity = ceil((money_circulation * velocity_of_money)/current_product_price)

        delta_quantity = new_quantity - current_quantity

        if delta_quantity > 0:
            # 4.3 Check if increase in quantity is more than threshold
            if delta_quantity > Market.THRESHOLD_QUANTITY_INCREASE * current_quantity:
                delta_possible_quantity = ceil(Market.THRESHOLD_QUANTITY_INCREASE * current_quantity)
                money_needed = delta_possible_quantity * current_product_price

                # 4.4 Check if money in bank enough to make more products
                if country.bank.liquid_capital * Market.MIN_BALANCE_INFLATION > money_needed:
                    country.bank.liquid_capital = country.bank.liquid_capital - money_needed
                    new_quantity = delta_possible_quantity + current_quantity
                else:
                    money_available =  country.bank.liquid_capital * Market.BANK_LOAN_INFLATION
                    delta_possible_quantity = ceil(money_available/current_product_price)
                    country.bank.liquid_capital = country.bank.liquid_capital - money_available
                    new_quantity = delta_possible_quantity + current_quantity

                new_product_price = (money_circulation * velocity_of_money)/new_quantity                

                country.product_price = new_product_price
                country.quantity = new_quantity
                inflation = calculate_inflation(current_product_price,new_product_price, old_inflation, metrics)
            # 4.5 quantity is less than threshold
            else:
                new_quantity = delta_quantity + current_quantity
                money_needed = delta_quantity * current_product_price

                # 4.6 Check if bank has enough money to produce more products
                if country.bank.liquid_capital * Market.MIN_BALANCE_INFLATION > money_needed:
                    country.bank.liquid_capital = country.bank.liquid_capital - money_needed
                    new_quantity = delta_quantity + current_quantity
                    country.quantity = new_quantity
                else:
                    money_available =  country.bank.liquid_capital * Market.BANK_LOAN_INFLATION
                    delta_possible_quantity = ceil(money_available/current_product_price)
                    country.bank.liquid_capital = country.bank.liquid_capital - money_available
                    new_quantity = delta_possible_quantity + current_quantity
                    new_product_price = (money_circulation * velocity_of_money)/new_quantity

                    country.product_price = new_product_price
                    country.quantity = new_quantity

                    inflation = calculate_inflation(current_product_price,new_product_price, old_inflation, metrics)

                country.quantity = new_quantity
    
def calculate_inflation(current_product_price, new_product_price, old_inflation, metrics):
    inflation = (new_product_price - current_product_price)/current_product_price
    inflation_rate = (old_inflation - inflation)/old_inflation if old_inflation> 0 else 0
    metrics.inflation = inflation
    metrics.inflation_rate = inflation_rate

    return inflation



def buy_products(fin_workers_list, country, poverty_count, metrics):

    jun_workers = 0
    sen_workers = 0
    exec_workers = 0

    jun_worker_sal = 0
    sen_worker_sal = 0
    exec_worker_sal = 0

    unemployed = 0

    for each_worker in fin_workers_list:
    # if this condition true buy products
        if each_worker.worker_account_balance > country.product_price * 12:
            each_worker.worker_account_balance = each_worker.worker_account_balance - country.product_price * 12
            country.bank.liquid_capital = country.bank.liquid_capital + country.product_price * 12

        else:
            payable_months = floor(each_worker.worker_account_balance/country.product_price)
            each_worker.worker_account_balance = each_worker.worker_account_balance - country.product_price * payable_months
            country.bank.liquid_capital = country.bank.liquid_capital + country.product_price * payable_months
            poverty_count = poverty_count + 1

            salary_metrics(each_worker, jun_workers, sen_workers, exec_workers, jun_worker_sal, sen_worker_sal, exec_worker_sal)

            if not(each_worker.is_employed):
                unemployed = unemployed + 1
        
    # Add mertrics
    metrics.average_jun_sal = jun_worker_sal/jun_workers if jun_workers > 0 else 0
    metrics.average_sen_sal = sen_worker_sal/sen_workers if sen_workers > 0 else 0
    metrics.average_exec_sal = exec_worker_sal/exec_workers if exec_workers > 0 else 0
    metrics.average_sal = (jun_worker_sal + sen_worker_sal + exec_worker_sal)/len(fin_workers_list) if len(fin_workers_list) > 0 else 0
    metrics.unemployment_rate = unemployed/len(fin_workers_list) * 100
    metrics.poverty_rate = poverty_count/len(fin_workers_list) * 100
    metrics.population = len(fin_workers_list)
    metrics.minimum_wage = country.minimum_wage

def salary_metrics(each_worker, jun_workers, sen_workers, exec_workers, jun_worker_sal, sen_worker_sal, exec_worker_sal):

    if each_worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
        jun_workers = jun_workers + 1
        jun_worker_sal = jun_worker_sal + each_worker.salary
    elif each_worker.skill_level <= Worker.SENIOR_SKILL_LEVEL:
        sen_workers = sen_workers + 1
        sen_worker_sal = sen_worker_sal + each_worker.salary
    else:
        exec_workers = exec_workers + 1
        exec_worker_sal = exec_worker_sal + each_worker.salary
        
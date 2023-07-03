# from economic_simulator.models.metrics import Metric
# from ...models.market import Market
# from ...models.worker import Worker
# from functools import reduce
# from math import ceil, floor

# def set_product_price_and_quantity(emp_worker_list, unemp_worker_list, country, metrics):

#     emp_workers_acct = reduce(lambda result, worker: result + worker.worker_account_balance, emp_worker_list, 0 )
#     unemp_workers_acct = reduce(lambda result, worker: result + worker.worker_account_balance, unemp_worker_list, 0 )

#     money_circulation = emp_workers_acct + unemp_workers_acct
#     velocity_of_money = 1
#     current_product_price = country.product_price
#     current_quantity = country.quantity
#     old_inflation = country.inflation
#     inflation = 0.0
#     inflation_rate = 0.0
#     steady_product_price = False
#     new_quantity = 0

#     # 4.1 Check price change
#     new_product_price = (money_circulation * velocity_of_money)/country.quantity

#     if new_product_price > current_product_price:
#         # inflation = (new_product_price - current_product_price)/current_product_price
#         # inflation_rate = (old_inflation - inflation)/old_inflation if old_inflation> 0 else 0
#         inflation = calculate_inflation(current_product_price,new_product_price, old_inflation, metrics)
#         if inflation <= Market.LOW_THRESHOLD_INFLATION:
#             # increase quantity
#             new_quantity = ceil((money_circulation * velocity_of_money)/current_product_price)
#             delta_quantity = new_quantity - current_quantity
#             increase_quantity(money_circulation,velocity_of_money,delta_quantity, new_quantity, current_quantity, country, metrics)

#         elif inflation > Market.HIGH_THRESHOLD_INFLATION:
#             steady_product_price = True
#         else:
#             inflation = calculate_inflation(current_product_price,new_product_price, old_inflation, metrics)
#             country.product_price = new_product_price
            
#     else:
#         country.product_price = new_product_price
#         inflation = calculate_inflation(current_product_price,new_product_price, old_inflation, metrics)

#     # 4.2 Check quantity change : if inflation is more than threshold
#     if steady_product_price:
#         new_quantity = ceil((money_circulation * velocity_of_money)/current_product_price)

#         delta_quantity = new_quantity - current_quantity

#         if delta_quantity > 0:
#             # 4.3 Check if increase in quantity is more than threshold
#             if delta_quantity > Market.THRESHOLD_QUANTITY_INCREASE * current_quantity:
#                 delta_possible_quantity = ceil(Market.POSSIBLE_QUANTITY_INCREASE * current_quantity)
#                 money_needed = delta_possible_quantity * current_product_price

#                 # 4.4 Check if money in bank enough to make more products
#                 if country.bank.liquid_capital * Market.MIN_BALANCE_INFLATION > money_needed:
#                     country.bank.liquid_capital = country.bank.liquid_capital - money_needed
#                     new_quantity = delta_possible_quantity + current_quantity
#                 else:
#                     money_available =  country.bank.liquid_capital * Market.BANK_LOAN_INFLATION
#                     delta_possible_quantity = ceil(money_available/current_product_price)
#                     country.bank.liquid_capital = country.bank.liquid_capital - money_available
#                     new_quantity = delta_possible_quantity + current_quantity

#                 new_product_price = (money_circulation * velocity_of_money)/new_quantity                

#                 country.product_price = new_product_price
#                 country.quantity = new_quantity
#                 inflation = calculate_inflation(current_product_price,new_product_price, old_inflation, metrics)
#             # 4.5 quantity is less than threshold
#             else:
#                 new_quantity = delta_quantity + current_quantity
#                 increase_quantity(money_circulation,velocity_of_money,delta_quantity, new_quantity, current_quantity, country, metrics)

#                 # money_needed = delta_quantity * current_product_price

#                 # # 4.6 Check if bank has enough money to produce more products
#                 # if country.bank.liquid_capital * Market.MIN_BALANCE_INFLATION > money_needed:
#                 #     country.bank.liquid_capital = country.bank.liquid_capital - money_needed
#                 #     new_quantity = delta_quantity + current_quantity
#                 #     country.quantity = new_quantity
#                 # else:
#                 #     money_available =  country.bank.liquid_capital * Market.BANK_LOAN_INFLATION
#                 #     delta_possible_quantity = ceil(money_available/current_product_price)
#                 #     country.bank.liquid_capital = country.bank.liquid_capital - money_available
#                 #     new_quantity = delta_possible_quantity + current_quantity
#                 #     new_product_price = (money_circulation * velocity_of_money)/new_quantity

#                 #     country.product_price = new_product_price
#                 #     country.quantity = new_quantity

#                 #     inflation = calculate_inflation(current_product_price,new_product_price, old_inflation, metrics)

#                 # country.quantity = new_quantity


# def increase_quantity(money_circulation,velocity_of_money,delta_quantity, new_quantity, current_quantity, country, metrics):

#     money_needed = delta_quantity * country.product_price

#     # 4.6 Check if bank has enough money to produce more products
#     if country.bank.liquid_capital * Market.MIN_BALANCE_INFLATION > money_needed:
#         country.bank.liquid_capital = country.bank.liquid_capital - money_needed
#         new_quantity = delta_quantity + current_quantity
#         country.quantity = new_quantity
#         inflation = calculate_inflation(country.product_price,country.product_price, country.inflation, metrics)
#     else:
#         money_available =  country.bank.liquid_capital * Market.BANK_LOAN_INFLATION
#         delta_possible_quantity = ceil(money_available/country.product_price)
#         country.bank.liquid_capital = country.bank.liquid_capital - money_available
#         new_quantity = delta_possible_quantity + current_quantity
#         new_product_price = (money_circulation * velocity_of_money)/new_quantity

#         country.product_price = new_product_price
#         country.quantity = new_quantity

#         inflation = calculate_inflation(country.product_price,new_product_price, country.inflation, metrics)

#     country.quantity = new_quantity


# def calculate_inflation(current_product_price, new_product_price, old_inflation, metrics):
#     inflation = (new_product_price - current_product_price)/current_product_price
#     inflation_rate = (inflation - old_inflation)/old_inflation if old_inflation> 0 else (inflation - old_inflation)
#     metrics.inflation = inflation
#     metrics.inflation_rate = inflation_rate

#     return inflation

# def buy_products(fin_workers_list, country, poverty_count, metrics):

#     employee_details_map = {"jun_workers": 0, "sen_workers": 0, "exec_workers": 0, 
#                             "jun_worker_sal": 0.0, "sen_worker_sal": 0.0, "exec_worker_sal": 0.0}

#     unemployed = 0

#     for each_worker in fin_workers_list:
#     # if this condition true buy products
#         if each_worker.worker_account_balance > country.product_price * 12:
#             each_worker.worker_account_balance = each_worker.worker_account_balance - country.product_price * 12
#             country.bank.liquid_capital = country.bank.liquid_capital + country.product_price * 12
#             salary_metrics(each_worker, employee_details_map)            

#         else:
#             payable_months = floor(each_worker.worker_account_balance/country.product_price)
#             each_worker.worker_account_balance = each_worker.worker_account_balance - country.product_price * payable_months
#             country.bank.liquid_capital = country.bank.liquid_capital + country.product_price * payable_months
#             poverty_count = poverty_count + 1

#             salary_metrics(each_worker, employee_details_map)

#             if not(each_worker.is_employed):
#                 unemployed = unemployed + 1
        
#     # Add mertrics
#     metrics.total_filled_jun_pos = employee_details_map["jun_workers"]
#     metrics.total_filled_sen_pos = employee_details_map["sen_workers"]
#     metrics.total_filled_exec_pos = employee_details_map["exec_workers"]

#     metrics.average_jun_sal = employee_details_map["jun_worker_sal"]/employee_details_map["jun_workers"] if employee_details_map["jun_workers"] > 0 else 0
#     metrics.average_sen_sal = employee_details_map["sen_worker_sal"]/employee_details_map["sen_workers"] if employee_details_map["sen_workers"] > 0 else 0
#     metrics.average_exec_sal = employee_details_map["exec_worker_sal"]/employee_details_map["exec_workers"] if employee_details_map["exec_workers"] > 0 else 0
#     metrics.average_sal = (employee_details_map["jun_worker_sal"] + employee_details_map["sen_worker_sal"] + employee_details_map["exec_worker_sal"])/len(fin_workers_list) if len(fin_workers_list) > 0 else 0
#     metrics.unemployment_rate = unemployed/len(fin_workers_list) * 100
#     metrics.poverty_rate = poverty_count/len(fin_workers_list) * 100
#     metrics.population = len(fin_workers_list)
#     metrics.minimum_wage = country.minimum_wage

# def salary_metrics(each_worker, employee_details_map):

#     if each_worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
#         employee_details_map["jun_workers"] = employee_details_map["jun_workers"] + 1
#         employee_details_map["jun_worker_sal"] = employee_details_map["jun_worker_sal"] + each_worker.salary

#     elif each_worker.skill_level <= Worker.SENIOR_SKILL_LEVEL:
#         employee_details_map["sen_workers"] = employee_details_map["sen_workers"] + 1
#         employee_details_map["sen_worker_sal"] = employee_details_map["sen_worker_sal"] + each_worker.salary
#     else:
#         employee_details_map["exec_workers"] = employee_details_map["exec_workers"] + 1
#         employee_details_map["exec_worker_sal"] = employee_details_map["exec_worker_sal"] + each_worker.salary
        

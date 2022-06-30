# from django.db import models
# import uuid

# from numpy import product, quantile
# from .country import Country

class Metric():
    
    year = 0

    num_small_companies = 0
    num_medium_companies = 0
    num_large_companies = 0

    total_filled_jun_pos = 0
    total_filled_sen_pos = 0
    total_filled_exec_pos = 0

    unemployed_jun_pos = 0
    unemployed_sen_pos = 0
    unemployed_exec_pos = 0
    
    average_jun_sal = 0.0
    average_sen_sal = 0.0
    average_exec_sal = 0.0
    average_sal = 0.0

    unemployment_rate = 0.0
    poverty_rate = 0.0

    population = 0
    minimum_wage = 0.0

    # country_of_residence = None

    inflation = 0
    inflation_rate = 0

    bank_account_balance =  0.0
    product_price =  0.0
    quantity = 0
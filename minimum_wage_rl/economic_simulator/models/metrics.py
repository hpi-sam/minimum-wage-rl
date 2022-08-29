# from django.db import models
# import uuid

# from numpy import product, quantile
# from .country import Country

class Metric():
    def __init__(self) -> None:
        
        self.year = 0

        self.num_small_companies = 0
        self.num_medium_companies = 0
        self.num_large_companies = 0

        self.total_filled_jun_pos = 0
        self.total_filled_sen_pos = 0
        self.total_filled_exec_pos = 0

        self.unemployed_jun_pos = 0
        self.unemployed_sen_pos = 0
        self.unemployed_exec_pos = 0
        
        self.average_jun_sal = 0.0
        self.average_sen_sal = 0.0
        self.average_exec_sal = 0.0
        self.average_sal = 0.0

        self.unemployment_rate = 0.0
        self.poverty_rate = 0.0
        
        # add-to-web
        self.unemployed_junior_rate = 0.0
        self.unemployed_senior_rate = 0.0
        self.unemployed_exec_rate = 0.0

        self.old_poverty_rate = 0.0
        self.old_unemployment_rate = 0.0

        self.population = 0
        self.minimum_wage = 0.0

        # country_of_residence = None

        self.inflation = 0
        self.inflation_rate = 0

        self.bank_account_balance =  0.0
        self.product_price =  0.0
        self.quantity = 0
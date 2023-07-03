from ..models.worker import Worker
from ..models.company import Company
from ..models.metrics import Metric
from django.db import models
from . import definitions

# from functools import reduce
from django.db import transaction

import time
import logging
import os

log_file_name = os.path.join(definitions.get_project_root(), "my_log.log")

#"C:\\Users\\AkshayGudi\\Documents\\2_Model_MinWage\\minimum_wage_rl\\economic_simulator\\my_log.log"
logging.basicConfig(filename=log_file_name, level=logging.INFO)
# logging.basicConfig(filename="C:\\Users\\AkshayGudi\\Documents\\2_Model_MinWage\\minimum_wage_rl\\economic_simulator\\my_log.log", level=logging.INFO)

@transaction.atomic
def save_cached_data(game):
    
    # Save game
    game.country = None
    game.game_ended = True
    game.save()

    metric_list = game.game_metric_list

    Metric.objects.bulk_create(metric_list)
    
    return
    # country = game.country

    # # Save bank
    # country.bank.save()
    
    # # Save market
    # country.market.save()

    # # Save country
    # country.save()

    # Save all companies
    # country_companies_list = country.company_list
    # for each_company in country_companies_list:
    #     each_company.save()

    # Save unemployed workers
    # unemployed_workers_list = country.unemployed_workers
    # for each_unemp_worker in unemployed_workers_list:
    #     each_unemp_worker.save()

    # Save employed workers
    # for each_company in country_companies_list:
    #     worker_list = each_company.employed_workers_list

    #     for each_worker in worker_list:
    #         each_worker.save()



def extract_info(game):

    metric_list = game.game_metric_list

    unemp_list = []
    poverty_list = []
    inflation_list = []
    product_cost_list = []
    min_wage_list = []

    game_stats = dict()

    for each_metric in metric_list:
        unemp_list.append(each_metric.unemployment_rate)
        poverty_list.append(each_metric.poverty_rate)
        inflation_list.append(each_metric.inflation)
        product_cost_list.append(each_metric.product_price)
        min_wage_list.append(each_metric.minimum_wage)

    avg_unemp = round(sum(unemp_list)/len(unemp_list), 2)
    avg_poverty = round(sum(poverty_list)/len(poverty_list), 2)
    avg_inflation = round(sum(inflation_list)/len(inflation_list), 2)
    avg_product_cost = round(sum(product_cost_list)/len(product_cost_list), 2)
    avg_minwage = round(sum(min_wage_list)/len(min_wage_list), 2)

    game_stats["average_poverty"] = avg_poverty
    game_stats["average_unemployment"] = avg_unemp
    game_stats["average_inflation"] = avg_inflation
    game_stats["average_product_price"] = avg_product_cost
    game_stats["average_minimum_wage"] = avg_minwage

    return game_stats


@transaction.atomic
def save_data_to_db(country, metrics, open_companies_list, closed_companies_list, fin_workers_list, retired_workers_list):
    
    start = time.time()
    # Save the bank object
    country.bank.save()
    
    # Save the market object
    country.market.save()

    # Save the country object
    country.save()

    # Save metrics object
    metrics.country_of_residence = country
    metrics.product_price = country.product_price
    metrics.quantity  = country.quantity
    metrics.num_of_open_companies = len(open_companies_list)
    metrics.save()
    
    end = time.time()
    logging.info("9. Save country, market, metric - " + str (end-start))

    start = time.time()
    # save company list
    updated_field_list = ['company_size_type', 'num_junior_openings','num_senior_openings', 'num_executive_openings',
                          'junior_salary_offer', 'senior_salary_offer', 'executive_salary_offer',
                          'company_account_balance', 'company_age',
                          'company_score', 'num_junior_workers', 'num_senior_workers', 'num_executive_workers',
                          'avg_junior_salary', 'avg_senior_salary', 'avg_executive_salary',
                          'open_junior_pos', 'open_senior_pos', 'open_exec_pos',
                          'loan_taken', 'loan_amount', 'closed']

    open_companies_list.extend(closed_companies_list)
    Company.objects.bulk_update(open_companies_list, fields=updated_field_list)

    end = time.time()
    logging.info("10. Bulk Update for companies - " + str (end-start))


    # for each_company in open_companies_list:
    #     each_company.save()
    
    # for each_company in closed_companies_list:
    #     each_company.save()


    # save workers list
    create_emp_list = list()
    update_emp_list = list()

    for each_worker in fin_workers_list:
        if each_worker.worker_id == None:
            create_emp_list.append(each_worker)
        else:
            update_emp_list.append(each_worker)

    for each_worker in retired_workers_list:
        retired_people = retired_people + 1
        if each_worker.worker_id == None:
            create_emp_list.append(each_worker)
        else:
            update_emp_list.append(each_worker)

    start = time.time()    
    # update_emp_fields = ['works_for_company', 'skill_level', 'worker_account_balance', 'salary', 'age',
    #                      'is_employed', 'has_company', 'retired', 'worker_score',
    #                      'create_start_up', 'start_up_score', 'skill_improvement_rate']
    # Worker.objects.bulk_update(update_emp_list, fields=update_emp_fields, batch_size=1500)

    for each_worker in update_emp_list:
        each_worker.save()

    
    # end = time.time()
    # logging.info("11. Bulk update workers - 1500 - " + str(len(update_emp_list)) + " - " + str (end-start))

    # start = time.time()    
    Worker.objects.bulk_create(create_emp_list)
    
    end = time.time()
    logging.info("12. Bulk create workers - " + str(len(create_emp_list)) + " - " + str (end-start))


    # for each_worker in fin_workers_list:
    #     each_worker.save()
    
    # for each_worker in retired_workers_list:
    #     retired_people = retired_people + 1
    #     each_worker.save()

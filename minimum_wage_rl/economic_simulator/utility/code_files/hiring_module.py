from math import floor

# from ...models.company import Company
# from ...models.worker import Worker

# from .code_files import country_module
# from .code_files import company_module
from . import workers_module
# from .code_files import inflation_module
# from .code_files import metrics_module


# companies_list = [Company(200), Company(100), Company(100), Company(20), Company(30)]

# worker_list = []
# for i in range(9):
#     worker = Worker(i)
#     worker_list.append(worker)

# def hire(hiring_workers, each_company, emp_workers_list, jun_salary):
    
#     for each_worker in hiring_workers:
#         each_worker.company = each_company
#         emp_workers_list.append(each_worker)
#         each_worker.salary = jun_salary
#         each_company.total_hired = each_company.total_hired  + 1

def get_open_jobs(level, company):
    if level == "junior":
        return company.open_junior_pos
    
    elif level == "senior":
        return company.open_senior_pos
    
    elif level == "exec":
        return company.open_exec_pos

def change_num_positions(level, company, num_hires):
    if level == "junior":
        company.open_junior_pos = company.open_junior_pos - num_hires
    
    elif level == "senior":
        company.open_senior_pos = company.open_senior_pos - num_hires
    
    elif level == "exec":
        company.open_exec_pos = company.open_exec_pos - num_hires

def set_metrics(level, metrics, num_hires):
    if level == "junior":
        metrics.total_filled_jun_pos = metrics.total_filled_jun_pos + num_hires
    
    elif level == "senior":
        metrics.total_filled_exec_pos = metrics.total_filled_exec_pos + num_hires
    
    elif level == "exec":
        metrics.total_filled_sen_pos = metrics.total_filled_sen_pos + num_hires


def hire_workers(companies_list, worker_list, level, salary, metrics, emp_workers_list) -> list:

    done = True
    company_index = 0
    counter = 0
    extra_open_jobs = 0
    next_round = False

    if len(worker_list) > len(companies_list):
        fixed_hiring = floor(len(worker_list)/len(companies_list))
        rem_hiring = len(worker_list) % len(companies_list)
        total_extra_workers = 0
    else:
        fixed_hiring = 1
        rem_hiring = 0
        total_extra_workers = 0

    while done:
        
        company_index = counter % len(companies_list)
        each_company = companies_list[company_index]
        
        
        if get_open_jobs(level, each_company) > 0:
            
            if rem_hiring > 0:
                rem = 1
                rem_hiring = rem_hiring - 1
            else:
                rem = 0
            
            if get_open_jobs(level, each_company) - (fixed_hiring + rem + total_extra_workers) >= 0:
                if not(next_round):
                    extra_open_jobs = extra_open_jobs + get_open_jobs(level, each_company) - (fixed_hiring + rem + total_extra_workers)
                total_hiring = fixed_hiring + rem + total_extra_workers		
            else:
                current_extra_workers = (fixed_hiring + rem) - get_open_jobs(level, each_company)
                total_hiring = get_open_jobs(level, each_company)
                total_extra_workers = total_extra_workers + current_extra_workers

            if next_round:
                extra_open_jobs = extra_open_jobs - total_hiring
                total_extra_workers = total_extra_workers - total_hiring
                
            if total_hiring>0:
                hiring_workers = worker_list[:total_hiring]
                change_num_positions(level, each_company, total_hiring)
                worker_list = worker_list[total_hiring:]
                # hire(hiring_workers, each_company, emp_workers_list, jun_salary)
                workers_module.get_hired(hiring_workers, salary, each_company, emp_workers_list)
                set_metrics(level, metrics,len(hiring_workers))

        else:
            if rem_hiring > 0:
                rem = 1
                rem_hiring = rem_hiring - 1
            else:
                rem = 0
            current_extra_workers = (fixed_hiring + rem) - get_open_jobs(level, each_company)
            total_extra_workers = total_extra_workers + current_extra_workers        
            
        if counter+1 == len(companies_list):
            fixed_hiring = 0
            next_round = True
            
        if ((fixed_hiring == 0) and (rem_hiring == 0) and (total_extra_workers == 0)) or (next_round and (extra_open_jobs<=0)):
            done = False
        
        counter = counter + 1
    
    return worker_list


    # for each_company in companies_list:
    #     print(each_company.total_hired)
    # print("===================================")
    # print(len(emp_workers_list))
    # print(len(worker_list))


def hire_on_priority():
    pass
import logging
from math import ceil, floor

from .common_module import retire
from ...models.country import Country
from ...models.company import Company
from ...models.worker import Worker
from ...models.market import Market
# logging.basicConfig(filename="C:\\Users\\AkshayGudi\\Documents\\3_MinWage\\minimum_wage_rl\\economic_simulator\\my_log.log", level=logging.INFO)


def pay_loan(company, central_bank):

    if company.loan_taken:
        interest_amount = central_bank.interest_rate * company.loan_amount
        

        if company.loan_amount < 100:
            total_amount = interest_amount + company.loan_amount
            central_bank.deposit_money(total_amount)
            # logging.info("Loan deposited - " + str(total_amount))            
            company.loan_taken = False
            company.loan_amount = 0.0
        
        else:
            installment_amount = Company.INSTALLMENT_PERCENT * company.loan_amount
            total_amount = interest_amount + installment_amount
            central_bank.deposit_money(total_amount)
            company.loan_amount = company.loan_amount - installment_amount
            # logging.info("Loan deposited - " + str(total_amount))


def pay_tax(company, central_bank):
    tax = Country.CORPORATE_TAX * company.company_account_balance
    company.company_account_balance = company.company_account_balance - tax
    central_bank.deposit_money(tax)
    # logging.info("Corporate tax paid - " + str(tax) + " - Account Balance - " + str(company.company_account_balance))
    return tax    

def yearly_financial_transactions(company, country, retired_workers_list, cmp_worker_list):
    
    worker_list = cmp_worker_list

    all_workers_list = []    

    cumulative_junior_salary = 0.0
    cumulative_senior_salary = 0.0
    cumulative_executive_salary = 0.0

    company.junior_workers_list = []
    company.senior_workers_list = []
    company.exec_workers_list = []

    company.num_junior_workers = 0
    company.num_senior_workers = 0
    company.num_executive_workers = 0

    for each_worker in worker_list:
        
        retire_flag = False

        if each_worker.age >= 60:
            # retire(each_worker, country)
            # retire_flag = True
            # retired_workers_list.append(each_worker)
            pass

        if not(retire_flag):
            each_worker.skill_improvement_rate =  company.skill_improvement_rate
            # Adjust salary based on minimum wage and skill_set
            if each_worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
                each_worker.salary = country.minimum_wage
                company.num_junior_workers = company.num_junior_workers + 1
                cumulative_junior_salary = cumulative_junior_salary + each_worker.salary

                company.junior_workers_list.append(each_worker)

            elif each_worker.skill_level <= Worker.SENIOR_SKILL_LEVEL:
                each_worker.salary = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
                company.num_senior_workers = company.num_senior_workers + 1
                cumulative_senior_salary = cumulative_senior_salary + each_worker.salary
                company.senior_workers_list.append(each_worker)

            else:
                each_worker.salary = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE
                company.num_executive_workers = company.num_executive_workers + 1
                cumulative_executive_salary = cumulative_executive_salary + each_worker.salary
                company.exec_workers_list.append(each_worker)

            # Giving value back to company and getting salary and Pay income tax
            # profit_from_each_worker = get_salary_paid(each_worker, company)
            # total_profit = total_profit + profit_from_each_worker
        
            # all_workers_list.append(each_worker)
    all_workers_list.extend(company.exec_workers_list)
    all_workers_list.extend(company.senior_workers_list)
    all_workers_list.extend(company.junior_workers_list)

    for worker_obj in all_workers_list:
        get_salary_paid(worker_obj, company, country)

# ***************************************************************************************
# ****************** CHANGE COMPANY TYPE and IMPROVE WORKER SKILL RATE ******************
# ***************************************************************************************
    # pay corporate tax
    # corporate_tax = total_profit * Country.CORPORATE_TAX
    # company.company_account_balance = company.company_account_balance - corporate_tax
    # country.bank.deposit_money(corporate_tax)

    junior_salary_offer = country.minimum_wage
    senior_salary_offer = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
    executive_salary_offer = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE

    company.avg_junior_salary = cumulative_junior_salary/company.num_junior_workers if company.num_junior_workers > 0 else junior_salary_offer
    company.avg_senior_salary = cumulative_senior_salary/company.num_senior_workers if company.num_senior_workers > 0 else senior_salary_offer
    company.avg_executive_salary = cumulative_executive_salary/company.num_executive_workers if company.num_executive_workers > 0 else executive_salary_offer

    return all_workers_list

# ===================================== HIRING AND FIRING - START ===================================== 

def hiring_and_firing(company, operation_map):

    
    if company.company_account_balance < Market.MINIMUM_COMPANY_BALANCE:
        firing(company, operation_map)
    else:
        hiring(company)
        operation_map["employed_workers"].extend(company.junior_workers_list)
        operation_map["employed_workers"].extend(company.senior_workers_list)
        operation_map["employed_workers"].extend(company.exec_workers_list)

def firing(company, operation_map):
    deficit = Market.MINIMUM_COMPANY_BALANCE - company.company_account_balance

    num_juniors_to_be_fired = ceil(deficit/company.avg_junior_salary)

    num_seniors_to_be_fired = 0
    num_exec_to_be_fired = 0

    # fired_junior_workers = []
    # fired_senior_workers = []
    # fired_executive_workers = []
    # fired_workers

    fired_junior_workers = []
    fired_senior_workers = []
    fired_exec_workers = []
    not_fired_workers = []

    if num_juniors_to_be_fired > 0:

        # 1: Firing juniors
        if num_juniors_to_be_fired > company.num_junior_workers:
            
            # num_seniors_to_be_fired = num_juniors_to_be_fired - company.num_junior_workers

            # Fire all juniors
            fired_junior_workers = fire(company.junior_workers_list)
            operation_map["fired_workers"].extend(fired_junior_workers)
            company.junior_workers_list = list()            
        else:
            fired_junior_workers = fire(company.junior_workers_list[:num_juniors_to_be_fired])

            company.junior_workers_list = company.junior_workers_list[num_juniors_to_be_fired:]

            operation_map["fired_workers"].extend(fired_junior_workers)
        
        company.num_junior_workers = company.num_junior_workers - len(fired_junior_workers)
        deficit = deficit - len(fired_junior_workers) * company.avg_junior_salary
    
    operation_map["employed_workers"].extend(company.junior_workers_list)
        

    # 2: Firing seniors
    num_seniors_to_be_fired = ceil(deficit/company.avg_senior_salary)

    if num_seniors_to_be_fired > 0:
        if num_seniors_to_be_fired > company.num_senior_workers:
            
            # num_exec_to_be_fired = num_seniors_to_be_fired - company.num_senior_workers

            # Fire all juniors
            fired_senior_workers = fire(company.senior_workers_list)
            operation_map["fired_workers"].extend(fired_senior_workers)
            company.senior_workers_list = list()
        else:
            fired_senior_workers = fire(company.senior_workers_list[:num_seniors_to_be_fired])
            operation_map["fired_workers"].extend(fired_senior_workers)

            company.senior_workers_list = company.senior_workers_list[num_seniors_to_be_fired:]            

        company.num_senior_workers = company.num_senior_workers - len(fired_senior_workers)
        deficit = deficit - len(fired_senior_workers) * company.avg_senior_salary
    
    operation_map["employed_workers"].extend(company.senior_workers_list)            

    # 3: Firing executives
    num_exec_to_be_fired = ceil(deficit/company.avg_executive_salary)

    if num_exec_to_be_fired > 0:
        if num_exec_to_be_fired > company.num_executive_workers:
            
            # Fire all executives
            fired_exec_workers = fire(company.exec_workers_list)
            operation_map["fired_workers"].extend(fired_exec_workers)
            company.exec_workers_list = []
        else:
            fired_exec_workers = fire(company.exec_workers_list[:num_exec_to_be_fired])            
            operation_map["fired_workers"].extend(fired_exec_workers)

            company.exec_workers_list = company.exec_workers_list[num_exec_to_be_fired:]

        company.num_executive_workers = company.num_executive_workers - len(fired_exec_workers)
        deficit = deficit - len(fired_exec_workers) * company.avg_executive_salary
    
    operation_map["employed_workers"].extend(company.exec_workers_list)            

    if deficit > 0:
        operation_map["close"] = True


def fire(workers_list):
    
    for each_worker in workers_list:
        each_worker.works_for_company = None
        each_worker.is_employed = False
    
    return workers_list


def hiring(company):

    current_junior_job_percentage = 0.0
    current_senior_job_percentage = 0.0
    current_exec_job_percentage = 0.0

    # Flags to check whether there is a need to hire juniors/seniors/executives respectively
    juniors_needed = 0
    seniors_needed = 0
    exec_needed = 0

    # 1: You can hire if you can pay salary to current employees next year and also pay taxes
    # approx_future_balance = company.company_account_balance - ((company.num_junior_workers * company.avg_junior_salary) + 
    #                                                             (company.num_senior_workers * company.avg_senior_salary) + 
    #                                                             (company.num_executive_workers * company.avg_executive_salary))

    # tax = Country.CORPORATE_TAX * company.company_account_balance
    # approx_future_balance = approx_future_balance - tax

    # if approx_future_balance > Market.MINIMUM_COMPANY_BALANCE:
    if company.company_account_balance > Market.MINIMUM_COMPANY_BALANCE:

        hiring_budget = Market.COMPANY_HIRING_BUDGET_PERCENT * company.company_account_balance

        total_workers = company.num_junior_workers + company.num_senior_workers + company.num_executive_workers

        # 2: If current positions of juniors/seniors/executives is less than required number then go for hiring
        current_junior_job_percentage = float(company.num_junior_workers)/total_workers if total_workers > 0 else 0.0
        current_senior_job_percentage = float(company.num_senior_workers)/total_workers if total_workers > 0 else 0.0
        current_exec_job_percentage = float(company.num_executive_workers)/total_workers if total_workers > 0 else 0.0

        juniors_needed = 1 if current_junior_job_percentage - Market.REQUIRED_JUN_JOB_PERCENT <= 0 else 0
        seniors_needed = 1 if current_senior_job_percentage - Market.REQUIRED_SEN_JOB_PERCENT <= 0 else 0
        exec_needed = 1 if current_exec_job_percentage - Market.REQUIRED_EXEC_JOB_PERCENT <= 0 else 0

        # 3: Common factor to determine how many to hire
        # Formula: 
        # (REQUIRED_JUN_JOB_PERCENT * X) + (REQUIRED_SEN_JOB_PERCENT * X) + 
        # (REQUIRED_EXEC_JOB_PERCENT * X) = (current_junior_percent - REQUIRED_JUN_JOB_PERCENT) + 
        # (current_senior_percent - REQUIRED_SEN_JOB_PERCENT) + (current_exec_percent - REQUIRED_EXEC_JOB_PERCENT)
        # 
        # Find X in above equation to find the number of juniors/seniors/executives to be hired

        common_factor = (abs(current_junior_job_percentage - Market.REQUIRED_JUN_JOB_PERCENT) + 
                        abs(current_senior_job_percentage - Market.REQUIRED_SEN_JOB_PERCENT) +
                        abs(current_exec_job_percentage - Market.REQUIRED_EXEC_JOB_PERCENT))/ ((juniors_needed * Market.REQUIRED_JUN_JOB_PERCENT) + 
                        (seniors_needed * Market.REQUIRED_SEN_JOB_PERCENT) +
                        (exec_needed * Market.REQUIRED_EXEC_JOB_PERCENT))
        
        factor = 10 if total_workers == 0 else total_workers

        junior_pos = round(juniors_needed * Market.REQUIRED_JUN_JOB_PERCENT * common_factor * factor)
        senior_pos = round(seniors_needed * Market.REQUIRED_SEN_JOB_PERCENT * common_factor * factor)
        exec_pos = round(exec_needed * Market.REQUIRED_EXEC_JOB_PERCENT * common_factor * factor)

        budget_empty, hiring_budget = hire_by_ratio(hiring_budget, company, junior_pos, senior_pos, exec_pos)
        
        if not(budget_empty):
            open_new_positions(hiring_budget, company)


def open_new_positions(hiring_budget,company):
    junior_hires = int(Market.REQUIRED_JUN_JOB_PERCENT  * 10)
    senior_hires = int(Market.REQUIRED_SEN_JOB_PERCENT  * 10)
    exec_hires = int(Market.REQUIRED_EXEC_JOB_PERCENT  * 10)

    budget_empty = False

    while hiring_budget>0:

        if junior_hires > 0:
            hiring_budget = hiring_budget - (company.avg_junior_salary * 12)

            if hiring_budget>0:
                company.open_junior_pos = company.open_junior_pos + 1
                junior_hires = junior_hires - 1
            else:
                budget_empty = True
                break

        elif senior_hires > 0:
            hiring_budget = hiring_budget - (company.avg_senior_salary * 12)

            if hiring_budget>0:
                company.open_senior_pos = company.open_senior_pos + 1
                senior_hires = senior_hires - 1
            else:
                budget_empty = True
                break            
                # company.open_senior_pos = open_senior_pos
                # company.open_exec_pos = open_exec_pos
        else:
            hiring_budget = hiring_budget - (company.avg_executive_salary * 12)

            if hiring_budget>0:
                company.open_exec_pos = company.open_exec_pos + 1
                exec_hires = exec_hires - 1
            else:
                budget_empty = True
                break
        # Reset if budget still there to hire
        if hiring_budget>0 and junior_hires == 0 and senior_hires == 0 and exec_hires==0:
            junior_hires = Market.REQUIRED_JUN_JOB_PERCENT  * 10
            senior_hires = Market.REQUIRED_SEN_JOB_PERCENT  * 10
            exec_hires = Market.REQUIRED_EXEC_JOB_PERCENT  * 10


def hire_by_ratio(hiring_budget, company, junior_pos, senior_pos, exec_pos):

    total_pos = junior_pos + senior_pos + exec_pos

    n = max(junior_pos, senior_pos, exec_pos)
    open_junior_pos = 0
    open_senior_pos = 0
    open_exec_pos = 0
    budget_empty = False

    job_position_map = {"junior_pos":junior_pos,"senior_pos":senior_pos,"exec_pos":exec_pos}
    job_position_map = dict(sorted(job_position_map.items(), key=lambda x: x[1], reverse=True))

    for _ in range(n):
        
        for key, value in job_position_map.items():
            if key == "junior_pos" and value > 0:

                hiring_budget = hiring_budget - (company.avg_junior_salary * 12)
                if hiring_budget > 0:
                    open_junior_pos = open_junior_pos + 1
                    job_position_map[key] = value - 1
                else:
                    budget_empty = True
                    break
            
            if key == "senior_pos" and value > 0:

                hiring_budget = hiring_budget - (company.avg_senior_salary * 12)
                if hiring_budget > 0:
                    open_senior_pos = open_senior_pos + 1
                    job_position_map[key] = value - 1
                else:
                    budget_empty = True
                    break
            
            if key == "exec_pos" and value > 0:

                hiring_budget = hiring_budget - (company.avg_executive_salary * 12)
                if hiring_budget > 0:
                    open_exec_pos = open_exec_pos + 1
                    job_position_map[key] = value - 1
                else:
                    budget_empty = True
                    break
        
        if budget_empty:
            break
    
    company.open_junior_pos = open_junior_pos
    company.open_senior_pos = open_senior_pos
    company.open_exec_pos = open_exec_pos
    return (budget_empty, hiring_budget)

# def open_new_positions(hiring_budget, company, junior_pos, senior_pos, exec_pos):
#     total_pos = junior_pos + senior_pos + exec_pos

#     open_junior_pos = 0
#     open_senior_pos = 0
#     open_exec_pos = 0
#     account_empty = False

#     job_position_map = {"junior_pos":junior_pos,"senior_pos":senior_pos,"exec_pos":exec_pos}
#     job_position_map = sorted(job_position_map.items(), key=lambda x: x[1], reverse=True)

#     for each_pos in total_pos:
        
#         for key, value in job_position_map.items():
#             if key == "junior_pos" and value > 0:

#                 # balance = approx_future_balance - company.avg_junior_salary/2
#                 balance = hiring_budget- company.avg_junior_salary
#                 if balance > Market.MINIMUM_COMPANY_BALANCE:
#                     open_junior_pos = open_junior_pos + 1
#                     job_position_map[key] = value - 1
#                 else:
#                     account_empty = True
#                     break
            
#             if key == "senior_pos" and value > 0:

#                 balance = approx_future_balance - company.avg_senior_salary/2
#                 if balance > Market.MINIMUM_COMPANY_BALANCE:
#                     open_senior_pos = open_senior_pos + 1
#                     job_position_map[key] = value - 1
#                 else:
#                     account_empty = True
#                     break
            
#             if key == "exec_pos" and value > 0:

#                 balance = approx_future_balance - company.avg_executive_salary/2
#                 if balance > Market.MINIMUM_COMPANY_BALANCE:
#                     open_exec_pos = open_exec_pos + 1
#                     job_position_map[key] = value - 1
#                 else:
#                     account_empty = True
#                     break
        
#         if account_empty:
#             break
    
#     company.open_junior_pos = open_junior_pos
#     company.open_senior_pos = open_senior_pos
#     company.open_exec_pos = open_exec_pos

# ===================================== HIRING AND FIRING - END ===================================== 



# ========================================= Create Company - START ==========================================
def initialize_company(company, initial_balance, country):

    company.company_account_balance = initial_balance
    company.year_income = company.company_account_balance    
    company.country = country

    # company.hiring_rate = 0.02

    company.num_junior_openings = company.num_senior_openings = company.num_executive_openings = 0
    company.junior_salary_offer = country.minimum_wage
    company.senior_salary_offer = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
    company.executive_salary_offer = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE

    # Small Company
    # initial_balance >= Market.SMALL_CMP_INIT_BALANCE and 
    if initial_balance < Market.MEDIUM_CMP_INIT_BALANCE:
        company.skill_improvement_rate = Company.SML_CMP_SKILL_IMPROVEMENT
        company.company_size_type = Market.SMALL_COMPANY_TYPE    
    
    # Medium Company
    elif initial_balance >= Market.MEDIUM_CMP_INIT_BALANCE and initial_balance < Market.LARGE_CMP_INIT_BALANCE:
        company.skill_improvement_rate = Company.MEDIUM_CMP_SKILL_IMPROVEMENT
        company.company_size_type = Market.MEDIUM_COMPANY_TYPE    
    
    # Large Company
    else:
        company.skill_improvement_rate = Company.LARGE_CMP_SKILL_IMPROVEMENT
        company.company_size_type = Market.LARGE_COMPANY_TYPE

    company.avg_junior_salary = country.minimum_wage
    company.avg_senior_salary = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
    company.avg_executive_salary =  country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE
# ========================================= Create Company - END ==========================================

def set_company_size(company):

    # company.company_account_balance > Market.SMALL_CMP_INIT_BALANCE and 
    if company.company_account_balance < Market.MEDIUM_CMP_INIT_BALANCE:
        company.company_size_type = Market.SMALL_COMPANY_TYPE
        company.skill_improvement_rate = Company.SML_CMP_SKILL_IMPROVEMENT

    elif company.company_account_balance > Market.MEDIUM_CMP_INIT_BALANCE and company.company_account_balance < Market.LARGE_CMP_INIT_BALANCE:
        company.company_size_type = Market.MEDIUM_COMPANY_TYPE
        company.skill_improvement_rate = Company.MEDIUM_CMP_SKILL_IMPROVEMENT
          
    else:
        company.company_size_type = Market.LARGE_COMPANY_TYPE
        company.skill_improvement_rate = Company.LARGE_CMP_SKILL_IMPROVEMENT

def get_salary_paid(worker, company, country):

    if (company.company_account_balance + (worker.skill_level * 12) - (worker.salary * 12)) >= 0:    
        worker.worker_account_balance += worker.salary * 12
        company.company_account_balance -= worker.salary * 12
    
        # Pay income tax
        worker.worker_account_balance = worker.worker_account_balance - worker.salary*12*Country.INCOME_TAX

        company_earnings = worker.skill_level * country.COMPANY_REVENUE_PERCENTAGE * 12
        company.company_account_balance += company_earnings
        company.year_income = company.year_income + company_earnings
        return company_earnings
    else:
        return 0
    
def pay_cost_of_operation(country, company, central_bank):
    cost_of_operation = country.COST_OF_OPERATION * company.company_account_balance
    company.company_account_balance = company.company_account_balance - cost_of_operation

    # Add to standalone
    # central_bank.deposit_money(cost_of_operation)

    # logging.info("Cost of operation - " + str(cost_of_operation) + " - Account Balance - " + str(company.company_account_balance))
    return cost_of_operation
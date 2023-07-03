# from models.country import Country
from ...models.company import Company
from ...models.worker import Worker
from ...models.market import Market
# import .company_module
from .company_module import get_salary_paid, hiring, initialize_company
from .common_module import retire

def evaluate_worker(all_workers_list, startup_workers_list, unemp_jun_worker_list, unemp_sen_worker_list, unemp_exec_worker_list, 
                    emp_worker_list, min_startup_score, max_startup_score, MAX_SKILL_LEVEL):

    for worker in all_workers_list:

        # 3.1 Increase skill set for employed people
        if worker.is_employed:
            if worker.skill_level <= MAX_SKILL_LEVEL:
                worker.skill_level = worker.skill_level  + worker.skill_improvement_rate
        
        # 3.2 Calculate worker score
        # (w1 * skillset) + (w2 * experience) 
        # where experience is given by (age - 18)
        worker.worker_score = (Worker.SKILL_SET_WEIGHTAGE * worker.skill_level) + (Worker.EXPERIENCE_WEIGHTAGE * (worker.age-18))

        # 3.3 Decide whether to create startup
        if worker.worker_account_balance > (Market.SMALL_CMP_INIT_BALANCE * 300):
            worker.start_up_score = (Market.STARTUP_ACCT_WEIGHTAGE * worker.worker_account_balance) + \
                                    (Market.STARTUP_AGE_WEIGHTAGE * (1/worker.age)) + \
                                    (Market.STARTUP_SKILLSET_WEIGHTAGE * worker.skill_level) 

            if min_startup_score > worker.start_up_score:
                min_startup_score = worker.start_up_score
            
            if max_startup_score < worker.start_up_score:
                max_startup_score = worker.start_up_score
            
            if len(startup_workers_list) < 200:
                startup_workers_list.append(worker)
            else:
                add_to_workers_basket(worker, unemp_jun_worker_list, unemp_sen_worker_list,  unemp_exec_worker_list, emp_worker_list)    
        
        else:
            add_to_workers_basket(worker, unemp_jun_worker_list, unemp_sen_worker_list,  unemp_exec_worker_list, emp_worker_list)

# ====================================== EVALUATE FOR EMPLOYED - STANDALONE =========================================
def evaluate_emp_worker(all_companies, emp_worker_list, min_startup_score, max_startup_score, MAX_SKILL_LEVEL):

    number_of_workers = 0

    for each_company in all_companies:
        cmp_employed_list = []

        number_of_workers = number_of_workers + len(each_company.employed_workers_list)

        for worker in each_company.employed_workers_list:

            # 3.1 Increase skill set for employed people
            # if worker.is_employed:
            if worker.skill_level < MAX_SKILL_LEVEL:            
                worker.skill_level = worker.skill_level  + worker.skill_improvement_rate
            
            # 3.2 Calculate worker score
            # (w1 * skillset) + (w2 * experience) 
            # where experience is given by (age - 18)
            worker.worker_score = (Worker.SKILL_SET_WEIGHTAGE * worker.skill_level) + (Worker.EXPERIENCE_WEIGHTAGE * (worker.age-18))

            # 3.3 Decide whether to create startup
            # Market.START_MONEY_THERSHOLD_PERCENT
            if worker.worker_account_balance > (Market.SMALL_CMP_INIT_BALANCE * 300):
                
                worker.start_up_score = (Market.STARTUP_ACCT_WEIGHTAGE * worker.worker_account_balance) + \
                                        (Market.STARTUP_AGE_WEIGHTAGE * (1/worker.age)) + \
                                        (Market.STARTUP_SKILLSET_WEIGHTAGE * worker.skill_level) 

                if min_startup_score > worker.start_up_score:
                    min_startup_score = worker.start_up_score
                
                if max_startup_score < worker.start_up_score:
                    max_startup_score = worker.start_up_score

                if len(each_company.start_up_worker_list)<2000:
                    each_company.start_up_worker_list.append(worker)
                else:
                    cmp_employed_list.append(worker)
                    emp_worker_list.append(worker)
            else:
                cmp_employed_list.append(worker)
                emp_worker_list.append(worker)

        each_company.employed_workers_list = cmp_employed_list

    # print("Company wise numbers - ", number_of_workers)
# ====================================== EVALUATE FOR EMPLOYED - STANDALONE - END =========================================            

# ================================ CREATE START UP ===============================================
def create_start_up(country, new_companies_list, startup_workers_list, unemp_jun_worker_list, 
                                  unemp_sen_worker_list, unemp_exec_worker_list, emp_worker_list, successful_founders_list, open_companies_list):

    startup_workers_list = sorted(startup_workers_list, key=lambda obj: obj.start_up_score, reverse=True)

    bank_startup_budget = country.bank.liquid_capital * Market.STARTUP_LOAN_PERCENT

    
    successful_founders_list = []
    # successful_startup_index = []
    

    index = 0

    if len(open_companies_list) < 50000:
        for each_startup_founder in startup_workers_list:

            amount_needed = 3 * Market.SMALL_CMP_INIT_BALANCE - each_startup_founder.worker_account_balance

            if bank_startup_budget > amount_needed:
                
                # successful_startup_index.append(index)                     

                # Loan needed
                if amount_needed > 0:
                    company, amount_needed = start_company(amount_needed, each_startup_founder, country, loan_taken=True)
                    bank_startup_budget = bank_startup_budget - amount_needed
                    new_companies_list.append(company)                

                # Loan not needed -  Can open company without loan
                else:
                    company, amount_needed = start_company(0, each_startup_founder, country, loan_taken=False)
                    bank_startup_budget = bank_startup_budget - amount_needed
                    new_companies_list.append(company)
                
                retire(each_startup_founder, country)
                successful_founders_list.append(each_startup_founder)
            
            # Company could not be created
            else:
                # if each_startup_founder.skill_level <= MAX_SKILL_LEVEL
                each_startup_founder.skill_level = each_startup_founder.skill_level + \
                                                each_startup_founder.skill_level * Market.STARTUP_SKILL_IMPROVEMENT

                each_startup_founder.worker_score = (Worker.SKILL_SET_WEIGHTAGE * each_startup_founder.skill_level) + \
                                                    (Worker.EXPERIENCE_WEIGHTAGE * (each_startup_founder.age-18))

                add_to_workers_basket(each_startup_founder, unemp_jun_worker_list,unemp_sen_worker_list,
                            unemp_exec_worker_list, emp_worker_list)

            index = index + 1
    else:
        for each_startup_founder in startup_workers_list:
            add_to_workers_basket(each_startup_founder, unemp_jun_worker_list,unemp_sen_worker_list,unemp_exec_worker_list, emp_worker_list)
        

# ====================================== CREATE START UP FOR EMPLOYED - STANDALONE ======================================
def create_start_up_for_employed(country, new_companies_list, startup_workers_list, open_companies_list, emp_worker_list, successful_founders_list):

    # 
    for each_company in open_companies_list:

        startup_workers_list = each_company.start_up_worker_list
        startup_workers_list = sorted(startup_workers_list, key=lambda obj: obj.start_up_score, reverse=True)

        bank_startup_budget = country.bank.liquid_capital * Market.STARTUP_LOAN_PERCENT

        successful_founders_list = []
        # successful_startup_index = []
        # index = 0
        cmp_emp_list = []
        if len(open_companies_list) < 200:
            for each_startup_founder in startup_workers_list:
                
                
                amount_needed = (3 * Market.SMALL_CMP_INIT_BALANCE) - each_startup_founder.worker_account_balance

                if bank_startup_budget > amount_needed:
                    
                    # successful_startup_index.append(index)                     

                    # Loan needed
                    if amount_needed > 0:
                        company, amount_needed = start_company(amount_needed, each_startup_founder, country, loan_taken=True)
                        bank_startup_budget = bank_startup_budget - amount_needed
                        new_companies_list.append(company)                

                    # Loan not needed -  Can open company without loan
                    else:
                        company, amount_needed = start_company(0, each_startup_founder, country, loan_taken=False)
                        bank_startup_budget = bank_startup_budget - amount_needed
                        new_companies_list.append(company)
                    
                    retire(each_startup_founder, country)
                    successful_founders_list.append(each_startup_founder)
                
                # Company could not be created
                else:
                    each_startup_founder.skill_level = each_startup_founder.skill_level + \
                                                        each_startup_founder.skill_level * Market.STARTUP_SKILL_IMPROVEMENT

                    each_startup_founder.worker_score = (Worker.SKILL_SET_WEIGHTAGE * each_startup_founder.skill_level) + \
                                                        (Worker.EXPERIENCE_WEIGHTAGE * (each_startup_founder.age-18))

                    cmp_emp_list.append(each_startup_founder)
                    emp_worker_list.append(each_startup_founder)
        else:
            for each_startup_founder in startup_workers_list:
                cmp_emp_list.append(each_startup_founder)
                emp_worker_list.append(each_startup_founder)
            
        
            # index = index + 1
        each_company.employed_workers_list.extend(cmp_emp_list)
        each_company.start_up_worker_list = list()
# ====================================== CREATE START UP FOR EMPLOYED - STANDALONE END ======================================

def add_to_workers_basket(worker, unemp_jun_worker_list,unemp_sen_worker_list,
                         unemp_exec_worker_list, emp_worker_list):

    if not(worker.is_employed):
        if worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
            unemp_jun_worker_list.append(worker)

        elif worker.skill_level <= Worker.SENIOR_SKILL_LEVEL:
            unemp_sen_worker_list.append(worker)
        
        else:
            unemp_exec_worker_list.append(worker)
    else:
        emp_worker_list.append(worker)
                    

def start_company(amount_needed, worker, country, loan_taken):
    company = Company()
    initialize_company(company, amount_needed+worker.worker_account_balance, country)
    company.loan_taken = loan_taken
    company.loan_amount = amount_needed
    company.company_score = Market.COMPANY_AGE_WEIGHTAGE * company.company_age + \
                            Market.COMPANY_ACCT_BALANCE_WEIGHTAGE * company.company_account_balance
                                                        
    # bank_startup_budget = bank_startup_budget - amount_needed
    country.bank.liquid_capital = country.bank.liquid_capital - amount_needed
    
    # Create positions
    hiring(9999, company)
    return company, amount_needed

def get_hired(country, worker_list, salary, company, emp_worker_list):
    for worker in worker_list:
        worker.is_employed=True
        worker.salary=salary
        
        get_salary_paid(worker, company, country)
        worker.skill_improvement_rate = company.skill_improvement_rate

        # worker.works_for_company = company
        company.employed_workers_list.append(worker)
        emp_worker_list.append(worker)

# def get_skill_level(worker):

#     if worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
#        return Worker.JUNIOR_SKILL_LEVEL
#     elif (worker.skill_level > Worker.JUNIOR_SKILL_LEVEL) and (worker.skill_level <= Worker.SENIOR_SKILL_LEVEL):
#        return Worker.SENIOR_SKILL_LEVEL
        
#     else:
#         return Worker.EXEC_SKILL_LEVEL
# ==================================== old code ========================================
# def get_hired(needed_positions, unemployed_worker_list,salary, company,emp_worker_list):
     
#     available_positions = 0
#     if needed_positions > len(unemployed_worker_list):
#         available_positions = len(unemployed_worker_list)
#     else:
#         available_positions = needed_positions

#     workers = unemployed_worker_list[:available_positions]

#     for each_worker in workers:
#         each_worker.is_employed=True
#         each_worker.salary=salary
        
#         get_salary_paid(each_worker, company)
#         each_worker.skill_improvement_rate = company.skill_improvement_rate

#         each_worker.works_for_company = company
#         emp_worker_list.append(each_worker)
    
#     # unemp_jun_worker_list = unemp_jun_worker_list[available_positions:]
#     # company_item.open_junior_pos = company_item.open_junior_pos - available_positions  

#     return available_positions


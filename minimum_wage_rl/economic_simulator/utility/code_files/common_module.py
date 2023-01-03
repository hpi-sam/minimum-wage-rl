from ...models.worker import Worker

def retire(worker, country):
    worker.is_employed = False
    worker.retired = True
    country.population = country.population - 1
    worker.works_for_company = None

def get_avg_acct_balance(emp_worker_list, unemp_worker_list):
    
    all_sen_acct_balance = 0
    all_jun_acct_balance = 0
    all_exec_acct_balance = 0
    all_num_jun = 0
    all_num_sen = 0
    all_num_exec = 0



    for each_worker in emp_worker_list:
        if each_worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
            all_jun_acct_balance = all_jun_acct_balance + each_worker.worker_account_balance
            all_num_jun = all_num_jun + 1
        elif each_worker.skill_level <= Worker.SENIOR_SKILL_LEVEL:
            all_sen_acct_balance = all_sen_acct_balance + each_worker.worker_account_balance
            all_num_sen = all_num_sen + 1
        else:
            all_exec_acct_balance = all_exec_acct_balance + each_worker.worker_account_balance
            all_num_exec = all_num_exec + 1

    for each_worker in unemp_worker_list:
        if each_worker.skill_level <= Worker.JUNIOR_SKILL_LEVEL:
            all_jun_acct_balance = all_jun_acct_balance + each_worker.worker_account_balance
            all_num_jun = all_num_jun + 1
        elif each_worker.skill_level <= Worker.SENIOR_SKILL_LEVEL:
            all_sen_acct_balance = all_sen_acct_balance + each_worker.worker_account_balance
            all_num_sen = all_num_sen + 1
        else:
            all_exec_acct_balance = all_exec_acct_balance + each_worker.worker_account_balance
            all_num_exec = all_num_exec + 1


    avg_jun_acct_balance = all_jun_acct_balance/all_num_jun
    avg_sen_acct_balance = all_sen_acct_balance/all_num_sen
    avg_exec_acct_balance = all_exec_acct_balance/all_num_exec

    return avg_jun_acct_balance, avg_sen_acct_balance, avg_exec_acct_balance
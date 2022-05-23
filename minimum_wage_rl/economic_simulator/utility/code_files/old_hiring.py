
    # while counter < hire_loop_counter:

    #     company_index = company_counter % num_of_companies
    #     current_company = open_companies_list[company_index]

    #     # if second round - check if 
    #         #  companies have junior openings and is junior worker list non empty
    #         #  companies have senior openings and is senior worker list non empty
    #         #  companies have exec openings and is exec worker list non empty

    #     print("Positions - ", current_company.open_junior_pos, " , ", current_company.open_senior_pos, " , " , current_company.open_exec_pos)
    #     print("Account balance - ", current_company.company_account_balance)
    #     if current_company.open_junior_pos > 0:
    #         jun_salary = country.minimum_wage

    #         if len(unemp_jun_worker_list)>0:
    #             current_worker = unemp_jun_worker_list[0]
    #             workers_module.get_hired(current_worker, jun_salary, current_company, emp_worker_list)
    #             unemp_jun_worker_list = unemp_jun_worker_list[1:]
    #             current_company.open_junior_pos = current_company.open_junior_pos - 1
    #             metrics.total_filled_jun_pos = metrics.total_filled_jun_pos + 1
    #             counter = counter + 1
        
    #     if current_company.open_senior_pos > 0:
    #         senior_salary = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE

    #         if len(unemp_sen_worker_list)>0:
    #             current_worker = unemp_sen_worker_list[0]
    #             workers_module.get_hired(current_worker, senior_salary, current_company, emp_worker_list)
    #             unemp_sen_worker_list = unemp_sen_worker_list[1:]
    #             current_company.open_senior_pos = current_company.open_senior_pos - 1
    #             metrics.total_filled_sen_pos = metrics.total_filled_sen_pos + 1
    #             counter = counter + 1

    #     if current_company.open_exec_pos > 0:
    #         exec_salary = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE

    #         if len(unemp_exec_worker_list)>0:
    #             current_worker = unemp_exec_worker_list[0]
    #             workers_module.get_hired(current_worker, exec_salary, current_company, emp_worker_list)
    #             unemp_exec_worker_list = unemp_exec_worker_list[1:]
    #             current_company.open_exec_pos = current_company.open_exec_pos - 1
    #             metrics.total_filled_exec_pos = metrics.total_filled_exec_pos + 1
    #             counter = counter + 1
        
    #     company_counter = company_counter + 1
        # company_module.set_company_size(current_company)
        # metrics_module.set_company_size_metrics(current_company, metrics)



# =======================================================================================================================
 # for company_item in open_companies_list:
    #     if company_item.open_junior_pos > 0:
    #         needed_positions = company_item.open_junior_pos
    #         jun_salary = country.minimum_wage
    #         available_positions  = workers_module.get_hired(needed_positions,unemp_jun_worker_list,jun_salary,
    #                                                         company_item,emp_worker_list)
    #         unemp_jun_worker_list = unemp_jun_worker_list[available_positions:]
    #         company_item.open_junior_pos = company_item.open_junior_pos - available_positions
    #         metrics.total_filled_jun_pos = metrics.total_filled_jun_pos + available_positions            
        
    #     if company_item.open_senior_pos > 0:
    #         needed_positions = company_item.open_senior_pos
    #         senior_salary = country.minimum_wage + country.minimum_wage * Market.SENIOR_SALARY_PERCENTAGE
    #         available_positions  = workers_module.get_hired(needed_positions,unemp_sen_worker_list,senior_salary,
    #                                                         company_item,emp_worker_list)
    #         unemp_sen_worker_list = unemp_sen_worker_list[available_positions:]
    #         company_item.open_senior_pos = company_item.open_senior_pos - available_positions
    #         metrics.total_filled_sen_pos = metrics.total_filled_sen_pos + available_positions
        
    #     if company_item.open_exec_pos > 0:
    #         needed_positions = company_item.open_exec_pos
    #         exec_salary = country.minimum_wage + country.minimum_wage * Market.EXEC_SALARY_PERCENTAGE
    #         available_positions  = workers_module.get_hired(needed_positions,unemp_exec_worker_list,exec_salary,
    #                                                         company_item,emp_worker_list)
    #         unemp_exec_worker_list = unemp_exec_worker_list[available_positions:]
    #         company_item.open_exec_pos = company_item.open_exec_pos - available_positions
    #         metrics.total_filled_exec_pos = metrics.total_filled_exec_pos + available_positions

        # company_module.set_company_size(company_item)
        # metrics_module.set_company_size_metrics(company_item, metrics)
        # metrics_module.set_job_pos_metrics(company_item, metrics)

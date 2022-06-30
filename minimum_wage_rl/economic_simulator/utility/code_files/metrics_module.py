from models.market import Market

def set_company_size_metrics(company, metrics_obj):

    if company.company_size_type == Market.SMALL_COMPANY_TYPE:
        metrics_obj.num_small_companies = metrics_obj.num_small_companies + 1

    elif company.company_size_type == Market.MEDIUM_COMPANY_TYPE:
        metrics_obj.num_medium_companies = metrics_obj.num_medium_companies + 1
          
    else:
        metrics_obj.num_large_companies = metrics_obj.num_large_companies + 1

# def set_job_pos_metrics(company, metrics_obj):
#     metrics_obj.total_jun_pos = metrics_obj.total_jun_pos + company.open_junior_pos
#     metrics_obj.total_sen_pos = metrics_obj.total_sen_pos + company.open_senior_pos
#     metrics_obj.total_exec_pos = metrics_obj.total_exec_pos + company.open_exec_pos
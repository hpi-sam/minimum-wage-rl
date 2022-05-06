
def retire(worker, country):
    worker.is_employed = False
    worker.retired = True
    country.population = country.population - 1
    worker.works_for_company = None
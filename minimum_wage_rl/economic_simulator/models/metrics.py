from django.db import models
import uuid

from .country import Country


class Metric(models.Model):

    class Meta:
        db_table = "metric"
    
    year = models.IntegerField()

    metric_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)    

    num_small_companies = models.IntegerField(default=0)
    num_medium_companies = models.IntegerField(default=0)
    num_large_companies = models.IntegerField(default=0)

    total_filled_jun_pos = models.IntegerField(default=0)
    total_filled_sen_pos = models.IntegerField(default=0)
    total_filled_exec_pos = models.IntegerField(default=0)

    unemployed_jun_pos = models.IntegerField(default=0)
    unemployed_sen_pos = models.IntegerField(default=0)
    unemployed_exec_pos = models.IntegerField(default=0)
    
    average_jun_sal = models.FloatField(default=0.0)
    average_sen_sal = models.FloatField(default=0.0)
    average_exec_sal = models.FloatField(default=0.0)
    average_sal = models.FloatField(default=0.0)

    unemployment_rate = models.FloatField(default=0.0)
    poverty_rate = models.FloatField(default=0.0)
    
    # add-to-web
    unemployed_junior_rate = 0.0
    unemployed_senior_rate = 0.0
    unemployed_exec_rate = 0.0

    old_poverty_rate = 0.0
    old_unemployment_rate = 0.0

    population = models.IntegerField(default=0)
    minimum_wage = models.FloatField(default=0.0)

    country_of_residence = models.ForeignKey(to=Country, null=True, blank=True, on_delete=models.CASCADE)

    inflation = models.FloatField()
    inflation_rate = models.FloatField()

    bank_account_balance =  models.FloatField(default=0.0)
    product_price =  models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)

    money_circulation = models.FloatField(default=0.0)

    avg_jun_skill_level = models.FloatField(default=0.0)
    avg_sen_skill_level = models.FloatField(default=0.0)
    avg_exec_skill_level = models.FloatField(default=0.0)

    num_retired = models.IntegerField(default=0)
    startup_founders = models.IntegerField(default=0)

    small_comp_acct_balance = models.FloatField(default=0.0)
    medium_comp_acct_balance = models.FloatField(default=0.0)
    large_comp_acct_balance = models.FloatField(default=0.0)

    jun_worker_avg_balance = models.FloatField(default=0.0)
    sen_worker_avg_balance = models.FloatField(default=0.0)
    exec_worker_avg_balance = models.FloatField(default=0.0)

    current_year_filled_jun_pos = models.IntegerField(default=0)
    current_year_filled_sen_pos = models.IntegerField(default=0)
    current_year_filled_exec_pos = models.IntegerField(default=0)

    avg_juniors_small_cmp = models.IntegerField(default=0)
    avg_seniors_small_cmp = models.IntegerField(default=0)
    avg_execs_small_cmp = models.IntegerField(default=0)
    avg_juniors_medium_cmp = models.IntegerField(default=0)
    avg_seniors_medium_cmp = models.IntegerField(default=0)
    avg_execs_medium_cmp = models.IntegerField(default=0)
    avg_juniors_large_cmp = models.IntegerField(default=0)
    avg_seniors_large_cmp = models.IntegerField(default=0)
    avg_execs_large_cmp = models.IntegerField(default=0)

    uemp_jun_acct_balance = models.FloatField(default=0.0)
    uemp_sen_acct_balance = models.FloatField(default=0.0)
    uemp_exec_acct_balance = models.FloatField(default=0.0)
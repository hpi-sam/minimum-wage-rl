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

    total_jun_pos = models.IntegerField(default=0)
    total_sen_pos = models.IntegerField(default=0)
    total_exec_pos = models.IntegerField(default=0)

    average_jun_sal = models.FloatField(default=0.0)
    average_sen_sal = models.FloatField(default=0.0)
    average_exec_sal = models.FloatField(default=0.0)
    average_sal = models.FloatField(default=0.0)

    unemployment_rate = models.FloatField(default=0.0)
    poverty_rate = models.FloatField(default=0.0)

    population = models.IntegerField(default=0)
    minimum_wage = models.FloatField(default=0.0)

    country_of_residence = models.ForeignKey(to=Country, null=True, blank=True, on_delete=models.CASCADE)

    inflation = models.FloatField()
    inflation_rate = models.FloatField()
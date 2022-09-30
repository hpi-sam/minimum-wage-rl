from django.db import models

from .bank import Bank
from .country import Country
from .company import Company
import uuid

from ..utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser


class Worker(models.Model):

    class Meta:
        db_table = "worker"    

    BUY_EXTRA_ACCT_BALANCE = 5
    BUY_LUXURY_ACCT_BALANCE = 10
    JUNIOR_SKILL_LEVEL = int(config_parser.get("worker","junior_skill_level"))
    SENIOR_SKILL_LEVEL = int(config_parser.get("worker","senior_skill_level"))
    EXEC_SKILL_LEVEL = int(config_parser.get("worker","exec_skill_level"))

    INITIAL_WORKER_BANK_BALANCE = float(config_parser.get("worker","initial_acct_balance")) 

    SKILL_SET_WEIGHTAGE = float(config_parser.get("worker","skill_set_weightage"))
    EXPERIENCE_WEIGHTAGE = float(config_parser.get("worker","experience_weightage"))
    SAVINGS_PERCENT = float(config_parser.get("worker","savings_percent"))

    worker_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country_of_residence = models.ForeignKey(to=Country, null=True, blank=True, on_delete=models.CASCADE)
    works_for_company = models.ForeignKey(to=Company, null=True, blank=True, on_delete=models.CASCADE)

     # Current skill level of the employee. Junior: (1-25) Senior: (25.1 - 70) Executive (70.1 - 100)
    skill_level = models.FloatField(default=float(config_parser.get("market","initial_skill_level")))
    worker_account_balance = models.FloatField(default=0)
    salary = models.FloatField(default=0)
    age = models.IntegerField()

    is_employed = models.BooleanField(default=False)
    has_company = models.BooleanField(default=False)
    retired = models.BooleanField(default=False)

    worker_score = models.FloatField(default=0.0)

    create_start_up = models.BooleanField(default=False)
    start_up_score = models.FloatField(default=0.0)
    skill_improvement_rate = models.FloatField(default=0.0)
# from django.db import models
# import uuid

from utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser

class Bank():

    liquid_capital = 0.0
    interest_rate = config_parser.get("bank","initial_interest_rates")
    # bank_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        
    def initialize_bank(self, cash):
        self.liquid_capital = cash

    def deposit_money(self, cash):
        self.liquid_capital += cash

    def lend_loan(self, amount):
        # Risk assesment
        self.liquid_capital = self.liquid_capital - amount
        return amount
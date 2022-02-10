from django.db import models
import uuid

class Bank(models.Model):

    def __init__(self):
        self.liquid_capital = models.FloatField(default=0.0)
        self.interest_rates = models.FloatField()
        self.bank_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        
    # def initialize_bank(self, cash):
    #     self.liquid_capital = cash

    def deposit_money(self, cash):
        self.liquid_capital += cash

    def lend_loan(self, amount):
        # Risk assesment
        self.liquid_capital = self.liquid_capital - amount
        return amount
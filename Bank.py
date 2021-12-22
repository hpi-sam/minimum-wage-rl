class Bank:

    def __init__(self, id):
        self.liquid_capital = 0
        self.interest_rates = None
        self.bank_id = id
        
    def initialize_bank(self, cash):
        self.liquid_capital = cash

    def receive_money(self, cash):
        self.liquid_capital += cash

    def lend_loan(self, amount):
        # Risk assesment
        self.liquid_capital = self.liquid_capital - amount
        return amount
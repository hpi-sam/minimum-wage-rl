import configparser

from numpy import choose
# from minimum_wage_rl.economic_simulator.models.country import Country
from minimum_wage_rl.economic_simulator.models.market import Market

from ..utility import simulate

class Government:

    def __init__(self) -> None:

        # self.country = Country()
        self.market = Market.get_instance()
        
        self.parser = configparser.ConfigParser()
        self.parser.read("config_file.txt")

        self.inflation = float(self.parser.get("market","inflation"))
        # self.action_list = [self.__no_change, self.__inflation_based, self.__random_five_percent]
        self.action_number = 0

        self.num_of_steps = 10 # Configure this

    def choose_action(self, state):
        state_reward = self.get_state()

        min_wage = state_reward["reward"]
        
        self.action_number = (self.action_number + 1) % len(self.action_list)

        # action_function = self.action_list[self.action_number]
        
        # new_min_wage = action_function(min_wage)

        state_reward = simulate(self.action_number) 
        # -> unemploymentRate, povertyRate, minimumWage, averageSalary-productPrice
        return state_reward

    def execute_action(self):
        state_reward = self.get_state()

        for _ in range(self.num_of_steps):
            state_reward = self.choose_action(state_reward)

            print(state_reward["state"]) 
            print(state_reward["reward"])

    def get_state(self):
        return self.market.get_state()

    # def __no_change(self, min_wage):
    #     return min_wage
    
    # def __inflation_based(self, min_wage):
    #     min_wage =  min_wage + (self.inflation * min_wage)
    #     return min_wage
    
    # def __random_five_percent(self, min_wage):
    #     min_wage =  min_wage + (0.05 * min_wage)
    #     return min_wage
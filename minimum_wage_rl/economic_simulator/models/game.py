# from ..utility.config import ConfigurationParser
# config_parser = ConfigurationParser.get_instance().parser

# For Pycharm
# from economic_simulator.utility.start_up_2 import start
# from economic_simulator.utility.simulate_2 import step
# from economic_simulator.utility.simulate_2 import get_state

# For VS Code
from utility.start_up_2 import start
from utility.simulate_2 import step
from utility.simulate_2 import get_state


import torch

class Game():

    def __init__(self, game_number, level) -> None:        
        self.game_number = game_number
        self.game_ended = False
        self.country = None
        self.game_metric_list = list()
        self.episode_number=0
        self.level = level
    
    def test(self):
        # print("------------> " , self.game_number)
        pass

    def reset(self, episode_number):
        return start(self, episode_number)

    def step(self,action):
        return step(self,action)
    
    def get_state(self):
        # _, state_values, _, _, _ = get_state(self)
        state_values, _, _, _ = get_state(self)
        return state_values
    
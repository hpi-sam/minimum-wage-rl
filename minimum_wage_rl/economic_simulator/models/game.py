# from ..utility.config import ConfigurationParser
# config_parser = ConfigurationParser.get_instance().parser
from utility.start_up_2 import start
from utility.simulate_2 import step
from utility.simulate_2 import get_state
import torch

class Game():

    def __init__(self, game_number) -> None:        
        self.game_number = game_number
        self.game_ended = False
        self.country = None
        self.game_metric_list = list()
    
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
    
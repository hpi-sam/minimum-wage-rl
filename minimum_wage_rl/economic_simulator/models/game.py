# from ..utility.config import ConfigurationParser
# config_parser = ConfigurationParser.get_instance().parser
from utility.start_up_2 import start
from utility.simulate_2 import step

class Game():

    def __init__(self, game_number) -> None:        
        self.game_number = game_number
        self.game_ended = False
        self.country = None
        
    def reset(self):
        return start(self)

    def step(self,action):
        return step(self,action)
    
from math import inf
import gym
from gym import spaces
import numpy as np
from models.game import Game
from utility.config import ConfigurationParser


config_parser = ConfigurationParser.get_instance().parser

min_wage_lower_limit = config_parser.get("minwage","initial_minimum_wage")
product_price_lower_limit = config_parser.get("market","initial_product_price")

class EconomyEnv(gym.Env):

    def __init__(self) -> None:
        super(EconomyEnv, self).__init__()
        self.action_space = spaces.Box(low=7.0, high=15.0, shape=(1,))
        
        # Observation Space
        # 1.minimum_wage  2.product_price   3.quantity
        # 4.unemployment_rate  5.inflation  6.bank_account_balance
        # 7.population
        
        self.observation_space = spaces.Box(np.array([min_wage_lower_limit,0,0,0,-1,0,0]), 
        np.array([inf,inf,inf,100,1,inf,1500]), shape=(7,), dtype=np.float64)

        # self.observation_space = spaces.Box(low=0.1, high=10.5, shape=(1,))

        self.env = Game(1)
        self.game_episode_num = 0
        self.game_step = 0
    
    def step(self, action):
        self.game_step = self.game_step + 1
        print(self.game_step)

        action_map = {"minimum_wage":action[0]}
        obs, rew, done, info = self.env.step(action_map)

        temp = np.array(obs)
        if temp.shape[0] < 7:
            print("here")

        return np.array(obs), rew, done, info
    
    def reset(self):
        self.game_episode_num = self.game_episode_num  + 1 
        self.game_step = 0
        val_dict =  self.env.reset(self.game_episode_num)
        l1 = list()
        for k,v in val_dict.items():
            l1.append(v)

        return np.array(l1)

    def close(self) -> None:
        pass
    
    def render(self, mode="human"):
        pass
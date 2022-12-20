from math import inf
import gym
from gym import spaces
import numpy as np
from models.game import Game
from utility.config import ConfigurationParser

file_name = "config_file.txt"
config_parser = ConfigurationParser.get_instance(file_name).parser


min_wage_lower_limit = config_parser.get("minwage","initial_minimum_wage")
product_price_lower_limit = config_parser.get("market","initial_product_price")

class EconomyEnv(gym.Env):

    def __init__(self) -> None:
        super(EconomyEnv, self).__init__()
        self.action_space = spaces.Box(low=7.0, high=15.0, shape=(1,))

        # -2, -1, -0.5, 0.5, 1.0, 2.0, 5.0
        # self.action_space = spaces.Discrete(10)
        
        # Observation Space
        # 1.minimum_wage  
        # 2.product_price   
        # 3.quantity
        # 4.unemployment_rate  
        # 5.inflation
        # 6. new bank_account_balance - old bank_account_balance
        # 7. Population
        # 8.Poverty rate
        # 9. New Money Circulation  - old Money Circulation
        
        self.observation_space = spaces.Box(
            np.array([min_wage_lower_limit,0,0,0,-10,0,0,0,0]), 
            np.array([15,inf,inf,100,10,inf,100,inf,inf]), shape=(9,), dtype=np.float64)

        # self.observation_space = spaces.Box(low=0.1, high=10.5, shape=(1,))
        level = 1
        self.env = Game(1, level)
        self.game_episode_num = 0
        self.game_step = 0
        self.full_training_step = 0
    
    def step(self, action):
        self.game_step = self.game_step + 1
        self.full_training_step = self.full_training_step + 1
        print("Full Game Step - ", self.full_training_step)
        print("Episode Step - ", self.game_step)

        # action_map = {"minimum_wage":action[0]}
        action_map = {"minimum_wage":action}
        obs, rew, done, info = self.env.step(action_map)

        # print("Observations - ")
        # print(obs)
        print("rewards - " )
        print(rew)

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
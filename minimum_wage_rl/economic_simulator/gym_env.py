from math import inf
import gym
from gym import spaces
import numpy as np
from models.game import Game
from utility.config import ConfigurationParser

root_folder = "C:\\Users\\AkshayGudi\\Documents\\3_MinWage\\minimum_wage_rl\\"
file_name = root_folder + "config_file.txt"
config_parser = ConfigurationParser.get_instance(file_name).parser


min_wage_lower_limit = config_parser.get("minwage", "initial_minimum_wage")
min_wage_upper_limit = config_parser.get("minwage", "final_minimum_wage")
# config_parser.get("minwage","initial_minimum_wage")

low_min_wage_action = config_parser.get("minwage", "delta_minwage_start")
high_min_wage_action = config_parser.get("minwage", "delta_minwage_end")


product_price_lower_limit = config_parser.get("market", "initial_product_price")

class EconomyEnv(gym.Env):

    def __init__(self) -> None:
        super(EconomyEnv, self).__init__()

        
        self.action_space = spaces.Box(low=low_min_wage_action, high=high_min_wage_action, shape=(1,))

        # -2, -1, -0.5, 0.5, 1.0, 2.0, 5.0
        # self.action_space = spaces.Discrete(10)
        
        # Observation Space
        # 1.minimum_wage
        minimum_wage_low = min_wage_lower_limit
        minimum_wage_high = min_wage_upper_limit

        # 2.product_price
        product_price_low = 0
        product_price_high = inf

        # 3.quantity
        quantity_low = 0
        quantity_high = inf

        # 4.unemployment_rate
        unemployment_rate_low = 0
        unemployment_rate_high = 1

        # 5.inflation
        inflation_low = -10
        inflation_high = 10

        # 6. bank_account_balance
        bank_bal_low = 0
        bank_bal_high = inf

        # 7. Poverty rate
        poverty_rate_low = 0
        poverty_rate_high = 1

        # 8. Money Circulation
        money_circulation_low = 0
        money_circulation_high = inf

        # 9. Population
        population_low = 0
        population_high = inf
        
        
        self.observation_space = spaces.Box(
            # np.array([min_wage_lower_limit,0,0,0,-10,0,0,0,0]), 
            # np.array([15,inf,inf,100,10,inf,100,inf,inf]), shape=(9,), dtype=np.float64)
            np.array([minimum_wage_low, product_price_low, quantity_low,
                      unemployment_rate_low, inflation_low, bank_bal_low,
                      poverty_rate_low, money_circulation_low ,population_low]),

            np.array([minimum_wage_high, product_price_high, quantity_high,
                      unemployment_rate_high, inflation_high, bank_bal_high,
                      poverty_rate_high, money_circulation_high ,population_high]), shape=(9,), dtype=np.float64)


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
from gym_env import EconomyEnv
from stable_baselines3.common.env_checker import check_env

my_env = EconomyEnv()
my_env.observation_space
check_env(my_env)
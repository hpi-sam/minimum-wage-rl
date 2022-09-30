from ..gym_env import EconomyEnv
from stable_baselines3 import A2C

def generate_agent():
    game_env = EconomyEnv()
    A2C(policy="MlpPolicy", env=game_env, learning_rate=0.01, n_steps=5, gamma=0.9)
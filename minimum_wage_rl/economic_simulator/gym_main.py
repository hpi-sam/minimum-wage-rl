from gc import callbacks
from gym_env import EconomyEnv
import numpy as np
import sys

import mlflow

from stable_baselines3 import DDPG
from stable_baselines3 import A2C

from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise
from baseline.callback import SimulatorCallBack
from baseline.logger import MLflowOutputFormat
# from baseline.utiliy import generate_agent
from stable_baselines3.common.logger import Logger, HumanOutputFormat
from utility.publish import export_from_game_metric




mlflow.set_experiment(experiment_name="First")
with mlflow.start_run(run_name="one"):
    game_env = EconomyEnv()
    sim_call_back = SimulatorCallBack()
    logger = Logger(folder=None, output_formats=[HumanOutputFormat(sys.stdout), MLflowOutputFormat()])

    # Log Agent hyperparameters here
    # Log environment paramters here
    # 

    # agent = A2C(policy="MlpPolicy", env=game_env, learning_rate=0.0001, n_steps=5, gamma=0.9)
    # agent.set_logger(logger=logger)
    # agent.learn(total_timesteps=1000, callback=sim_call_back)


    # The noise objects for DDPG
    n_actions = game_env.action_space.shape[-1]
    action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))


    agent = DDPG(policy="MlpPolicy", env=game_env, action_noise=action_noise, verbose=1)
    agent.learn(total_timesteps=150)

    my_game = game_env.env
    export_from_game_metric(my_game.game_number, my_game.game_metric_list)

# model.learn(total_timesteps=10000, log_interval=10)
# model.save("ddpg_pendulum")
# env = model.get_env()

# del model # remove to demonstrate saving and loading

# model = DDPG.load("ddpg_pendulum")

# obs = env.reset()
# while True:
#     action, _states = model.predict(obs)
#     obs, rewards, dones, info = env.step(action)
#     env.render()
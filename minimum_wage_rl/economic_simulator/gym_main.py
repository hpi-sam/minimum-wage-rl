from gym_env import EconomyEnv
import numpy as np
import sys

import mlflow

from stable_baselines3 import DDPG
from stable_baselines3 import A2C
from stable_baselines3 import DQN
from stable_baselines3 import SAC
from stable_baselines3 import TD3

from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise
from baseline.callback import SimulatorEvaluationCallBack
from baseline.logger import MLflowOutputFormat
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.logger import Logger, HumanOutputFormat
from utility.publish import export_from_game_metric
from utility.publish_test import export_test_data
import numpy as np

from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv

# 1. SAC - stagflation_test_v1
# 2. TD3 - 

# def run_all_stuff(run_name, folder_name, seed_num):

mlflow.set_experiment(experiment_name="sac_with_ent_v1")

with mlflow.start_run(run_name="sac_ent_v3"):

    mlflow.log_param("Population_increase", 0.03)
    mlflow.log_param("Initial Population", 1500)
    mlflow.log_param("Stagflation", False)
    mlflow.log_param("Poverty Penalty", False)
    mlflow.log_param("Initial Above poverty percentage", 0)
    mlflow.log_param("Batch Size", "default")
    mlflow.log_param("Initial Exploration", True)
    mlflow.log_param("Negative Reward", True)
    mlflow.log_param("Subsidy", 100)
    mlflow.log_param("Entropy temperature", 1)
    # mlflow.log_text("Increasing Entropy of the Algorithm")
    # mlflow.log_param("Only trained PP", True)

    game_env_1 = EconomyEnv()
    game_env_1.env.level = 1

    test_game = EconomyEnv()
    test_game.env.level = 1
    eval_game_env = Monitor(test_game)
    best_model_name = "sac_with_ent_v3"


    # "C:\\Users\\AkshayGudi\\Documents\\3_MinWage\\minimum_wage_rl\\SAC\\stagflation\\normal\\"
    # "C:\\Users\\AkshayGudi\\Documents\\3_MinWage\\minimum_wage_rl\\SAC_No_Ent\\no_stag\\"
    root_folder = "C:\\Users\\AkshayGudi\\Documents\\3_MinWage\\minimum_wage_rl\\SAC\\stagflation\\normal\\"
    # root_folder = "Stagflation_test/no_stagflation/"
    tuned_model_root_folder = "C:\\Users\\AkshayGudi\\Documents\\3_MinWage\\minimum_wage_rl\\SAC\\stagflation\\normal\\"
    # tuned_model_root_folder = "Stagflation_test/no_stagflation/"
    best_model_folder =  root_folder + "best_model\\"
    train_data_folder = root_folder + "train_data\\"
    test_data_folder = root_folder + "test_data\\"
    trained_model_folder = root_folder + "model\\"
    tuned_model_folder = tuned_model_root_folder + "model\\"

    sim_eval_callback = SimulatorEvaluationCallBack(eval_env=eval_game_env, eval_freq=300, n_eval_episodes=1, best_model_save_path=best_model_folder+best_model_name+"/")
    logger = Logger(folder=None, output_formats=[HumanOutputFormat(sys.stdout), MLflowOutputFormat()])

    # The noise objects for TD3
    # n_actions = game_env_1.action_space.shape[-1]
    # action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
    # agent = DDPG(policy="MlpPolicy", env=game_env_1, action_noise=action_noise, verbose=1, learning_starts=10000, seed=1)
    # agent.set_env(game_env_1)
    # agent.set_logger(logger=logger)
    # agent.learn(total_timesteps=60000, callback=sim_eval_callback)


    agent = SAC(policy="MlpPolicy", env=game_env_1, verbose=1)
    agent.set_env(game_env_1)
    agent.set_logger(logger=logger)
    agent.learn(total_timesteps=60000, callback=sim_eval_callback)

    print(" =============================== train complete --- saving files and models ===============================")


    final_model_prefix = "sac_with_ent_v3"
    agent.save(trained_model_folder + "model"+final_model_prefix)



    env_list = [game_env_1.env]
    train_excel_file_name = "_" + "sac_with_ent_v3" +"_"
    for i, each_env in enumerate(env_list):
        j = 1 + i
        my_game = each_env
        # .envs[0].env
        gm_list = my_game.game_metric_list
        # [150:]
        #
        export_from_game_metric(my_game.game_number, gm_list, train_excel_file_name + str(j), train_data_folder)


    game_env_2 = EconomyEnv()
    game_env_2.env.level=1
    obs = game_env_2.reset()

    results = list()

    print(" ============================= testing model ============================")
    for i in range(30):
        action, _states = agent.predict(obs, deterministic=True)
        obs, reward, done, info = game_env_2.step(action)
        # env.render()
        results.append(list(obs))
        if done:
            obs = game_env_2.reset()

    test_excel_file_name = "_" + "sac_with_ent_v3" + "_"
    export_test_data(results, test_excel_file_name, test_data_folder)

    # =============================================================================================

    # Log Agent hyperparameters here
    # Log environment paramters here
    #

    # agent = A2C(policy="MlpPolicy", env=game_env, learning_rate=0.0001, n_steps=5, gamma=0.9)
    # agent.learn(total_timesteps=1000, callback=sim_call_back)

    # The noise objects for DDPG
    # n_actions = game_env_1.action_space.shape[-1]
    # action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))


    # agent = DDPG(policy="MlpPolicy", env=game_env_1, action_noise=action_noise, verbose=1, learning_starts=15000)
    # agent.set_logger(logger=logger)
    # agent.learn(total_timesteps=35000)


    # agent = DQN(policy="MlpPolicy", env=game_env_1, verbose=1, learning_starts=5000)
    # agent.set_logger(logger=logger)
    # agent.learn(total_timesteps=10000)


    # game_env_2 = EconomyEnv(level=2)
    # game_env_2 = DummyVecEnv([EconomyEnv])
    # game_env_2.envs[0].env.level=2
    # agent.env = game_env_2
    # agent.learn(total_timesteps=35000)

    # , callback=sim_eval_callback
    # game_env_2
    # , game_env_2.envs[0].env

# all_runs = ["ddpg_seed_23_v3"]
# folder_names = ["seed23"]
# seed_nums = [23]
#
# for i in range(len(all_runs)):
#     run_all_stuff(all_runs[i], folder_names[i], seed_nums[i])
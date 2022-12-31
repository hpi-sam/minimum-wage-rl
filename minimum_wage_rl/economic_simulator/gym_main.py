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
# from baseline.callback import SimulatorCallBack
from baseline.callback import SimulatorEvaluationCallBack
from baseline.logger import MLflowOutputFormat
# from baseline.utiliy import generate_agent
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.logger import Logger, HumanOutputFormat
from utility.publish import export_from_game_metric
from utility.publish_test import export_test_data
import numpy as np

from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv

mlflow.set_experiment(experiment_name="Level3_with_stag")

with mlflow.start_run(run_name="L1_sml_epi_80p_poor_explore"):

    mlflow.log_param("Population_increase" ,0.03)
    mlflow.log_param("Initial Population", 1500)
    mlflow.log_param("Stagflation", True)
    mlflow.log_param("Poverty Penalty",True)
    mlflow.log_param("Initial Above poverty percentage", 20)

    game_env_1 = EconomyEnv()
    game_env_1.env.level=4

    test_game = EconomyEnv()
    test_game.env.level=4
    eval_game_env = Monitor(test_game)
    best_model_name = "L1_sml_epi_80p_v1"
    root_folder = "Level3_with_stag/"
    best_model_folder =  root_folder + "best_model/"
    train_data_folder = root_folder + "train_data/"
    test_data_folder = root_folder + "test_data/"
    trained_model_folder = root_folder + "model/"

    sim_eval_callback = SimulatorEvaluationCallBack(eval_env=eval_game_env, eval_freq=500,n_eval_episodes=1,best_model_save_path=best_model_folder+best_model_name+"/")
    logger = Logger(folder=None, output_formats=[HumanOutputFormat(sys.stdout), MLflowOutputFormat()])

    agent = SAC(policy="MlpPolicy", env=game_env_1, verbose=1, learning_starts=15000)
    # old_best_model_name="L1_PP_v2/"
    # old_best_model_name="L1_NP_v1/"
    # agent = SAC.load(trained_model_folder +"model_L1_PP_to_NP_full_model_v1")
    # agent.set_env(game_env_1)    

    agent.set_logger(logger=logger)
    agent.learn(total_timesteps=45000, callback=sim_eval_callback)

    print(" ============================================= here ======================================")

    
    env_list = [game_env_1.env]
    train_excel_file_name = "_" + "L1_stag_sml_epi_80p_v1" +"_"
    for i, each_env in enumerate(env_list):
        j = 1   + i
        my_game = each_env
        # .envs[0].env
        gm_list = my_game.game_metric_list
        # [300:]
        # 
        export_from_game_metric(my_game.game_number, gm_list, train_excel_file_name + str(j), train_data_folder)


    game_env_2 = EconomyEnv()
    game_env_2.env.level=4
    obs = game_env_2.reset()

    results = list()

    for i in range(30):
        action, _states = agent.predict(obs, deterministic=True)
        obs, reward, done, info = game_env_2.step(action)
        # env.render()
        results.append(list(obs))
        if done:
            obs = game_env_2.reset()

    test_excel_file_name = "_" + "L1_stag_sml_epi_80p_v1" + "_"
    export_test_data(results, test_excel_file_name, test_data_folder)

    final_model_prefix = "_" + "L1_stag_sml_epi_80p_v1"
    agent.save(trained_model_folder + "model"+final_model_prefix)

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

    # agent = TD3(policy="MlpPolicy", env=game_env_1, action_noise=action_noise, verbose=1, learning_starts=15000)
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

from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.vec_env import VecEnv
from stable_baselines3.common.evaluation import evaluate_policy

import mlflow
from typing import Optional, Union
import gym
import numpy as np
import os



# class SimulatorCallBack(BaseCallback):
    
#     def __init__(self, verbose: int = 0):
#         super().__init__(verbose)
    
#     def _on_training_start(self) -> None:
#         my_step_num = self.training_env.envs[0].game_step
#         my_epi_num = self.training_env.envs[0].game_episode_num

#         print(f"Starting training ---> Episode - {my_epi_num},  Step - {my_step_num}")
#         return super()._on_training_start()
    
#     def _on_step(self) -> bool:
#         my_step_num = self.training_env.envs[0].game_step
#         my_epi_num = self.training_env.envs[0].game_episode_num
#         print(f"Next Step ---> Episode - {my_epi_num},  Step - {my_step_num}")
#         return super()._on_step()
    
class SimulatorEvaluationCallBack(EvalCallback):

    def __init__(self, eval_env: Union[gym.Env, VecEnv], callback_on_new_best: Optional[BaseCallback] = None, 
                callback_after_eval: Optional[BaseCallback] = None, n_eval_episodes: int = 5, eval_freq: int = 10000, 
                log_path: Optional[str] = None, best_model_save_path: Optional[str] = None, deterministic: bool = True, 
                render: bool = False, verbose: int = 1, warn: bool = True):
        
        super().__init__(eval_env, callback_on_new_best, callback_after_eval, n_eval_episodes, eval_freq, 
                        log_path, best_model_save_path, deterministic, render, verbose, warn)
        
        self.money_circulation = []
            

    def _on_step(self) -> bool:
        if self.eval_freq>0 and self.n_calls%self.eval_freq==0:
            
            self._reset_metrics()

            episode_rewards, episode_lengths = evaluate_policy(self.model, self.eval_env, n_eval_episodes=self.n_eval_episodes, return_episode_rewards=True, warn=True, callback=self._economic_metric_callback)

            reward_mean_per_episode, reward_std = np.mean(episode_rewards), np.std(episode_rewards)
            episode_len_mean = np.mean(episode_lengths)
            reward_mean = reward_mean_per_episode/episode_len_mean
            self.logger.record("eval/reward_per_episode", reward_mean_per_episode)
            self.logger.record("eval/reward_mean", reward_mean)
            self.logger.record("eval/episode_mean_len", episode_len_mean)
            
            self._record_economic_metrics()

            if reward_mean > self.best_mean_reward:
                if self.verbose > 0:
                    print("New best mean reward!")
                if self.best_model_save_path is not None:
                    self.model.save(os.path.join(self.best_model_save_path, "best_model"))
                self.best_mean_reward = reward_mean
                self.logger.record("eval/best_mean", self.best_mean_reward)
                # Trigger callback if needed
                # if self.callback is not None:
                #     return self._on_event()

        return True
    
    def _reset_metrics(self):
        self.money_circulation = []

    def _economic_metric_callback(self, locals_, globals_):
        self.money_circulation.append(locals_['info']['money_circulation'])
    
    def _record_economic_metrics(self):
        average_money_circulation = np.mean(self.money_circulation)
        self.logger.record("eval/average_money_circulation", average_money_circulation)

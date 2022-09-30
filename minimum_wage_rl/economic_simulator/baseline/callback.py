from stable_baselines3.common.callbacks import BaseCallback
import mlflow


class SimulatorCallBack(BaseCallback):
    
    def __init__(self, verbose: int = 0):
        super().__init__(verbose)
    
    def _on_training_start(self) -> None:
        my_step_num = self.training_env.envs[0].game_step
        my_epi_num = self.training_env.envs[0].game_episode_num

        print(f"Starting training ---> Episode - {my_epi_num},  Step - {my_step_num}")
        return super()._on_training_start()
    
    def _on_step(self) -> bool:
        my_step_num = self.training_env.envs[0].game_step
        my_epi_num = self.training_env.envs[0].game_episode_num
        
        # mean_params = self.model.get_parameters()
        # for k,v in mean_params.items():
        #     if k == "policy":
        #         for k1,v1 in v.items():
        #             print("Key --> ", k1)
        #             #  , "  Value --> ", v1
        #             print(v1.grad)

        print("========================= one ========================")

        # Log metrics
        # observations

        # Log weights

        print(f"Next Step ---> Episode - {my_epi_num},  Step - {my_step_num}")
        return super()._on_step()
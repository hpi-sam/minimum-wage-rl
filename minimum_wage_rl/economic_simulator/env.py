import numpy as np


class Task:
    def __init__(self, num_workers, envs):
        self.num_workers = num_workers
        self.env = DummyVecEnv(envs)

    def reset(self, episode_number):
        return self.env.reset(episode_number)

    def step(self, actions, episode_number):
        # if isinstance(self.action_space, Box):
        #     actions = np.clip(actions, self.action_space.low, self.action_space.high)
        return self.env.step(actions, episode_number)

    def get_state(self):
        return self.env.get_state()

class DummyVecEnv():
    def __init__(self, env_fns):
        self.envs = list(env_fns)
        self.num_envs = len(env_fns)
        self.i = 1
        # env = self.envs[0]
        # VecEnv.__init__(self, len(env_fns), env.observation_space, env.action_space)
        self.actions = None
	
    def step(self, actions, episode_number):		
        self.step_async(actions)
        return self.step_wait(episode_number)

    def construct_actions(self, actions):
        
        # action_val  = self.i * 200
        action_list = list()
        for each_action in actions:
            action_map = {"minimum_wage":round(each_action, 2)}
            action_list.append(action_map)

        return action_list

    def step_async(self, actions):
        self.actions = self.construct_actions(actions)
    
    def step_wait(self, episode_number):
        data = []
        for i in range(self.num_envs):
            # _, obs, rew, info, done  = self.envs[i].step(self.actions[i])
            obs, rew, info, done  = self.envs[i].step(self.actions[i])
            if done:
                obs = self.envs[i].reset(episode_number)
                action_val = {"minimum_wage": obs["Minimum wage"]}
                obs, rew, info, done = self.envs[i].step(action_val)

            data.append([obs, rew, info, done])
        obs, rew, info, done = zip(*data)
        return obs, np.asarray(rew), info, np.asarray(done)

    def reset(self, episode_number):
        return [env.reset(episode_number) for env in self.envs]
    
    def get_state(self):
        data = []
        for env in self.envs:
            obs = env.get_state()
            data.append(obs)
        # obs, rew, done, info = zip(*data)
        # , np.asarray(rew), np.asarray(done), info
        return data           

    def close(self):
        return
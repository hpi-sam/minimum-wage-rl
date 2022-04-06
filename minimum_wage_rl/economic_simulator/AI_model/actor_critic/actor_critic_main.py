from .utility import Storage
from .models import CategoricalActor, Critic
import torch.optim as optim
from economic_simulator.utility import simulate
from torch import tensor

roll_out_length = 2
discount = 0.9
num_steps = 5
actor_lr = 0.01
critic_lr = 0.05


class ActorCritic:

    def __init__(self,user) -> None:    
        self.actor_model = CategoricalActor()
        self.critic_model = Critic()
        self.actor_optimizer = optim.Adam(self.actor_model.parameters(), lr=actor_lr)
        self.critic_optimizer = optim.Adam(self.critic_model.parameters(), lr=critic_lr)
        self.user = user
    
    def step(self):
        current_state = self.get_state()
        storage = Storage(roll_out_length)

        for _ in range(roll_out_length):
            action_prediction = self.actor_model(current_state)
            state_value_prediction = self.critic_model(current_state)
            
            
            storage.actions.append(action_prediction["action"])
            storage.state_values.append(state_value_prediction["value"])
            storage.log_actions.append(action_prediction["log_pi_a"])

            state_reward = simulate.step(action_prediction["action"].item(), self.user) 
            next_state = tensor(state_reward["state"])
            reward = tensor(state_reward["reward"]).unsqueeze(-1)
            terminate = tensor(1 - state_reward["done"]).unsqueeze(-1)

            storage.rewards.append(reward)
            storage.episode_end_flag.append(terminate)

            current_state = next_state
        
        action_prediction = self.actor_model(current_state)
        state_value_prediction = self.critic_model(current_state)

        storage.actions.append(action_prediction["action"])
        storage.state_values.append(state_value_prediction["value"])
        storage.log_actions.append(action_prediction["log_pi_a"])

        returns = state_value_prediction["value"].detach()

        advantages = [0] * roll_out_length
        ret = [0] * roll_out_length
        for i in reversed(range(roll_out_length)):
            returns = storage.rewards[i] + discount * storage.episode_end_flag[i] * returns            
            advantages[i] = returns - storage.state_values[i].detach()
            advantages[i] = advantages[i].detach()
            ret[i] = returns.detach()
            
        storage.advantages = advantages
        storage.expected_returns = ret
        keys = ["log_actions","state_values",
                "advantages","expected_returns","rewards",
                "episode_end_flag"]
        entries = storage.extract(keys)

        policy_loss = -(entries.log_actions * entries.advantages).mean()
        value_loss = 0.5 * (entries.expected_returns - entries.state_values).pow(2).mean()

        self.actor_optimizer.zero_grad()
        self.critic_optimizer.zero_grad()

        policy_loss.backward()
        value_loss.backward()

        self.actor_optimizer.step()
        self.critic_optimizer.step()


    def get_state(self):
        state_reward = simulate.get_state(self.user)
        return tensor(state_reward["state"])


def train(user):
    actor_critic = ActorCritic(user)

    for _ in range(num_steps):
        actor_critic.step()
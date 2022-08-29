from .utility import Storage
from .models import Critic, GaussianActor
import torch.optim as optim
from utility import simulate_2
from utility.config import ConfigurationParser
import torch
# from . import utility
from torch.utils.tensorboard import SummaryWriter

roll_out_length = 5
discount = 0.9
num_steps = 5
actor_lr = 0.01
critic_lr = 0.05

config_parser = ConfigurationParser.get_instance().parser
num_steps = int(config_parser.get("training","num_steps"))
episodes = int(config_parser.get("training","episodes"))
min_wage_lower_bound = float(config_parser.get("minwage","initial_minimum_wage"))
penalize_lower_bound = int(config_parser.get("training","penalize_lower_bound"))


class ActorCriticAgent:

    def __init__(self, task, user, action_dim) -> None:    
        self.actor_model = GaussianActor(action_dim=action_dim, lower_limit=min_wage_lower_bound) 
        # CategoricalActor()
        self.critic_model = Critic()
        self.actor_optimizer = optim.Adam(self.actor_model.parameters(), lr=actor_lr)
        self.critic_optimizer = optim.Adam(self.critic_model.parameters(), lr=critic_lr)
        self.user = user
        self.task = task
        self.writer = None
    
    def step(self, mu_dict, sigma_dict, step_num,loss_step, episode_num):
        
        state_values = self.task.get_state()
        current_state = torch.tensor(state_values, dtype=torch.float)
        storage = Storage(roll_out_length)

        for _ in range(roll_out_length):
            step_num = step_num + 1
            action_prediction = self.actor_model(current_state)
            state_value_prediction = self.critic_model(current_state)
                        
            storage.actions.append(action_prediction["action"])
            storage.state_values.append(state_value_prediction["value"])
            storage.log_actions.append(action_prediction["log_pi_a"])
            
            # if action_prediction["predicted_action"].item() < min_wage_lower_bound:
            #     storage.low_action_value_count.append(torch.tensor([1]))
            # else:
            #     storage.low_action_value_count.append(torch.tensor([0]))
            
            state_values, reward, message, done = self.task.step((action_prediction["action"]).detach().squeeze().numpy(), episode_num) 
            next_state = torch.tensor(state_values , dtype=torch.float)
            reward = torch.tensor(reward, dtype=torch.float).unsqueeze(-1)
            terminate = torch.tensor(1 - done).unsqueeze(-1)

            current_state = next_state

            storage.rewards.append(reward)
            storage.episode_end_flag.append(terminate)

            
        
        action_prediction = self.actor_model(current_state)
        state_value_prediction = self.critic_model(current_state)

        storage.actions.append(action_prediction["action"])
        storage.state_values.append(state_value_prediction["value"])
        storage.log_actions.append(action_prediction["log_pi_a"])
        
        # if action_prediction["predicted_action"].item() < min_wage_lower_bound:
        #     storage.low_action_value_count.append(torch.tensor([1]))
        # else:
        #     storage.low_action_value_count.append(torch.tensor([0]))
        
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
                # low_action_value_count
        entries = storage.extract(keys)

        # Mu_Loss
        # mu_loss = sum(entries.low_action_value_count) * penalize_lower_bound
        # mu_loss = max(1,mu_loss)
        # exp_mu_loss = torch.exp(max(0,mu_loss))

        # loss = mu_loss.item() if mu_loss.item() > 0 else 1

        # Actor loss
        policy_loss = -(entries.log_actions * entries.advantages).mean()
        # print("Policy Loss - " , policy_loss)
        # * (loss)
        
        # Critic Loss
        value_loss = 0.5 * (entries.expected_returns - entries.state_values).pow(2).mean()
        # print("Value Loss - ", value_loss)

        self.writer.add_scalar("Actor Loss", policy_loss.item(), loss_step)
        # self.writer.add_scalar("Actor Loss Game 2", policy_loss[1].item(), loss_step)

        self.writer.add_scalar("Critic Loss", value_loss.item(), loss_step)
        # self.writer.add_scalar("Critic Loss Game 2", value_loss[1].item(), loss_step)

        self.actor_optimizer.zero_grad()
        self.critic_optimizer.zero_grad()

        policy_loss.backward()
        value_loss.backward()

        self.actor_optimizer.step()
        self.critic_optimizer.step()

        for name, param in self.actor_model.named_parameters():
            self.writer.add_histogram(f"{name}_actor", param, loss_step)
            self.writer.add_histogram(f"{name}_actor.grad", param.grad, loss_step)
        
        for name, param in self.critic_model.named_parameters():
            self.writer.add_histogram(f"{name}_critic", param, loss_step)
            self.writer.add_histogram(f"{name}_critic.grad", param.grad, loss_step)
            # print(param.grad)

        print("here")

    def reset(self, episode_num):
        self.task.reset(episode_num)

    def get_state(self):
        user_data, state_values, reward,message, done = simulate_2.get_state(self.user)
        return torch.tensor(state_values, dtype=torch.float)

    def save_model(self):
        torch.save(self.actor_model, "saved_models/actor.pt")
        torch.save(self.critic_model, "saved_models/critic.pt")

def train(num_workers, task):
    user = None
    a2c_agent = ActorCriticAgent(task, user, action_dim=1)

    for episode_num in range(episodes):
        
        a2c_agent.writer = SummaryWriter("new_arch_v4/episode_" + str(episode_num))

        current_state = a2c_agent.task.reset(episode_num)
        action_value = current_state[0]["Minimum wage"]
        actions = [action_value]*num_workers
        state_values, reward, message, done = a2c_agent.task.step(actions, episode_num)

        state_values = a2c_agent.task.get_state()

        mu_dict = dict()
        sigma_dict = dict()
        step_num = 0

        # Normalize initial Inputs
        step_num = 1
        for loss_step in range(num_steps):
            a2c_agent.step(mu_dict, sigma_dict, step_num,loss_step, episode_num)
        
        a2c_agent.writer.close()

        # a2c_agent.reset(episode_num)
        # utility.close_game(user)
    # save model

# def get_policy():
#     pass
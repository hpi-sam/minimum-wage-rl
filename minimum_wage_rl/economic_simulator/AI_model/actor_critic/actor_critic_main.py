# from .utility import Storage
# from . import utility
# from .models import CategoricalActor, Critic, GaussianActor
# import torch.optim as optim
# from economic_simulator.utility import simulate_2
# from economic_simulator.utility import start_up_2
# from economic_simulator.utility.config import ConfigurationParser
# import torch

# roll_out_length = 5
# discount = 0.9
# actor_lr = 0.01
# critic_lr = 0.05


# config_parser = ConfigurationParser.get_instance().parser
# num_steps = int(config_parser.get("training","num_steps"))
# episodes = int(config_parser.get("training","episodes"))
# min_wage_lower_bound = float(config_parser.get("minwage","initial_minimum_wage"))
# penalize_lower_bound = int(config_parser.get("training","penalize_lower_bound"))


# class ActorCritic:

#     def __init__(self,user, action_dim) -> None:    
#         self.actor_model = GaussianActor(action_dim=action_dim) 
#         # CategoricalActor()
#         self.critic_model = Critic()
#         self.actor_optimizer = optim.Adam(self.actor_model.parameters(), lr=actor_lr)
#         self.critic_optimizer = optim.Adam(self.critic_model.parameters(), lr=critic_lr)
#         self.user = user
    
#     def step(self, mu_dict, sigma_dict, step_num):
        
#         current_state = self.get_state()
#         # state_dict = utility.map_inputs(current_state)
#         # normalized_state = utility.get_normalized_state(state_dict, mu_dict, sigma_dict, step_num)

#         storage = Storage(roll_out_length)

#         for _ in range(roll_out_length):
#             step_num = step_num + 1
#             action_prediction = self.actor_model(current_state)
#             state_value_prediction = self.critic_model(current_state)
                        
#             storage.actions.append(action_prediction["action"])
#             storage.state_values.append(state_value_prediction["value"])
#             storage.log_actions.append(action_prediction["log_pi_a"])
#             if action_prediction["predicted_action"].item() < min_wage_lower_bound:
#                 storage.low_action_value_count.append(torch.tensor([1]))
#             else:
#                 storage.low_action_value_count.append(torch.tensor([0]))
#             # action_prediction["mean"][0] =  2 - action_prediction["mean"].item()
#             # storage.mean_values.append(action_prediction["mean"])
            
#             action_value = round(action_prediction["action"].item(), 2)

#             action_map = {"minimum_wage" : action_value}

#             _, state_values, reward, message, done = simulate_2.step(action_map, self.user)
            
#             # state_dict = utility.map_inputs(state_values)
#             # normalized_state = utility.get_normalized_state(state_dict, mu_dict, sigma_dict, step_num)    

#             next_state = torch.tensor(state_values)
#             reward = torch.tensor(reward).unsqueeze(-1)
#             terminate = torch.tensor(1 - done).unsqueeze(-1)

#             current_state = next_state

#             storage.rewards.append(reward)
#             storage.episode_end_flag.append(terminate)
        
#         action_prediction = self.actor_model(current_state)
#         state_value_prediction = self.critic_model(current_state)

#         storage.actions.append(action_prediction["action"])
#         print(action_prediction["action"])
#         storage.state_values.append(state_value_prediction["value"])
#         storage.log_actions.append(action_prediction["log_pi_a"])

#         if action_prediction["predicted_action"].item() < min_wage_lower_bound:
#             storage.low_action_value_count.append(torch.tensor([1]))
#         else:
#             storage.low_action_value_count.append(torch.tensor([0]))

#         returns = state_value_prediction["value"].detach()

#         advantages = [0] * roll_out_length
#         ret = [0] * roll_out_length
#         for i in reversed(range(roll_out_length)):
#             returns = storage.rewards[i] + discount * storage.episode_end_flag[i] * returns            
#             advantages[i] = returns - storage.state_values[i].detach()
#             advantages[i] = advantages[i].detach()
#             ret[i] = returns.detach()
            
#         storage.advantages = advantages
#         storage.expected_returns = ret
#         keys = ["log_actions","state_values",
#                 "advantages","expected_returns","rewards",
#                 "episode_end_flag", "low_action_value_count"]
#         entries = storage.extract(keys)

#         # Mu_Loss
#         mu_loss = sum(entries.low_action_value_count) * penalize_lower_bound
#         # mu_loss = max(1,mu_loss)
#         # exp_mu_loss = torch.exp(max(0,mu_loss))

#         loss = mu_loss.item() if mu_loss.item() > 0 else 1

#         policy_loss = - (entries.log_actions * entries.advantages).mean() 
#         # * (loss)
#         value_loss = 0.5 * (entries.expected_returns - entries.state_values).pow(2).mean()

#         self.actor_optimizer.zero_grad()
#         self.critic_optimizer.zero_grad()

#         policy_loss.backward()
#         value_loss.backward()

#         self.actor_optimizer.step()
#         self.critic_optimizer.step()

#     def get_state(self):
#         user_data, state_values, reward, message, done = simulate_2.get_state(self.user)
#         return torch.tensor(state_values)
    
#     def save_model(self):
#         torch.save(self.actor_model, "saved_models/actor.pt")
#         torch.save(self.critic_model, "saved_models/critic.pt")


# def train(user):
#     actor_critic = ActorCritic(user, action_dim=1)

#     for episode_num in range(episodes):
        
#         # Reset environment
#         # start game
#         # if (episode_num+1) <= 1:
#         current_state = start_up_2.start(user)
#         action_map = {"minimum_wage" : current_state["Minimum wage"]}
#         _, state_values, reward, message, done = simulate_2.step(action_map, user)

        
#         mu_dict = dict()
#         sigma_dict = dict()
#         step_num = 0

#         # Normalize initial Inputs
#         step_num = 1
#         for _ in range(num_steps):            
#             actor_critic.step(mu_dict, sigma_dict, step_num)

#         # end game
#         utility.close_game(user)

#     # save model
#     # actor_critic.save_model()





# #     mean_map = dict()
# #     mean_map = {"minimum_wage":0.0, "product_price":0.0, "quantity":0.0,
# #                     "poverty_rate":0.0, "unemployment_rate":0.0,
# #                     "inflation":0.0, "bank_account_balance":0.0}


# #     old_state["minimum_wage"] = mean_map["minimum_wage"] = state_values[0]
# #     old_state["product_price"] = mean_map["product_price"] = state_values[1]
# #     old_state["quantity"] = mean_map["quantity"] = state_values[2]
# #     old_state["poverty_rate"] = mean_map["poverty_rate"] = state_values[3]
# #     old_state["unemployment_rate"] = mean_map["unemployment_rate"] = state_values[4]
# #     old_state["inflation"] = mean_map["inflation"] = state_values[5]
# #     old_state["bank_account_balance"] = mean_map["bank_account_balance"] = state_values[6]

# #     sigma_map = dict()
# #     sigma_map = {"minimum_wage":0.01, "product_price":0.01, "quantity":0.01,
# #                     "poverty_rate":0.01, "unemployment_rate":0.01,
# #                     "inflation":0.01, "bank_account_balance":0.01}
                
# #     return old_state, mean_map, sigma_map

# # def get_policy():
# #     pass

#     # state_values.append(metric.minimum_wage)
#     # state_values.append(metric.product_price)
#     # state_values.append(metric.quantity)
#     # state_values.append(metric.poverty_rate)
#     # state_values.append(metric.unemployment_rate)

#     # state_values.append(metric.inflation)
#     # state_values.append(metric.bank_account_balance)
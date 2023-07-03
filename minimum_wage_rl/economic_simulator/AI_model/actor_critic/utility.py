# from collections import namedtuple
# import torch
# from django.db import models
# from economic_simulator.models.game import Game

# class Storage:
    
#     def __init__(self, memory_size) -> None:
#         self.actions = list()
#         self.log_actions = list()
#         self.state_values = list()
#         self.advantages = list()
#         self.expected_returns = list()
#         self.rewards = list()
#         self.episode_end_flag = list()
#         # self.mean_values = list()
#         self.low_action_value_count = list()

#         self.memory_size = memory_size

#     def extract(self, keys):
#         data = [getattr(self, k)[:self.memory_size] for k in keys]
#         data = map(lambda x: torch.cat(x, dim=0), data)
#         Entry = namedtuple('Entry', keys)
#         return Entry(*list(data))

#         # keys = ["actions","log_actions","state_values",
#                 # "advantages","expected_returns","rewards","episode_end_flag"]

# state_element_list = ["minimum_wage", "product_price", "quantity",
#                     "poverty_rate", "unemployment_rate",
#                     "inflation","bank_account_balance"]

# def get_new_mu(current_mu, current_state, n):
#     return (current_mu + (current_state-current_mu)/n )

# def get_new_sigma(new_mu, current_mu, current_sigma, current_state, n):
#     return current_sigma + (current_state-current_mu)*(current_state-new_mu)/n

# def get_normalized_state(state_dict, mu_dict, sigma_dict, step):
	
#     normalized_state_list = list()
#     for state_element in state_element_list:

#         current_state = state_dict[state_element]
#         try:
#             mu_list = mu_dict[state_element]
#             current_mu = mu_list[-1]
#         except:
#             mu_list = list()
#             current_mu = current_state
#             mu_list.append(current_mu)	
			
#         try:
#             sigma_list = sigma_dict[state_element]
#             current_sigma = sigma_list[-1]
#         except:
#             sigma_list = list()
#             current_sigma = 0.001
#             sigma_list.append(current_sigma)
		
#         if step > 1:
#             new_mu = get_new_mu(current_mu, current_state, len(mu_list)+1)
#             mu_list.append(new_mu)
            
                    
#             new_sigma = get_new_sigma(new_mu, current_mu, current_sigma, current_state, len(mu_list)+1)
#             sigma_list.append(new_sigma)
            

#             normalized_state = (current_state - new_mu)/new_sigma
#         else:
#             normalized_state = current_state
        
#         sigma_dict[state_element] = sigma_list
#         mu_dict[state_element] = mu_list
#         normalized_state_list.append(normalized_state)
#     normalized_state_tensor = torch.tensor(normalized_state_list)
#     return normalized_state_tensor

# def map_inputs(state_values):
#     state_dict = dict()
#     for index, each_item in enumerate(state_element_list):
#         state_dict[each_item] = state_values[index]

#     return state_dict

# def close_game(user):
#     game_obj = get_latest_game(user)

#     if game_obj == None:
#         return
#     else:
#         game_obj.game_ended = True
#         game_obj.save()

# def get_latest_game(user):
    
#     game_obj = None
#     max_game_number = None
#     max_game_query = Game.objects.filter(player=user, game_ended=False).aggregate(max_game_number=models.Max("game_number"))
    
#     if not max_game_query:
#         pass
#     else:
#         max_game_number = max_game_query["max_game_number"]
#         game_obj = Game.objects.filter(player=user, game_ended = False, game_number = max_game_number).first()

#     return game_obj

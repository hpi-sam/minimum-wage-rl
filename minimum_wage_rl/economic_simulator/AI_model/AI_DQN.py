# # %matplotlib inline
# # import gym
# import math
# import random
# import numpy as np
# import matplotlib
# import matplotlib.pyplot as plt
# from collections import namedtuple
# from itertools import count
# from PIL import Image
# import torch
# import torch.nn as nn
# import torch.optim as optim
# import torch.nn.functional as F


# class DQN(nn.Module):
#     def __init__(self):
#         super().__init__()
         
#         self.fc1 = nn.Linear(in_features=4, out_features=24)   
#         self.fc2 = nn.Linear(in_features=24, out_features=32)
#         self.out = nn.Linear(in_features=32, out_features=3)            

#     def forward(self, t):
#         t = F.relu(self.fc1(t))
#         t = F.relu(self.fc2(t))
#         t = self.out(t)
#         return t

# Experience = namedtuple(
#     'Experience',
#     ('state', 'action', 'next_state', 'reward')
# )

# class ReplayMemory():
#     def __init__(self, capacity):
#         self.capacity = capacity
#         self.memory = []
#         self.push_count = 0
        
#     def push(self, experience):
#         if len(self.memory) < self.capacity:
#             self.memory.append(experience)
#         else:
#             self.memory[self.push_count % self.capacity] = experience
#         self.push_count += 1

#     def sample(self, batch_size):
#         return random.sample(self.memory, batch_size)

#     def can_provide_sample(self, batch_size):
#         return self.push_count > batch_size

# class EpsilonGreedyStrategy():
#     def __init__(self, start, end, decay):
#         self.start = start
#         self.end = end
#         self.decay = decay
    
#     def get_exploration_rate(self, current_step):
#         return self.end + (self.start - self.end) * \
#             math.exp(-1. * current_step * self.decay)


# class Agent():
#     def __init__(self, strategy, num_actions, device):
#         self.current_step = 0
#         self.strategy = strategy
#         self.num_actions = num_actions
#         self.device = device

#     def select_action(self, state, policy_net):
#         rate = self.strategy.get_exploration_rate(self.current_step)
#         self.current_step += 1

#         if rate > random.random():
#             action = random.randrange(self.num_actions)
#             return torch.tensor([action]) # explore      
#         else:
#             with torch.no_grad():
#                 pred = policy_net(state)
#                 return pred.argmax(dim=1) # exploit


# def extract_tensors(experiences):
#     # Convert batch of Experiences to Experience of batches  
#     batch = Experience(*zip(*experiences))
#     t1 = torch.stack(batch.state, dim=0)
#     t2 = torch.stack(batch.action, dim=0)
#     t3 = torch.stack(batch.reward, dim=0)
#     t4 = torch.stack(batch.next_state, dim=0)
#     return (t1,t2,t3,t4)


# class QValues():
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
#     @staticmethod
#     def get_current(policy_net, states, actions):
#         pred = policy_net(states)        
#         return pred.gather(dim=1, index=actions)
    
#     @staticmethod        
#     def get_next(target_net, next_states):                        
#         values = target_net(next_states).max(dim=1).values.unsqueeze(dim=1).detach()
#         return values
from django.test import TestCase


# import gym

# print("hello")

import numpy as np

l1 = np.array([1.1])
print(l1.shape)


# from ..economic_simulator.utility.config import ConfigurationParser
# config_parser = ConfigurationParser.get_instance().parser
# JUNIOR_SKILL_LEVEL = int(config_parser.get("worker","junior_skill_level"))

# print(JUNIOR_SKILL_LEVEL)


# import atari_py
# print(atari_py.list_games())


# a = torch.randn((3,3), requires_grad=True)
# w1 = torch.randn((3,3), requires_grad=True)

# b = w1 * a

# b.grad_fn

# Create your tests here.
# game = Game(1)
# game.reset()
# print("one")
# action_map = {"minimum_wage":3.2}
# _, obs, rew, info, done = game.step(action_map)

# all_cmp = game.country.company_list
# cmp = all_cmp[0]

# print(obs)

# print("two")

# game.reset()

# print("done")





# def construct_actions(actions):

#     action_list = list()
#     for each_action in actions:
#         action_map = {"minimum_wage":round(each_action, 2)}
#         action_list.append(action_map)

#     return action_list



# import torch
# from AI_model.actor_critic.models import GaussianActor
# from AI_model.actor_critic.models import Critic
# import numpy as np

# ga = GaussianActor(1)

# data = []

# for i in range(1, 4):
#     d1 = [[i*0.1,i+0.2,i+0.3, i+0.4,i+0.5,i+0.6,i+0.7], i*0.5, i *2.5, False]
#     data.append(d1)

# # obs,  np.asarray(reward), message, state = 
# obs, rew, info, done = zip(*data)

# rew = np.asarray(rew)
# done = np.asarray(done)

# obs = torch.tensor(obs)
# rew = torch.tensor(rew).unsqueeze(-1)

# # v = ga(obs)
# critic = Critic()
# v1 = critic(obs)

# print(v1)

# actions = v["action"].detach().squeeze().numpy()

# p = construct_actions(actions)

# print(p)


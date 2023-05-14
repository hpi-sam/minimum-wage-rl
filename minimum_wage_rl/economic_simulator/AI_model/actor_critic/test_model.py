import torch
from models import CategoricalActor, Critic, GaussianActor
# actor_model = GaussianActor(action_dim=1)

# for name, param in actor_model.named_parameters():
#     print(f"{name}_actor")
#     print(param.grad)

# print("done")

# from torch.utils.tensorboard import SummaryWriter


# writer = SummaryWriter('runs/my_test')

# ==========================================
# data = []

# for i in range(1,4):
#     d1 = [[i,i,i,i], i*10, True]
#     data.append(d1)

# obs, reward, done = zip(*data)

# print(obs)
# print(reward)
# print(done)
# =========================================

t1 = input = torch.tensor([[1,2,3,4,5,6,7], [1,2,3,4,5,6,7]], dtype=torch.float32)

t2 = torch.tensor([[1,2,3],[1,2,3]], dtype=torch.float32)

v = t2.sum()

print(v)

# t2 = torch.tensor([[1.0],[2.0]])

# print(t2[0].item())

# a = t1.size()[0]

# for i in range(a):
#     if t1[i] < 2.0:
#         t1[i] = 2.0

# print(t1)

# print(t1.item())
# action = torch.tensor([1.3],[1.5])
# epsilon = 1e-6
# torch.log(1 - action.pow(2) + epsilon)


# p = actor_model(t1)
# print(p)
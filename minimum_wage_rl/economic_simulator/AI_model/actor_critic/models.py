from turtle import forward
import torch
import torch.nn as nn
import torch.nn.functional as F

class CategoricalActor(nn.Module):

    def __init__(self):
        super(CategoricalActor, self).__init__()

        self.input = nn.Linear(in_features=4, out_features=32)
        self.hidden1 = nn.Linear(in_features=32,out_features=16)
        self.hidden2 = nn.Linear(in_features=16, out_features=8)
        self.out = nn.Linear(in_features=8, out_features=3)

    def forward(self, obs, action=None):
        obs = torch.tensor(obs)
        h1 = self.input(obs)
        h1_act = F.tanh(h1)

        h2 = self.hidden1(h1_act)
        h2_act = F.tanh(h2)

        h3 = self.hidden2(h2_act)
        h3_act = F.tanh(h3)

        logits = self.out(h3_act)
        # v = self.fc_critic(phi_v)
        dist = torch.distributions.Categorical(logits=logits)
        if action is None:
            action = dist.sample()
        log_prob = dist.log_prob(action).unsqueeze(-1)
        entropy = dist.entropy().unsqueeze(-1)
        return {'action': action,
                'log_pi_a': log_prob,
                'entropy': entropy}

class GaussianActor(nn.Module):

    def __init__(self):
        super(GaussianActor, self).__init__()
        self.input = nn.Linear(in_features=4, out_features=32)
        self.hidden1 = nn.Linear(in_features=32,out_features=16)
        self.hidden2 = nn.Linear(in_features=16, out_features=8)
        self.mu = nn.Linear(in_features=8, out_features=1)
        self.sigma = nn.Linear(in_features=8,out_features=1)
    
    def forward(self, obs):
        obs = torch.tensor(obs)
        h1 = self.input(obs)
        h1_act = F.tanh(h1)

        h2 = self.hidden1(h1_act)
        h2_act = F.tanh(h2)

        h3 = self.hidden2(h2_act)
        h3_act = F.tanh(h3)

        mean = self.mu(h3_act)
        sigma = self.sigma(h3_act)

        dist = torch.distributions.Normal(mean, F.softplus(sigma))
        if action is None:
            action = dist.sample()
        log_prob = dist.log_prob(action).sum(-1).unsqueeze(-1)
        entropy = dist.entropy().sum(-1).unsqueeze(-1)
        return {'action': action,
                'log_pi_a': log_prob,
                'entropy': entropy,
                'mean': mean}

class Critic(nn.Module):

    def __init__(self):
        super(Critic, self).__init__()

        self.input = nn.Linear(in_features=4, out_features=32)
        self.hidden1 = nn.Linear(in_features=32,out_features=16)
        self.hidden2 = nn.Linear(in_features=16, out_features=8)
        self.out = nn.Linear(in_features=8, out_features=1)
            
    def forward(self, obs):
        obs = torch.tensor(obs)
        h1 = self.input(obs)
        h1_act = F.tanh(h1)

        h2 = self.hidden1(h1_act)
        h2_act = F.tanh(h2)

        h3 = self.hidden2(h2_act)
        h3_act = F.tanh(h3)

        # logits = self.fc_action(h3)
        v = self.out(h3_act)
        # dist = torch.distributions.Categorical(logits=logits)
        # if action is None:
        #     action = dist.sample()
        # log_prob = dist.log_prob(action).unsqueeze(-1)
        # entropy = dist.entropy().unsqueeze(-1)
        return {'value': v}        
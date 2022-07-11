import math
from cv2 import log
import torch
import torch.nn as nn
import torch.nn.functional as F
import logging

logging.basicConfig(filename="C:\\Users\\AkshayGudi\\Documents\\3_MinWage\\minimum_wage_rl\\economic_simulator\\AI_model\\actor_critic\\model_log.log", level=logging.INFO)

class CategoricalActor(nn.Module):

    def __init__(self):
        super(CategoricalActor, self).__init__()

        self.input = nn.Linear(in_features=8, out_features=32)
        self.hidden1 = nn.Linear(in_features=32,out_features=16)
        self.hidden2 = nn.Linear(in_features=16, out_features=8)
        self.out = nn.Linear(in_features=8, out_features=3)

    def forward(self, obs, action=None):
        obs = torch.tensor(obs)
        h1 = self.input(obs)
        h1_act = torch.relu(h1)

        h2 = self.hidden1(h1_act)
        h2_act = torch.relu(h2)

        h3 = self.hidden2(h2_act)
        h3_act = torch.relu(h3)

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

    def initialize_weights(self):        
        for m in self.modules:
            torch.nn.init.ones_(m.weight, gain=1)

class GaussianActor(nn.Module):

    def __init__(self, action_dim,lower_limit=2.0, log_std_min = -20, log_std_max=2, min_mean=2):
        super(GaussianActor, self).__init__()

        self.lower_limit = lower_limit

        # self.input = nn.Linear(in_features=7, out_features=32)
        # self.hidden1 = nn.Linear(in_features=32,out_features=48)
        # self.hidden2 = nn.Linear(in_features=48, out_features=32)
        # self.hidden3 = nn.Linear(in_features=32, out_features=16)
        # self.hidden4 = nn.Linear(in_features=16, out_features=8)

        self.input = nn.Linear(in_features=7, out_features=32)
        self.hidden1 = nn.Linear(in_features=32,out_features=16)
        self.hidden2 = nn.Linear(in_features=16, out_features=8)


        self.mu = nn.Linear(in_features=8, out_features=1)
        self.sigma = nn.Linear(in_features=8,out_features=1)
        # self.sigma = nn.Parameter(torch.zeros(action_dim))
        self.std = nn.Parameter(torch.zeros(action_dim))
        self.log_std_min =log_std_min
        self.log_std_max = log_std_max
        self.min_mean = min_mean

        for m in self.modules():
            if isinstance(m, nn.Linear):
                m.weight = torch.nn.init.ones_(m.weight)
                #  orthogonal_

    
    def forward(self, obs, action=None, epsilon=1e-6):
        
        obs = obs.clone().detach()
        # torch.tensor(obs)
        h1 = self.input(obs)
        h1_act = torch.tanh(h1)

        h2 = self.hidden1(h1)
        h2_act = torch.tanh(h2)

        h3 = self.hidden2(h2_act)
        h3_act = torch.tanh(h3)

        # h4 = self.hidden3(h3_act)
        # h4_act = torch.relu(h4)

        # h5 = self.hidden4(h4_act)
        # h5_act = torch.relu(h5)

        mean = torch.relu(self.mu(h3_act))
        logging.info("Mean - " + str(mean))
        # mean = torch.clamp(mean, self.min_mean)
        sigma = F.softplus(self.std)
        # sigma = F.softplus(self.sigma(h3_act))
        # clamped_sigma = torch.clamp(sigma,self.log_std_min, self.log_std_max)
        # sigma = self.sigma(h3_act)
        # log_sigma = self.sigma(h3_act)
        # log_clamped_sigma = torch.clamp(log_sigma,self.log_std_min, self.log_std_max)
        # clamped_sigma = log_clamped_sigma.exp()
        # logging.info("Log_sigma - " + str(log_sigma))
        # logging.info("Log_clamped_sigma - " + str(log_clamped_sigma))
        # logging.info("Clamped Sigma - " + str(clamped_sigma))
        logging.info(" ==================================== ")

        # normal = torch.distributions.Normal(0,1)
        # z =  normal.sample() 

        # action = torch.relu(mean + clamped_sigma * z)
        dist = torch.distributions.Normal(mean, sigma)
        action = dist.sample()
        log_prob = dist.log_prob(action).sum(-1).unsqueeze(-1)
        entropy = dist.entropy().sum(-1).unsqueeze(-1)

        size = action.size()[0]
        for i in range(size):
            if math.isnan(action[i]):
                print("NAN value")

        predicted_action = action.clone().detach()
        print("Predicted Action ===> ", predicted_action.numpy())
        
        size = action.size()[0]
        for i in range(size):
            if action[i] < self.lower_limit:
                action[i] = self.lower_limit

        # min_action = torch.clone(action)
        # min_action[0] = 2
        # action = max(min_action, action)
        # v = torch.log(1 - action.pow(2) + epsilon)
        # log_prob = torch.distributions.Normal(mean,clamped_sigma).log_prob(action) 
        # - torch.log(1 - action.pow(2) + epsilon)
        # log_prob2 = torch.distributions.Normal(mean,clamped_sigma).log_prob(action).sum(-1).unsqueeze(-1)
        # entropy = torch.distributions.Normal(mean,clamped_sigma).entropy().sum(-1).unsqueeze(-1)

        # dist = torch.distributions.Normal(mean, F.softplus(self.sigma))
        # if action is None:
        #     action = dist.sample()
        # log_prob = dist.log_prob(action).sum(-1).unsqueeze(-1)
        # entropy = dist.entropy().sum(-1).unsqueeze(-1)
        return {'action': action,
                'log_pi_a': log_prob,
                'entropy': entropy,
                'mean': mean,
                'predicted_action':predicted_action}

class Critic(nn.Module):

    def __init__(self):
        super(Critic, self).__init__()

        # self.input = nn.Linear(in_features=7, out_features=32)
        # self.hidden1 = nn.Linear(in_features=32,out_features=48)
        # self.hidden2 = nn.Linear(in_features=48, out_features=32)
        # self.hidden3 = nn.Linear(in_features=32, out_features=16)
        # self.hidden4 = nn.Linear(in_features=16, out_features=8)

        self.input = nn.Linear(in_features=7, out_features=32)
        self.hidden1 = nn.Linear(in_features=32,out_features=16)
        self.hidden2 = nn.Linear(in_features=16, out_features=8)


        self.out = nn.Linear(in_features=8, out_features=1)
        
        for m in self.modules():
            if isinstance(m, nn.Linear):
                m.weight = torch.nn.init.ones_(m.weight)
                #  orthogonal_
            
    def forward(self, obs):
        obs = obs.clone().detach()
        h1 = self.input(obs)
        h1_act = torch.tanh(h1)

        h2 = self.hidden1(h1)
        h2_act = torch.tanh(h2)

        h3 = self.hidden2(h2_act)
        h3_act = torch.tanh(h3)

        # h4 = self.hidden3(h3_act)
        # h4_act = torch.relu(h4)

        # h5 = self.hidden4(h4_act)
        # h5_act = torch.relu(h5)

        # logits = self.fc_action(h3)
        v = self.out(h3_act)
        # v1 = v.unsqueeze(-1)
        # dist = torch.distributions.Categorical(logits=logits)
        # if action is None:
        #     action = dist.sample()
        # log_prob = dist.log_prob(action).unsqueeze(-1)
        # entropy = dist.entropy().unsqueeze(-1)
        return {'value': v}

    
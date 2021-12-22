import numpy as np
from Country import Country
import torch

class AICountry:

    __ai_country_instance = None

    @staticmethod
    def get_instance():
        if AICountry.__ai_country_instance == None:
            AICountry()
        return AICountry.__ai_country_instance

    def __init__(self):

        if AICountry.__ai_country_instance != None:
            raise Exception("Market instance already exists, USE get_instance method")
        else:
            AICountry.__ai_country_instance = self

        # countryObject =  GameObject.Find("CountryD_AI");
        self.inflationRate = 0.0 # float
        self.unemploymentRate = 0.0 # float
        self.povertyRate = 0.0 # float
        self.minimumWage = 0.0 # float
        self.productPrice = 0.0 # float
        self.averageSkill = 0.0 # float
        self.averageSalary = 0.0 # float
        self.numberOfBusinesses = 0.0 # float
        self.numOfJobPositions = 0.0 # float

        # Previous stats
        self.prevPovertyRate = 0.0 # float
        self.prevNumJobPositions = 0.0 # float

        # Country to make policies for 
        # self.countryObject # GameObject
        # self.country # MWCountry
        self.country = Country.get_instance()

        # Magic Numbers
        self.max_wage = 90
        self.min_wage = 2
        self.weight_lb = 2
        self.weight_mb = 1.5
        self.weight_sb = 1
        self.wage_threshold = 50
        self.negative_reward = -1 
    
    def collect_observations(self, state_values):
    
        self.inflationRate = self.country.market.inflationRate # Inflation remains static in our simulations
        self.productPrice = 30 * self.country.market.productPrice
        self.unemploymentRate = self.country.unemploymentRate
        self.povertyRate = self.country.povertyRate
        self.minimumWage = self.country.minimumWage
        self.averageSkill = self.country.averageSkillLevel
        self.averageSalary = self.country.averageIncome
        self.numberOfBusinesses = self.country.numOfLargeBusinesses + self.country.numOfMediumBusinesses + self.country.numOfSmallBusinesses
        self.numOfJobPositions = self.country.totalExecutivePos + self.country.totalSeniorPos + self.country.totalJuniorPos

        state_values.append(self.unemploymentRate)
        state_values.append(self.povertyRate)
        state_values.append(self.minimumWage)
        state_values.append(self.averageSalary - self.productPrice) # NEW ADDITION

    def __on_action_received(self,vectorAction):

        if vectorAction[0] == 0: # No change to MW
            # Do nothing - Semantically leaving this IF Statement
            pass

        elif vectorAction[0] == 1: # Increase MW based on inflation
            self.country.minimumWage += self.country.minimumWage * self.inflationRate

        elif vectorAction[0] == 2: # Dramatic Increase in MW 5%        
            self.country.minimumWage += self.country.minimumWage * 0.05

        if self.country.minimumWage < self.min_wage:
            self.country.minimumWage = self.min_wage

        # This is case it reaches the maximum possible MW for this simulations settings
        if self.country.minimumWage > self.max_wage:
            self.country.minimumWage = self.max_wage

    def give_rewards(self):
        # 3. Companies
        # r1 = self.weight_lb * np.log10(self.country.numOfLargeBusinesses/self.minimumWage + 1)
        # r2 = self.weight_mb * np.log10(self.country.numOfMediumBusinesses / self.minimumWage + 1)
        # r3 = self.weight_sb * np.log10(self.country.numOfSmallBusinesses / self.minimumWage + 1)
        # r4 = 0.0

        r1 = 1/self.country.povertyRate
        r2 = 1/self.country.unemploymentRate

        # if self.minimumWage > self.wage_threshold:
        #     r4 = self.negative_reward

        # return torch.tensor([r1 + r2 + r3 + r4])
        return torch.tensor([r1 + r2])

    def num_actions_available(self):
        return 3
    
    def reset(self):
        pass

    def get_state(self):
        state_values = []
        self.collect_observations(state_values)
        return torch.tensor(state_values, dtype=torch.float32)
        
    def take_action(self, action):
        self.__on_action_received(action)
from numpy.core.arrayprint import _void_scalar_repr
from Country import Country
from AICountry import AICountry
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from AI_model.AI_DQN import DQN, EpsilonGreedyStrategy, Agent, ReplayMemory, Experience, extract_tensors, QValues
import configparser

class Market:

    __market_instance = None
    
    @staticmethod
    def get_instance():
        if Market.__market_instance == None:
            Market()
        return Market.__market_instance

    def __init__(self) -> None:
        
        if Market.__market_instance !=None:
            raise Exception("Market instance already exists, USE get_instance method")
        else:
            Market.__market_instance = self

        self.all_data = list()
        self.out_file_name = None
        self.day = None
        self.month = None
        self.year = None

        self.parser = configparser.ConfigParser()
        self.parser.read("config_file.txt")

        self.unregulatedScenario = None
        self.adjustedScenario = None
        self.dramaticScenario = None
        self.aiScenario = None
        
        # SET LATER
        self.marketValueYear = 0 # change name
        self.amountOfNewCitizens = 0
        
        self.inflationRate = None

        # SET LATER
        
        self.productPrice = float(self.parser.get("market","product_price")) # Current price of product adjusted to inflation
        self.initialProductPrice = float(self.parser.get("market","product_price"))

        self.testingCountryObject = None # GameObject
        self.testingCountry = None # MWCountry

        self.citizensToRemove = list() # List<MWEmployee>

        self.run = None # int
        # self.slowDown = None # int - Slows down simulation for demo purposes (remove when training)
        self.training = False # bool - Flag for AI training - CHANGED PROGRAMATICALLY

        # private float[] inflations = { 0.0025f, 0.005f, 0.0075f, 0.01f };
        # self.inflationIdx = 0;

        # =========== AI Network ==============
        self.batch_size = 0
        self.gamma = 0.0
        self.eps_start = 0
        self.eps_end = 0.0
        self.eps_decay = 0.0
        self.target_update = 0
        self.memory_size = 0
        self.lr = 0.0
        self.num_episodes = 0 # run for more episodes for better results

        self.device = None
        self.saved_model = None

        # Magic
        self.num_citizens_limit = 100
        self.citizen_max_age = 100

    def load_model(self):
        self.saved_model = torch.load("model//trained_model.pt")
        
    def Start(self):
    
        self.day = self.month = self.year = 0
        self.initialProductPrice = self.productPrice
        # self.slowDown = 0
        
        self.testingCountry = Country.get_instance()
        self.em = AICountry.get_instance()        
        
        # Apply user settings from menu preferences
        self.ApplyUserSettings(float(self.parser.get("market","inflation")), 
        int(self.parser.get("market","citizens")), int(self.parser.get("market","small_business")),  
        int(self.parser.get("market","medium_business")), int(self.parser.get("market","large_business")))
        
        self.testingCountry.EstablishCountry()
        self.marketValueYear = 0
        self.run = 0
        self.initialize_network()

        if bool(int(self.parser.get("scenario","unregulated"))):
            self.testingCountry.policyCode = 0
            self.out_file_name = self.parser.get("file","unregulated_file")

        if bool(int(self.parser.get("scenario","adjusted"))):
            self.testingCountry.policyCode = 1
            self.out_file_name = self.parser.get("file","adjusted_file")

        if bool(int(self.parser.get("scenario","dramatic"))):
            self.testingCountry.policyCode = 2
            self.out_file_name = self.parser.get("file","dramatic_file")

        if bool(int(self.parser.get("scenario","ai_scenario"))):
            self.testingCountry.policyCode = 3
            self.out_file_name = self.parser.get("file","ai_scenario_file")
            self.aiScenario = True
    
    def ApplyUserSettings(self, inflation, num_of_citizens, small_business, medium_business, large_business):
    
        self.inflationRate = inflation
        self.testingCountry.initialNumOfCitizens = num_of_citizens
        self.testingCountry.initial_num_small_business =  small_business
        self.testingCountry.initialNumMB = medium_business
        self.testingCountry.initialNumLB = large_business

    def ExitToMenu(self):
        self.ResetMarket()        
    
    def step(self, action):
        # Step 1 - Change minimum wage
        self.testingCountry.minimumWage = action

        # Step 2 - Change inflation rate : fixed
        
        # Step 3 - run market step
        self.run_market()
        
        return self.get_state()

    def get_state(self):
        return self.testingCountry.get_current_state_reward()

    def FixedUpdate(self):
        
        if self.year <= 3000:
            
            print("year - ", self.year , ", month - ", self.month%12)
            # Executed only when training
            if self.aiScenario and self.training:                    
                self.Train_network()                
            else:                    
                self.run_market()
        else:            
            # Give rewards and reset the market
            if self.aiScenario and self.training:            
                self.run = self.run + 1 
                self.ResetMarket()
            print("<========== Ending Simulation =========>")        
    

    def ResetMarket(self):
    
        self.day = self.month = self.year = 0
        self.productPrice = self.initialProductPrice 
        self.amountOfNewCitizens = 0
        self.testingCountry.ResetCountry()
        self.testingCountry.EstablishCountry()
    
    def run_market(self):
    
        self.month = self.month + 1 # Instead of day to speed up simulation 12x

        countryCompanies = self.testingCountry.companies # Dictionary<int, MWCompany> 
        countryCitizens = self.testingCountry.citizens # Dictionary<int, MWEmployee> 
        speedup = 30.415  # 365/12 is the speedup

        # 1. Companies must pay employees and employees must give value back to the companies        
        for _,V in countryCompanies.items():
        
            company = V
            # MWEmployee
            for employee in company.companyEmployees:            
                # Paying employees
                employee.accountBalance += employee.salary
                company.accountBalance -= employee.salary

                # Giving value back to company
                company.accountBalance += employee.skillLevel
                company.yearIncome += (employee.skillLevel - employee.salary)        

        # 2. People must buy products YO
        # Employee Iteration  
        for _,V in countryCitizens.items():        
            citizen = V # MWEmployee
            citizen.BuyProducts(speedup)
        
        # 3. Check if year to be increased. Yearly 
        if self.month % 12 == 0:
            self.year = self.year + 1 

            # 4. Every year - Add new citizens
            self.testingCountry.add_new_citizens(self.amountOfNewCitizens)
            if self.amountOfNewCitizens < self.num_citizens_limit:
                self.amountOfNewCitizens += 1

            totalOpenPositions = 0
            totalUnemployed = self.testingCountry.totalUnemployed

            # 5. Every year - Company Iteration
            for _,V in countryCompanies.items():            
                company = V # MWCompany 
                company.EvaluateAndReset() # Step 1. Evaluate year and reset
                totalOpenPositions += company.OpenJobPositions() # Step 2. Open new job positions based on balance and company size
            
            # 6. Every year - Employee Iteration
            for _,V in countryCitizens.items():
                citizen = V # MWEmployee 
                citizen.EvaluateAndGrow()
                if citizen.hasCompany or citizen.age > self.citizen_max_age:
                    self.citizensToRemove.append(citizen)

            # 7. Every year - Removing citizens that have created their own companies or HAVE DIED
            # MWEmployee
            for citizen in self.citizensToRemove:
                if not(citizen.hasCompany):
                    citizen.element_citizens()

                countryCitizens.pop(citizen.citizenID)
            
            self.citizensToRemove = list()

            # 8. Every year - Upadating Minimum Wage CHANGE THIS TO FIT ALL SCENARIOS
            # if self.aiScenario and not(self.training):
            #     self.__request_decision()
            
            # else:
            #     self.testingCountry.UpdateMinimumWage()

            # 9. Every year - Updating product prices
            self.__update_product_prices()

            # 10. Every year - Calculate Stats
            countryStatsOutput = self.testingCountry.calculate_statistics() # string 
            self.marketValueYear = 0            
                        
            # SETTING EXCEL VALUES
            values_dict = dict()
            values_dict["year"] = self.year
            values_dict["Average Salary"] = self.testingCountry.averageIncome
            values_dict["productPrice"] = self.productPrice
            values_dict["Poverty"] = self.testingCountry.povertyRate
            values_dict["Unemployment"] = self.testingCountry.unemploymentRate
            values_dict["Small Company"] = self.testingCountry.numOfSmallBusinesses
            values_dict["Medium Company"] = self.testingCountry.numOfMediumBusinesses
            values_dict["Large Company"] = self.testingCountry.numOfLargeBusinesses
            values_dict["Junior"] = self.testingCountry.totalJuniorPos
            values_dict["Senior"] = self.testingCountry.totalSeniorPos
            values_dict["Executive"] = self.testingCountry.totalExecutivePos
            values_dict["Minimum Wage"] = self.testingCountry.minimumWage

            self.all_data.append(values_dict)

            print("============ YEAR - " + str(self.year) + "=============")


    def __update_product_prices(self):
        self.productPrice = round((self.productPrice + self.productPrice * self.inflationRate), 3)
        
    def __request_decision(self):
        curr_state = self.em.get_state()
        action = self.saved_model(curr_state).argmax()
        self.em.take_action(torch.tensor([action]))

    def initialize_network(self):
        self.batch_size = 20
        self.gamma = 0.999
        self.eps_start = 1
        self.eps_end = 0.01
        self.eps_decay = 0.001
        self.target_update = 10
        self.memory_size = 10000
        self.lr = 0.001
        self.num_episodes = 100 # run for more episodes for better results
        self.episode = 0
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.strategy = EpsilonGreedyStrategy(self.eps_start, self.eps_end, self.eps_decay)
        self.agent = Agent(self.strategy, self.em.num_actions_available(), self.device)
        self.memory = ReplayMemory(self.memory_size)

        self.policy_net = DQN()
        self.target_net = DQN()
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.optimizer = optim.Adam(params=self.policy_net.parameters(), lr=self.lr)
        

    def Train_network(self):
        # ======================= Training Logic - START ==============================        

        # episode_durations = []
        # for episode in range(self.num_episodes):
            # self.em.reset()

        state = self.em.get_state()
        # state = state.unsqueeze(dim=0)
        action = self.agent.select_action(state.unsqueeze(dim=0), self.policy_net)
                
        # Change minimum wage
        self.em.take_action(action)
        reward = self.em.give_rewards()

        # Run Market - this should return states
        self.run_market()

        # Get next state
        next_state = self.em.get_state()

        self.memory.push(Experience(state, action, next_state, reward))
        state = next_state

        if self.memory.can_provide_sample(self.batch_size):
            experiences = self.memory.sample(self.batch_size)
            states, actions, rewards, next_states = extract_tensors(experiences)
                    
            current_q_values = QValues.get_current(self.policy_net, states, actions)
            next_q_values = QValues.get_next(self.target_net, next_states)
            target_q_values = (next_q_values * self.gamma) + rewards
           
            loss = F.mse_loss(current_q_values.float(), target_q_values.float()) #.unsqueeze(1)

            # loss = F.cross_entropy(current_q_values.float(), target_q_values.float()) #.unsqueeze(1)

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
                
                # Check this logic
                # if em.done:
                #     episode_durations.append(timestep)
                #     plot(episode_durations, 100)
                #     break

        if self.episode % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
                
        self.episode = self.episode + 1
        # em.close()

        # ======================= Training Logic - END ================================
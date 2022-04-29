import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
# from AI_model.AI_DQN import DQN, EpsilonGreedyStrategy, Agent, ReplayMemory, Experience, extract_tensors, QValues

from django.db import models
# from .country import Country
from ..utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser

class Market(models.Model):
    
    class Meta:
        db_table = "market"

    # Magic
    NUM_CITIZENS_LIMIT = 100
    CITIZEN_MAX_AGE = 100
    INITIAL_PRODUCT_PRICE = config_parser.get("market","product_price")
    
    SENIOR_SALARY_PERCENTAGE = float(config_parser.get("market","senior_salary_percent"))
    EXEC_SALARY_PERCENTAGE = float(config_parser.get("market","exec_salary_percent"))

    MINIMUM_COMPANY_BALANCE = float(config_parser.get("market","min_company_balance"))

    REQUIRED_JUN_JOB_PERCENT = float(config_parser.get("market","required_jun_job_percent"))
    REQUIRED_SEN_JOB_PERCENT = float(config_parser.get("market","required_sen_job_percent"))
    REQUIRED_EXEC_JOB_PERCENT = float(config_parser.get("market","required_exec_job_percent"))

    SMALL_CMP_INIT_BALANCE = float(config_parser.get("market","small_company_init_balance"))
    MEDIUM_CMP_INIT_BALANCE = float(config_parser.get("market","medium_company_init_balance"))
    LARGE_CMP_INIT_BALANCE = float(config_parser.get("market","large_company_init_balance"))

    COMPANY_AGE_WEIGHTAGE =  float(config_parser.get("market","cmp_age_weightage"))
    COMPANY_ACCT_BALANCE_WEIGHTAGE = float(config_parser.get("market","cmp_acct_balance_weightage"))
    COMPANY_HIRING_BUDGET_PERCENT = float(config_parser.get("company","hiring_budget_percent"))

    STARTUP_ACCT_WEIGHTAGE = float(config_parser.get("startup","acct_balance_weightage"))
    STARTUP_AGE_WEIGHTAGE = float(config_parser.get("startup","age_weightage"))
    STARTUP_SKILLSET_WEIGHTAGE = float(config_parser.get("startup","skill_set_weightage"))
    START_MONEY_THERSHOLD_PERCENT = float(config_parser.get("startup","startup_money_percent"))
    STARTUP_LOAN_PERCENT = float(config_parser.get("startup","bank_loan_budget"))
    STARTUP_SKILL_IMPROVEMENT = float(config_parser.get("startup","startup_skill"))

    THRESHOLD_INFLATION = float(config_parser.get("inflation","threshold_inflation"))
    THRESHOLD_QUANTITY_INCREASE = float(config_parser.get("inflation","threshold_quantity_increase"))
    MIN_BALANCE_INFLATION = float(config_parser.get("inflation","bank_min_balance_inflation"))
    BANK_LOAN_INFLATION = float(config_parser.get("inflation","bank_threshold_loan_inflation"))
        
    
    SMALL_COMPANY_TYPE=0
    MEDIUM_COMPANY_TYPE=0
    LARGE_COMPANY_TYPE=0

    all_data = list()
    out_file_name = None
    month = models.IntegerField(default=0)
    year = models.IntegerField(default=0)

    unregulatedScenario = None
    adjustedScenario = None
    dramaticScenario = None
    aiScenario = None
    
    # SET LATER
    market_value_year = models.FloatField()
    amount_of_new_citizens = models.IntegerField(default=0)    
    inflation_rate = models.FloatField(default=config_parser.get("market","inflation"))

    # SET LATER
    product_price = models.FloatField(default=INITIAL_PRODUCT_PRICE)
        
    training = False # bool - Flag for AI training - CHANGED PROGRAMATICALLY

    # =========== AI Network ==============
    batch_size = 0
    gamma = 0.0
    eps_start = 0
    eps_end = 0.0
    eps_decay = 0.0
    target_update = 0
    memory_size = 0
    lr = 0.0
    num_episodes = 0 # run for more episodes for better results

    device = None
    saved_model = None

    def load_model(self):
        self.saved_model = torch.load("model//trained_model.pt")
        
    # def ExitToMenu(self):
    #     self.ResetMarket()

    def get_state_and_reward(self):
        return self.testingCountry.get_current_state_reward()

    # def FixedUpdate(self):
        
    #     if self.year <= 3000:
            
    #         print("year - ", self.year , ", month - ", self.month%12)
    #         # Executed only when training
    #         if self.aiScenario and self.training:                    
    #             self.Train_network()                
    #         else:                    
    #             self.run_market()
    #     else:            
    #         # Give rewards and reset the market
    #         if self.aiScenario and self.training:            
    #             self.run = self.run + 1 
    #             self.ResetMarket()
    #         print("<========== Ending Simulation =========>")        
    

    # def ResetMarket(self):
    
    #     self.month = self.year = 0
    #     self.product_price = Market.INITIAL_PRODUCT_PRICE
    #     self.amount_of_new_citizens = 0
    #     self.testingCountry.ResetCountry()
    #     self.testingCountry.EstablishCountry()
    
    # def run_market(self):
    
    #     self.month = self.month + 1 # Instead of day to speed up simulation 12x

    #     country_companies = self.testingCountry.companies # Dictionary<int, MWCompany> 
    #     country_workers = self.testingCountry.workers # Dictionary<int, MWEmployee> 
    #     speedup = 30.415  # 365/12 is the speedup

    #     # 1. Companies must pay employees and employees must give value back to the companies        
    #     for _,V in country_companies.items():
        
    #         company = V
    #         # MWEmployee
    #         for employee in company.companyEmployees:            
    #             # Paying employees
    #             employee.worker_account_balance += employee.salary
    #             company.company_account_balance -= employee.salary

    #             # Giving value back to company
    #             company.company_account_balance += employee.skill_level
    #             company.year_income += (employee.skill_level - employee.salary)        

    #     # 2. People must buy products YO
    #     # Employee Iteration  
    #     for _,V in country_workers.items():        
    #         citizen = V # MWEmployee
    #         citizen.buy_products(speedup)
        
    #     # 3. Check if year to be increased. Yearly 
    #     if self.month % 12 == 0:
    #         self.year = self.year + 1 

    #         # 4. Every year - Add new citizens
    #         self.testingCountry.add_new_citizens(self.amount_of_new_citizens)
    #         if self.amount_of_new_citizens < Market.NUM_CITIZENS_LIMIT:
    #             self.amount_of_new_citizens += 1

    #         totalOpenPositions = 0
    #         totalUnemployed = self.testingCountry.total_unemployed

    #         # 5. Every year - Company Iteration
    #         for _,V in country_companies.items():            
    #             company = V # MWCompany 
    #             company.evaluate_company_step() # Step 1. Evaluate year and reset
    #             totalOpenPositions += company.open_job_positions() # Step 2. Open new job positions based on balance and company size
            
    #         citizensToRemove = list()
    #         # 6. Every year - Employee Iteration
    #         for _,V in country_workers.items():
    #             citizen = V # MWEmployee 
    #             citizen.evaluate_worker_step()
    #             if citizen.has_company or citizen.age > Market.CITIZEN_MAX_AGE:
    #                 citizensToRemove.append(citizen)

    #         # 7. Every year - Removing citizens that have created their own companies or HAVE DIED
    #         for citizen in citizensToRemove:
    #             if not(citizen.has_company):
    #                 citizen.remove_worker()

    #             country_workers.pop(citizen.citizenID)        

    #         # 9. Every year - Updating product prices
    #         self.update_product_prices()

    #         # 10. Every year - Calculate Stats
    #         countryStatsOutput = self.testingCountry.calculate_statistics() # string 
    #         self.market_value_year = 0            
                        
    #         # SETTING EXCEL VALUES
    #         values_dict = dict()
    #         values_dict["year"] = self.year
    #         values_dict["Average Salary"] = self.testingCountry.average_income
    #         values_dict["productPrice"] = self.product_price
    #         values_dict["Poverty"] = self.testingCountry.poverty_rate
    #         values_dict["Unemployment"] = self.testingCountry.unemployment_rate
    #         values_dict["Small Company"] = self.testingCountry.num_small_companies
    #         values_dict["Medium Company"] = self.testingCountry.num_medium_company
    #         values_dict["Large Company"] = self.testingCountry.num_large_company
    #         values_dict["Junior"] = self.testingCountry.total_jun_jobs
    #         values_dict["Senior"] = self.testingCountry.total_senior_jobs
    #         values_dict["Executive"] = self.testingCountry.total_executive_jobs
    #         values_dict["Minimum Wage"] = self.testingCountry.minimum_wage

    #         self.all_data.append(values_dict)

    #         print("============ YEAR - " + str(self.year) + "=============")


    def update_product_prices(self):
        self.product_price = round((self.product_price + self.product_price * self.inflation_rate), 3)
        
    def __request_decision(self):
        curr_state = self.em.get_state()
        action = self.saved_model(curr_state).argmax()
        self.em.take_action(torch.tensor([action]))

    # def initialize_network(self):
    #     self.batch_size = 20
    #     self.gamma = 0.999
    #     self.eps_start = 1
    #     self.eps_end = 0.01
    #     self.eps_decay = 0.001
    #     self.target_update = 10
    #     self.memory_size = 10000
    #     self.lr = 0.001
    #     self.num_episodes = 100 # run for more episodes for better results
    #     self.episode = 0
        
    #     self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #     self.strategy = EpsilonGreedyStrategy(self.eps_start, self.eps_end, self.eps_decay)
    #     self.agent = Agent(self.strategy, self.em.num_actions_available(), self.device)
    #     self.memory = ReplayMemory(self.memory_size)

    #     self.policy_net = DQN()
    #     self.target_net = DQN()
    #     self.target_net.load_state_dict(self.policy_net.state_dict())
    #     self.target_net.eval()
    #     self.optimizer = optim.Adam(params=self.policy_net.parameters(), lr=self.lr)
        

    # def Train_network(self):
    #     # ======================= Training Logic - START ==============================        

    #     # episode_durations = []
    #     # for episode in range(self.num_episodes):
    #         # self.em.reset()

    #     state = self.em.get_state()
    #     # state = state.unsqueeze(dim=0)
    #     action = self.agent.select_action(state.unsqueeze(dim=0), self.policy_net)
                
    #     # Change minimum wage
    #     self.em.take_action(action)
    #     reward = self.em.give_rewards()

    #     # Run Market - this should return states
    #     self.run_market()

    #     # Get next state
    #     next_state = self.em.get_state()

    #     self.memory.push(Experience(state, action, next_state, reward))
    #     state = next_state

    #     if self.memory.can_provide_sample(self.batch_size):
    #         experiences = self.memory.sample(self.batch_size)
    #         states, actions, rewards, next_states = extract_tensors(experiences)
                    
    #         current_q_values = QValues.get_current(self.policy_net, states, actions)
    #         next_q_values = QValues.get_next(self.target_net, next_states)
    #         target_q_values = (next_q_values * self.gamma) + rewards
           
    #         loss = F.mse_loss(current_q_values.float(), target_q_values.float()) #.unsqueeze(1)

    #         # loss = F.cross_entropy(current_q_values.float(), target_q_values.float()) #.unsqueeze(1)

    #         self.optimizer.zero_grad()
    #         loss.backward()
    #         self.optimizer.step()
                
    #             # Check this logic
    #             # if em.done:
    #             #     episode_durations.append(timestep)
    #             #     plot(episode_durations, 100)
    #             #     break

    #     if self.episode % self.target_update == 0:
    #         self.target_net.load_state_dict(self.policy_net.state_dict())
                
    #     self.episode = self.episode + 1
    #     # em.close()

    #     # ======================= Training Logic - END ================================
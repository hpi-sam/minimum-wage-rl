import torch
from Government import Government
from Market import Market
import pandas  as pd
import configparser


# ============== 1. Extract Configured Params - Start ==============

parser = configparser.ConfigParser()
parser.read("config_file.txt")

ai_case = bool(int(parser.get("scenario","ai_scenario")))
ai_training = bool(int(parser.get("scenario","training")))

training_file = parser.get("file","training_file")
root_folder = parser.get("file","root_folder")

training_steps = int(parser.get("meta","training_steps"))
market_steps = int(parser.get("meta","market_steps"))

# ============== Extract Configured Params - End ==============



# ===================== SAVE data - START ====================
def save_data(filename):
    list_of_data = market.all_data

    list_of_values = list()
    column_list = list()

    for each_data in list_of_data:
        column_list = list(each_data.keys())
        list_of_values.append(each_data.values())

    my_df = pd.DataFrame(columns=column_list, data=list_of_data)

    my_df.to_excel(filename)
# ===================== SAVE data - END ====================

# Making singleton instance
market = Market.get_instance()

# Initialize:
# Create singleton instance of Country
# Create Company objects (Initial set of companies)
# Create Employee objects (Equal to number of citizens)
# For Web app this will during server start.
market.Start()

# Create instance based on Government implementation (AI, Data collection etc.)
# For Web app this will during server start - based on configuration
government = Government()

# Start playing/ Start training
# For Web app  - this will be a call from front end
government.execute_action()

# save trained AI model here

# save data here
save_data(root_folder+ "\\" + training_file)


# if ai_training and ai_case:
#     print("here=====================")
#     market.training = True

#     for _ in range(training_steps):
#         market.FixedUpdate()

#     save_data(root_folder+ "\\" + training_file)

#     # =========== Saving model =============
#     print("Saving model ... ")
#     output = open("model\\trained_model.pt", mode="wb")
#     torch.save(market.policy_net, output)
#     output.close() 
    
#     market.training = False
#     ai_training = False
   

# if not(ai_training) and ai_case:
#     market.load_model()
#     market.all_data = list()
#     market.ResetMarket()

# for i in range(market_steps):
#     market.FixedUpdate()

# save_data(root_folder + "\\" + market.out_file_name)


print("================================== done ==================================")
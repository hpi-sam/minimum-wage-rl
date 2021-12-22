import torch
from Market import Market
import pandas  as pd
import configparser

market = Market.get_instance()

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

parser = configparser.ConfigParser()
parser.read("config_file.txt")

print(parser.get("scenario","ai_scenario"))

ai_case = bool(int(parser.get("scenario","ai_scenario")))
ai_training = bool(int(parser.get("scenario","training")))


training_file = parser.get("file","training_file")
root_folder = parser.get("file","root_folder")

training_steps = int(parser.get("meta","training_steps"))
market_steps = int(parser.get("meta","market_steps"))

market.Start()

if ai_training and ai_case:
    print("here=====================")
    market.training = True

    for _ in range(training_steps):
        market.FixedUpdate()

    save_data(root_folder+ "\\" + training_file)

    # =========== Saving model =============
    print("Saving model ... ")
    output = open("model\\trained_model.pt", mode="wb")
    torch.save(market.policy_net, output)
    output.close() 
    
    market.training = False
    ai_training = False
    

# else:

if not(ai_training) and ai_case:
    market.load_model()
    market.all_data = list()
    market.ResetMarket()

for i in range(market_steps):
    market.FixedUpdate()

save_data(root_folder + "\\" + market.out_file_name)


print("================================== done ==================================")
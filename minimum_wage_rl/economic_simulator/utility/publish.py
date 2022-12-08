# from ..models import *
import pandas as pd
from ..models.metrics import Metric
from ..models.country import Country
from ..models.game import Game
from django.db.models import Max

from economic_simulator.models import game

# col_values=["Year", "Minimum wage", "Unemp Rate", "Poverty Rate", 
#             "Population", "Inflation", "Product Price", "Quantity",
#             "Bank Balance", "Small Comp", "Medium Comp", 
#             "Large Comp", "Filled Jun", "Filled Sen", "Filled Exec",
#             "Avg Jun Skill", "Avg Sen Skill", "Avg Exec Skill",
#             "Unemp Jun", "Unemp Sen", "Unemp Exec", 
#             "Avg Jun", "Avg Sen", "Avg Exec", "Avg Sal",         
#             "Inflation Rate"]

col_values = ["Year", "Minimum Wage", "Unemp Rate", "Poverty Rate", "Inflation", "Product Price", 
"Quantity", "Bank Balance", "Population", "Oil Cost", "Company Revenue",  "Cost of Operation", "Junior Employment", "Senior Unemployment", "Executive Unemployment",
"Small Comp", "Medium Comp", "Large Comp", "Money Circulation", "Game Level"]            

# col_values = ["Year", "Minimum Wage", "Unemp Rate", "Poverty Rate", 
# "Inflation", "Product Price", 
# "Quantity", "Bank Balance", "Population", 
# "Junior Unemployment", "Senior Unemployment", 
# "Executive Unemployment",
# "Small Comp", "Medium Comp", "Large Comp"]


def get_metric_data(data_map, metric):

    for i, col_val in enumerate(col_values):
        data_map[col_val].append(metric[i])

    # data_map["Year"].append(metric.year)
    # data_map["Small Comp"].append(metric.num_small_companies)
    # data_map["Medium Comp"].append(metric.num_medium_companies)
    # data_map["Large Comp"].append(metric.num_large_companies)
    # data_map["Filled Jun"].append(metric.total_filled_jun_pos)
    # data_map["Filled Sen"].append(metric.total_filled_sen_pos)
    # data_map["Filled Exec"].append(metric.total_filled_exec_pos)
    # data_map["Unemp Jun"].append(metric.unemployed_jun_pos)
    # data_map["Unemp Sen"].append(metric.unemployed_sen_pos)
    # data_map["Unemp Exec"].append(metric.unemployed_exec_pos)
    # data_map["Avg Jun"].append(metric.average_jun_sal)
    # data_map["Avg Sen"].append(metric.average_sen_sal)
    # data_map["Avg Exec"].append(metric.average_exec_sal)
    # data_map["Avg Sal"].append(metric.average_sal)
    # data_map["Unemp Rate"].append(metric.unemployment_rate)
    # data_map["Poverty Rate"].append(metric.poverty_rate)
    # data_map["Population"].append(metric.population)
    # data_map["Minimum wage"].append(metric.minimum_wage)
    # data_map["Inflation"].append(metric.inflation)
    # data_map["Inflation Rate"].append(metric.inflation_rate)
    # data_map["Bank Balance"].append(metric.bank_account_balance)
    # data_map["Product Price"].append(metric.product_price)
    # data_map["Quantity"].append(metric.quantity)


def export_from_game_metric(game_num, game_metric_list):
    
    df_list = []
    
    for game_episode in game_metric_list:
        data_map = dict()

        for each_col in col_values:
            data_map[each_col] = list()
        
        for each_metric in game_episode.metric_list:
            metric_list = []


            get_metric_data(data_map, each_metric)
        
        new_df = pd.DataFrame(data_map)

        df_list.append(new_df)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('game_' + str(game_num)+ '.xlsx')

    # Write each dataframe to a different worksheet.
    for index,each_df in enumerate(df_list):
        name = "episode" + str(index + 1)
        each_df.to_excel(writer, sheet_name=name)


    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()

def export_to_excel(user):
    game_num = get_latest_game_number(user)
    print(game_num)
    latest_game = Game.objects.filter(game_number=game_num)[0]

    country_list = list(Country.objects.filter(player=user, game=latest_game))
    df_list = list()

    for each_country in country_list:
        metrics_list = list(Metric.objects.filter(country_of_residence=each_country))
        
        data_map = dict()

        for each_col in col_values:
            data_map[each_col] = list()

        for each_metric in metrics_list:
            metric_list = get_metric_values(each_metric)
            get_metric_data(data_map, metric_list)

        new_df = pd.DataFrame(data_map)

        df_list.append(new_df)
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter("metric_game_" + str(game_num) + ".xlsx")

    # Write each dataframe to a different worksheet.
    for index,each_df in enumerate(df_list):
        name = "game" + str(index + 1)
        each_df.to_excel(writer, sheet_name=name)


    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
# col_values=["Year", "Minimum wage", "Unemp Rate", "Poverty Rate", 
#             "Population", "Inflation", "Product Price", "Quantity",
#             "Bank Balance", "Small Comp", "Medium Comp", 
#             "Large Comp", "Filled Jun", "Filled Sen", "Filled Exec", 
#             "Unemp Jun", "Unemp Sen", "Unemp Exec", 
#             "Avg Jun", "Avg Sen", "Avg Exec", "Avg Sal",         
#             "Inflation Rate"]

def get_metric_values(each_metric):
    metric_list = []
    metric_list.append(each_metric.year)
    metric_list.append(each_metric.minimum_wage)    
    metric_list.append(each_metric.unemployment_rate)
    metric_list.append(each_metric.poverty_rate)
    metric_list.append(each_metric.population)
    metric_list.append(each_metric.inflation)
    metric_list.append(each_metric.product_price)
    metric_list.append(each_metric.quantity)
    metric_list.append(each_metric.bank_account_balance)
    metric_list.append(each_metric.num_small_companies)
    metric_list.append(each_metric.num_medium_companies)
    metric_list.append(each_metric.num_large_companies)
    metric_list.append(each_metric.total_filled_jun_pos)
    metric_list.append(each_metric.total_filled_sen_pos)
    metric_list.append(each_metric.total_filled_exec_pos)
    metric_list.append(each_metric.avg_jun_skill_level)
    metric_list.append(each_metric.avg_sen_skill_level)
    metric_list.append(each_metric.avg_exec_skill_level)
    metric_list.append(each_metric.unemployed_jun_pos)
    metric_list.append(each_metric.unemployed_sen_pos)
    metric_list.append(each_metric.unemployed_exec_pos)
    metric_list.append(each_metric.average_jun_sal)
    metric_list.append(each_metric.average_sen_sal)
    metric_list.append(each_metric.average_exec_sal)
    metric_list.append(each_metric.average_sal)
    metric_list.append(each_metric.inflation_rate)


    return metric_list


def get_latest_game_number(user):
    max_game_query = Game.objects.filter(player=user).aggregate(max_game_number=Max("game_number"))
    return max_game_query["max_game_number"]
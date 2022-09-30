# from ..models import *
import pandas as pd

# col_values=["Year","Small Comp", "Medium Comp", "Large Comp", "Filled Jun",
#         "Filled Sen", "Filled Exec", "Unemp Jun", "Unemp Sen", "Unemp Exec", 
#         "Avg Jun", "Avg Sen", "Avg Exec", "Avg Sal", "Unemp Rate", "Poverty Rate", "Population", "Minimum wage",
#         "Inflation", "Inflation Rate", "Bank Balance", "Product Price", "Quantity"]

col_values = ["Year", "Minimum Wage", "Unemp Rate", "Poverty Rate", "Inflation", "Product Price", 
"Quantity", "Bank Balance", "Population", "Junior Employment", "Senior Unemployment", "Executive Unemployment",
"Small Comp", "Medium Comp", "Large Comp"]


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
            get_metric_data(data_map, each_metric)
        
        new_df = pd.DataFrame(data_map)

        df_list.append(new_df)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('game_test_' + str(game_num)+ '.xlsx')

    # Write each dataframe to a different worksheet.
    for index,each_df in enumerate(df_list):
        name = "episode" + str(index + 1)
        each_df.to_excel(writer, sheet_name=name)


    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()

# def export_to_excel(user):
#     country_list = list(Country.objects.filter(player=user))
#     df_list = list()

#     for each_country in country_list:
#         metrics_list = list(Metric.objects.filter(country_of_residence=each_country))
        
#         data_map = dict()

#         for each_col in col_values:
#             data_map[each_col] = list()

#         for each_metric in metrics_list:
#             get_metric_data(data_map, each_metric)

#         new_df = pd.DataFrame(data_map)

#         df_list.append(new_df)
    
#     # Create a Pandas Excel writer using XlsxWriter as the engine.
#     writer = pd.ExcelWriter('metric_data.xlsx')

#     # Write each dataframe to a different worksheet.
#     for index,each_df in enumerate(df_list):
#         name = "game" + str(index + 1)
#         each_df.to_excel(writer, sheet_name=name)


#     # Close the Pandas Excel writer and output the Excel file.
#     writer.save()


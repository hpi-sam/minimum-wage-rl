import pandas as pd
column_list = ["minimum_wage", "product_price", "quantity", "unemployment_rate", "inflation", "bank", "Poverty", "Money_c", "Population"]

def export_test_data(all_data, version, test_data_folder):

    data_map = dict()
    a = zip(*all_data)

    for each_col in column_list:
        data_map[each_col] = list()

    for num, i in enumerate(a):
        data_map[column_list[num]] = list(i)
        # print(column_list[num], i)
    new_df = pd.DataFrame(data_map)
    writer = pd.ExcelWriter(test_data_folder + 'game_test' + str(version)  + '.xlsx')
    new_df.to_excel(writer, sheet_name="test")
    writer.save()
    writer.close()

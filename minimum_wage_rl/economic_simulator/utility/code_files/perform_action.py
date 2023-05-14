import enum

class CountryActionEnum(enum.Enum):
    MIN_WAGE = "minimum_wage"
    # CORPORATE_TAX = "corporatetax"
    # INCOME_TAX = "incometax"

# Can be used for other actions
# class BankActionEnum(enum.Enum):
#     INTEREST_RATE = "interestrate"
#     INFLATION ="inflation"



# action_map = {"minimum_wage":2,"interestrate":1}

disc_actions = dict()
disc_actions[0] = -2.0
disc_actions[1] = -1.0
disc_actions[2] = -0.2
disc_actions[3] = -0.1
disc_actions[4] = 0.0
disc_actions[5] = 0.1
disc_actions[6] = 0.2
disc_actions[7] = 0.3
disc_actions[8] = 1.0
disc_actions[9] = 2.0

def perform_action(action_map, country, discrete):

    enum_obj_map = {CountryActionEnum:country}

    min_wage_value = action_map["minimum_wage"]

    if discrete:
        if country.minimum_wage + get_discrete_action(min_wage_value) < 7:
            pass
        elif country.minimum_wage + get_discrete_action(min_wage_value) > 15:
            pass
        else:
            country.minimum_wage = country.minimum_wage + get_discrete_action(min_wage_value)
    else:
        # if country.minimum_wage + min_wage_value[0] < 7.0:
        #     pass
        # elif country.minimum_wage + min_wage_value[0] > 15:
        #     pass
        # else:
        #     country.minimum_wage = country.minimum_wage + min_wage_value[0]

        country.minimum_wage = min_wage_value[0]

    # if discrete:
    # for attribute_name,attribute_value in action_map.items():
        
    #     for each_enum in enum_obj_map.keys():
    #         try:
    #             each_enum(attribute_name)
    #             attri_value = float(attribute_value)
    #         except ValueError:
    #             pass
    #         else:
    #             if discrete:
    #                 func = getattr(enum_obj_map[each_enum],attribute_name+"_action",None) 
    #                 func(attri_value) # <-- this should work!
    #             else:
    #                 setattr(enum_obj_map[each_enum],attribute_name,attri_value)



def get_discrete_action(index):
    return disc_actions[index]
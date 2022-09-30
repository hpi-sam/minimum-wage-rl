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

def perform_action(action_map, country, discrete):

    enum_obj_map = {CountryActionEnum:country}

    min_wage_value = action_map["minimum_wage"]

    if discrete:
        country.minimum_wage = country.minimum_wage + min_wage_value
    else:
        country.minimum_wage = min_wage_value

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


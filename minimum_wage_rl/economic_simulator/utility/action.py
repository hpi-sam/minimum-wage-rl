import enum

class CountryAction(enum.Enum):
    MINIMUM_WAGE = "minimumwage"

class BankAction():
    # Single function
    pass

def perform_action():
    # dictionary action-variable and action-value.
    # action-variable register in config.
    # pick action-type = Continuous vs Discrete from config.
    pass

# import enum

# discrete = True

# class CountryActionEnum(enum.Enum):
#     MIN_WAGE = "minimumwage"
#     CORPORATE_TAX = "corporatetax"
#     INCOME_TAX = "incometax"

# class BankActionEnum(enum.Enum):
#     INTEREST_RATE = "interestrate"
#     INFLATION ="inflation"


# class C_class():
#     minimumwage = 10
#     inflation = 0.01

#     def minimumwage_action(self,action_option):

#         if action_option == 0:
#             pass

#         elif action_option == 1:
#             self.minimumwage = self.minimumwage + self.minimumwage * 0.01
        
#         else:
#             self.minimumwage = self.minimumwage + self.minimumwage * 0.05

#         return self.minimumwage

# class B_class():
#     interestrate = 10

#     def interestrate_action(self,action_option):
        
#         if action_option == 0:
#             self.interestrate = self.interestrate + self.interestrate * 0.01
#         else:
#             self.interestrate = self.interestrate + self.interestrate * 0.05
        
#         return self.interestrate


# c_class = C_class()
# b_class = B_class()

# action_map = {"minimumwage":2,"interestrate":1}

# def perform_action(action_map, country, bank):

#     enum_obj_map = {CountryActionEnum:country, BankActionEnum:bank}

#     if discrete:
#         for attribute_name,attribute_value in action_map.items():
            
#             for each_enum in enum_obj_map.keys():
#                 try:
#                     each_enum(attribute_name)
#                 except ValueError:
#                     pass
#                 else:
#                     # setattr(enum_obj_map[each_enum],attribute_name,attribute_value)
#                     func = getattr(enum_obj_map[each_enum],attribute_name+"_action",None) 
#                     func(attribute_value) # <-- this should work!
#     else:

#         for attribute_name,attribute_value in action_map.items():
            
#             for each_enum in enum_obj_map.keys():
#                 try:
#                     each_enum(attribute_name)
#                 except ValueError:
#                     pass
#                 else:
#                     setattr(enum_obj_map[each_enum],attribute_name,attribute_value)


# perform_action(action_map,country=c_class,bank=b_class)            

# print("========================================================================")
# print("Minimum wage - " , c_class.minimumwage)
# print("Interest rate - " , b_class.interestrate)



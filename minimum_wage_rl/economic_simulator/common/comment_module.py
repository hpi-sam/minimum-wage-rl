import json
import numpy as np

role_map = {"worker":1, "company":2, "government":3}

def get_interactive_comments(game_obj, worker_fileconfig, company_fileconfig):
    current_year_metric = game_obj.game_metric_list[-1]
    previous_year_metric = game_obj.game_metric_list[-2]

    change_in_minwage = ((current_year_metric.minimum_wage - previous_year_metric.minimum_wage)/previous_year_metric.minimum_wage)*100

    print("Change - ", change_in_minwage)

    if change_in_minwage <= 0:
        interact_data = get_worker_comments(change_in_minwage, worker_fileconfig)
    elif change_in_minwage > 0:
        interact_data = get_company_comments(change_in_minwage, company_fileconfig)
    
    return interact_data



def get_worker_comments(diff_value, file_config):

    diff_value = abs(diff_value)

    print("Inside worker")

    emotion = get_emotion()

    if diff_value>25 and diff_value<=35:
        worker_comment=file_config.get(f"one.{emotion}","worker")
        government_comment=file_config.get(f"one.{emotion}","government")
        has_comments = True

    elif diff_value>35 and diff_value<=50:
        # Slot2
        worker_comment=file_config.get(f"two.{emotion}","worker")
        government_comment=file_config.get(f"two.{emotion}","government")
        has_comments = True

    elif diff_value>50 and diff_value<=70:
        # Slot3
        worker_comment=file_config.get(f"three.{emotion}","worker")
        government_comment=file_config.get(f"three.{emotion}","government")
        has_comments = True

    elif diff_value>70:
        # Slot4
        worker_comment=file_config.get(f"four.{emotion}","worker")
        government_comment=file_config.get(f"four.{emotion}","government")
        has_comments = True

    else:
        # Empty
        worker_comment=""
        government_comment=""
        has_comments = False


    data_dict = [{"role":role_map["worker"], "Message":worker_comment},              
             {"role":role_map["government"], "Message":government_comment}]

    # interact_data = {"emotion":emotion, "comments":data_dict, "has_comments":has_comments}

    print("Exiting Worker")
    return data_dict


def get_company_comments(diff_value, file_config):
    
    print("Inside Company")

    emotion = get_emotion()

    if diff_value>25 and diff_value<=35:
        company_comment=file_config.get(f"one.{emotion}","company")
        government_comment=file_config.get(f"one.{emotion}","government")
        has_comments = True

    elif diff_value>35 and diff_value<=50:
        # Slot2
        company_comment=file_config.get(f"two.{emotion}","company")
        government_comment=file_config.get(f"two.{emotion}","government")
        has_comments = True

    elif diff_value>50 and diff_value<=70:
        # Slot3
        company_comment=file_config.get(f"three.{emotion}","company")
        government_comment=file_config.get(f"three.{emotion}","government")
        has_comments = True

    elif diff_value>70:
        # Slot4
        company_comment=file_config.get(f"four.{emotion}","company")
        government_comment=file_config.get(f"four.{emotion}","government")
        has_comments = True

    else:
        # Empty
        company_comment=""
        government_comment=""
        has_comments = False

    data_dict = [{"role":role_map["company"], "Message":company_comment},              
             {"role":role_map["government"], "Message":government_comment}]
    
    # interact_data = {"emotion":emotion, "comments":data_dict, "has_comments":has_comments}

    print("Exiting Company")
    return data_dict


def get_emotion():
    
    emotion_dict = {1:"sarcastic", 2:"anger", 3:"sad"}
    estimation = np.random.multinomial(n=1, pvals=[1/3, 1/3, 1/3])
    emotion_number = np.where(estimation==1)[0][0] + 1
    emotion = emotion_dict[emotion_number]

    return emotion


from django.core.cache import cache
# from django.http import HttpResponse
# from .utility.start_up import Start
# from .utility.simulate import step
from .utility.start_up_2 import start
from .utility.simulate_2 import step
from .utility.simulate_2 import get_state
from .utility.publish import export_to_excel
from .common.save import save_data_to_db, save_cached_data, extract_info
from .common.utility_func import get_game_stats
from .common.comment_module import get_interactive_comments


from .cached_utility.start_game import initialize_and_start
from .cached_utility.cached_simulation import game_step

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from .models import *
from rest_framework.authtoken.models import Token

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
import json
from .serializer import UserSerializer
from django.db import models
from .AI_model.actor_critic import actor_critic_main
from rest_framework.authtoken.views import ObtainAuthToken
import numpy as np
from stable_baselines3 import SAC
from .config import ConfigurationParser
from configparser import ConfigParser
from pathlib import Path
import os

BASEDIR = Path(__file__).parent.parent

file_name = os.path.join(BASEDIR, "config_file.txt")
config_parser = ConfigurationParser.get_instance(file_name).parser

worker_file_name = os.path.join(BASEDIR, "worker_comments.ini")
worker_config_parser = ConfigParser()
worker_config_parser.read(worker_file_name)

company_file_name = os.path.join(BASEDIR, "company_comments.ini")
company_config_parser = ConfigParser()
company_config_parser.read(company_file_name)


model_root_folder = "economic_simulator/trained_models/"
Level1_AI_model_name = "model_L1_1500"
Level2_AI_model_name = "model_L2_3000"
Level3_AI_model_name = "model_L3_Stagflation"

# Level-1 AI model
model_L1 = SAC.load(model_root_folder + Level1_AI_model_name)

# Level-2 AI model
model_L2 = SAC.load(model_root_folder + Level2_AI_model_name)

# Level-3 AI model
model_L3_Stagflation = SAC.load(model_root_folder + Level3_AI_model_name)

game_duration = int(config_parser.get("meta","game_duration"))

@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def start_game(request):

    default_level = "1"
    level = int(request.GET.get('level', default_level))
    return start_cached_game(request, level) 


def start_cached_game(request, level):
    
    current_user_name = request.user.username

    # 1. Clear cache
    __clear_redis_cache_for_user(current_user_name)

    # 1. Start player Game
    ai_flag = False
    player_game = None
    normalized_player_game_state, player_game_state, player_game = initialize_and_start(request.user, level, ai_flag, player_game)

    # 2. Start AI Game
    ai_flag = True
    normalized_ai_game_state, ai_game_state, ai_game = initialize_and_start(request.user, level, ai_flag, player_game)    

    # 3. Prepare response
    final_response = {"User Data": player_game_state, "AI Data": ai_game_state, "end flag":False, "message":""}
    json_reponse = json.loads(json.dumps(final_response))

    cache.set(str(current_user_name) + '_player_game', player_game)
    cache.set(str(current_user_name) + '_ai_game', ai_game)
    cache.set(str(current_user_name) + '_normazlized_ai_state', normalized_ai_game_state)
    cache.set(str(current_user_name) + "_game_ended", False)

    return Response({'status':200, 'message':json_reponse})


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def stop_game(request):

    current_user_name = request.user.username

    player_game = cache.get(str(current_user_name) + '_player_game')
    ai_game = cache.get(str(current_user_name) + '_ai_game')
    
    player_game_stats = extract_info(player_game)
    ai_game_stats = extract_info(ai_game)
    
    final_response = {"player_game_stats":player_game_stats, "ai_game_stats":ai_game_stats}
    json_reponse = json.loads(json.dumps(final_response))

    return Response({'status':200, 'message':json_reponse})

@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def end_and_save_game(request):

    current_user_name  = request.user
    # Check save flag
    save_game_value = request.GET.get('save_game',"False")
    save_flag = save_game_value.lower() == "true"

    # Get Cached values
    player_game = cache.get(str(current_user_name) + '_player_game')
    ai_game = cache.get(str(current_user_name) + '_ai_game')

    # Get stats and save game
    close_cached_game(player_game, save_flag)
    close_cached_game(ai_game, save_flag)

    # Clear redis cache
    __clear_redis_cache_for_user(current_user_name)

    # final_response = {"player_game_stats":player_game_stats, "ai_game_stats":ai_game_stats}
    final_response = {"game_ended":True}
    json_reponse = json.loads(json.dumps(final_response))

    return Response({'status':200, 'message':json_reponse})
    # user = request.user
    # return close_game(user)

def close_cached_game(game, save_flag):
    # game_stats = extract_info(game)
    if save_flag:
        save_cached_data(game)    
    
    return

# def close_game(user):
#     # game_obj = get_latest_game(user)
#     game_obj_list = get_all_games_for_user(user)

#     if game_obj_list == None:
#         return Response({"status":200, "message":"No Game to end"})
#     else:
#         for each_game in game_obj_list:
#             each_game.game_ended = True
#             each_game.save()
#         return Response({"status":200, "message":"Game to ended successfully"})

def get_all_games_for_user(user):
    
    game_objects = None
    game_objects = list(Game.objects.filter(player=user, game_ended = False))
    
    # max_game_query = Game.objects.filter(player=user, game_ended=False).aggregate(max_game_number=models.Max("game_number"))    
    # if not max_game_query:
    # pass
    # else:
    # max_game_number = max_game_query["max_game_number"]
    # game_obj = Game.objects.filter(player=user, game_ended = False, game_number = max_game_number).first()

    return game_objects

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def delete_user(request):
    u = User.objects.get(username="Test")
    u.delete()
    return Response({'status':200, 'message':'Delete it'})

@api_view(http_method_names=['POST'])
@authentication_classes([])
@permission_classes([])
def create_user(request):

    serialized = UserSerializer(data=request.data)

    if serialized.is_valid():        

        User.objects.create_user(
            username = serialized.validated_data['username'],
            email = serialized.validated_data['email'],
            password = serialized.validated_data['password']
        )

        my_user = User.objects.get(username=serialized.validated_data['username'])

        token_value  = Token.objects.create(user=my_user)
        message_data = f"New User {my_user.username} Created"
        status_value = 200
    
    else:
        message_data = "User with given name already exists"
        status_value = 403

    return Response({'status':status_value, 'message':message_data})


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perform_action(request):

    action_map = request.data
    user = request.user
    # __run_step(user, action_map)
    return __run_cached_game_step(request, action_map)

def __run_cached_game_step(request, action_map):

    current_user_name = request.user.username

    game_ended = cache.get(str(current_user_name) + "_game_ended")

    if not(game_ended):
        # 1. Simulate Game for Player
        ai_flag = False
        player_game = cache.get(str(current_user_name) + '_player_game')    
        player_game, user_data, normalized_state_values, reward, done, message  = game_step(player_game, action_map)

        # 2. Simulate Game for AI
        ai_flag = True
        ai_game = cache.get(str(current_user_name) + '_ai_game')
        normalized_ai_game_state = cache.get(str(current_user_name) + '_normazlized_ai_state')            

        # 2.1 Predicted Minimum Wage
        ai_game_state = np.array(normalized_ai_game_state)
        ai_minwage_action = predict_minwage_action(ai_game, ai_game_state)
        
        # 2.2 Run AI Game Simulation
        ai_action_map = {"minimum_wage": ai_minwage_action}
        ai_game, ai_game_state, normalized_ai_state_values, reward, done, message = game_step(ai_game, ai_action_map)

        year = user_data["Year"]
        interact_data = get_interactive_comments(player_game, worker_config_parser, company_config_parser)
        # getDialogue(year)

        print("Interact Data - ")
        print(interact_data)

        if year >= game_duration:
            cache.set(str(current_user_name) + "_game_ended", True)

            player_game_stats = extract_info(player_game)
            ai_game_stats = extract_info(ai_game)

            game_stats_map = dict()
            game_stats_map["player_game_stats"] = player_game_stats
            game_stats_map["ai_game_stats"]  = ai_game_stats
            final_response = {"User Data": user_data, "AI Data": ai_game_state, "game_stats":game_stats_map , "interact": interact_data, "end flag":done, "message":message}
        else:
            final_response = {"User Data": user_data, "AI Data": ai_game_state, "interact": interact_data, "end flag":done, "message":message}


        cache.set(str(current_user_name) + '_player_game', player_game)
        cache.set(str(current_user_name) + '_ai_game', ai_game)
        cache.set(str(current_user_name) + '_normazlized_ai_state', normalized_ai_state_values)


        # final_response = {"User Data": user_data, "AI Data": ai_game_state, "game_stats":game_stats_map , "interact": interact_data, "end flag":done, "message":message}
        json_reponse = json.loads(json.dumps(final_response))
    
    else:
        final_response = {"Game Ended":True, "end_flag": True}
        json_reponse = json.loads(json.dumps(final_response))

    return Response({'status':200, 'message':json_reponse})


# def __run_step(user, action_map):
    
#     ai_flag = False
#     player_game_number = 0
#     player_model_dictionary, game, user_data, state_values, reward, message, done = step(action_map, user, ai_flag, player_game_number)

#     ai_flag = True
    
#     ai_game, ai_unnormalized_state, ai_normalized_state_values, ai_reward, ai_info, ai_done = get_state(user, ai_flag, game.game_number)

#     ai_game_state = np.array(ai_normalized_state_values)
#     ai_minwage_action = predict_minwage_action(ai_game, ai_game_state)
    
#     ai_action_map = {"minimum_wage": ai_minwage_action}
    
#     ai_model_dictionary, ai_game, ai_game_state, state_values, reward, message, done = step(ai_action_map, user, ai_flag, game.game_number)


#     save_data_to_db(player_model_dictionary["country"], player_model_dictionary["metrics"], player_model_dictionary["open_company_list"], 
#                     player_model_dictionary["closed_company_list"], player_model_dictionary["final_workers_list"], player_model_dictionary["retired_workers_list"])
    
#     save_data_to_db(ai_model_dictionary["country"], ai_model_dictionary["metrics"], ai_model_dictionary["open_company_list"], 
#                     ai_model_dictionary["closed_company_list"], ai_model_dictionary["final_workers_list"], ai_model_dictionary["retired_workers_list"])

#     year = user_data["Year"]
#     interact_data = getDialogue(year)

#     final_response = {"User Data": user_data, "AI Data": ai_game_state, "interact": interact_data, "end flag":done, "message":message}
#     json_reponse = json.loads(json.dumps(final_response))
    
#     return Response({'status':200, 'message':json_reponse})

def predict_minwage_action(ai_game, ai_game_state):
    
    if ai_game.level == 1:
        # Level 1: 1500 Population level
        ai_minwage_action, _states = model_L1.predict(ai_game_state, deterministic=True)
    elif ai_game.level == 2:
        # Level 2: 3000 Population level        
        ai_minwage_action, _states = model_L2.predict(ai_game_state, deterministic=True)
    else:
        # Level 3: 1500 Population level along with Stagflation
        ai_minwage_action, _states = model_L3_Stagflation.predict(ai_game_state, deterministic=True)        
    return ai_minwage_action

def getDialogue(year):
    role = [1,2,3]
    dialogue_list = ["Message from Government", "Message from Workers", "Message from CEO"]

    index = year%len(role)
    index2 = (year+1)%len(role)
    interact_dict = [{"role" : role[index], "Message":dialogue_list[index]},
                    {"role" : role[index2], "Message":dialogue_list[index2]}]

    return interact_dict


# @api_view(http_method_names=['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def train(request):
#     actor_critic_main.train(request.user)
#     return Response({'status':200, 'message':"Traning completed"})


@api_view(http_method_names=['GET'])
@authentication_classes([])
@permission_classes([])
def test_url(request):
    print("test URL")
    return Response({'status':200, 'message':"test code"})


@authentication_classes([])
@permission_classes([])
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


# @api_view(http_method_names=['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def perform_get_action(request):
    
#     min_wage_action = request.GET.get('minimum_wage',None)
#     action_map = dict()
#     action_map["minimum_wage"] = float(min_wage_action)

#     user = request.user
#     return __run_step(user, action_map)


@api_view(http_method_names=['GET'])
def clear_cache(request):

    current_user_name = request.user.username
    return __clear_redis_cache(current_user_name)


def __clear_redis_cache(current_user_name):
    
    cache.clear()

    # Check if cache is cleared
    player_game = cache.get(str(current_user_name) + '_player_game')
    ai_game = cache.get(str(current_user_name) + '_ai_game')
    normalized_ai_game_state = cache.get(str(current_user_name) + '_normazlized_ai_state')
    
    if player_game !=None or ai_game != None or normalized_ai_game_state !=None:
        cache.delete(str(current_user_name) + "_player_game")
        cache.delete(str(current_user_name) + "_ai_game")
        cache.delete(str(current_user_name) + "_normazlized_ai_state")
        print("Cache had to be cleared manually")
    else:
        print("Cache Cleared")

    return Response({'status':200, 'message':"cleared"})


def __clear_redis_cache_for_user(current_user_name):
    
    # Check if cache is cleared
    player_game = cache.get(str(current_user_name) + '_player_game')
    ai_game = cache.get(str(current_user_name) + '_ai_game')
    normalized_ai_game_state = cache.get(str(current_user_name) + '_normazlized_ai_state')
    
    if player_game !=None or ai_game != None or normalized_ai_game_state !=None:
        cache.delete(str(current_user_name) + "_player_game")
        cache.delete(str(current_user_name) + "_ai_game")
        cache.delete(str(current_user_name) + "_normazlized_ai_state")
        print("Cache had to be cleared manually")
    else:
        print("Cache Cleared")

    return Response({'status':200, 'message':"cleared"})


@api_view(http_method_names=["GET"])
def get_stats(request):
    user = request.user
    stats_map = get_game_stats(user)

    json_reponse = json.loads(json.dumps(stats_map))
    return Response({'status':200, 'message':json_reponse})

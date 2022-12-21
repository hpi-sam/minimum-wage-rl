from django.shortcuts import render
# from django.http import HttpResponse
# from .utility.start_up import Start
# from .utility.simulate import step
from .utility.start_up_2 import start
from .utility.simulate_2 import step
from .utility.simulate_2 import get_state
from .utility.publish import export_to_excel

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

# Create your views here.

model_Lbasic = SAC.load("economic_simulator/best_model_basic")
model_L4 = SAC.load("economic_simulator/model_l4_full_sub_v1")


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def start_game(request):

    default_level = "1"
    level = int(request.GET.get('level', default_level))
    # request.GET.get('level', default_level)

    ai_flag = False
    player_game = None
    player_game_state, player_game = start(request.user, level, ai_flag, player_game)


    # player_game_number
    ai_flag = True
    ai_game_state, ai_game = start(request.user, level, ai_flag, player_game)
    # ai_game_state = player_game_state.copy()

    final_response = {"User Data": player_game_state, "AI Data": ai_game_state, "end flag":False, "message":""}

    json_reponse = json.loads(json.dumps(final_response))
    

    return Response({'status':200, 'message':json_reponse})


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def end_game(request):

    user = request.user
    return close_game(user)

def close_game(user):
    # game_obj = get_latest_game(user)
    game_obj_list = get_all_games_for_user(user)

    if game_obj_list == None:
        return Response({"status":200, "message":"No Game to end"})
    else:
        for each_game in game_obj_list:
            each_game.game_ended = True
            each_game.save()
        return Response({"status":200, "message":"Game to ended successfully"})

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
def delete_user(request):
    u = User.objects.get(username="Test")
    u.delete()
    return Response({'status':200, 'message':'Delete it'})

@api_view(http_method_names=['POST'])
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

        print(token_value.key)

    return Response({'status':200, 'message':'User Created'})


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perform_action(request):

    action_map = request.data
    user = request.user
    return __run_step(user, action_map)

def __run_step(user, action_map):
    ai_flag = False
    player_game_number = 0
    game, user_data, state_values, reward, message, done = step(action_map, user, ai_flag, player_game_number)

    ai_flag = True
    
    ai_game, ai_current_state, ai_state_values, ai_reward, ai_info, ai_done = get_state(user, ai_flag, game.game_number)
    ai_game_state = np.array(ai_state_values)
    if ai_game.level == 1:        
        ai_minwage_action, _states = model_Lbasic.predict(ai_game_state, deterministic=True)
    else:
        ai_minwage_action, _states = model_L4.predict(ai_game_state, deterministic=True)
    
    ai_action_map = {"minimum_wage": ai_minwage_action}
    
    ai_game, ai_game_state, state_values, reward, message, done = step(ai_action_map, user, ai_flag, game.game_number)

    final_response = {"User Data": user_data, "AI Data": ai_game_state, "end flag":done, "message":message}

    json_reponse = json.loads(json.dumps(final_response))
    return Response({'status':200, 'message':json_reponse})

@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def train(request):
    actor_critic_main.train(request.user)
    return Response({'status':200, 'message':"Traning completed"})


@api_view(http_method_names=['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
@authentication_classes([])
@permission_classes([])
#@api_view(http_method_names=['GET'])
def test_url(request):
    # export_to_excel(request.user)
    print("test code")
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


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perform_get_action(request):
    
    min_wage_action = request.GET.get('minimum_wage',None)
    action_map = dict()
    action_map["minimum_wage"] = float(min_wage_action)

    user = request.user
    return __run_step(user, action_map)

    # if min_wage_action:
    #     user_data, state_values, reward, message, done = step(action_map, request.user)

    #     ai_data = user_data.copy()

    #     final_response = {"User Data": user_data, "AI Data": ai_data}

    #     json_reponse = json.loads(json.dumps(final_response))
    #     return Response({'status':200, 'message':json_reponse})
    # else:
    #     return Response({'status':400, 'message':"Invalid Minimum wage"})

# @api_view(http_method_names=['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def test_post(request):
#     d = request.data
#     print(d["minwage"])
#     print(d["interest"])
#     print("hello")
#     return Response({'status':200, 'message':"test completed"})
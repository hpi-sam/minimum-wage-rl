from django.shortcuts import render
from django.http import HttpResponse
from .utility.start_up import Start
from .utility.simulate import step

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

# Create your views here.

@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def start_game(request):
    print("========================== Ready Function ===================================")
    # creaste user
    mm_model = Start(request.user)
    return Response({'status':200, 'message':'Hello from here'})

@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def end_game(request):

    game_obj = get_latest_game(request)

    if game_obj == None:
        return HttpResponse({"status":200, "message":"No Game to end"})
    else:
        game_obj.game_ended = True
        game_obj.save()
        return HttpResponse({"status":200, "message":"Game to ended successfully"})

def get_latest_game(request):
    
    game_obj = None
    max_game_number = None
    max_game_query = Game.objects.filter(player=request.user, game_ended=False).aggregate(max_game_number=models.Max("game_number"))
    
    if not max_game_query:
        pass
    else:
        max_game_number = max_game_query["max_game_number"]
        game_obj = Game.objects.filter(player=request.user, game_ended = False, game_number = max_game_number).first()

    return game_obj

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


# @api_view(http_method_names=['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def test_obj(request):

#     print(request.user)

#     return Response({'status':200, 'message':'Hello from here'})

@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perform_action(request, action):

    state_reward = step(action, request.user)

    print(state_reward)

    json_reponse = json.dumps(state_reward)
    return Response({'status':200, 'message':json_reponse})

@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def train(request):
    actor_critic_main.train(request.user)
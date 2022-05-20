from django.shortcuts import render
# from django.http import HttpResponse
# from .utility.start_up import Start
# from .utility.simulate import step
from .utility.start_up_2 import start
from .utility.simulate_2 import step

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
    user_data = start(request.user)

    ai_data = user_data.copy()

    final_response = {"User Data": user_data, "AI Data": ai_data}

    json_reponse = json.loads(json.dumps(final_response))
    return Response({'status':200, 'message':json_reponse})


@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def end_game(request):

    game_obj = get_latest_game(request)

    if game_obj == None:
        return Response({"status":200, "message":"No Game to end"})
    else:
        game_obj.game_ended = True
        game_obj.save()
        return Response({"status":200, "message":"Game to ended successfully"})

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

@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perform_action(request):

    action_map = request.data
    user_data, state_values, reward, done = step(action_map, request.user)

    ai_data = user_data.copy()

    final_response = {"User Data": user_data, "AI Data": ai_data}

    json_reponse = json.loads(json.dumps(final_response))
    return Response({'status':200, 'message':json_reponse})

@api_view(http_method_names=['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def train(request):
    actor_critic_main.train(request.user)
    return Response({'status':200, 'message':"Traning completed"})


@api_view(http_method_names=['GET'])
@authentication_classes([])
@permission_classes([])
#@api_view(http_method_names=['GET'])
def test_url(request):
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

# @api_view(http_method_names=['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def test_post(request):
#     d = request.data
#     print(d["minwage"])
#     print(d["interest"])
#     print("hello")
#     return Response({'status':200, 'message':"test completed"})
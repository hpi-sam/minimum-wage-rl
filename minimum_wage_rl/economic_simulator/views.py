from django.shortcuts import render
from django.http import HttpResponse
from .utility.start_up import Start
from .utility.simulate import step

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *

import json

# Create your views here.

@api_view(http_method_names=['GET'])
def create_user(request):
    print(request)
    print("========================== Ready Function ===================================")
    mm_model = Start()
    return Response({'status':200, 'message':'Hello from here'})

@api_view(http_method_names=['GET'])
def test_obj(request):
    
    country = Country.objects.first()
    bank = country.bank

    print("================================================================")
    print(bank.liquid_capital)
    print(bank.deposit_money(100))
    print(bank.liquid_capital)
    print("================================================================")

    return Response({'status':200, 'message':'Hello from here'})

@api_view(http_method_names=['GET'])
def perform_action(request, action):

    print(action)
    state_reward = step(action)

    print(state_reward)

    json_reponse = json.dumps(state_reward)
    return Response({'status':200, 'message':json_reponse})
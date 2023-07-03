from ..models.metrics import Metric
from django.db import models
from ..models.game import Game

def get_game_stats(user):

    complete_game_stats = dict()
    max_game_query = Game.objects.distinct().filter(player=user).aggregate(max_game_number=models.Max("game_number"))
    latest_game_number =  max_game_query["max_game_number"]

    player_game = Game.objects.get(game_number = latest_game_number, ai_flag = False)

    player_game_metrics = list(Metric.objects.filter(game__game_id = player_game.game_id))
    player_game_stats = extract_game_stats(player_game_metrics)

    # player_game.game_id
    # game=player_game
    # game=ai_game
    # ai_game.game_id
    
    ai_game = Game.objects.get(game_number = latest_game_number, ai_flag = True)
    ai_game_metrics = list(Metric.objects.filter(game__game_id = ai_game.game_id))
    ai_game_stats = extract_game_stats(ai_game_metrics)

    complete_game_stats["player_game_stats"] = player_game_stats
    complete_game_stats["ai_game_stats"] = ai_game_stats

    return complete_game_stats


def extract_game_stats(metric_list):
    
    unemp_list = []
    poverty_list = []
    inflation_list = []
    product_cost_list = []
    min_wage_list = []

    game_stats = dict()

    for each_metric in metric_list:
        unemp_list.append(each_metric.unemployment_rate)
        poverty_list.append(each_metric.poverty_rate)
        inflation_list.append(each_metric.inflation)
        product_cost_list.append(each_metric.product_price)
        min_wage_list.append(each_metric.minimum_wage)

    avg_unemp = round(sum(unemp_list)/len(unemp_list), 2)
    avg_poverty = round(sum(poverty_list)/len(poverty_list), 2)
    avg_inflation = round(sum(inflation_list)/len(inflation_list), 2)
    avg_product_cost = round(sum(product_cost_list)/len(product_cost_list), 2)
    avg_minwage = round(sum(min_wage_list)/len(min_wage_list), 2)

    game_stats["average_poverty"] = avg_poverty
    game_stats["average_unemployment"] = avg_unemp
    game_stats["average_inflation"] = avg_inflation
    game_stats["average_product_price"] = avg_product_cost
    game_stats["average_minimum_wage"] = avg_minwage

    return game_stats
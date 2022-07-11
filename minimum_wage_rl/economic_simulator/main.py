from models.game import Game
# from utility.config import ConfigurationParser
from AI_model.actor_critic import actor_critic_main
from env import Task
from utility.publish import export_from_game_metric

num_workers = 5


def make_env(num_workers):
    envs = []
    for i in range(1, num_workers+1):
        envs.append(Game(i))

    return envs

task = Task(num_workers, make_env(num_workers=num_workers))

actor_critic_main.train(num_workers, task)

games = task.env.envs

for each_game in games:
    export_from_game_metric(each_game.game_number, each_game.game_metric_list)


print("done")
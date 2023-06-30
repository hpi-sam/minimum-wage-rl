from django.db import models
import uuid
from django.contrib.auth.models import User

from ..utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser

class Game(models.Model):

    class Meta:
        db_table = "game_info"

    # def __init__(self, level):
    #     super().__init__(self)
    #     self.level = level

    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game_number = models.IntegerField(default=1)
    game_ended = models.BooleanField(default=False)
    player_game_number = models.IntegerField(default=0)
    level = models.IntegerField()


# only for cached version - start
    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self.country = None
        self.game_metric_list = list()    
        self.episode_number=0

    
# only for cached version - start    

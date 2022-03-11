from django.db import models
import uuid
from django.contrib.auth.models import User

from ..utility.config import ConfigurationParser
config_parser = ConfigurationParser.get_instance().parser

class Game(models.Model):

    class Meta:
        db_table = "game_info"

    # def __init__(self, player):
    #     self.player = player
    #     super().__init__(self)

    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game_number = models.IntegerField(default=1)
    game_ended = models.BooleanField(default=False)
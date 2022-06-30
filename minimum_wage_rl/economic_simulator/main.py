from models.game import Game
from utility.config import ConfigurationParser


g1 =  Game(1)

g1.reset()

action = {"minimum_wage":3.2}
current_state, state_values, reward, done = g1.step(action)

print(current_state)
print(state_values)
print(reward)
print(done)
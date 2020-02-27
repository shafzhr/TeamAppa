from penguin_game import * # pylint: disable=F0401
import math
import itertools
from ManangeGame import *

def do_turn(game):
    manager = Manage(game)
    manager.do_turn()


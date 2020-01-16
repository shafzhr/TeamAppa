from penguin_game import * # pylint: disable=F0401


class QuantitativeFunctions(object):
    def __init__(self, game):
        """
        :type game: Game
        """
        self.ices_by_player = [ game.‎get_my_icebergs(), game.‎get_enemy_icebergs() ]        
        self.p_groups_by_player = [ game.get_my_penguin_groups(), ‎get_enemy_penguin_groups() ]

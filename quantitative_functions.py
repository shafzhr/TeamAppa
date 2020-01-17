from penguin_game import * # pylint: disable=F0401


class QuantitativeFunctions(object):
    def __init__(self, game):
        """
        :param game: current game's state
        :type game: Game
        """
        self.game = game
        self.ices_by_player = [ game.‎get_my_icebergs(), game.‎get_enemy_icebergs() ]        
        self.p_groups_by_player = [ game.get_my_penguin_groups(), ‎get_enemy_penguin_groups() ]
        self.players_index = { game.get_myself(): 0, game.get_enemy(): 1 }
        
    
    def get_players_indexes(self, player):
        return self.players_index[player], ~ self.players_index[player]


    def get_nearest_opposite_iceberg(self, player, iceberg):
        """
        :type player: Player
        """
        return sorted( self.ices_by_player[self.get_players_indexes(player)[1]], key=lambda x: x.‎get_turns_till_arrival(iceberg) )[0]


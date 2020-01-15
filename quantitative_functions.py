from penguin_game import * # pylint: disable=F0401


class QuantitativeFunctions(object):
    def __init__(self, game):
        """
        :type game: Game
        """
        self.ices_by_player = { player : None for player in ‎get_all_players() }
        for player, ices in self.ices_by_player.iteritems():
            ices = list(filter(lambda ice: ice.owner == player, game.‎get_all_icebergs()))
        
        self.p_groups_by_player = { player : [] for player in ‎‎get_all_players() }
        for player, p_groups in self.p_groups_by_player.iteritems():
            p_groups = list(filter(lambda group: group.owner == player, get_all_penguin_groups()))

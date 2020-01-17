from penguin_game import *


class QuantitativeFunctions(object):
    def __init__(self, game):
        """
        :param game: the current game state
        :type game: Game
        """
        self.game = game
        self.ices_by_player = [ game.get_my_icebergs(), game.get_enemy_icebergs() ]        
        self.p_groups_by_player = [ game.get_my_penguin_groups(), game.get_enemy_penguin_groups() ]
        self.players_index = { game.get_myself(): 0, game.get_enemy(): 1 }
        
    
    def get_players_indexes(self, player):
        """
        Returns the indexes of the players (given player, opposite) that are used in the properties for the lists
        ~0 == -1
        ~1 == -2
        """
        return self.players_index[player], ~ self.players_index[player]


    def get_nearest_opposite_iceberg(self, iceberg, player):
        """
        Returns the nearest iceberg of the opposite team to a given iceberg
        :type player: Player
        :rtype: Iceberg
        """
        return sorted( self.ices_by_player[self.get_players_indexes(player)[1]], key=lambda x: x.get_turns_till_arrival(iceberg) )[0]


    def get_iceberg_balance(self, dest, player):
        """
        Returns the balance of a specific iceberg after all the penguin groups that were sent to it by his enemy have reached it
        :type dest: Iceberg
        """
        player_i, eny_i = self.get_players_indexes(player)
        groups_per_distance = {}
        for eny_group in self.p_groups_by_player[eny_i]:
            if eny_group.destination == dest:
                if eny_group.turns_till_arrival in groups_per_distance.keys():
                    groups_per_distance[eny_group.turns_till_arrival] += eny_group.penguin_amount
                else:
                    groups_per_distance[eny_group.turns_till_arrival] = eny_group.penguin_amount
        if len(groups_per_distance.keys()) == 0:
            return dest.penguin_amount
        
        min_balance = dest.penguin_amount
        balance = dest.penguin_amount
        for turn in range(1, max(groups_per_distance.keys()) + 1):
            balance += dest.penguins_per_turn

            if turn in groups_per_distance.keys():
                balance -= groups_per_distance[turn]
            
            for send in self.get_my_sends_on_iceberg(dest, player):
                if send.turns_till_arrival == turn:
                    balance += send.penguin_amount
            
            if balance < min_balance:
                min_balance = balance
        return min_balance
    

    def get_my_sends_on_iceberg(self, dest, player):
        """
        :type dest: Iceberg
        :type player: Player
        """
        return [ send for send in self.p_groups_by_player[self.players_index[player]] if send.destination == dest ]


    
                

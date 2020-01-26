from penguin_game import * # pylint: disable=F0401


class QuantitativeFunctions(object):
    def __init__(self, game, player):
        """
        :param game: the current game state
        :type game: Game
        :type player: Player
        """
        self.game = game
        self.player = player
        self.ices_by_player = [ game.get_my_icebergs(), game.get_enemy_icebergs() ]        
        self.p_groups_by_player = [ game.get_my_penguin_groups(), game.get_enemy_penguin_groups() ]
        self.players_index = { game.get_myself(): 0, game.get_enemy(): 1 }

        
    def __get_players_indexes(self):
        """
        Returns the indexes of the players (given player, opposite) that are used in the properties for the lists
        ~0 == -1
        ~1 == -2
        """
        return self.players_index[self.player], ~ self.players_index[self.player]


    def get_nearest_opposite_iceberg(self, iceberg):
        """
        Returns the nearest iceberg of the opposite team to a given iceberg
        :type iceberg: Iceberg
        """
        return sorted( self.ices_by_player[self.__get_players_indexes()[1]], key=lambda x: x.get_turns_till_arrival(iceberg) )[0]


    def get_iceberg_balance(self, dest):
        """
        Returns the balance of a specific iceberg after all the penguin groups that were sent to it by his enemy have reached it
        :type dest: Iceberg
        """
        player_i, eny_i = self.__get_players_indexes()
        groups_per_distance = {}
        for eny_group in self.p_groups_by_player[eny_i]:
            if eny_group.destination == dest:
                if eny_group.turns_till_arrival in groups_per_distance.keys():
                    groups_per_distance[eny_group.turns_till_arrival] += eny_group.penguin_amount
                else:
                    groups_per_distance[eny_group.turns_till_arrival] = eny_group.penguin_amount
        if not groups_per_distance.keys():
            return dest.penguin_amount
        
        min_balance = dest.penguin_amount
        balance = dest.penguin_amount
        for turn in range(1, max(groups_per_distance.keys()) + 1):
            balance += dest.penguins_per_turn

            if turn in groups_per_distance.keys():
                balance -= groups_per_distance[turn]
            
            for send in self.get_player_sends_on_iceberg(dest):
                if send.turns_till_arrival == turn:
                    balance += send.penguin_amount
            
            if balance < min_balance:
                min_balance = balance
        return min_balance - 1
    

    def get_player_sends_on_iceberg(self, dest):
        """
        :type dest: Iceberg
        """
        return [ send for send in self.p_groups_by_player[self.players_index[self.player]] if send.destination == dest ]


    def get_opposite_sends_on_iceberg(self, dest):
        """
        :type dest: Iceberg
        """
        return [ send for send in self.p_groups_by_player[~self.players_index[self.player]] if send.destination == dest]


    def get_nearest_opposite_penguin_group(self, iceberg):
        """
        returns the nearest opposite penguin group to a given iceberg
        :type iceberg: Iceberg
        """
        opposite_penguin_groups = sorted(self.get_opposite_sends_on_iceberg(iceberg), key=lambda x:x.turns_till_arrival)
        return opposite_penguin_groups[0] if opposite_penguin_groups else None
    

    def get_nearest_neutral_iceberg(self, iceberg):
        """
        returns the nearest neutral iceberg
        :type iceberg: Iceberg
        """
        neutral_icebergs = self.sort_by_distance_from_iceberg(iceberg, self.game.get_neutral_icebergs())
        return neutral_icebergs[0] if neutral_icebergs else None

    
    def sort_by_distance_from_iceberg(self, iceberg, icebergs_list):
        """
        returns sorted list of icebergs by their distances from iceberg
        """
        return sorted(icebergs_list, key=lambda x: x.get_turns_till_arrival(iceberg))
    

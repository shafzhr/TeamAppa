from penguin_game import * # pylint: disable=F0401
import quantitative_functions as qc

class Manage(object):
    def __init__(self, game):
        """
        :type game: Game
        """
        self.game = game
        
        self.my_icebergs = game.get_my_icebergs()
        self.my_penguin_groups = game.get_my_penguin_groups()
        self.my_qc = qc.QuantitativeFunctions(game, game.get_myself())
        self.icebergs_balance = { iceberg: self.my_qc.get_iceberg_balance(iceberg) for iceberg in self.my_icebergs }
        self.our_pengs_sum = sum([ ice.penguin_amount for ice in self.my_icebergs ]) + sum([ group.penguin_amount for group in self.my_penguin_groups ])

        self.enemy_icebergs = game.get_enemy_icebergs()
        self.enemy_penguins_groups = game.get_enemy_penguin_groups()
        self.enemy_qc = qc.QuantitativeFunctions(game, game.get_enemy())
        self.enemy_balance = { iceberg: self.enemy_qc.get_iceberg_balance(iceberg) for iceberg in self.enemy_icebergs }
        self.enemy_pengs_sum = sum([ eny_ice.penguin_amount for eny_ice in self.enemy_icebergs ]) + sum([ group.penguin_amount for group in self.enemy_penguins_groups ])



    def defend(self):
        pass


    def risk_heuristic(self, game, our_ice):
        """
        :type game: Game
        :type our_ice: Iceberg
        """
        risk = 0
        for eny_ice in game.get_enemy_icebergs():
            risk += eny_ice.penguin_amount*1.0/(eny_ice.get_turns_till_arrival(our_ice)*1.0*eny_ice.get_turns_till_arrival(our_ice)*1.0)
        total = self.our_pengs_sum(game)
        # risk = risk*1.0 * (1.0/(our_ice.level * 10.0))
        # risk = risk*1.0 * ((total-self.icebergs_balance[our_ice]*1.0) / total*1.0) * (1.0/(our_ice.level * 10.0))
        return risk


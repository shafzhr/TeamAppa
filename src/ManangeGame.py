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
        self.icebergs_state = { iceberg: True for iceberg in self.my_icebergs } 
        
        self.enemy_icebergs = game.get_enemy_icebergs()
        self.enemy_penguins_groups = game.get_enemy_penguin_groups()
        self.enemy_qc = qc.QuantitativeFunctions(game, game.get_enemy())
        self.enemy_balance = { iceberg: self.enemy_qc.get_iceberg_balance(iceberg) for iceberg in self.enemy_icebergs }
        self.enemy_pengs_sum = sum([ eny_ice.penguin_amount for eny_ice in self.enemy_icebergs ]) + sum([ group.penguin_amount for group in self.enemy_penguins_groups ])



    def defend(self):
        """
        :type game: Game
        """
        global icebergs_balance
        need_help = { iceberg: [] for iceberg in game.get_my_icebergs() if icebergs_balance[iceberg] <= 0 } # { need_help_iceberg: [possible_helpers] }
        helps_icebergs = {iceberg: (0, []) for iceberg in game.get_my_icebergs() if iceberg not in need_help.keys()} # { helper_iceberg: (amount_of_need_help, [icebergs that need the helper]) }
        for need_help_iceberg, possible_helps in need_help.iteritems():
            nearest_group_distance = nearest_enemy_penguin_group_distance(game, need_help_iceberg)
            for iceberg in game.get_my_icebergs():
                # if penguin_amount_in_n_turns(game, need_help_iceberg, iceberg.get_turns_till_arrival(iceberg)) > 0 and icebergs_balance[iceberg] > 0:
                if penguin_amount_in_n_turns(game, need_help_iceberg, iceberg.get_turns_till_arrival(iceberg)) > 0 and icebergs_balance[iceberg] > 0 \
                and iceberg.get_turns_till_arrival(need_help_iceberg) <= get_turns_to_help(game, need_help_iceberg) :
                    print("iceberg amount: {0}, balance: {1}".format(iceberg.penguin_amount, icebergs_balance[iceberg]))
                    possible_helps.append(iceberg)
                    if iceberg in helps_icebergs.keys():
                        helps_icebergs[iceberg] = (helps_icebergs[iceberg][0] + 1, helps_icebergs[iceberg][1])              
                    else:
                        helps_icebergs[iceberg] = (1, [])              
                    helps_icebergs[iceberg][1].append(need_help_iceberg)
        
        # for need_help_iceberg, possible_helps in need_help.iteritems():
        #     need_help[need_help_iceberg] = sorted(possible_helps, key=lambda x: risk_heuristic(game, x))
        
        our_icebergs_prioritized = sorted(need_help.keys(), key= lambda x: x.level, reverse= True)
        defenders_devision = {iceberg: [] for iceberg in our_icebergs_prioritized}
        if len(need_help.keys()) == 0:
            return
        max_defenders = len(helps_icebergs.keys()) / len(need_help.keys())
        if max_defenders == 0:
            max_defenders = 1
        for iceberg in our_icebergs_prioritized:
            if len(defenders_devision[iceberg]) > max_defenders:
                break
            possible_helps =  need_help[iceberg]
            for helper in possible_helps:
                if helper in helps_icebergs.keys():
                    defenders_devision[iceberg].append(helper)
                    del helps_icebergs[helper]
        print defenders_devision
        for iceberg, defenders in defenders_devision.iteritems():
            defenders = sorted(defenders, key= lambda x: x.level, reverse=True)
            
            already_done = False
            for defender in defenders:
                if self.icebergs_balance[defender] + self.icebergs_balance[iceberg] > 0 and penguin_amount_in_n_turns(game, iceberg, iceberg.get_turns_till_arrival(defender)) > 0:
                    self.smart_send(defender, iceberg, self.our_abs(self.icebergs_balance[iceberg]) + 1)
                    already_done = True
                    break
            if not already_done:
                defenders_needed = 0
                sum = 0
                for defender in defenders:
                    defenders_needed += 1
                    sum += self.icebergs_balance[defender]
                    if sum > our_abs(self.icebergs_balance[iceberg]):
                        break
                if sum > self.icebergs_balance[iceberg]:
                    print "ACTUAL AMOUNT ",our_abs(self.icebergs_balance[iceberg]) + 1
                    amount_per_defender = split_amount_for_send(defenders, our_abs(self.icebergs_balance[iceberg]) + 1, game)
                    if amount_per_defender is None:
                        return
                    for defender, amount in amount_per_defender.iteritems():
                        print "amount: ", amount
                        self.smart_send(defender, iceberg, our_abs(amount))
                    print "Defending!/?????????????????????????????????"
                    print "Defenders: " + str(len(defenders)) + "--------------------_"
                else:
                    print "Gave up----------------------------------"


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

    def smart_send(self, src, dest, p_amount):
        """
        :type p_amount: int
        :type src: Iceberg
        :type dest: Iceberg
        """
        # if not icebergs_state[src]:
        #     return
        if src.already_acted:
            return
        if p_amount > 0:
            src.send_penguins(dest, p_amount)
            self.icebergs_balance[src] -= p_amount
            self.icebergs_state[src] = False #TODO:add
        else:
            print "Cant send negative!!!!!"

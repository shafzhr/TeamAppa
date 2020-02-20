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
        self.our_icebergs_risk = { iceberg: self.risk_heuristic(iceberg) for iceberg in self.my_icebergs }
        self.our_upgrade_vals = { iceberg: self.upgrade_val(iceberg) for iceberg in self.my_icebergs }


        self.enemy_icebergs = game.get_enemy_icebergs()
        self.enemy_penguins_groups = game.get_enemy_penguin_groups()
        self.enemy_qc = qc.QuantitativeFunctions(game, game.get_enemy())
        self.enemy_balance = { iceberg: self.enemy_qc.get_iceberg_balance(iceberg) for iceberg in self.enemy_icebergs }
        self.enemy_pengs_sum = sum([ eny_ice.penguin_amount for eny_ice in self.enemy_icebergs ]) + sum([ group.penguin_amount for group in self.enemy_penguins_groups ])



    def do_turn(self):
        self.defend()
        self.handle_upgrading()
        self.handle_trap()
        self.handle_conquering_neutrals
        


    def defend(self):
        need_help = { iceberg: [] for iceberg in self.my_icebergs if self.icebergs_balance[iceberg] <= 0 } # { need_help_iceberg: [possible_helpers] }
        helps_icebergs = {iceberg: (0, []) for iceberg in self.my_icebergs if iceberg not in need_help.keys()} # { helper_iceberg: (amount_of_need_help, [icebergs that need the helper]) }
        for need_help_iceberg, possible_helps in need_help.iteritems():
            for iceberg in self.my_icebergs:
                # if self.penguin_amount_in_n_turns(need_help_iceberg, iceberg.get_turns_till_arrival(iceberg)) > 0 and self.icebergs_balance[iceberg] > 0:
                if self.penguin_amount_in_n_turns(need_help_iceberg, iceberg.get_turns_till_arrival(iceberg)) > 0 and self.icebergs_balance[iceberg] > 0 \
                and iceberg.get_turns_till_arrival(need_help_iceberg) <= self.get_turns_to_help(need_help_iceberg) :
                    print("iceberg amount: {0}, balance: {1}".format(iceberg.penguin_amount, self.icebergs_balance[iceberg]))
                    possible_helps.append(iceberg)
                    if iceberg in helps_icebergs.keys():
                        helps_icebergs[iceberg] = (helps_icebergs[iceberg][0] + 1, helps_icebergs[iceberg][1])              
                    else:
                        helps_icebergs[iceberg] = (1, [])              
                    helps_icebergs[iceberg][1].append(need_help_iceberg)
        
        # for need_help_iceberg, possible_helps in need_help.iteritems():
        #     need_help[need_help_iceberg] = sorted(possible_helps, key=lambda x: risk_heuristic(x))
        
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
                if self.icebergs_balance[defender] + self.icebergs_balance[iceberg] > 0 and self.penguin_amount_in_n_turns(iceberg, iceberg.get_turns_till_arrival(defender)) > 0:
                    self.smart_send(defender, iceberg, abs(self.icebergs_balance[iceberg]) + 1)
                    already_done = True
                    break
            if not already_done:
                defenders_needed = 0
                sum = 0
                for defender in defenders:
                    defenders_needed += 1
                    sum += self.icebergs_balance[defender]
                    if sum > abs(self.icebergs_balance[iceberg]):
                        break
                if sum > self.icebergs_balance[iceberg]:
                    print "ACTUAL AMOUNT ", abs(self.icebergs_balance[iceberg]) + 1
                    amount_per_defender = self.split_amount_for_send(defenders, abs(self.icebergs_balance[iceberg]) + 1)
                    if amount_per_defender is None:
                        return
                    for defender, amount in amount_per_defender.iteritems():
                        print "amount: ", amount
                        self.smart_send(defender, iceberg, abs(amount))
                    print "Defending!/?????????????????????????????????"
                    print "Defenders: " + str(len(defenders)) + "--------------------_"
                else:
                    print "Gave up----------------------------------"


    def handle_upgrading(self):
        """
        TODO: - Take into account the risk measurement of each icebergs
        """
        upgrade_more_than_zero = [ ice for ice, upg_val in self.our_upgrade_vals if upg_val > 0 ]
        if upgrade_more_than_zero:
            upgrades_priority = sorted( upgrade_more_than_zero, key= lambda x: self.upgrade_val(x), reverse= True )
            to_upgrade = upgrades_priority[0]
            if to_upgrade.can_upgrade() and not to_upgrade.already_acted and self.icebergs_balance > to_upgrade.upgrade_cost:
                to_upgrade.upgrade()
                self.icebergs_state[to_upgrade] = False
    
    def handle_trap(self):
        """
        TODO: - Implement enemy_target()
        """
        if self.game.get_neutral_icebergs():
            self.enemy_target()

    def handle_conquering_neutrals(self):
        """
        TODO: - Take into account the neutral icebergs that will be conquered 
                soon (because there are penguin groups heading to the iceberg) - both for us and enemy.
              - removing enemy icebergs with negative balance + our icebergs with negative balance.
              - implement get_neutral_to_take() without being dependent on a iceberg as an argument.
              - implement get_amount_to_conquer_neutral(iceberg)
              - implement can_attack_neutral(iceberg)
        """
        conquered_icebergs = [ eny_ice for eny_ice in self.enemy_icebergs if self.enemy_balance[eny_ice] < 0 ] # Our
        enemy_conquered_icebergs = [ ice for ice in self.my_icebergs if self.icebergs_balance[ice] < 0 ] # Enemy's

        our_ices = [ ice for ice in self.my_icebergs if self.icebergs_balance[ice] > 0 ] + conquered_icebergs
        enemy_ices = [ eny_ice for eny_ice in self.enemy_icebergs if self.enemy_balance[eny_ice] > 0 ] + enemy_conquered_icebergs

        if self.game.get_neutral_icebergs() and len(our_ices) <= len(enemy_ices):
            source_attacker, to_conquer = self.get_neutral_to_take()
            needed_amount = self.get_amount_to_conquer_neutral(to_conquer)
            if (    to_conquer is not None
                and self.can_attack_neutral(source_attacker, to_conquer)
                and needed_amount <= self.icebergs_balance[source_attacker]
                ):
                self.smart_send(source_attacker, to_conquer, needed_amount)


    def risk_heuristic(self, our_ice):
        """
        :type our_ice: Iceberg
        """
        risk = 0
        for eny_ice in self.my_icebergs():
            risk += eny_ice.penguin_amount*1.0/((eny_ice.get_turns_till_arrival(our_ice)*1.0)**2)
        # for eny_group in game.get_enemy_penguin_groups():
        #     if eny_group.destination == our_ice:
        #         risk += eny_group.penguin_amount*1.0/((eny_group.turns_till_arrival*1.0)**2)
        # for our_group in self.my_penguin_groups:
        #     if our_group.destination == our_ice:
        #         risk -= 0.5*our_group.penguin_amount*1.0/((our_group.turns_till_arrival*1.0)**2)
        # total = self.our_pengs_sum
        risk = risk*1.0 * (1.0/(our_ice.level ** 2))
        # risk = risk*1.0 * ((total-self.icebergs_balance[our_ice]*1.0) / total*1.0) * (1.0/(our_ice.level * 10.0))
        # risk = risk*1.0 * (1.0 / icebergs_balance[our_ice]*1.0) * (1.0/(our_ice.level * 10.0))
        print "RISK_VAL:" + str(risk)
        return risk


    def upgrade_val(self, iceberg):
        """
        :type iceberg: Iceberg
        """
        if iceberg.level == iceberg.upgrade_level_limit:
            return 0
        cost_eff = 1.0/iceberg.upgrade_cost*1.0 / iceberg.upgrade_value
        final_val = (iceberg.penguin_amount*1.0/iceberg.upgrade_cost)*(iceberg.penguins_per_turn + iceberg.upgrade_value)*cost_eff*1.0
        print ("UPGRADE VAL: " + str(final_val))
        return final_val



    def smart_send(self, src, dest, p_amount):
        """
        :type p_amount: int
        :type src: Iceberg
        :type dest: Iceberg
        """
        if not self.icebergs_state[src]:
            return
        if p_amount > 0:
            src.send_penguins(dest, p_amount)
            self.icebergs_balance[src] -= p_amount
        else:
            print "Cant send negative!!!!!"

    def penguin_amount_in_n_turns(self, iceberg, n):
        p_per_turn = iceberg.penguins_per_turn
        penguin_sum = iceberg.penguin_amount + p_per_turn * n
        for group in self.enemy_penguins_groups:
            if group.destination == iceberg and group.turns_till_arrival <= n:
                penguin_sum -= group.penguin_amount
        for group in self.my_penguin_groups:
            if group.destination == iceberg and group.turns_till_arrival <= n:
                penguin_sum += group.penguin_amount
        return penguin_sum


    def get_turns_to_help(self, iceberg):
        sends = [ send.turns_till_arrival for send in self.enemy_penguins_groups if send.destination == iceberg ]
        for i in range(max(sends)+1):
            if self.penguin_amount_in_n_turns(iceberg, i) <= 0:
                return i

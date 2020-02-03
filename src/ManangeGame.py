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

    def risk_heuristic(self, our_ice):
        """
        :type our_ice: Iceberg
        """
        risk = 0
        for eny_ice in self.my_icebergs:
            risk += eny_ice.penguin_amount*1.0/((eny_ice.get_turns_till_arrival(our_ice)*1.0)**2)
        risk = risk*1.0 * (1.0/(our_ice.level ** 2))
        print "RISK_VAL:" + str(risk)

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
        return 0

    def split_amount_for_send(self, icebergs, amount):
        """
        iceberg_to_send: target ICEBERG
        icebergs: LIST of icebergs to send from
        amount: int, total amount to be sent
        
        returns a dictionary. for each iceberg in icebergs returns how much to send.
        """
        sum_balance = 0
        for sender in icebergs:
            sum_balance += self.icebergs_balance[sender]
        
        amount_by_iceberg = {iceberg: (self.icebergs_balance[iceberg], self.icebergs_balance[iceberg] / sum_balance) for iceberg in icebergs}
        to_send_by_iceberg = {iceberg: 0 for iceberg in icebergs}
        # amount_by_iceberg: second value in tuple is ratio between amount and sendable penguin amount for iceberg. 
        sum = 0 
        to_be_sent = 0
        for key, value in amount_by_iceberg.iteritems(): 
            sum += value[0]
        if sum < amount:
            print "Split Failed => sum < amount"
            return None
        else:
            for iceberg in icebergs:
                to_send_by_iceberg[iceberg] = int(amount_by_iceberg[iceberg][1] * amount)
                to_be_sent += to_send_by_iceberg[iceberg]
            while not to_be_sent >= amount:
                for iceberg in icebergs:
                    if to_be_sent >= amount:
                        break
                    if to_send_by_iceberg[iceberg] + 1 <= amount_by_iceberg[iceberg] and self.icebergs_balance[iceberg] - to_send_by_iceberg[iceberg] > 0:
                        to_send_by_iceberg[iceberg] += 1
                        to_be_sent += 1
        print to_send_by_iceberg          
        return to_send_by_iceberg

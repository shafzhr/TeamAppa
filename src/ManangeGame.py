from penguin_game import * # pylint: disable=F0401
import quantitative_functions as qc
import itertools

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
        self.our_pengs_produce = self.my_qc.penguin_produce()

        self.icebergs_state = { iceberg: True for iceberg in self.my_icebergs } 
        self.our_icebergs_risk = { iceberg: self.risk_heuristic(iceberg) for iceberg in self.my_icebergs }
        self.our_upgrade_vals = { iceberg: self.upgrade_val(iceberg) for iceberg in self.my_icebergs }


        self.enemy_icebergs = game.get_enemy_icebergs()
        self.enemy_penguins_groups = game.get_enemy_penguin_groups()
        self.enemy_qc = qc.QuantitativeFunctions(game, game.get_enemy())
        self.enemy_balance = { iceberg: self.enemy_qc.get_iceberg_balance(iceberg) for iceberg in self.enemy_icebergs }
        self.enemy_pengs_sum = sum([ eny_ice.penguin_amount for eny_ice in self.enemy_icebergs ]) + sum([ group.penguin_amount for group in self.enemy_penguins_groups ])
        self.enemy_pengs_produce = self.enemy_qc.penguin_produce()



    def do_turn(self):
        self.defend()
        self.handle_conquering_neutrals()
        self.handle_trap()
        self.handle_transfer()
        self.handle_upgrading()
        self.conquer_enemy_icebergs()
        self.tie_breaker()


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
        Handles the neutral icebergs trap
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
            source_attacker, to_conquer = self.get_neutral_to_take(self.my_icebergs[0])
            needed_amount = self.get_amount_to_conquer_neutral(to_conquer)
            if (    to_conquer is not None
                and needed_amount <= self.icebergs_balance[source_attacker]
                ):
                self.smart_send(source_attacker, to_conquer, needed_amount)

    def handle_transfer(self):
        best_target = sorted(self.enemy_icebergs, key= lambda ice: ice.level, reverse= True)[0]
        self.transfer_to_closest_to_target(best_target)


    def get_amount_to_conquer_neutral(self, target):
        return self.neutral_iceberg_state(target) + 1


    def get_neutral_to_take(self, base):
        neutrals_not_attacked = self.game.get_neutral_icebergs()
        for neutral_ice in neutrals_not_attacked:
            attk_sum = 0
            for send in self.my_qc.get_player_sends_on_iceberg(neutral_ice):
                attk_sum += send.penguin_amount
            for send in self.my_qc.get_opposite_sends_on_iceberg(neutral_ice):
                attk_sum += send.penguin_amount
            if attk_sum > neutral_ice.penguin_amount:
                neutrals_not_attacked.remove(neutral_ice)

        neutral_lives = [iceberg.penguin_amount for iceberg in neutrals_not_attacked]
        min_lives = list(filter(lambda ice: ice.penguin_amount == min(neutral_lives), neutrals_not_attacked))
        # fix:
        # neutrals = sorted(min_lives, key=lambda ice: self.average_distance_from_my_icebergs(ice))
        # to be replaced with the line above:
        neutrals = sorted(min_lives, key=lambda ice: ice.get_turns_till_arrival(base))
        if neutrals == []:
            return None
        return neutrals[0]

    def neutral_iceberg_state(self, iceberg, n=None):
        my_groups = []
        eny_groups = []
        max_turn = 0
        for group in self.my_penguin_groups:
            if group.destination == iceberg:
                my_groups.append(group)
                if group.turns_till_arrival > max_turn:
                    max_turn = group.turns_till_arrival
        for group in self.enemy_penguins_groups:
            if group.destination == iceberg:
                eny_groups.append(group)
                if group.turns_till_arrival > max_turn:
                    max_turn = group.turns_till_arrival

        eny_groups_to_neutral = {i: [group for group in my_groups if group.turns_till_arrival == i] for i in
                                 range(max_turn + 1)}
        my_groups_to_neutral = {i: [group for group in eny_groups if group.turns_till_arrival == i] for i in
                                range(max_turn + 1)}
        neutral_pengs = iceberg.penguin_amount
        still_neutral = True
        peng_sum = 0
        for turn in range(0, max_turn):
            if n == turn:
                break
            current_sum = sum(my_groups_to_neutral[turn]) - sum(eny_groups_to_neutral[turn])
            if still_neutral:
                if current_sum > neutral_pengs:
                    still_neutral = False
                    peng_sum = current_sum - neutral_pengs
                elif current_sum < -1 * neutral_pengs:
                    still_neutral = False
                    peng_sum = neutral_pengs - current_sum
                else:
                    neutral_pengs -= current_sum

            else:
                if peng_sum < 0:
                    peng_sum -= iceberg.penguins_per_turn
                else:
                    peng_sum += iceberg.penguins_per_turn

                peng_sum += current_sum

        if still_neutral:
            return 0
        return peng_sum


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


    def enemy_target(self):
        """
        :type game: Game
        """
        for group in self.my_penguin_groups:
            if group.destination in self.game.get_neutral_icebergs():
                nearest_base = self.my_icebergs[0]
                for base in self.my_icebergs:
                    if base.get_turns_till_arrival(group.destination) < nearest_base.get_turns_till_arrival(group.destination):
                        nearest_base = base

                if nearest_base.get_turns_till_arrival(group.destination) > group.turns_till_arrival:
                    needed_peng_abs = abs(self.sum_all_enemy_groups_to_dest(group.destination)-group.destination.penguin_amount)
                    needed_peng_abs += nearest_base.get_turns_till_arrival(group.destination) * group.destination.penguins_per_turn
                    if self.icebergs_balance[nearest_base] >= needed_peng_abs:
                        if nearest_base.can_send_penguins(group.destination, needed_peng_abs):
                            self.smart_send(nearest_base, group.destination, needed_peng_abs)
    
    
    def sum_all_enemy_groups_to_dest(self, dest):
        enemy_group = self.enemy_penguins_groups
        sum_all = 0
        for x in enemy_group:
            if x.destination == dest:
                sum_all += x.penguin_amount
        return sum_all
    

    def transfer_to_closest_to_target(self, target):
        """
        :type target: Iceberg
        """
        nearest_to_target = self.my_icebergs[0]
        for our_ice in self.my_icebergs:
            if our_ice.get_turns_till_arrival(target) < nearest_to_target.get_turns_till_arrival(target):
                nearest_to_target = our_ice
        nearest_to_target = self.get_iceberg_with_nearest_enemy()
        if (1 == 2 and not all([ice.level == 4 for ice in self.my_icebergs])) or \
                self.our_pengs_produce < self.enemy_pengs_produce: 
            nearest_to_target = self.get_iceberg_with_nearest_enemy()

            if self.icebergs_balance[nearest_to_target] <= 0:
                return
            iceberg_sendable = self.max_tribute()
            if iceberg_sendable == {}:
                return

            amount_required = nearest_to_target.upgrade_cost - self.icebergs_balance[nearest_to_target] + 1
            if amount_required == 0:
                print "Can upgrade, not transfering"
                return
            helpers = [(ice, amount) for ice, amount in iceberg_sendable.iteritems() if
                       ice.level == ice.upgrade_level_limit]
            helpers = sorted(helpers, key=lambda x: self.risk_heuristic(x[0]))
            for helper, amount in helpers:
                real_send_amount = min(amount, amount_required)
                if helper.can_send_penguins(nearest_to_target, real_send_amount):
                    self.smart_send(helper, nearest_to_target, real_send_amount)
                    amount_required -= real_send_amount
                    if amount_required == 0:
                        break
            return

        iceberg_sendable = self.max_tribute()
        if iceberg_sendable == {}:
            return
        helpers = [(ice, amount) for ice, amount in iceberg_sendable.iteritems() if
                   ice.level <= ice.upgrade_level_limit and ice != nearest_to_target]
        if len(helpers) < 2:
            return
        helpers = sorted(helpers, key=lambda x: self.risk_heuristic(x[0]))
        for iceberg, sendable in helpers:
            if iceberg.can_send_penguins(nearest_to_target, sendable):
                self.smart_send(iceberg, nearest_to_target, sendable)

    def get_iceberg_with_nearest_enemy(self):
        icebergs = self.my_icebergs
        nearest_ice = icebergs[0]
        nearest_range = sorted(self.enemy_icebergs, key=lambda x: x.get_turns_till_arrival(nearest_ice))[0].get_turns_till_arrival(nearest_ice)
        for ice in icebergs:
            curr_range = sorted(self.enemy_icebergs, key=lambda x: x.get_turns_till_arrival(ice))[0].get_turns_till_arrival(ice)
            if curr_range < nearest_range:
                nearest_range = curr_range
                nearest_ice = ice
            elif curr_range == nearest_range:
                nearest_range_risk = self.risk_heuristic(nearest_ice)
                curr_risk = self.risk_heuristic(ice)
                if curr_risk > nearest_range_risk:
                    nearest_range = curr_range
                    nearest_ice = ice
        return nearest_ice
    
    
    def max_tribute(self):
        """
        Returns a dictionary of {tributers: max_tribute}
        """

        our_icebergs = self.my_icebergs
        tributers = {}
        # For each of our icebergs, checks whether they were used. If so, doesn't consider them as potential tributers.
        for iceberg in our_icebergs:
            if not self.icebergs_state[iceberg]:
                our_icebergs.remove(iceberg)
            else:
                tributers[iceberg] = 0
        # For each of the potential tributers, calculates the potential tribute. If it is positive, it changes the dictionary value, if not, it leaves it a 0.
        # Calculation: potential_tribute = our_penguins + our_level * distance - nearest_enemy_penguins
        for iceberg in tributers.keys():
            our_sends_sum = sum([send.penguin_amount for send in self.my_qc.get_player_sends_on_iceberg(iceberg)])
            #   our_sends_sum = 0
            #   nearest_enemy = nearest_enemy_iceberg(game, iceberg).penguin_amount
            nearest_enemy = 0
            potential_tribute = self.icebergs_balance[iceberg] - nearest_enemy - our_sends_sum
            if potential_tribute > 0:
                tributers[iceberg] = potential_tribute
            else:
                del tributers[iceberg]

        return tributers


    def tie_breaker(self):
        if not self.game.turn > self.game.max_turns * 28 / 30 or len(self.game.get_neutral_icebergs()) == 0:
            return
        attackers = [iceberg for iceberg in self.my_icebergs if
                     self.icebergs_balance[iceberg] > 0 and self.icebergs_state[iceberg]]
        if len(attackers) == 0:
            print "no attackers availabe"
            return
        target = sorted(self.game.get_neutral_icebergs(), key=lambda x: self.average_distance_from_enemy_icebergs(x))[0]
        if sorted(attackers, key=lambda x: x.get_turns_till_arrival(target), reverse=True)[0].get_turns_till_arrival(
                target) == self.game.max_turns - self.game.turn + 1:
            amount_required = target.penguin_amount + 1
            attacker = attackers[0]
            if attacker.can_send_penguins(target, amount_required):
                self.smart_send(attacker, target, amount_required)
    
    
    def average_distance_from_enemy_icebergs(self, iceberg):
        eny_icebergs = self.enemy_icebergs
        if iceberg in eny_icebergs:
            eny_icebergs.remove(iceberg)
        distances = [ice.get_turns_till_arrival(iceberg) for ice in eny_icebergs]
        return sum(distances) / len(distances)

    
    def conquer_enemy_icebergs(self):
        enemy_dangered = self.enemy_get_dangered_icebergs()
        for icebergs in enemy_dangered:
            if self.can_attack_enemy(icebergs[0], icebergs[1]):
                self.game.debug("Attacking. . . | " + str(icebergs[0].penguin_amount) + " | " + str(icebergs[1].penguin_amount))
                self.smart_send(icebergs[0], icebergs[1], self.get_send_to_attack(icebergs[0], icebergs[1]))
                break


    def enemy_get_dangered_icebergs(self):
        """
        ...
        :param game: current game state
        :type game: Game
        :type p_group: PenguinGroup
        :return: enemy's icebergs that are in danger by p_amount and danger_range
        """
        enemy_dangered_icebergs = []
        for our_iceberg in self.my_icebergs:
            for enemy_iceberg in self.enemy_icebergs:
                enemy_dangered_icebergs.append((our_iceberg, enemy_iceberg))

        return enemy_dangered_icebergs


    def can_attack_enemy(self, our_iceberg, enemy_iceberg):

        after_attacked_balance = self.icebergs_balance[our_iceberg]
        all_our_sends = sum([ send.penguin_amount for send in self.my_qc.get_player_sends_on_iceberg(our_iceberg) ])
        after_attacked_balance -= all_our_sends
        # after_attacked_balance -= sum([ send.penguin_amount for send in get_our_sends_on_iceberg(game, our_iceberg) ])
        if after_attacked_balance <= 0:
            return False
        enemy_defense_sum = 0
        # for eny_ice in game.get_enemy_icebergs():
        #     if eny_ice.get_turns_till_arrival(enemy_iceberg) <= our_iceberg.get_turns_till_arrival(enemy_iceberg) and enemy_iceberg != eny_ice:
        #         enemy_defense_sum += enemy_balance[eny_ice]
        for group in self.enemy_penguins_groups:
            if group.destination == enemy_iceberg:
                enemy_defense_sum += group.penguin_amount

        can_take = after_attacked_balance > enemy_iceberg.penguin_amount + enemy_defense_sum + our_iceberg.get_turns_till_arrival(enemy_iceberg) * enemy_iceberg.penguins_per_turn
        # can_take = use_peng(game, our_iceberg) + additional > enemy_iceberg.penguin_amount + our_iceberg.get_turns_till_arrival(enemy_iceberg) * is_not_neutral * enemy_iceberg.level

        for group in self.my_penguin_groups:
            if group.destination == enemy_iceberg:
                return False
        return can_take

    def get_send_to_attack(self, our_iceberg, enemy_iceberg):
        """
        """
        enemy_defense_sum = 0
        # for eny_ice in game.get_enemy_icebergs():
        #     if eny_ice.get_turns_till_arrival(enemy_iceberg) <= our_iceberg.get_turns_till_arrival(enemy_iceberg) and enemy_iceberg != eny_ice:
        #         enemy_defense_sum += enemy_balance[eny_ice]
        for group in self.enemy_penguins_groups:
            if group.destination == enemy_iceberg:
                enemy_defense_sum += group.penguin_amount
        amount = enemy_iceberg.penguin_amount + our_iceberg.get_turns_till_arrival(enemy_iceberg)*enemy_iceberg.penguins_per_turn + 1 + enemy_defense_sum
        return amount


    # ---------------------------------- Defend ---------------------------------------------
    
    def get_all_combinations(self, icebergs):
        combos = []
        for i in range(1, len(icebergs) + 1):
            current_combos = list(itertools.combinations(icebergs, i))
            for value in current_combos:
                combos.append(list(value))
        return combos


    def get_best_defense(self, defenders, target):
        combinations = self.get_all_combinations(defenders)
        for combo in combinations:
            turns_till_arrival = max([ice.get_turns_till_arrival(target) for ice in combo])
            if not sum([self.icebergs_balance[defender] for defender in combo]) + self.icebergs_balance[
                target] > 0 and self.penguin_amount_in_n_turns(target, turns_till_arrival) > 0:
                combinations.remove(combo)
        combinations = sorted(combinations, key=lambda x: len(x))
        if not len(combinations) == 0:
            return combinations[0]
        else:
            return None


    def get_continues_defense(self, defenders, target):
        """
        CONSIDERING get_best_defense RETURNED NONE
        :param defenders: List of Icebergs
        :param target: Iceberg
        :return: list of icebergs that can defend the target if they send their balance to target every turn.
        """
        combinations = self.get_all_combinations(defenders)
        # turns:
        mid_calc = sorted(self.my_qc.get_opposite_sends_on_iceberg(target), key=lambda x: x.turns_till_arrival, reverse=True)
        if not mid_calc:
            return
        turns = mid_calc[0].turns_till_arrival
        amount_required = -1 * (self.penguin_amount_in_n_turns(target, turns)) + 1
        for combo in combinations:
            if not sum([self.icebergs_balance[defender] for defender in combo]) + \
                    sum([defender.penguins_per_turn for defender in combo]) * turns >= amount_required:
                combinations.remove(combo)
        if not combinations:
            return None
        return sorted(combinations, key=lambda x: len(x))[0]


    def defend(self):
        """
        TODO: - create a list of all possible defender combinations and pick the one that involves the least amount
                of icebergs using the method get_all_combinations
                - in case non of the combinations is enough, consider the amount that will add up if a combination
                of icebergs starts sending their balance every turn. If a combination is found, make sure to turn their
                icebergs_state value negative.
        """
        need_help = {iceberg: [] for iceberg in self.my_icebergs if
                        self.icebergs_balance[iceberg] <= 0}  # { need_help_iceberg: [possible_helpers] }
        helps_icebergs = {iceberg: (0, []) for iceberg in self.my_icebergs if
                            iceberg not in need_help.keys()}  # { helper_iceberg: (amount_of_need_help, [icebergs that need the helper]) }
        for need_help_iceberg, possible_helps in need_help.iteritems():
            for iceberg in self.my_icebergs:
                # if self.penguin_amount_in_n_turns(need_help_iceberg, iceberg.get_turns_till_arrival(iceberg)) > 0 and self.icebergs_balance[iceberg] > 0:
                if self.penguin_amount_in_n_turns(need_help_iceberg, iceberg.get_turns_till_arrival(iceberg)) > 0 and \
                        self.icebergs_balance[iceberg] > 0 \
                        and iceberg.get_turns_till_arrival(need_help_iceberg) <= self.get_turns_to_help(
                    need_help_iceberg):
                    print("iceberg amount: {0}, balance: {1}".format(iceberg.penguin_amount,
                                                                        self.icebergs_balance[iceberg]))
                    possible_helps.append(iceberg)
                    if iceberg in helps_icebergs.keys():
                        helps_icebergs[iceberg] = (helps_icebergs[iceberg][0] + 1, helps_icebergs[iceberg][1])
                    else:
                        helps_icebergs[iceberg] = (1, [])
                    helps_icebergs[iceberg][1].append(need_help_iceberg)

        # for need_help_iceberg, possible_helps in need_help.iteritems():
        #     need_help[need_help_iceberg] = sorted(possible_helps, key=lambda x: risk_heuristic(x))

        our_icebergs_prioritized = sorted(need_help.keys(), key=lambda x: x.level, reverse=True)
        defenders_devision = {iceberg: [] for iceberg in our_icebergs_prioritized}
        if len(need_help.keys()) == 0:
            return
        max_defenders = len(helps_icebergs.keys()) / len(need_help.keys())
        if max_defenders == 0:
            max_defenders = 1
        for iceberg in our_icebergs_prioritized:
            if len(defenders_devision[iceberg]) > max_defenders:
                break
            possible_helps = need_help[iceberg]
            for helper in possible_helps:
                if helper in helps_icebergs.keys():
                    defenders_devision[iceberg].append(helper)
                    del helps_icebergs[helper]
        print defenders_devision
        for iceberg, defenders in defenders_devision.iteritems():
            defenders = sorted(defenders, key=lambda x: x.level, reverse=True)

            defense = self.get_best_defense(defenders, iceberg)
            if defense:
                amount_per_defender = self.split_amount_for_send(defense, abs(self.icebergs_balance[iceberg]) + 1)
                if amount_per_defender:
                    for defender in defense:
                        self.smart_send(defender, iceberg, amount_per_defender[defender])
                    return
            # continues defense
            defense = self.get_continues_defense(defenders, iceberg)
            if not defense:
                return

            for defender in defense:
                self.smart_send(defender, iceberg, self.icebergs_balance[defender])
                # self.icebergs_state[defender] = False


    def split_amount_for_send(self, icebergs, amount):
        """
        iceberg_to_send: target iceberg
        icebergs: list of icebergs to send from
        amount: int, total amount to be sent

        returns a dictionary. for each iceberg in icebergs returns how much to send.
        """
        sum_balance = 0
        for sender in icebergs:
            sum_balance += self.icebergs_balance[sender]

        amount_by_iceberg = {iceberg: (self.icebergs_balance[iceberg],
                                       self.icebergs_balance[iceberg] / sum_balance) for iceberg in
                             icebergs}
        to_send_by_iceberg = {iceberg: 0 for iceberg in icebergs}
        # amount_by_iceberg: second value in tuple is ratio between amount and sendable penguin amount for iceberg.
        sum = 0
        to_be_sent = 0
        for key, value in amount_by_iceberg.iteritems():
            sum += value[0]
        if sum < amount:
            return None
        else:
            for iceberg in icebergs:
                to_send_by_iceberg[iceberg] = int(amount_by_iceberg[iceberg][1] * amount)
                to_be_sent += to_send_by_iceberg[iceberg]
            while not to_be_sent >= amount:
                for iceberg in icebergs:
                    if to_be_sent >= amount:
                        break
                    if to_send_by_iceberg[iceberg] + 1 <= amount_by_iceberg[iceberg] and self.icebergs_balance[
                        iceberg] - \
                            to_send_by_iceberg[iceberg] > 0:
                        to_send_by_iceberg[iceberg] += 1
                        to_be_sent += 1
        print to_send_by_iceberg
        return to_send_by_iceberg

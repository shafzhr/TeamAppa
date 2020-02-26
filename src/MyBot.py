from penguin_game import * # pylint: disable=F0401
import math


def neutral_icebergs_distances(game, my_iceberg):
    """
    :params game: The current game state
    :type game: Game
    :type my_iceberg: Iceberg
    """
    neutral_icebergs = game.get_neutral_icebergs()
    sorted_neutral_icebergs = []
   
    while len(neutral_icebergs) > 0:
        min_iceberg = neutral_icebergs[0]
        for x in neutral_icebergs:
            if my_iceberg.get_turns_till_arrival(x) < my_iceberg.get_turns_till_arrival(min_iceberg):
                min_iceberg = x
      
        sorted_neutral_icebergs.append(min_iceberg)
        neutral_icebergs.remove(min_iceberg)
    return sorted_neutral_icebergs

def neutral_nearest_iceberg(game, my_iceberg):
    """
    :type game: Game
    :type my_iceberg: Iceberg
    """
    neutral_distances = neutral_icebergs_distances(game, my_iceberg)
    if len(neutral_distances) > 0:
        if len(neutral_distances) > 1:
            if neutral_distances[0].level < neutral_distances[1].level:
                return neutral_distances[0]
            else:
                return neutral_distances[1]
        else:
            return neutral_distances[0]
    return None




def enemy_get_dangered_icebergs(game, p_amount = 35, danger_range = 20):
    """
    ...
    :param game: current game state
    :type game: Game
    :type p_group: PenguinGroup
    :return: enemy's icebergs that are in danger by p_amount and danger_range
    """
    enemy_dangered_icebergs = []
    for our_iceberg in game.get_my_icebergs():
        for enemy_iceberg in game.get_enemy_icebergs():
            if our_iceberg.get_turns_till_arrival(enemy_iceberg) <= danger_range and enemy_iceberg.penguin_amount <= p_amount:
                enemy_dangered_icebergs.append((our_iceberg, enemy_iceberg))

    return enemy_dangered_icebergs


def enemy_priority(game):
    icebergs = game.get_enemy_icebergs()
    maxberg = icebergs[0]
    for ice in icebergs:
        if ice.level > maxberg.level:
            maxberg = ice
        
    return maxberg
    
    
def our_attacked_icebergs(game, distance=20):
    """
    returns a list of attacked icebergs
    :type game: Game
    """
    attacked = []
    enemy_penguin_groups = game.get_enemy_penguin_groups()
    for enemy_group in enemy_penguin_groups:
        if enemy_group.destination in game.get_my_icebergs():
            if enemy_group.turns_till_arrival <= distance:
                if all_groups_to_dest(game, enemy_group.destination) >= enemy_group.destination.penguin_amount + enemy_group.turns_till_arrival*enemy_group.destination.level:
                    attacked.append(enemy_group.destination)
                    
    return attacked


def all_groups_to_dest(game, dest):
    enemy_group = game.get_enemy_penguin_groups()
    sum = 0
    for x in enemy_group:
        if x.destination == dest:
            sum += x.penguin_amount
    return sum


def all_groups_to_dest_minus_distances(game, dest):
    """
    :type game: Game
    :type dest: Iceberg
    """
    groups_per_distance = {}
    for enemy_group in game.get_enemy_penguin_groups():
        if enemy_group.destination == dest:
            if enemy_group.turns_till_arrival in groups_per_distance.keys():
                groups_per_distance[enemy_group.turns_till_arrival] += enemy_group.penguin_amount
            else:  
                groups_per_distance[enemy_group.turns_till_arrival] = enemy_group.penguin_amount
    if len(groups_per_distance.keys()) == 0:
        return dest.penguin_amount
    min_balance = dest.penguin_amount
    balance = dest.penguin_amount
    for turn in range(1, max(groups_per_distance.keys()) +1):
        balance += dest.penguins_per_turn
        if turn in groups_per_distance.keys():
            balance -= groups_per_distance[turn]
        for send in get_our_sends_on_iceberg(game, dest):
            if send.turns_till_arrival == turn:
                balance += send.penguin_amount
        if balance < min_balance:
            min_balance = balance
    # balance = dest.penguin_amount + dest.level*max(groups_per_distance.keys())
    # for key, value in groups_per_distance.iteritems():
    #     balance -= value
    return min_balance-1



def get_our_sends_on_iceberg(game, iceberg):
    sends = []
    for send in game.get_my_penguin_groups():
        if send.destination == iceberg:
            sends.append(send)
    return sends


def can_attack(game, our_iceberg, enemy_iceberg, additional = 0, is_not_neutral = 1):
    global enemy_balance

    after_attacked_balance = all_groups_to_dest_minus_distances(game, our_iceberg)
    all_our_sends = sum([ send.penguin_amount for send in get_our_sends_on_iceberg(game, our_iceberg) ])
    after_attacked_balance -= all_our_sends
    # after_attacked_balance -= sum([ send.penguin_amount for send in get_our_sends_on_iceberg(game, our_iceberg) ])
    if after_attacked_balance <= 0:
        return False
    enemy_defense_sum = 0
    if is_not_neutral == 1:
        # for eny_ice in game.get_enemy_icebergs():
        #     if eny_ice.get_turns_till_arrival(enemy_iceberg) <= our_iceberg.get_turns_till_arrival(enemy_iceberg) and enemy_iceberg != eny_ice:
        #         enemy_defense_sum += enemy_balance[eny_ice]
        for group in game.get_enemy_penguin_groups():
            if group.destination == enemy_iceberg:
                enemy_defense_sum += group.penguin_amount

    can_take = after_attacked_balance + additional > enemy_iceberg.penguin_amount + enemy_defense_sum + our_iceberg.get_turns_till_arrival(enemy_iceberg) * is_not_neutral * enemy_iceberg.penguins_per_turn
    # can_take = use_peng(game, our_iceberg) + additional > enemy_iceberg.penguin_amount + our_iceberg.get_turns_till_arrival(enemy_iceberg) * is_not_neutral * enemy_iceberg.level

    for group in game.get_my_penguin_groups():
        if group.destination == enemy_iceberg:
            return False
    return can_take

def get_send_to_attack(game, our_iceberg, enemy_iceberg):
    """
    """
    enemy_defense_sum = 0
    # for eny_ice in game.get_enemy_icebergs():
    #     if eny_ice.get_turns_till_arrival(enemy_iceberg) <= our_iceberg.get_turns_till_arrival(enemy_iceberg) and enemy_iceberg != eny_ice:
    #         enemy_defense_sum += enemy_balance[eny_ice]
    for group in game.get_enemy_penguin_groups():
        if group.destination == enemy_iceberg:
            enemy_defense_sum += group.penguin_amount
    amount = enemy_iceberg.penguin_amount + our_iceberg.get_turns_till_arrival(enemy_iceberg)*enemy_iceberg.penguins_per_turn + 1 + enemy_defense_sum
    return amount


def neutral_get_send_to_attack(game, our_iceberg, enemy_iceberg):
    """
    """
    return enemy_iceberg.penguin_amount + 1


def upgrade_val(game, iceberg):
    if iceberg.level == iceberg.upgrade_level_limit:
        return 0
    cost_eff = 1.0/iceberg.upgrade_cost*1.0 / iceberg.upgrade_value
    final_val = (iceberg.penguin_amount*1.0/iceberg.upgrade_cost)*(iceberg.penguins_per_turn + iceberg.upgrade_value)*cost_eff*1.0
    print ("UPGRADE VAL: " + str(final_val))
    return final_val


def enemy_icebergs_distances(game, my_iceberg):
    """
    :params game: The current game state
    :type game: Game
    :type my_iceberg: Iceberg
    """
    enemy_icebergs = game.get_enemy_icebergs()
    sorted_enemy_icebergs = []

    while len(enemy_icebergs) > 0:
        min_iceberg = enemy_icebergs[0]
        for x in enemy_icebergs:
            if my_iceberg.get_turns_till_arrival(x) < my_iceberg.get_turns_till_arrival(min_iceberg):
                min_iceberg = x

        sorted_enemy_icebergs.append(min_iceberg)
        enemy_icebergs.remove(min_iceberg)
    if my_iceberg in sorted_enemy_icebergs:
        sorted_enemy_icebergs.remove(my_iceberg)
    return sorted_enemy_icebergs[0]


def our_icebergs_distances(game, my_iceberg):
    """
    :params game: The current game state
    :type game: Game
    :type my_iceberg: Iceberg
    """
    our_icebergs = game.get_my_icebergs()
    sorted_our_icebergs = []
   
    while len(our_icebergs) > 0:
        min_iceberg = our_icebergs[0]
        for x in our_icebergs:
            if my_iceberg.get_turns_till_arrival(x) < my_iceberg.get_turns_till_arrival(min_iceberg):
                min_iceberg = x
      
        sorted_our_icebergs.append(min_iceberg)
        our_icebergs.remove(min_iceberg)
    if my_iceberg in sorted_our_icebergs:
        sorted_our_icebergs.remove(my_iceberg)
    if sorted_our_icebergs == []:
        return []
    return sorted_our_icebergs[0]

def our_abs(n):
    if n == 0:
        return 0
    elif n > 0:
        return n
    else:
        return n*(-1)
    
def get_enemy_balance_iceberg(game, dest):
    """
    :type game: game
    :type dest: Iceberg
    """
    groups_per_distance = {}
    for group in game.get_my_penguin_groups():
        if group.destination == dest:
            if group.turns_till_arrival in groups_per_distance.keys():
                groups_per_distance[group.turns_till_arrival] += group.penguin_amount
            else:  
                groups_per_distance[group.turns_till_arrival] = group.penguin_amount
    if len(groups_per_distance.keys()) == 0:
        return dest.penguin_amount
    min_balance = dest.penguin_amount
    balance = dest.penguin_amount
    for turn in range(1, max(groups_per_distance.keys()) +1):
        balance += dest.penguins_per_turn
        if turn in groups_per_distance.keys():
            balance -= groups_per_distance[turn]
        for send in get_enemy_sends_on_iceberg(game, dest):
            if send.turns_till_arrival == turn:
                balance += send.penguin_amount
        if balance < min_balance:
            min_balance = balance
    return min_balance-1


def get_enemy_sends_on_iceberg(game, iceberg):
    sends = []
    for send in game.get_enemy_penguin_groups():
        if send.destination == iceberg:
            sends.append(send)
    return sends

    
def ko(game, base):
    """
    Heavy attack with multiple icebergs
    :type game: Game
    :type base: Iceberg
    """
    global icebergs_balance
    
    target = sorted( game.get_enemy_icebergs(), key= lambda ice: ice.get_turns_till_arrival(base) )[0]
    if get_enemy_balance_iceberg(game, target) < 0:
        return
    ice1 = target
    to_send_from = []
    our_sum = 0
    enemy_sum = ice1.penguin_amount
    for turn in range(1, 30):
        enemy_sum += ice1.penguins_per_turn
        for our_ice in game.get_my_icebergs():
            if not icebergs_state[our_ice]:  # !!!
                continue
            if our_ice.get_turns_till_arrival(ice1) == turn:
                our_sum += icebergs_balance[our_ice]
                to_send_from.append(our_ice)
        for eny_ice in game.get_enemy_icebergs():
            if eny_ice.get_turns_till_arrival(ice1) == turn:
                enemy_sum += eny_ice.penguin_amount + turn*eny_ice.penguins_per_turn
        for group in game.get_enemy_penguin_groups():
            if group.destination == ice1 and group.turns_till_arrival == turn:
                enemy_sum += group.penguin_amount
        if our_sum > enemy_sum and to_send_from != []:
            for sender in to_send_from:
                our_sends_sum = sum([send.penguin_amount for send in get_our_sends_on_iceberg(game, sender)])
                if sender.can_send_penguins(ice1, icebergs_balance[sender] - our_sends_sum):
                    smart_send(sender, ice1, icebergs_balance[sender] - our_sends_sum)
                    print "koing . . ."


def get_possible_defense(game, enemy_iceberg, turns):
    global enemy_balance
    enemy_defense_sum = 0
    for eny_ice in game.get_enemy_icebergs():
        defense_turns = eny_ice.get_turns_till_arrival(enemy_iceberg)
        if defense_turns <= turns and enemy_iceberg != eny_ice:
            enemy_defense_sum += enemy_balance[eny_ice] + ((turns-defense_turns)*eny_ice.penguins_per_turn)
    # for group in game.get_enemy_penguin_groups():
    #     if group.destination == enemy_iceberg:
    #         enemy_defense_sum += group.penguin_amount
    return enemy_defense_sum


def smart_send(src, dest, p_amount):
    """
    :type p_amount: int
    :type src: Iceberg
    :type dest: Iceberg
    """
    global icebergs_state
    global icebergs_balance

    if not icebergs_state[src]:
        return
    if p_amount > 0:
        src.send_penguins(dest, p_amount)
        icebergs_balance[src] -= p_amount
    else:
        print "Cant send negative!!!!!"

    
def enemy_target(game):
    """
    :type game: Game
    """
    global icebergs_balance
    for group in game.get_enemy_penguin_groups():
        if group.destination in game.get_neutral_icebergs():
            nearest_base = game.get_my_icebergs()[0]
            for base in game.get_my_icebergs():
                if base.get_turns_till_arrival(group.destination) < nearest_base.get_turns_till_arrival(group.destination):
                    nearest_base = base
            if nearest_base.get_turns_till_arrival(group.destination) > group.turns_till_arrival:
                if icebergs_balance[nearest_base] >= our_abs(all_groups_to_dest(game, group.destination)-group.destination.penguin_amount) + nearest_base.get_turns_till_arrival(group.destination):
                    if nearest_base.can_send_penguins(group.destination, our_abs(all_groups_to_dest(game, group.destination)-group.destination.penguin_amount) + nearest_base.get_turns_till_arrival(group.destination)):
                        smart_send(nearest_base, group.destination, our_abs(all_groups_to_dest(game, group.destination)-group.destination.penguin_amount) + nearest_base.get_turns_till_arrival(group.destination))
                        print "DA-VI --> " + str(our_abs(all_groups_to_dest(game, group.destination)-group.destination.penguin_amount) + nearest_base.get_turns_till_arrival(group.destination)) + " penguin_amount = "+ str(nearest_base.penguin_amount)
                        print "DA-VI2  --> " + str(our_abs(all_groups_to_dest(game, group.destination)-group.destination.penguin_amount)) + " " + str(nearest_base.get_turns_till_arrival(group.destination))
                        print "DA-VI3 --> " + str(nearest_base.get_turns_till_arrival(group.destination)) + "     " + str(group.turns_till_arrival)


def use_peng(game,iceberg):
    
    sum = 0
    for x in game.get_enemy_penguin_groups():
        if x.destination == iceberg:
            sum += x.penguin_amount
    return iceberg.penguin_amount - sum - 2


def nearest_enemy_penguin_group_distance(game, iceberg):
    """
    :type game: Game
    :type iceberg: Iceberg
    """
    enemy_groups = game.get_enemy_penguin_groups()
    if enemy_groups == []:
        return -1
    
    nearest_distance = enemy_groups[0].turns_till_arrival
    for group in enemy_groups:
        if group.destination == iceberg and group.turns_till_arrival < nearest_distance:
            nearest_distance = group.turns_till_arrival
    return nearest_distance


def penguin_amount_in_n_turns(game, iceberg, n):
    level = iceberg.level
    penguin_sum = iceberg.penguin_amount + level * n
    for group in game.get_enemy_penguin_groups():
        if group.destination == iceberg and group.turns_till_arrival <= n:
            penguin_sum -= group.penguin_amount
    for group in game.get_my_penguin_groups():
        if group.destination == iceberg and group.turns_till_arrival <= n:
            penguin_sum += group.penguin_amount
    return penguin_sum

def get_turns_to_help(game, iceberg):
    sends = [send.turns_till_arrival for send in get_enemy_sends_on_iceberg(game, iceberg)]
    for i in range(max(sends)+1):
        if penguin_amount_in_n_turns(game, iceberg, i) <= 0:
            return i
    return 0

def defend(game):
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
            if icebergs_balance[defender] + icebergs_balance[iceberg] > 0 and penguin_amount_in_n_turns(game, iceberg, iceberg.get_turns_till_arrival(defender)) > 0:
                smart_send(defender, iceberg, our_abs(icebergs_balance[iceberg]) + 1)
                already_done = True
                break
        if not already_done:
            defenders_needed = 0
            sum = 0
            for defender in defenders:
                defenders_needed += 1
                sum += icebergs_balance[defender]
                if sum > our_abs(icebergs_balance[iceberg]):
                    break
            if sum > icebergs_balance[iceberg]:
                print "ACTUAL AMOUNT ",our_abs(icebergs_balance[iceberg]) + 1
                amount_per_defender = split_amount_for_send(defenders, our_abs(icebergs_balance[iceberg]) + 1, game)
                if amount_per_defender is None:
                    return
                for defender, amount in amount_per_defender.iteritems():
                    print "amount: ", amount
                    smart_send(defender, iceberg, our_abs(amount))
                print "Defending!/?????????????????????????????????"
                print "Defenders: " + str(len(defenders)) + "--------------------_"
            else:
                print "Gave up----------------------------------"


def split_amount_for_send(icebergs, amount, game):
    """
    iceberg_to_send: target ICEBERG
    icebergs: LIST of icebergs to send from
    amount: int, total amount to be sent
    :type game: Game
    
    returns a dictionary. for each iceberg in icebergs returns how much to send.
    """
    sum_balance = 0
    for sender in icebergs:
        sum_balance += all_groups_to_dest_minus_distances(game, sender)
    
    amount_by_iceberg = {iceberg: (all_groups_to_dest_minus_distances(game, iceberg), all_groups_to_dest_minus_distances(game, iceberg) / sum_balance) for iceberg in icebergs}
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
                if to_send_by_iceberg[iceberg] + 1 <= amount_by_iceberg[iceberg] and icebergs_balance[iceberg] - to_send_by_iceberg[iceberg] > 0:
                    to_send_by_iceberg[iceberg] += 1
                    to_be_sent += 1
    print to_send_by_iceberg          
    return to_send_by_iceberg
                        
        
def old_ko(game, base):
    """
    Heavy attack with multiple icebergs
    :type game: Game
    :type base: Iceberg
    """
    global icebergs_balance

    icebergs = game.get_enemy_icebergs()
    ices = [icebergs[0]]
    for ice in icebergs:
        if ice.level == ices[0].level:
            ices.append(ice)
        if ice.level > ices[0].level:
            ices = [ice]
    target = ices[0]
    for x in ices:
        if x.get_turns_till_arrival(base) < target.get_turns_till_arrival(base):
            target = x
    
    ice1 = target
    sum = 0
    farest_iceberg = game.get_my_icebergs()[0]
    for iceberg in game.get_my_icebergs():
        balance = icebergs_balance[iceberg]
        if balance > 0:
            sum += balance
        if iceberg.get_turns_till_arrival(ice1) > farest_iceberg.get_turns_till_arrival(ice1):
            farest_iceberg = iceberg
    for fire in game.get_my_icebergs():
        if fire.can_send_penguins(ice1, icebergs_balance[fire]) and sum > ice1.penguin_amount + ice1.level*farest_iceberg.get_turns_till_arrival(ice1):
            smart_send(fire, ice1, icebergs_balance[fire])


def risk_heuristic(game, our_ice):
    """
    :type game: Game
    :type our_ice: Iceberg
    """
    global icebergs_balance
    risk = 0
    for eny_ice in game.get_enemy_icebergs():
        risk += eny_ice.penguin_amount*1.0/((eny_ice.get_turns_till_arrival(our_ice)*1.0)**2)
    # for eny_group in game.get_enemy_penguin_groups():
    #     if eny_group.destination == our_ice:
    #         risk += eny_group.penguin_amount*1.0/((eny_group.turns_till_arrival*1.0)**2)
    # for our_group in game.get_my_penguin_groups():
    #     if our_group.destination == our_ice:
    #         risk -= our_group.penguin_amount*1.0/((our_group.turns_till_arrival*1.0)**2)
    total = get_our_pengs(game)
    risk = risk*1.0 * (1.0/(our_ice.level ** 2))
    # risk = risk*1.0 * ((total-icebergs_balance[our_ice]*1.0) / total*1.0) * (1.0/(our_ice.level * 10.0))
    # risk = risk*1.0 * (1.0 / icebergs_balance[our_ice]*1.0) * (1.0/(our_ice.level * 10.0))
    print "RISK_VAL:" + str(risk)
    return risk


def get_iceberg_with_nearest_enemy(game):
    icebergs = game.get_my_icebergs()
    nearest_ice = icebergs[0]
    nearest_range = sorted(game.get_enemy_icebergs(), key=lambda x: x.get_turns_till_arrival(nearest_ice))[0].get_turns_till_arrival(nearest_ice)
    for ice in icebergs:
        curr_range = sorted(game.get_enemy_icebergs(), key=lambda x: x.get_turns_till_arrival(ice))[0].get_turns_till_arrival(ice)
        if curr_range < nearest_range:
            nearest_range = curr_range
            nearest_ice = ice
        elif curr_range == nearest_range:
            nearest_range_risk = risk_heuristic(game, nearest_ice)
            curr_risk = risk_heuristic(game, ice)
            if curr_risk > nearest_range_risk:
                nearest_range = curr_range
                nearest_ice = ice
    return nearest_ice


def transfer_to_closest_to_target(game, target):
    """
    :type game: Game
    :type target: Iceberg
    """
    global icebergs_balance
    nearest_to_target = game.get_my_icebergs()[0]
    for our_ice in game.get_my_icebergs():
        if our_ice.get_turns_till_arrival(target) < nearest_to_target.get_turns_till_arrival(target):
            nearest_to_target = our_ice
    # nearest_to_target = sorted(game.get_my_icebergs(), key=lambda x: risk_heuristic(game, x), reverse=True)[0]
    nearest_to_target = get_iceberg_with_nearest_enemy(game)
    if (1==2 and not all([ice.level == 4 for ice in game.get_my_icebergs()]) ) or penguin_produce(game, game.get_myself()) < penguin_produce(game, game.get_enemy()):
        # nearest_to_target = sorted(game.get_my_icebergs(), key=lambda x: x.level)[0]
        nearest_to_target = get_iceberg_with_nearest_enemy(game)
        # nearest_to_target = sorted(game.get_my_icebergs(), key=lambda x: risk_heuristic(game, x), reverse=True)[0]

        if icebergs_balance[nearest_to_target] <= 0:
            return
        iceberg_sendable = max_tribute(game)
        if iceberg_sendable == {}:
            return
    
        amount_required = nearest_to_target.upgrade_cost - icebergs_balance[nearest_to_target] + 1
        if amount_required == 0:
            print "Can upgrade, not transfering"
            return
        helpers = [ (ice, amount) for ice, amount in iceberg_sendable.iteritems() if ice.level == 4]
        helpers = sorted(helpers, key=lambda x: risk_heuristic(game, x[0]))
        for helper, amount in helpers:
            real_send_amount = min(amount, amount_required)
            if helper.can_send_penguins(nearest_to_target, real_send_amount):
                smart_send(helper, nearest_to_target, real_send_amount)
                amount_required -= real_send_amount
                if amount_required == 0:
                    break
        return
    
    iceberg_sendable = max_tribute(game)
    if iceberg_sendable == {}:
        return
    helpers = [ (ice, amount) for ice, amount in iceberg_sendable.iteritems() if ice.level <= 4 and ice != nearest_to_target]
    if len(helpers) < 2:
        return
    helpers = sorted(helpers, key=lambda x: risk_heuristic(game, x[0]))
    for iceberg, sendable in helpers:
        if iceberg.can_send_penguins(nearest_to_target, sendable):
            smart_send(iceberg, nearest_to_target, sendable)


def nearest_enemy_iceberg(game, dest):
  """
  type game: Game
  type dest: Iceberg
  """
  enemy_icebergs = game.get_enemy_icebergs()
  #sorting the list of the enemy icebergs by their distances from the given destination island.
  enemy_icebergs = sorted(enemy_icebergs, key = lambda x: dest.get_turns_till_arrival(x))
  #returns the closest one
  return enemy_icebergs[0]


def max_tribute(game):
  """
  Returns a dictionary of {tributers: max_tribute}
  type game: Game
  """
  global icebergs_state
  global icebergs_balance
  our_icebergs = game.get_my_icebergs()
  tributers = {}
  #For each of our icebergs, checks whether they were used. If so, doesn't consider them as potential tributers.
  for iceberg in our_icebergs:
      if not icebergs_state[iceberg]:
          our_icebergs.remove(iceberg)
      else:
          tributers[iceberg] = 0
  #For each of the potential tributers, calculates the potential tribute. If it is positive, it changes the dictionary value, if not, it leaves it a 0.
  #Calculation: potential_tribute = our_penguins + our_level * distance - nearest_enemy_penguins
  for iceberg in tributers.keys():
      our_sends_sum = sum( [ send.penguin_amount for send in get_our_sends_on_iceberg(game, iceberg) ] )
    #   our_sends_sum = 0
    #   nearest_enemy = nearest_enemy_iceberg(game, iceberg).penguin_amount
      nearest_enemy = 0
      potential_tribute = icebergs_balance[iceberg] - nearest_enemy - our_sends_sum
      if potential_tribute > 0:
          tributers[iceberg] = potential_tribute
      else:
          del tributers[iceberg]
 
  return tributers

def penguin_produce(game, player):
    if player == game.get_myself():
        return sum([ice.level for ice in game.get_my_icebergs()])
    else:
        return sum([ice.level for ice in game.get_enemy_icebergs()])


def average_distance_from_enemy_icebergs(game, iceberg):
    distance = sum([eny_iceberg.get_turns_till_arrival(iceberg) for eny_iceberg in game.get_enemy_icebergs()])
    distance /= len(game.get_enemy_icebergs())
    return distance


def tie_breaker(game):
    if not game.turn > game.max_turns * 28 / 30 or len(game.get_neutral_icebergs()) == 0:
        return 
    attackers = [iceberg for iceberg in game.get_my_icebergs() if icebergs_balance[iceberg] > 0 and icebergs_state[iceberg]]
    if len(attackers) == 0:
        print "no attackers availabe"
        return
    target = sorted(game.get_neutral_icebergs(), key=lambda x: average_distance_from_enemy_icebergs(game, x))[0]
    if sorted(attackers, key=lambda x: x.get_turns_till_arrival(target), reverse=True)[0].get_turns_till_arrival(target) == game.max_turns - game.turn+1:
        amount_required = target.penguin_amount + 1
        attacker = attackers[0]
        if attacker.can_send_penguins(target, amount_required):
            smart_send(attacker, target, amount_required)


def help_upgarde(game):
    helpers = [ice for ice in game.get_my_icebergs() if ice.level == 4 and icebergs_balance[ice] > 0]
    to_upgrade = sorted(game.get_my_icebergs(), key=lambda x: x.level)[0]
    if to_upgrade.level == 4 or len(game.get_my_icebergs()) <= 4 or len(helpers) == 0:
        return
    amount_required = to_upgrade.upgrade_cost - to_upgrade.penguin_amount + 1
    if amount_required < sum([icebergs_balance[helper] for helper in helpers]) and amount_required > 0:
        amounts = split_amount_for_send(helpers, amount_required, game)
        for helper in helpers:
            if helper.can_send_penguins(to_upgrade, amounts[helper]):
                smart_send(helper, to_upgrade, amounts[helper])


def get_neutral_to_take(game, base):
    neutrals_not_attacked = game.get_neutral_icebergs()
    # for pgroup in game.get_all_penguin_groups():
    #     if pgroup.destination in neutrals_not_attacked:
    #         neutrals_not_attacked.remove(pgroup.destination)
    for neutral_ice in neutrals_not_attacked:
        attk_sum = 0
        for send in get_our_sends_on_iceberg(game, neutral_ice):
            attk_sum += send.penguin_amount
        for send in get_enemy_sends_on_iceberg(game, neutral_ice):
            attk_sum += send.penguin_amount
        if attk_sum > neutral_ice.penguin_amount:
            neutrals_not_attacked.remove(neutral_ice)
        
    neutral_lives = [ iceberg.penguin_amount for iceberg in neutrals_not_attacked ]
    min_lives = list(filter(lambda ice: ice.penguin_amount == min(neutral_lives), neutrals_not_attacked ))
    neutrals = sorted(min_lives, key= lambda ice: ice.get_turns_till_arrival(base) )
    if neutrals == []:
        return None
    return neutrals[0]
    

def get_enemy_pengs(game):
    global enemy_pengs_sum
    return enemy_pengs_sum

def get_our_pengs(game):
    global our_pengs_sum
    return our_pengs_sum

icebergs_state = {}
icebergs_balance = {}
enemy_balance = {}
state = 1 # 1 = attack, 0 = defend
turns_no_attacks_streak = 0
our_pengs_sum = 0
enemy_pengs_sum = 0
mint = 100
def do_turn(game):
    """
    Makes the bot run a single turn.
    :param game: the current game state.
    :type game: Game
    """
    global icebergs_state
    global icebergs_balance
    global turns_no_attacks_streak
    global enemy_balance
    global our_pengs_sum
    global enemy_pengs_sum
    global mint

    our_pengs_sum = sum([ ice.penguin_amount for ice in game.get_my_icebergs() ]) + sum([ group.penguin_amount for group in game.get_my_penguin_groups() ])
    enemy_pengs_sum = sum([ eny_ice.penguin_amount for eny_ice in game.get_enemy_icebergs() ]) + sum([ group.penguin_amount for group in game.get_enemy_penguin_groups() ])
    
    icebergs_state = { iceberg: True for iceberg in game.get_my_icebergs() }
    icebergs_balance = { iceberg: all_groups_to_dest_minus_distances(game, iceberg) for iceberg in game.get_my_icebergs() }
    enemy_balance = { iceberg: get_enemy_balance_iceberg(game, iceberg) for iceberg in game.get_enemy_icebergs() }
    
    base = game.get_my_icebergs()[0]

    if game.get_all_penguin_groups() == []:
        turns_no_attacks_streak += 1
    else:
        turns_no_attacks_streak = 0
    
    if turns_no_attacks_streak >= 150:
        old_ko(game, base)
    
    if base.level == 1:
        if base.can_upgrade():
            base.upgrade()
    else:

        defend(game)
        risk_more_than_zero = list(filter(lambda x: risk_heuristic(game, x) != 0, game.get_my_icebergs()))  
        if risk_more_than_zero:
            upgrades = sorted([ ice for ice in risk_more_than_zero ], key=lambda x: upgrade_val(game, x))
            to_upgrade = upgrades[-1]
            if to_upgrade.can_upgrade() and not to_upgrade.already_acted and all_groups_to_dest_minus_distances(game, to_upgrade) > to_upgrade.upgrade_cost:
                to_upgrade.upgrade()
                icebergs_state[to_upgrade] = False

        # transfer_to_closest_to_target(game, best_target)
        if len(game.get_neutral_icebergs()) != 0:
            enemy_target(game)
            
        our_conquered_icebergs = game.get_my_icebergs()# + [ eny_ice for eny_ice in game.get_enemy_icebergs() if enemy_balance[eny_ice] < 0 ]
        if len(our_conquered_icebergs) < len(game.get_all_icebergs())/2+1 and len(game.get_neutral_icebergs()) != 0:
            # to_attack = neutral_nearest_iceberg(game, base)
            to_attack = get_neutral_to_take(game, base)
            if to_attack is not None:
                if can_attack(game, base, to_attack, 0, 0):
                    if neutral_get_send_to_attack(game, base, to_attack)+0 <= icebergs_balance[base]:
                        smart_send(base, to_attack, neutral_get_send_to_attack(game, base, to_attack)+0)
        
        best_target = sorted(game.get_enemy_icebergs(), key= lambda ice: ice.level, reverse= True)[0]
        # if len(game.get_my_icebergs()) >= 4:
        transfer_to_closest_to_target(game, best_target)
        
        

        if 1==1 or penguin_produce(game, game.get_myself()) >= 7:
            enemy_dangered = enemy_get_dangered_icebergs(game)
            if enemy_dangered != []:
                game.debug("YAYA ---> " + " our_penguin_amount = "+ str(enemy_dangered[0][0].penguin_amount)+ " enemy_penguin_amount = "+ str(enemy_dangered[0][1].penguin_amount) + 
                " Turns till enemy = " + str(enemy_dangered[0][0].get_turns_till_arrival(enemy_dangered[0][1]))
                + " Enemy to our = " + str(all_groups_to_dest(game,enemy_dangered[0][0])))
                game.debug("YAYA2 ---> " + str(enemy_dangered))
            if enemy_dangered != []:
                for icebergs in enemy_dangered:
                    if can_attack(game, icebergs[0], icebergs[1]):
                        game.debug("Attacking. . . | " + str(icebergs[0].penguin_amount) + " | " + str(icebergs[1].penguin_amount))
                        smart_send(icebergs[0], icebergs[1], get_send_to_attack(game, icebergs[0], icebergs[1]))
                        break
            
        # if game.turn >= 40:
        #     ko(game, base)

        # if penguin_produce(game, game.get_enemy()) > penguin_produce(game, game.get_myself()):
        #     help_upgarde(game)

        tie_breaker(game)
        
        mint = min(mint, game.get_time_remaining())
        print mint # DO NOT REMOVE THIS PRINT !!!



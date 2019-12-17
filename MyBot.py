from penguin_game import *
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

# def ultimate_attack(game,base):
#     attack = enemy_icebergs_distances(game, base)
#     if can_attack(game,base,attack):
#         base.send_penguins(attack, get_send_to_attack(game,base,attack))


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
    balance = dest.penguin_amount + dest.level*max(groups_per_distance.keys())
    for key, value in groups_per_distance.iteritems():
        balance -= value
    return balance



def can_attack(game, our_iceberg, enemy_iceberg, additional = 0, is_not_neutral = 1):
    
    after_attacked_balance = all_groups_to_dest_minus_distances(game, our_iceberg)
    if after_attacked_balance <= 0:
        return False
    can_take = after_attacked_balance + additional > enemy_iceberg.penguin_amount + our_iceberg.get_turns_till_arrival(enemy_iceberg) * is_not_neutral * enemy_iceberg.level
    # can_take = use_peng(game, our_iceberg) + additional > enemy_iceberg.penguin_amount + our_iceberg.get_turns_till_arrival(enemy_iceberg) * is_not_neutral * enemy_iceberg.level
    
    for group in game.get_my_penguin_groups():
        if group.destination == enemy_iceberg:
            return False
    return can_take

def get_send_to_attack(game, our_iceberg, enemy_iceberg):
    """
    """
    return enemy_iceberg.penguin_amount + our_iceberg.get_turns_till_arrival(enemy_iceberg)*enemy_iceberg.level + 1


def neutral_get_send_to_attack(game, our_iceberg, enemy_iceberg):
    """
    """
    return enemy_iceberg.penguin_amount + 1

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
def ko(game, base):
    """
    Heavy attack with multiple icebergs
    :type game: Game
    :type base: Iceberg
    """
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
        sum += use_peng(game, iceberg)
        if iceberg.get_turns_till_arrival(ice1) > farest_iceberg.get_turns_till_arrival(ice1):
            farest_iceberg = iceberg
    sum = sum - farest_iceberg.get_turns_till_arrival(ice1)
    for fire in game.get_my_icebergs():
        if fire.can_send_penguins(ice1, use_peng(game,fire)) and sum > ice1.penguin_amount + ice1.level*farest_iceberg.get_turns_till_arrival(ice1):
            smart_send(fire, ice1,use_peng(game,fire))
            
def smart_send(src, dest, p_amount):
    """
    :type p_amount: int
    :type src: Iceberg
    :type dest: Iceberg
    """
    global icebergs_state
    icebergs_state[src] = False
    if p_amount > 0:
        src.send_penguins(dest, p_amount)

    
def enemy_target(game):
    """
    :type game: Game
    """
    our_attacked = our_attacked_icebergs(game)

    for attacked in our_attacked:
        defense = our_icebergs_distances(game, attacked)
        if defense != []:
            if defense.can_send_penguins(attacked, use_peng(game,defense)):
                smart_send(defense, attacked, use_peng(game,defense))

    for group in game.get_enemy_penguin_groups():
        if group.destination in game.get_neutral_icebergs():
            nearest_base = game.get_my_icebergs()[0]
            for base in game.get_my_icebergs():
                if base.get_turns_till_arrival(group.destination) < nearest_base.get_turns_till_arrival(group.destination):
                    nearest_base = base
            if nearest_base.get_turns_till_arrival(group.destination) > group.turns_till_arrival:
                if use_peng(game, nearest_base) >= our_abs(all_groups_to_dest(game, group.destination)-group.destination.penguin_amount) + nearest_base.get_turns_till_arrival(group.destination):
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

icebergs_state = {}
def do_turn(game):
    """
    Makes the bot run a single turn.

    :param game: the current game state.
    :type game: Game
    """
    global icebergs_state
    icebergs_state = { iceberg: True for iceberg in game.get_my_icebergs() }

    base = game.get_my_icebergs()[0]
    if base.level == 1:
        if base.can_upgrade():
            base.upgrade()
    else:
        if len(game.get_neutral_icebergs()) != 0:
            enemy_target(game)
        if len(game.get_my_icebergs()) < 2 and len(game.get_neutral_icebergs()) != 0:
            to_attack = neutral_nearest_iceberg(game, base)
            if to_attack is not None:
                if can_attack(game, base, to_attack, 2, 0):
                    if neutral_get_send_to_attack(game, base, to_attack)+2 <= use_peng(game,base):
                        smart_send(base, to_attack, neutral_get_send_to_attack(game, base, to_attack)+2)
            

        enemy_dangered = enemy_get_dangered_icebergs(game)
        if enemy_dangered != []:
            game.debug("YAYA ---> " + " our_penguin_amount = "+ str(enemy_dangered[0][0].penguin_amount)+ " enemy_penguin_amount = "+ str(enemy_dangered[0][1].penguin_amount) + 
            " Turns till enemy = " + str(enemy_dangered[0][0].get_turns_till_arrival(enemy_dangered[0][1]))
            + " Enemy to our = " + str(all_groups_to_dest(game,enemy_dangered[0][0])))
            game.debug("YAYA2 ---> " + str(enemy_dangered))
        if enemy_dangered != []:
            for icebergs in enemy_dangered:
                if can_attack(game, icebergs[0], icebergs[1]):
                    game.debug("Attacking. . .")
                    smart_send(icebergs[0], icebergs[1], get_send_to_attack(game, icebergs[0], icebergs[1]))
            
        if len(game.get_my_icebergs()) < 3 and len(game.get_neutral_icebergs()) != 0:
            to_attack = neutral_nearest_iceberg(game, base)
            if to_attack is not None:
                if can_attack(game, base, to_attack):
                    if neutral_get_send_to_attack(game, base, to_attack) <= use_peng(game,base):
                        smart_send(base, to_attack, neutral_get_send_to_attack(game, base, to_attack))

        ko(game,base)
        
        for iceberg in game.get_my_icebergs():
            if all_groups_to_dest(game,iceberg) == 0:
                if iceberg.can_upgrade():
                    if icebergs_state[iceberg]:
                        iceberg.upgrade()

#!/bin/env python3
import army, board, colors, combat, golem

DISPLAY = True

the_board = board.Board(4,4)
armies = list()
armies.append(army.Army(name="Attacker", color=colors.fg.green, 
                    golems=[ 
                        golem.golems['G0001'],
                            ]))
armies.append(army.Army(name="Targets", color=colors.fg.red,
                        golems=[ 
                            golem.golems['G0028'],
                            golem.golems['G0028'],
                            golem.golems['G0028'],
                            golem.golems['G0028'],
                            ]))

armies[0].golems[0].x,armies[0].golems[0].y = 0,0
armies[1].golems[0].x,armies[1].golems[0].y = 0,0
armies[1].golems[1].x,armies[1].golems[1].y = 1,0
armies[1].golems[2].x,armies[1].golems[2].y = 3,2
armies[1].golems[3].x,armies[1].golems[3].y = 2,0
the_board.populate(armies=armies)

def test_range():
# Melee attacks target golems in the same region as the attacker
    melee_targets = combat.find_targets_within_range(the_board=the_board, attacker=armies[0].golems[0], attack="Kick")
    assert len(melee_targets) == 1
    assert melee_targets[0].x == 0
    assert melee_targets[0].y == 0
    assert melee_targets[0].army == "Targets"

# Ranged attacks target golems outside attacker's region within range of the attack
# Attacker's region isn't counted in range, target's is
# Range is measured in Regions from center of attacker's region to center of target's region
# Note, I don't know whether "measured in Regions" means Euclidean distance or the count of
# regions a line segment drawn between region centers passes through. I'm going to use Euclidean
# distance, because the alternative has undefined behavior when the two regions are strictly
# diagonal from each other, and the line segment passes through corners between regions.
    ranged_targets = combat.find_targets_within_range(the_board=the_board, attacker=armies[0].golems[0], attack="Scouting Flare")
    assert len(ranged_targets) == 2
    assert ranged_targets[0].x == 1
    assert ranged_targets[0].y == 0
    assert ranged_targets[0].army == "Targets"
    assert ranged_targets[1].x == 2
    assert ranged_targets[1].y == 0
    assert ranged_targets[1].army == "Targets"

# Hills add 1 range to ranged attacks.
# I assume this is for the target or attacker's region, but not intervening regions
    assert 2 == combat.range_to_target(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[3], attack="Scouting Flare")
    the_board.region(0,0).terrain = "Hills"
    assert 3 == combat.range_to_target(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[3], attack="Scouting Flare")
    the_board.region(2,0).terrain = "Hills"
    assert 4 == combat.range_to_target(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[3], attack="Scouting Flare")
    the_board.region(0,0).terrain = "Plains"
    assert 3 == combat.range_to_target(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[3], attack="Scouting Flare")
    the_board.region(2,0).terrain = "Plains"
 
def test_los():
# Whether a region blocks LOS is determined by a circular collision volume the size of the region
    assert True == combat.is_region_in_line_of_sight( region=(1,1), point_a=(1,1), point_b=(2,2) )
    assert False == combat.is_region_in_line_of_sight( region=(3,1), point_a=(1,1), point_b=(2,2) )
    assert False == combat.is_region_in_line_of_sight( region=(0,0), point_a=(1,1), point_b=(2,2) )
    assert False == combat.is_region_in_line_of_sight( region=(3,3), point_a=(1,1), point_b=(2,2) )
    assert False == combat.is_region_in_line_of_sight( region=(0,0), point_a=(2,2), point_b=(1,1) )
    assert False == combat.is_region_in_line_of_sight( region=(3,3), point_a=(2,2), point_b=(1,1) )

    the_board.region(1,1).terrain = "Shallow Water"
    assert False == combat.is_target_blocked(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[2], attack="Scouting Flare")

# Mountains block all line of sight
# Map edges block all line of sight
    assert False == combat.is_target_blocked(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[2], attack="Scouting Flare")

    the_board.region(1,1).terrain = "Mountains"
    assert True == combat.is_target_blocked(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[2], attack="Scouting Flare")

    the_board.region(1,1).terrain = "Map Edge"
    assert True == combat.is_target_blocked(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[2], attack="Scouting Flare")

# If attacker is not in an elevated region and LOS passes through an elevated region, LOS is blocked
    the_board.region(1,1).terrain = "Hills"
    assert True == combat.is_target_blocked(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[2], attack="Scouting Flare")

# If attacker is on elevated region they ignore all other elevated terrain when determining LOS
    the_board.region(0,0).terrain = "Hills"
    assert False == combat.is_target_blocked(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[2], attack="Scouting Flare")

# Elevation of target's region does not block LOS
    the_board.region(0,0).terrain = "Plains"
    the_board.region(1,1).terrain = "Plains"
    the_board.region(3,2).terrain = "Hills"
    assert False == combat.is_target_blocked(the_board=the_board, attacker=armies[0].golems[0], target=armies[1].golems[2], attack="Scouting Flare")

def test_melee_to_hit():
    to_hit = combat.calculate_melee_to_hit(attacker=armies[0].golems[0], target=armies[1].golems[1], attack="Kick")
    assert to_hit == -1
    to_hit = combat.calculate_melee_to_hit(attacker=armies[0].golems[0], target=armies[1].golems[0], attack="Scouting Flare")
    assert to_hit == -1
    to_hit = combat.calculate_melee_to_hit(attacker=armies[0].golems[0], target=armies[1].golems[0], attack="Kick")
    assert to_hit == 56

# Ranged attacks have -20 if target is in a contested region
def test_contested():
    assert False == the_board.region(1,0).is_contested()
    assert True  == the_board.region(0,0).is_contested()

# Add intervening cover modifiers for every region LOS passes through
# Add target region cover modifier
# Melee AoE attacks have different to-hit values for every target
# Ranged AoE targets the region, ignores all cover (including intervening): accuracy - contested region penalty - individual target's dodge
# For AoE roll dice once, compare that result to every eligible to-hit
# THe Pit gives -30 accuracy to ranged attacks

# Roll percentage dice, hit on <= to-hit
# Doubles convert miss to lucky hit - as though hit were made
# Doubles convert hit to crit, 1.5x net damage
# 00 (100%) is super crit, 1.5x net damage, no doubling activation cost, attack gains no cooldown

if __name__ == "__main__":
    test_range()
    test_los()
    test_melee_to_hit()
    test_contested()
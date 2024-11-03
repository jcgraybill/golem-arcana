#!/bin/env python3
import golem

g = golem.golems['G0028']
assert( g.get_movement_options() == {'Walk': [{'ap': 1, 'base_ap': 1, 'mp': 3, 'nimble': False}, {'ap': 1, 'base_ap': 1, 'mp': 3, 'nimble': False}]} )

g.activate_cooldown(ability='Walk', choice=0)
g.activate_cooldown(ability='Walk', choice=1)
g.activate_cooldown(ability='Walk', choice=1)
assert(g.get_movement_options() == {'Walk': [{'ap': 2, 'mp': 3, 'nimble': False, 'base_ap': 1, 'cooldown_refresh': 1}, {'ap': 4, 'mp': 3, 'nimble': False, 'base_ap': 1, 'cooldown_refresh': 2}]})

g.end_turn()
assert(g.get_movement_options() == {'Walk': [{'ap': 1, 'mp': 3, 'nimble': False, 'base_ap': 1, 'cooldown_refresh': 0}, {'ap': 4, 'mp': 3, 'nimble': False, 'base_ap': 1, 'cooldown_refresh': 1}]})

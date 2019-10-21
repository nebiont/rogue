import tcod as libtcod
import os
import definitions

class Role:
    name = ''
    description = ''
    portrait = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','joe.png'))

class Warrior(Role):
    name = 'Rageaholic'
    description = '''Joe cannot live without rageahol. He crushes his foes with sheer rage
and feeds off of their pain. In dire situation he can unleash his inner monster:

A creature so powerful that nothing can contain its rage. Joe has a large pool of HP.'''

    portrait = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','joe.png'))
    con = 14
    base_defense = 12
    base_power = 14
    dmg = [1,8]
    hitdie = [1,10]

    def role_init(self):
        self.owner.fighter.con = self.con
        self.owner.fighter.base_defense = self.base_defense
        self.owner.fighter.base_power = self.base_power
        self.owner.fighter.dmg = self.dmg
        self.owner.fighter.hitdie = self.hitdie
        self.owner.name = 'Joe'
        self.owner.fighter.init_hp()
# class Rogue:

# class Warlock:

# class Ranger:

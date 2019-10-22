import tcod as libtcod
import os
import definitions
from ability_functions import tackle
from .ability import Ability
from game_messages import Message

class Role:
    name = ''
    description = ''
    portrait = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','joe.png'))

class Warrior(Role):
    name = 'Rageoholic'
    description = '''Joe cannot live without rageahol. He crushes his foes with sheer rage
and feeds off of their pain. In dire situation he can unleash his inner monster:

A creature so powerful that nothing can contain its rage. Joe has a large pool of HP and can use the power of rageohol to destroy his foes.'''

    portrait = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','joe.png'))
    con = 14
    base_defense = 12
    base_power = 14
    dmg = [1,8]
    hitdie = [1,10]
    tackle = Ability('Tackle', description = None, ability_function=tackle, targeting=True, targeting_message=Message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan))
    abilities = [tackle]

    def role_init(self):
        self.owner.fighter.con = self.con
        self.owner.fighter.base_defense = self.base_defense
        self.owner.fighter.base_power = self.base_power
        self.owner.fighter.dmg = self.dmg
        self.owner.fighter.hitdie = self.hitdie
        self.owner.name = 'Joe'
        self.owner.fighter.init_hp()
        self.owner.abilities =self.abilities

class Rogue(Role):
    name = 'Sense Bender'
    description = '''Brett is a creature of the shadows. He uses shadows and nonsense to confuse his foes and then takes advantage of their vulnerable state.

Brett is a frontline fighter that lacks HP, but makes up for it with his unit control capabilities.'''

    portrait = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','brett.png'))
    con = 10
    base_defense = 10
    base_power = 14
    dmg = [1,8]
    hitdie = [1,8]

    def role_init(self):
        self.owner.fighter.con = self.con
        self.owner.fighter.base_defense = self.base_defense
        self.owner.fighter.base_power = self.base_power
        self.owner.fighter.dmg = self.dmg
        self.owner.fighter.hitdie = self.hitdie
        self.owner.name = 'Brett'
        self.owner.fighter.init_hp()

class Ranger(Role):
    name = 'Beast Master'
    description = '''Kyle is a trained beaster master who holds domain over many beast. He summons these beasts to support him on the battlefield.

Kyle is a ranged fighter using bows as his primary weapon, but his true power lies with the beasts he summons to aid him in battle.'''

    portrait = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','kyle.png'))
    con = 10
    base_defense = 8
    base_power = 12
    dmg = [1,6]
    hitdie = [1,6]

    def role_init(self):
        self.owner.fighter.con = self.con
        self.owner.fighter.base_defense = self.base_defense
        self.owner.fighter.base_power = self.base_power
        self.owner.fighter.dmg = self.dmg
        self.owner.fighter.hitdie = self.hitdie
        self.owner.name = 'Kyle'
        self.owner.fighter.init_hp()
        
class Warlock(Role):
    name = 'Eldritch Blast'
    description = '''Kelsey is Eldritch Blast incarnate. He throws an Eldritch Blast at every opportunity. Don't try and loot first when this guys around because you will get an Eldritch Blast to the face.

Kelsey is a ranged magic user that relies on his many types of Eldritch Blast to turn the tide of battle in his favor.'''

    portrait = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','kelsey.png'))
    con = 10
    base_defense = 10
    base_power = 12
    dmg = [1,4]
    hitdie = [1,6]

    def role_init(self):
        self.owner.fighter.con = self.con
        self.owner.fighter.base_defense = self.base_defense
        self.owner.fighter.base_power = self.base_power
        self.owner.fighter.dmg = self.dmg
        self.owner.fighter.hitdie = self.hitdie
        self.owner.name = 'Kelsey'
        self.owner.fighter.init_hp()

class Paladin(Role):
    name = 'Bald Bro'
    description = '''Devon is a devout follower of Baldicus. As a 'Bald Bro' Devon can harness the power of Baldicus' divine will to smite his foes and heal his wounds.

Devon is a front line fighter that relies on his divine powers to defeat his oponents.'''

    portrait = libtcod.image_load(os.path.join(definitions.ROOT_DIR,'data','devon.png'))
    con = 10
    base_defense = 14
    base_power = 12
    dmg = [1,6]
    hitdie = [1,8]

    def role_init(self):
        self.owner.fighter.con = self.con
        self.owner.fighter.base_defense = self.base_defense
        self.owner.fighter.base_power = self.base_power
        self.owner.fighter.dmg = self.dmg
        self.owner.fighter.hitdie = self.hitdie
        self.owner.name = 'Devon'
        self.owner.fighter.init_hp()
# class Rogue:

# class Warlock:

# class Ranger:

class Warrior:
    name = 'Rageaholic'
    description = '''Joe cannot live without rageahol. He crushes his foes with sheer rage
                    and feeds off of pain. In dire situation he can unleash his inner monster:
                    a creature so powerful that nothing can contain its rage. Joe has a large pool of HP.'''

    def role_init(self):
        self.owner.fighter.con = 14
        self.owner.fighter.base_defense = 12
        self.owner.fighter.base_power = 14
        self.owner.fighter.dmg = [1,8]
        self.owner.fighter.hitdie = [1,10]
        self.owner.name = 'Joe'
        self.owner.fighter.init_hp()
# class Rogue:

# class Warlock:

# class Ranger:

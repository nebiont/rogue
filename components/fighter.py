import tcod as libtcod
from random import randint
from game_messages import Message
import components.animator as animator

class Fighter:
	def __init__(self, hp, defense, power, xp=0, hitdie=None, con=None, dmg=None):
		self.base_max_hp = hp
		self.hp = hp
		self.base_defense = defense
		self.base_power = power
		self.xp = xp
		self.hitdie = hitdie
		self.con = con
		self.dmg = dmg

		if not self.con == None:
			self.base_max_hp = self.hitdie[1] + (int((self.con - 10) / 2))
			self.hp = self.base_max_hp

		
	@property
	def max_hp(self):
		if self.owner and self.owner.equipment:
			bonus = self.owner.equipment.max_hp_bonus
		else:
			bonus = 0

		return self.base_max_hp + bonus

	@property
	def power(self):
		if self.owner and self.owner.equipment:
			bonus = self.owner.equipment.power_bonus
		else:
			bonus = 0

		return self.base_power + bonus

	@property
	def defense(self):
		if self.owner and self.owner.equipment:
			bonus = self.owner.equipment.defense_bonus
		else:
			bonus = 0

		return self.base_defense + bonus

	def init_hp(self):
		self.base_max_hp = self.hitdie[1] + (int((self.con - 10) / 2))
		self.hp = self.base_max_hp

	def take_damage(self, amount):
		results = []
		self.hp -= amount

		if self.hp <= 0:
			results.append({'dead': self.owner, 'xp': self.xp})

		else:
			animation = animator.Flash(self.owner, .25, libtcod.red, caller=None, blocking=True)


		return results
	
	def heal(self, amount):
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp
	
	def attack(self, target):
		results = []
		attack_roll = randint(1,20) + ((self.power - 10) /2)
		
		if attack_roll >= target.fighter.defense:
			damage = int(randint(self.dmg[0], self.dmg[1]) + ((self.power - 10) / 2))
			results.append({'message': Message('{0} attacks {1} for {2} hit points.'.format(
				self.owner.name.capitalize(), target.name, str(damage)), libtcod.white)})
			results.extend(target.fighter.take_damage(damage))
		else:
			results.append({'message': Message('{0} attacks {1} but misses.'.format(
				self.owner.name.capitalize(), target.name), libtcod.white)})
			text = '*MISS*'
			animation = animator.FloatingText(int(self.owner.x - (len(text) / 2)), self.owner.y, text, libtcod.orange, int(self.owner.x - (len(text) / 2)), self.owner.y - 5, 10) 

		return results        
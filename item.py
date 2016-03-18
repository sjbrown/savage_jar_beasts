#!/usr/bin/env python
"""
Here is some description about this module
"""

#Import Modules
import os, pygame, operator
from pygame.locals import *
from utils import *

from s_constants import *
from events import *


#-----------------------------------------------------------------------------
class UsableInFight:
	"""This is an interface for any Items that can be used in a fight.
	Any such items have a button to show in a fight, and an identifier
	that indicates what kind of animation to play"""
	pass


#-----------------------------------------------------------------------------
class Item:
	"""Anything that can be put into an inventory"""
	name = "Abstract Item"
	def __init__(self, eventManager, owner=None):
		self.evManager = eventManager
		self.owner = owner
		self.description = "Abstract Item"
		self.value = 0
		self.isStackable = 0
		#self.reprClasses = { }
		self.barterTarget = None
		self.currentPrice = self.value

	#----------------------------------------------------------------------
	def Delete(self):
		self.evManager = None
		self.owner = None
		self.barterTarget = None
		#for sprite in self.reprClasses.values():
			#sprite.Delete()
		#self.reprClasses = { }

	#----------------------------------------------------------------------
	def GetValue(self):
		return self.value;

	#----------------------------------------------------------------------
	def SetBarterVars(self, barterTarget, price):
		self.barterTarget = barterTarget
		self.currentPrice = price

	#----------------------------------------------------------------------
	def Barter(self):
		#TODO: this should be replaced by a Barter object, probably

		print "Bartering item.", self, "from ", self.owner, " to ", self.barterTarget
		if self.owner is not None:
			self.owner.SellItem( self )

	#----------------------------------------------------------------------
	#def GetFightRepr(self):
		#if self.reprClasses.has_key('fight'):
			#return self.reprClasses['fight']( self )
		#else:
			#print "WARN:calling GetFightRepr, but doesn't exist"

	#----------------------------------------------------------------------
	#def GetShopRepr(self):
		#if self.reprClasses.has_key('shop'):
			#return self.reprClasses['shop']( self )
		#else:
			#print "WARN:calling GetShopRepr, but doesn't exist"

	#----------------------------------------------------------------------
	def Use(self):
		print "BEING USED -- but i don't know how"

#-----------------------------------------------------------------------------
class HealthCard(Item, UsableInFight):
	name = "Health"
	FACE_DOWN = 0
	FACE_UP = 1
	#----------------------------------------------------------------------
	def __init__(self, evManager, owner=None):
		Item.__init__(self, evManager, owner)
		self.power = 50
		self.isStackable = 1
		self.description = "Health Card"
		self.facing = HealthCard.FACE_DOWN

	#----------------------------------------------------------------------
	def Copy(self):
		clone = HealthCard( self.evManager, self.owner )
		clone.facing = self.facing
		return clone

	#----------------------------------------------------------------------
	def Flip(self, duel):
		if self.facing == HealthCard.FACE_UP:
			ev = ExceptionEvent( 'card already face up' )
			self.evManager.Post( ev )
			return 0

		myPlayer = self.owner.player
		myMonsters = duel.GetMonstersForPlayer(myPlayer)
		if not myMonsters:
			return 0

		for m in myMonsters:
			m.health += self.power

		self.facing = HealthCard.FACE_UP

		ev = DuelFlipCardEvent( self, duel )
		self.evManager.Post( ev )

		return 1

	#----------------------------------------------------------------------
	def GetPower(self):
		return self.power


#-----------------------------------------------------------------------------
class Weapon(Item, UsableInFight):
	"""Items that can be used to attack"""
	name = "Weapon"
	def __init__(self, eventManager, owner=None):
		Item.__init__(self, eventManager, owner)
		self.power = 1
		#self.reprClasses = {
		               #'fight': WeaponFightButton,
		               #}

	#----------------------------------------------------------------------
	def Use(self):
		self.owner.Attack( self )

	#----------------------------------------------------------------------
	def GetPower(self):
		return self.power


#-----------------------------------------------------------------------------
class DefaultSquirrelAttack(Weapon):
	def __init__(self, eventManager, owner):
		Weapon.__init__(self,eventManager, owner)
		#self.reprClasses = {
		               #'fight': WeaponFightButton,
		               #}
	#----------------------------------------------------------------------
	def GetPower(self):
		from model import rng
		return rng.randint( 7,9 )
	
#-----------------------------------------------------------------------------
class DefaultManateeAttack(Weapon):
	def __init__(self, eventManager, owner):
		Weapon.__init__(self,eventManager, owner)
		#self.reprClasses = {
		               #'fight': WeaponFightButton,
		               #}
	#----------------------------------------------------------------------
	def GetPower(self):
		from model import rng
		return rng.randint( 16,28 )
		#return rng.randint( 6,18 )
	
#-----------------------------------------------------------------------------
class Powerup(Item):
	name = "Walrus Power"
	def __init__(self, eventManager, owner=None):
		Item.__init__(self,eventManager, owner)
		self.numCharges = 10
		#self.reprClasses = {
		               #'fight': PowerupFightButton,
		               #'shop': PowerupInventoryRepr,
		               #}

	#----------------------------------------------------------------------
	def GetAttackModifier(self):
		#TODO: the removeItem stiff shouldn't really be here.  more
		#properly, we should be listening for a UseItem event.
		self.numCharges -= 1
		if self.numCharges < 1:
			self.owner.RemoveItem( self )
		return 10


#-----------------------------------------------------------------------------
class ManateeAttack2(Weapon):
	name = "Walrus Attack"
	def __init__(self, eventManager, owner=None):
		Weapon.__init__(self,eventManager, owner)
		#self.reprClasses = {
		               #'fight': ManateeAttack2FightButton,
		               #'shop': ManateeAttack2InventoryRepr,
		               #}
	#----------------------------------------------------------------------
	def GetPower(self):
		from model import rng
		return rng.randint( 16,28 )

#-----------------------------------------------------------------------------
class Money(Item):
	name = "Money"
	def __init__(self, eventManager, owner=None):
		Item.__init__(self, eventManager, owner)
		self.isStackable = 1
		self.value = 1
		#self.reprClasses = { 
		    #'shop': MoneyInventoryRepr,
		    #}



from events import *
import preferences

from item import *


DIRECTION_UP = 0
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3

from random import Random
rng = Random()


#------------------------------------------------------------------------------
class Game:
	"""..."""

	STATE_PREPARING = 0
	STATE_RUNNING = 1
	STATE_PAUSED = 2

	#----------------------------------------------------------------------
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.Reset()

	#----------------------------------------------------------------------
	def Reset( self ):
		self.state = Game.STATE_PREPARING

		self.arena = Arena( self.evManager )
		
		self.players = [ ]
		self.maxPlayers = 3
		self.map = Map( self.evManager )


	#----------------------------------------------------------------------
	def Start(self):
		self.map.Build()
		self.state = Game.STATE_RUNNING
		ev = GameStartedEvent( self )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def AddHumanPlayer(self, player):
		self.players.append( player )
		player.SetGame( self )
		ev = PlayerJoinEvent( player )
		self.evManager.Post( ev )


	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, GameStartRequest ):
			if self.state == Game.STATE_PREPARING:
				self.Start()
			elif self.state == Game.STATE_RUNNING:
				self.Reset()
				self.Start()

		elif isinstance( event, PlayerJoinRequest ):
			if len(self.players) < self.maxPlayers:
				player = HumanPlayer( self.evManager )
				player.SetData( event.playerDict )
				for p in self.players:
					if p.name == player.name:
						#FAIL
						raise NotImplementedError, "Dup Player"
				self.AddHumanPlayer( player )

		#TODO: model shouldn't know about the GUI events
		elif isinstance( event, GUIChangeScreenRequest ):
			ev = GameSyncEvent( self )
			self.evManager.Post( ev )

		elif isinstance( event, DuelStartRequest ):
			p1 = event.player1
			p2 = event.player2
			if not p2:
				p2 = ComputerPlayer(self.evManager)
				p2.SetGame( self )
			duel = Duel( self.evManager, p1, p2 )
			duel.Start()


#------------------------------------------------------------------------------
class Arena:
	"""An Arena
	A place for players to meet up and duel their monsters against
	one another's."""
	#----------------------------------------------------------------------
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.waitingPlayers = {}

	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, AnnounceDuelAvailability ):
			self.waitingPlayers[ event.player ] = 0
		elif isinstance( event, WithdrawDuelAvailability ):
			try:
				del self.waitingPlayers[ event.player ]
			except KeyError:
				#tried to remove something not in the list
				pass

#------------------------------------------------------------------------------
class Duel:
	"""A Duel
	Beginning of turn
	FLIP1 - Player flips any magic cards
	COUNTERFLIP1 - 
	ATTACK - 
	COUNTERATTACK - Opponent can flip magic cards
	SET - Player can set cards face down
	FLIP2 - Player can flip any magic cards
	COUNTERFLIP2 - """

	STEP_FLIP1 = 0
	STEP_COUNTERFLIP1 = 1
	STEP_ATTACK = 2
	STEP_COUNTERATTACK = 3
	STEP_SET = 4
	STEP_FLIP2 = 5
	STEP_COUNTERFLIP2 = 6

	STATE_PREPARING = 0
	STATE_ACTIVE = 1
	STATE_FINISHED = 2

	#----------------------------------------------------------------------
	def __init__(self, evManager, player1, player2 ):
		self.state = Duel.STATE_PREPARING
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.cardFieldMax = 4
		self.monsterFieldMax = 4

		self.players = [player1, player2]

		d0 = self.players[0].avatar.GetDeck()
		d1 = self.players[1].avatar.GetDeck()
		self.decks = [ d0, d1 ]
		self.cardField = [ [], [] ]
		self.cardGraveyard = [ [], [] ]

		self.monsterField = [ [], [] ]
		self.monsterGraveyard = [ [], [] ]

		#should be [attacker, attackee] or None
		self.pendingAttack = None

		self.step = Duel.STEP_ATTACK
		self.activePlayerIndex = 0

	#----------------------------------------------------------------------
	def GetActivePlayer(self):
		return self.players[self.activePlayerIndex]

	#----------------------------------------------------------------------
	def InFlippingStep(self):
		if self.step in [ Duel.STEP_FLIP1,
		                  Duel.STEP_COUNTERFLIP1,
		                  Duel.STEP_COUNTERATTACK,
		                  Duel.STEP_FLIP2,
		                  Duel.STEP_COUNTERFLIP2,
		                ]:
			return 1

	#----------------------------------------------------------------------
	def SetStepAndPlayer(self, step, changePlayer=0):
		"""If the step AND the player are being changed, it should be
		all within this function"""
		oldStep = self.step
		#self.evManager.Tell()

		if changePlayer:
			self.activePlayerIndex = (self.activePlayerIndex+1)%2
			ev = DuelChangePlayerEvent( self )
			self.evManager.Post( ev )

		if oldStep != step:
			self.step = step	
			ev = DuelChangeStepEvent( self )
			self.evManager.Post( ev )



	#----------------------------------------------------------------------
	def EndTurn(self):
		ev = DuelTurnFinishedEvent( self )
		self.evManager.Post( ev )

		self.SetStepAndPlayer( Duel.STEP_FLIP1, 1 )

	#----------------------------------------------------------------------
	def GetDeckForPlayer( self, player ):
		index = self.players.index(player)
		return self.decks[index]
	#----------------------------------------------------------------------
	def GetCardFieldForPlayer( self, player ):
		index = self.players.index(player)
		return self.cardField[index]

	#----------------------------------------------------------------------
	def GetMonsterTarget(self, monster):
		if monster in self.monsterField[0]:
			return self.monsterField[1][0]
		elif monster in self.monsterField[1]:
			return self.monsterField[0][0]
		else:
			raise Exception('that monster is not in duel')
			return None
	#----------------------------------------------------------------------
	def GetMonstersForPlayer( self, player ):
		if player.duel is not self:
			ev = ExceptionEvent( 'This player is not in this duel' )
			self.evManager.Post( ev )
			return

		pIndex = self.players.index( player )
		return self.monsterField[pIndex]

	#----------------------------------------------------------------------
	def Start(self):
		self.state = Duel.STATE_ACTIVE
		if self.players[0].duel or self.players[1].duel:
			#Can't start this duel - one of the players is already
			#in a duel
			ev = ExceptionEvent( 'One of the players is dueling' )
		else:
			self.players[0].duel = self
			self.monsterField[0].append( self.players[0].monster )
			self.players[1].duel = self
			self.monsterField[1].append( self.players[1].monster )
			self.step = Duel.STEP_ATTACK
			ev = DuelStartEvent( self )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def Finish(self):
		self.state = Duel.STATE_FINISHED
		self.players[0].duel = None
		self.players[1].duel = None
		del self.players
		del self.monsterField
		del self.monsterGraveyard
		del self.cardField
		del self.cardGraveyard
		del self.decks
		ev = DuelFinishEvent( self )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def Continue(self, player):
		if player is not self.GetActivePlayer():
			ev = ExceptionEvent( 'not your turn' )
			self.evManager.Post( ev )
			return

		if self.step == Duel.STEP_FLIP1:
			self.SetStepAndPlayer( Duel.STEP_ATTACK )
		elif self.step == Duel.STEP_COUNTERFLIP1:
			self.SetStepAndPlayer( Duel.STEP_FLIP1, 1 )
		elif self.step == Duel.STEP_ATTACK:
			self.SetStepAndPlayer( Duel.STEP_SET )
		elif self.step == Duel.STEP_COUNTERATTACK:
			self.ExecuteAttack()
		elif self.step == Duel.STEP_SET:
			self.SetStepAndPlayer( Duel.STEP_FLIP2 )
		elif self.step == Duel.STEP_FLIP2:
			self.EndTurn()
		elif self.step == Duel.STEP_COUNTERFLIP2:
			self.SetStepAndPlayer( Duel.STEP_FLIP2, 1 )

	#----------------------------------------------------------------------
	def MonsterDied(self, monster):
		if monster in self.monsterField[0]:
			index = 0
		elif monster in self.monsterField[1]:
			index = 1
		else:
			raise Exception('that monster is not in duel')
			return None

		self.monsterField[index].remove( monster )
		self.monsterGraveyard[index].append( monster )
		#if that side of the field is empty...
		if not self.monsterField[index]:
			print "This probably isn't the best place to put this"
			self.Finish()


	#----------------------------------------------------------------------
	def InitAttack(self, monster, target):
		if monster.player is not self.GetActivePlayer():
			ev = ExceptionEvent( 'not your turn' )
			self.evManager.Post( ev )
			return
		if self.step > Duel.STEP_ATTACK:
			ev = ExceptionEvent( 'attack step finished' )
			self.evManager.Post( ev )
			return

		self.pendingAttack = [monster, target]

		self.SetStepAndPlayer( Duel.STEP_COUNTERATTACK, 1 )

	#----------------------------------------------------------------------
	def ExecuteAttack(self):
		monster = self.pendingAttack[0]
		target = self.pendingAttack[1]
		self.pendingAttack = None

		monster.Attack( target )

		#self.SetStepAndPlayer( self.step, 1 )

	#----------------------------------------------------------------------
	def FinishAttack(self):
		self.SetStepAndPlayer( Duel.STEP_SET, 1 )


	#----------------------------------------------------------------------
	def PlayCard(self, charactor, card):
		pIndex = self.activePlayerIndex
		if charactor.player is not self.GetActivePlayer():
			ev = ExceptionEvent( 'not your turn' )
			self.evManager.Post( ev )
			return
		if self.step > Duel.STEP_SET:
			ev = ExceptionEvent( 'set step finished' )
			self.evManager.Post( ev )
			return

		if card not in self.decks[pIndex]:
			ev = ExceptionEvent( 'playing card not in deck' )
			self.evManager.Post( ev )
			return

		if len( self.cardField[pIndex]) == self.cardFieldMax:
			ev = ExceptionEvent( 'max cards on the field' )
			self.evManager.Post( ev )
			return

		self.decks[pIndex].remove( card )
		self.cardField[pIndex].append( card )

		ev = CharactorPlayCardEvent( charactor, card )
		self.evManager.Post( ev )

		self.SetStepAndPlayer( Duel.STEP_FLIP2 )

	#----------------------------------------------------------------------
	def FlipCard(self, card):
		pIndex = self.activePlayerIndex
		if card not in self.cardField[pIndex]:
			ev = ExceptionEvent( 'flipping card not on field' )
			self.evManager.Post( ev )
			return
		if not self.InFlippingStep():
			ev = ExceptionEvent( 'flip step finished' )
			self.evManager.Post( ev )
			return

		success = card.Flip( self )

		if success:
			self.cardField[pIndex].remove(card)
			self.cardGraveyard[pIndex].append( card )

			if self.step == Duel.STEP_FLIP1:
				nextStep = Duel.STEP_COUNTERFLIP1
			else: # Duel.STEP_FLIP2:
				nextStep = Duel.STEP_COUNTERFLIP2
			self.SetStepAndPlayer( nextStep, 1 )

	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, DuelContinueRequest ) \
		 and event.player.duel is self:
			self.Continue( event.player )

		elif isinstance( event, CharactorAttackRequest ) \
		 and event.attacker.player.duel is self:
			self.InitAttack( event.attacker, event.defender )

		elif isinstance( event, CharactorAttackFinished ) \
		 and event.attacker.player.duel is self:
			self.FinishAttack()

		elif isinstance( event, CharactorDeathEvent ) \
		 and event.charactor.player.duel is self:
			self.MonsterDied(event.charactor)

		elif isinstance( event, CharactorPlayCardRequest ) \
		 and event.charactor.player.duel is self:
			self.PlayCard( event.charactor, event.card )

		elif isinstance( event, DuelFlipCardRequest ) \
		 and event.card.owner.player.duel is self:
			self.FlipCard( event.card )



#------------------------------------------------------------------------------
class Player:
	"""..."""
	def __init__(self, evManager ):
		self.name = "Abstract Player"
		self.evManager = evManager
		self.evManager.RegisterListener( self )
		self.game = None

		self.charactors = [ ]

		#self.placeableCharactorClasses = [ Charactor ]
		#self.startSector = None
		self.turns = 200
		self.duel = None

	#----------------------------------------------------------------------
	def GetPlaceData( self ):
		charactor = self.charactors[0]
		map = self.game.map
		sector =  map.sectors[map.startSectorIndex]
		return [charactor, sector]

	#----------------------------------------------------------------------
	def GetMoveData( self ):
		return [self.charactors[0]]

	#----------------------------------------------------------------------
	def SetGame( self, game ):
		self.game = game
		for c in self.charactors:
			c.SetGame( self.game )

	#----------------------------------------------------------------------
	def SetData( self, playerDict ):
		self.name = playerDict['name']

	#----------------------------------------------------------------------
	def TakeTurns( self, turns):
		self.turns -= turns
		if self.turns < 0:
			self.turns = 0

	#----------------------------------------------------------------------
	def Explore(self):
		print 'exploring...'+"\n"
		maxT = 2

		if self.turns > 0:
			turnsTaken = min( (rng.randrange(1,maxT), self.turns) )
			self.TakeTurns( turnsTaken )
			ev = PlayerExplorationEvent( self, turnsTaken )
			self.evManager.Post( ev )
		else:
			msg = 'No Turns Left'
			ev = GUIDialogAddRequest( 'msgDialog', msg )
			self.evManager.Post( ev )

		print 'remaining turns: ', self.turns

	#----------------------------------------------------------------------
	def Shop(self):
		print 'shopping...'+"\n"

		ev = GoToStoreEvent( self )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def GoToTown(self):
		print 'towning...'+"\n"

		ev = GoToTownEvent( self )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def Retreat(self):
		print 'retreating...'
		if not self.duel:
			ev = ExceptionEvent( 'retreating, but not in duel' )
			self.evManager.Post( ev )
			return
		self.duel.Finish()
		ev = PlayerRetreatEvent( self )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, PlayerExploreRequest ) \
		  and event.player is self:
			self.Explore()

		if isinstance( event, GoToStoreRequest ) \
		  and event.player is self:
			self.Shop()

		if isinstance( event, GoToTownRequest ) \
		  and event.player is self:
			self.GoToTown()

		if isinstance( event, PlayerRetreatRequest ) \
		  and event.player is self:
			self.Retreat()


#------------------------------------------------------------------------------
class HumanPlayer(Player):
	"""..."""
	def __init__(self, evManager ):
		Player.__init__(self, evManager)
		self.name = "Human Player"

		self.charactors = [ Manatee(evManager, self.game, self ),
		                    Avatar( evManager, self.game, self ) ]
		self.monster = self.charactors[0]
		self.avatar= self.charactors[1]

		#self.placeableCharactorClasses = [ Charactor ]
		#self.startSector = None
		self.turns = 200


#------------------------------------------------------------------------------
class ComputerPlayer(Player):
	"""..."""
	def __init__(self, evManager ):
		Player.__init__(self, evManager)

		self.name = "Computer Player"
		#self.charactors = [ ]
		self.charactors = [ Squirrel(evManager, self.game, self),
		                    Avatar( evManager, self.game, self ) ]
		self.monster = self.charactors[0]
		self.avatar= self.charactors[1]

	#----------------------------------------------------------------------
	def GetPlaceData( self ):
		charactor = self.charactors[0]
		map = self.game.map
		sector =  map.sectors[map.bartenderIndex]
		return [charactor, sector]

	#----------------------------------------------------------------------
	def ProcessDuelState( self ):
		if self.duel.step == Duel.STEP_FLIP1:
			ev = DuelContinueRequest( self )
		elif self.duel.step == Duel.STEP_COUNTERFLIP1:
			ev = DuelContinueRequest( self )
		elif self.duel.step == Duel.STEP_ATTACK:
			monster = self.monster
			opponent = self.duel.GetMonsterTarget( monster )
			ev = CharactorAttackRequest( monster, opponent )
		elif self.duel.step == Duel.STEP_COUNTERATTACK:
			ev = DuelContinueRequest( self )
		elif self.duel.step == Duel.STEP_SET:
			ev = DuelContinueRequest( self )
		elif self.duel.step == Duel.STEP_FLIP2:
			ev = DuelContinueRequest( self )
		elif self.duel.step == Duel.STEP_COUNTERFLIP2:
			ev = DuelContinueRequest( self )
		else:
			raise Exception( 'cpu player doesnt have duel state' )

		self.evManager.Post( ev )


	#----------------------------------------------------------------------
	def Notify( self, event ):
		Player.Notify( self, event )

		#if isinstance( event, DuelChangePlayerEvent ) \
		  #and event.duel.GetActivePlayer() is self:
			#self.ProcessDuelState( )
		if isinstance( event, DuelChangeStepEvent ) \
		  and event.duel.GetActivePlayer() is self:
			self.ProcessDuelState( )


#-----------------------------------------------------------------------------
class Inventory:
	"""..."""
	#----------------------------------------------------------------------
	def __init__(self, evManager, owner):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.internalDict = {}
		self.owner = owner

	#----------------------------------------------------------------------
	def Delete( self ):
		self.evManager = None
		self.owner = None
		for item in self.internalDict.values():
			if isinstance(item, dict):
				item = item['item']
			item.Delete()
		self.internalDict = {}

	#----------------------------------------------------------------------
	def AddItem( self, item, name=None ):
		if name is None:
			name = item.name
		item.owner = self.owner
		if item.isStackable:
			if self.internalDict.has_key(name):
				self.internalDict[name]['quantity'] += 1
			else:
				self.internalDict[name] = {
					'item': item,
					'quantity': 1
				}
		else:
			self.internalDict[name] = item

		event = EventInventoryChanged( self )
		self.evManager.Post( event )

	#----------------------------------------------------------------------
	def RemoveItem( self, item, name=None, quantity=1 ):
		"""This removes an item or items from the inventory.  
		It returns the number of those items left in the inventory.
		Note, it
		does not Delete() the item, that is the responsibility of the
		caller, if appropriate"""

		remaining = 0

		if name is None:
			name = item.name
		#check to see that the item is actually in the inventory
		if not self.internalDict.has_key(name):
			return 0

		#the item is in the inventory
		if item.isStackable and self.internalDict[name]['quantity'] > 1:
			self.internalDict[name]['quantity'] -= 1
			remaining = self.internalDict[name]['quantity']
		else:
			del self.internalDict[name]
			remaining = 0

		event = EventInventoryChanged( self )
		self.evManager.Post( event )

		return remaining

	#----------------------------------------------------------------------
	def GetOneItem( self, itemRepr ):
		"""Can be used to see if Inventory has an item"""

		if isinstance( itemRepr, str ):
			name = itemRepr
		else:
			name = itemRepr.name

		#check to see that the item is actually in the inventory
		if not self.internalDict.has_key(name):
			return 0

		#the item is in the inventory
		if isinstance( self.internalDict[name], dict ):
			return self.internalDict[name]['item']
		else:
			return self.internalDict[name]

	#----------------------------------------------------------------------
	def GetItemsWithAttrs( self, ifAttrs ):
		retlist = []
		for item in self.internalDict.values():
			quantity = 1
			candidate = item
			success = 1
			if isinstance( item, dict ):
				candidate = item['item'] 
				quantity = item['quantity']

			for attr in ifAttrs:
				if not hasattr( candidate, attr ):
					success = 0
					break
			if success:
				retlist.extend( [candidate] * quantity )

		return retlist
	#----------------------------------------------------------------------
	def GetItemsOfClass( self, ifClass ):
		retlist = []
		for item in self.internalDict.values():
			if isinstance( item, dict ) \
			 and isinstance( item['item'], ifClass ):
			 	for i in range(0, item['quantity']):
			 		retlist.append( item['item'].Copy() )

			elif isinstance( item, ifClass ):
				retlist.append( item )

		return retlist

	#----------------------------------------------------------------------
	def Notify( self, event ):
		pass


#-----------------------------------------------------------------------------
class Charactor:
	"""..."""

	STATE_INACTIVE = 0
	STATE_ACTIVE = 1

	#----------------------------------------------------------------------
	def __init__(self, evManager, game, player, name):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.game = game
		self.player = player
		self.sector = None

		self.state = Charactor.STATE_INACTIVE

		self.name = name
		self.enemy = None
		self.health = 100
		self.maxHealth = 100
		self.inventory = Inventory( self.evManager, self )

	#----------------------------------------------------------------------
	def SetGame( self, game ):
		self.game = game

	#----------------------------------------------------------------------
	def Delete( self ):
		self.evManager = None
		self.game = None
		self.player = None
		self.enemy = None
		self.inventory.Delete()
		self.inventory = None

	#----------------------------------------------------------------------
	def AddItem( self, item, name=None ):
		self.inventory.AddItem( item, name )

	#----------------------------------------------------------------------
	def RemoveItem( self, item, name=None, quantity=1 ):
		self.inventory.RemoveItem( item, name, quantity )

	#----------------------------------------------------------------------
	def GetWeapons(self):
		return self.inventory.GetItemsOfClass( Weapon )

	#----------------------------------------------------------------------
	def GetFightActions(self):
		"""Returns a list of items that can be used in a fight"""
		return self.inventory.GetItemsOfClass( UsableInFight )

	#----------------------------------------------------------------------
	def GetAttackModifiers(self):
		"""Returns an integer that adds up all the attack bonuses
		and penalties from all the weapons."""

		attrs = [ "GetAttackModifier" ]
		items = self.inventory.GetItemsWithAttrs( attrs )
		total = 0
		for item in items:
			total += item.GetAttackModifier()

		return total


	#----------------------------------------------------------------------
	def Activate(self, data=None):
		"""This is a bit of a hack.  Really, we should expose a 
		functional view to the Computer-controlled players"""
		self.player.Activate( data )


	#----------------------------------------------------------------------
	def SetEnemy(self, enemy):
		self.enemy = enemy

	#----------------------------------------------------------------------
	def Buy(self, item, seller):
		if seller == None:
			print "non-implemented seller!"

		self.AddItem( item )
		ev =  BuyItemEvent( self, item, seller )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def Attack(self, opponent):
		print 'attacking...'

		#Do I hit him?  I guess so! (TODO)

		#Add any charactor-based bonuses here to weapon.GetPower()
		weapon = self.GetWeapons()[0]
		power = weapon.GetPower() + self.GetAttackModifiers()

		ev = CharactorAttackInitiated( self, opponent, weapon, power )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def Defend(self, attacker, weapon, power):
		#Can I block it / avoid?

		#Add any charactor-based bonuses here

		#Take damage
		print "I, ", self, " was damaged for ", power
		damage = power
		self.health = self.health - damage
		if self.health <= 0:
			self.Die()
		#print "I was attacked.  my health is now", self.health

		ev = CharactorAttackFinished( attacker, self, weapon, damage )
		self.evManager.Post( ev )


	#----------------------------------------------------------------------
	def Die(self):
		self.health = 0

		event = CharactorDeathEvent( self )
		self.evManager.Post( event )

	#----------------------------------------------------------------------
 	def Move(self, direction):
		if self.state == Charactor.STATE_INACTIVE:
			return

		if self.sector.MovePossible( direction ):
			newSector = self.sector.neighbors[direction]
			self.sector = newSector
			ev = CharactorMoveEvent( self )
			self.evManager.Post( ev )

	#----------------------------------------------------------------------
 	def Place(self, sector):
		self.sector = sector
		self.state = Charactor.STATE_ACTIVE

		ev = CharactorPlaceEvent( self )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, CharactorPlaceRequest ) \
		 and event.charactor is self:
			self.Place( event.sector )

		elif isinstance( event, BuyItemRequest ) \
		 and event.charactor is self:
			self.Buy( event.item, event.seller )

		elif isinstance( event, CharactorMoveRequest ) \
		 and event.charactor is self:
			self.Move( event.direction )

		elif isinstance( event, CharactorAttackInitiated) \
		 and event.defender is self:
			self.Defend( event.attacker, event.weapon, event.power )

		if isinstance( event, CharactorAttackInitiated):
			print "Am I the one?"
			print "me:", self
			print "vs defender:", event.defender


#-----------------------------------------------------------------------------
class Avatar(Charactor):
	def __init__(self, evManager, game, player):
		Charactor.__init__(self,evManager, game,player,"avatar")
		self.name = "Avatar"
		#todo: shouldn't need this self.cardGraveyard = {}
		#TODO: should add this stuff elsewhere.
		self.AddItem( Money(self.evManager,self) )
		card = HealthCard(self.evManager,self)
		#self.AddItem( card )
		#self.AddItem( card )
		#self.AddItem( card )
		#self.AddItem( card )
		self.AddItem( card )

	#----------------------------------------------------------------------
	def GetDeck(self):
		return self.inventory.GetItemsOfClass( UsableInFight )



#-----------------------------------------------------------------------------
class Manatee(Charactor):
	def __init__(self, evManager, game, player):
		Charactor.__init__(self,evManager, game,player,"manatee")
		self.name = "Manatee"
		self.AddItem( Money(self.evManager,self) )
		self.AddItem( DefaultManateeAttack(self.evManager,self) )

#-----------------------------------------------------------------------------
class Squirrel(Charactor):
	def __init__(self, evManager, game, player):
		Charactor.__init__(self,evManager, game,player,"squirrel")
		self.name = "Squirrel"
		self.AddItem( Money(self.evManager,self) )
		self.AddItem( DefaultManateeAttack(self.evManager,self) )



#------------------------------------------------------------------------------
class Map:
	"""..."""

	STATE_PREPARING = 0
	STATE_BUILT = 1


	#----------------------------------------------------------------------
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.state = Map.STATE_PREPARING

		self.sectors = range(3)
		self.startSectorIndex = 0
		self.bartenderIndex = 2

	#----------------------------------------------------------------------
	def Build(self):
		for i in range(3):
			self.sectors[i] = Sector( self.evManager )

		self.state = Map.STATE_BUILT

		ev = MapBuiltEvent( self )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, CharactorPlaceEvent ):
			sect = event.charactor.sector
			#self.startSectorIndex = self.sectors.index(sect)+1

#------------------------------------------------------------------------------
class Sector:
	"""..."""
	def __init__(self, evManager):
		self.evManager = evManager
		#self.evManager.RegisterListener( self )

		self.neighbors = range(4)

		self.neighbors[DIRECTION_UP] = None
		self.neighbors[DIRECTION_DOWN] = None
		self.neighbors[DIRECTION_LEFT] = None
		self.neighbors[DIRECTION_RIGHT] = None

	#----------------------------------------------------------------------
	def MovePossible(self, direction):
		if self.neighbors[direction]:
			return 1


if __name__ == "__main__":
	print "wasn't expecting that"

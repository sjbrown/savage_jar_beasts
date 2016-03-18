
from model import *
from twisted.spread import pb

# A list of ALL possible events that a server can send to a client
serverToClientEvents = []
# A list of ALL possible events that a client can send to a server
clientToServerEvents = []

#------------------------------------------------------------------------------
#Mix-In Helper Functions
#------------------------------------------------------------------------------
def MixInClass( origClass, addClass ):
	if addClass not in origClass.__bases__:
		origClass.__bases__ += (addClass ,)

#------------------------------------------------------------------------------
def MixInCopyClasses( someClass ):
	MixInClass( someClass, pb.Copyable )
	MixInClass( someClass, pb.RemoteCopy )


#------------------------------------------------------------------------------
class Placeholder:
	"""Placeholder objects are used when the __init__ constructor to the
	actual object takes more arguments than just evManager or when a 
	particular subclass of an object is requested, but we don't know what
	subclass it is until we pull the remote state"""
	#----------------------------------------------------------------------
	def __init__(self, evManager):
		self.evManager = evManager 
		self.finished = 0
		self.targetClassName = 'Unknown'
		self.objDict = {'evManager': self.evManager}

	#----------------------------------------------------------------------
	def __repr__(self):
		return "<Placeholder for "+ self.targetClassName + \
		       " at localID "+ str(id( self )) +">"

	#----------------------------------------------------------------------
	def ChangeToFullObject(self):
		"""Create the actual object here, possibly based 
		on targetClassName.  Set values using objDict"""

		#This is an abstract method, the code in here is just for
		#example purposes.
		raise Exception( "This method should always be overridden")

		if not self.finished:
			return None
		# ...
		safeClassNames = ['Some', 'List', 'of', 'Classnames']
		if self.targetClassName not in safeClassNames:
			print "ChangeToFullObject Failed"
			print "WARNING: possible code injection"
			raise Exception( "ChangeToFullObject Failed" )
		else:
			import moduleContainingClass
			className = getattr( module, self.targetClassName )

		self.__dict__ = self.objDict
		#Changing self.__class__ might feel dirty, but it's the best
		#way I've found to implement the needed behaviour. 
		#People have suggested that it's the most "pythony" way 
		#to do it.  The only known times it wont work would be if 
		#the class uses __slots__, or inherits from builtin types
		self.__class__ = className

		return self

	#----------------------------------------------------------------------
	def setCopyableState(self, stateDict, registry):
		"""Populate objDict in this method, and set targetClassName"""

		#This is an abstract method, the code in here is just for
		#example purposes.
		raise Exception( "This method should always be overridden")

		success = 1

		# ...
		self.targetClassName = stateDict['copyableClassName']
		# ...

		if success:
			self.finished = 1
		return [success, neededObjIDs]


	
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# For each event class, if it is sendable over the network, we have 
# to Mix In the "copy classes", or make a replacement event class that is 
# copyable

#------------------------------------------------------------------------------
# TickEvent
# Direction: don't send.
#The Tick event happens hundreds of times per second.  If we think we need
#to send it over the network, we should REALLY re-evaluate our design


#class SecondEvent(Event):
	#def __init__(self):
		#self.name = "Clock One Second Event"

#class QuitEvent(Event):
	#def __init__(self):
		#self.name = "Program Quit Event"

#class MapBuiltEvent(Event):
	#def __init__(self, map):
		#self.name = "Map Finished Building Event"
		#self.map = map

#------------------------------------------------------------------------------
# GameStartRequest
# Direction: Client to Server only
MixInCopyClasses( GameStartRequest )
pb.setUnjellyableForClass(GameStartRequest, GameStartRequest)
clientToServerEvents.append( GameStartRequest )
#class GameStartRequest(Event):
	#def __init__(self):
		#self.name = "Game Start Request"


#------------------------------------------------------------------------------
# GameStartedEvent
# Direction: Server to Client only
class CopyableGameStartedEvent(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.gameID =  id(event.game)
		registry[self.gameID] = event.game
		#TODO: put this in a Player Join Event or something
		for p in event.game.players:
			registry[id(p)] = p

pb.setUnjellyableForClass(CopyableGameStartedEvent, CopyableGameStartedEvent)
serverToClientEvents.append( CopyableGameStartedEvent )
#class GameStartedEvent(Event):
	#def __init__(self, game):
		#self.name = "Game Started Event"
		#self.game = game



#class CharactorMoveRequest(Event):
	#def __init__(self, player, charactor, direction):
		#self.name = "Charactor Move Request"
		#self.player = player
		#self.charactor = charactor
		#self.direction = direction

#class CharactorMoveEvent(Event):
	#def __init__(self, charactor):
		#self.name = "Charactor Move Event"
		#self.charactor = charactor

#class CharactorPlaceEvent(Event):
	#"""this event occurs when a Charactor is *placed* in a sector, 
	#ie it doesn't move there from an adjacent sector."""
	#def __init__(self, charactor):
		#self.name = "Charactor Placement Event"
		#self.charactor = charactor


#class ServerConnectEvent(Event):
	#"""the client generates this when it detects that it has successfully
	#connected to the server"""
	#def __init__(self, serverReference):
		#self.name = "Network Server Connection Event"
		#self.server = serverReference

#class ClientConnectEvent(Event):
	#"""this event is generated by the Server whenever a client connects
	#to it"""
	#def __init__(self, client):
		#self.name = "Network Client Connection Event"
		#self.client = client
#
#class ClientDisconnectEvent(Event):
	#"""this event is generated by the Server when it finds that a client 
	#is no longer connected"""
	#def __init__(self, client):
		#self.name = "Network Client Disconnection Event"
		#self.client = client
#
#class ExplicitClientDisconnectEvent(Event):
	#"""this event is generated by the Server when the client explicitly 
	#disconnects from it"""
	#def __init__(self, client):
		#self.name = "Explicit Network Client Disconnection Event"
		#self.client = client
#
#class PlayerClientMismatchEvent(Event):
	#"""this event is generated by the Server when a client tries to do 
	#something with a player he doesn't control"""
	#def __init__(self, playerName):
		#self.name = "Player / Client Mismatch"
		#self.playerName = playerName



#class GameSyncEvent(Event):
	#"""..."""
	#def __init__(self, game):
		#self.name = "Game Synched to Authoritative State"
		#self.game = game

#------------------------------------------------------------------------------
# PlayerJoinRequest
# Direction: Client to Server only
MixInCopyClasses( PlayerJoinRequest )
pb.setUnjellyableForClass(PlayerJoinRequest, PlayerJoinRequest)
clientToServerEvents.append( PlayerJoinRequest )
#class PlayerJoinRequest(Event):
	#"""..."""
	#def __init__(self, playerDict):
		#self.name = "Player Joining Game Request"
		#self.playerDict = playerDict
		#if not playerDict.has_key( 'name' ):
			#raise "UnnamedPlayerException"

#------------------------------------------------------------------------------
# PlayerJoinEvent
# Direction: Server to Client only
class CopyablePlayerJoinEvent( pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.playerID = id(event.player)
		registry[self.playerID] = event.player

	#----------------------------------------------------------------------
	def ReformatLocalToClient( self, registry ):
		#IF the client already has all the needed objects, we can
		# just create a Local-style event and return
		player = registry.get( self.playerID )
		if player:
			ev = PlayerJoinEvent( player )
			return ev
		#OTHERWISE, we still need some objects from the remote source
		else:
			return None

	#----------------------------------------------------------------------
	def ClientFetchNeededRemoteObjects( self, phonyModel ):
		"""This function needs to create dummy objects
		in the registry at their appropriate index.  Hopefully the 
		objects can be created with information from the phonyModel 
		passed in as an argument.  Then this function should call
		GetObjectState on the server, which will populate the objects
		so that they are no longer 'dummy' objects, but fully functional
		ones"""
		self.phonyModel = phonyModel
		self.registry = phonyModel.sharedObjs
		player = Player( phonyModel.phonyEvManager )
		self.registry[ self.playerID ] = player
		remoteResponse = phonyModel.server.callRemote( "GetObjectState",
		                                               self.playerID )
		remoteResponse.addCallback( phonyModel.ObjStateReturned,
		                            self.ClientFinalize )
	#----------------------------------------------------------------------
	def ClientFinalize( self, *trashVars ):
		player = self.registry[ self.playerID ]
		ev = PlayerJoinEvent( player )
		self.phonyModel.ReformattingCallback( ev )
		self.phonyModel = None
		self.registry = None
	#----------------------------------------------------------------------
		

pb.setUnjellyableForClass(CopyablePlayerJoinEvent, CopyablePlayerJoinEvent)
serverToClientEvents.append( CopyablePlayerJoinEvent )




#class PlayerJoinEvent(Event):
	#"""..."""
	#def __init__(self, player):
		#self.name = "Player Joined Game Event"
		#self.player = player
#
#class CharactorPlaceRequest(Event):
	#"""..."""
	#def __init__(self, player, charactor, sector):
		#self.name = "Charactor Placement Request"
		#self.player = player
		#self.charactor = charactor
		#self.sector = sector



#------- Duel Events ----------------------
class CopyableDuelStartRequest( pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name

		#TODO: this is Linear!  make a data structure on the client
		# so that it is O(1)
		self.player1ID = None
		self.player2ID = None
		for k,v in registry.iteritems():
			if v is event.player1:
				self.player1ID = k
			if v is event.player2:
				self.player2ID = k
		if self.player1ID is None:
			raise KeyError( 'no key for ', event.player )
		#--------------------end todo

	def ReformatLocalToServer(self, registry):
		player1 = registry[ self.player1ID ]
		if self.player2ID is None:
			player2 = None
		else:
			player2 = registry[ self.player2ID ]
		ev = DuelStartRequest( player1, player2 )
		return ev

pb.setUnjellyableForClass(CopyableDuelStartRequest, CopyableDuelStartRequest)
clientToServerEvents.append( CopyableDuelStartRequest )

#
#class DuelStartEvent(Event):
	#"""..."""
	#def __init__(self, duel):
		#self.name = "Duel Started Event"
		#self.duel = duel
class CopyableDuelStartEvent(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.duelID = id(event.duel)
		registry[self.duelID] = event.duel

	#----------------------------------------------------------------------
	def ReformatLocalToClient( self, registry ):
		#IF the client already has all the needed objects, we can
		# just create a Local-style event and return
		duel = registry.get( self.duelID )
		if duel:
			ev = DuelStartEvent( duel, self.turns )
			return ev
		#OTHERWISE, we still need some objects from the remote source
		else:
			return None

	#----------------------------------------------------------------------
	def ClientFetchNeededRemoteObjects( self, phonyModel ):
		"""This function needs to create dummy objects
		in the registry at their appropriate index.  Hopefully the 
		objects can be created with information from the phonyModel 
		passed in as an argument.  Then this function should call
		GetObjectState on the server, which will populate the objects
		so that they are no longer 'dummy' objects, but fully functional
		ones"""
		self.registry = phonyModel.sharedObjs
		duel = PlaceholderDuel( phonyModel.phonyEvManager )
		self.registry[ self.duelID ] = duel
		self.phonyModel = phonyModel
		remoteResponse = phonyModel.server.callRemote( "GetObjectState",
		                                               self.duelID )
		remoteResponse.addCallback( phonyModel.ObjStateReturned,
		                            self.ClientFinalize )
	def ClientFinalize( self, *trashVars ):
		"""ClientFinalize will be called by GetAllNeededObjects when all
		the needed objects have been retreived"""
		duel = self.registry[ self.duelID ]
		duel.Start()
		ev = DuelStartEvent( duel )
		self.phonyModel.ReformattingCallback( ev )
		self.phonyModel = None
		self.registry = None
	#----------------------------------------------------------------------
pb.setUnjellyableForClass(CopyableDuelStartEvent, CopyableDuelStartEvent)
serverToClientEvents.append( CopyableDuelStartEvent )


#
#class DuelChangePlayerEvent(Event):
class CopyableDuelChangePlayerEvent(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.duelID = id(event.duel)
		#registry should already have duel
		if not registry.has_key(self.duelID):
			print "Server Registry Should Already Have WeaponID"
			raise Exception()

	#----------------------------------------------------------------------
	def ReformatLocalToClient( self, registry ):
		#IF the client already has all the needed objects, we can
		# just create a Local-style event and return
		duel = registry.get( self.duelID )
		if not duel:
			print "This should not have happened."
			print "Maybe the server is being too chatty"
			print "We should already have duel"
			raise Exception()
		ev = DuelChangePlayerEvent( duel )
		return ev


pb.setUnjellyableForClass(CopyableDuelChangePlayerEvent, CopyableDuelChangePlayerEvent)
serverToClientEvents.append( CopyableDuelChangePlayerEvent )
	#"""..."""
	#def __init__(self, duel):
		#self.name = "Duel Changed Active Player"
		#self.duel = duel
#
#class DuelChangeStepEvent(Event):
class CopyableDuelChangeStepEvent(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.duelID = id(event.duel)
		#registry should already have duel
		if not registry.has_key(self.duelID):
			print "Server Registry Should Already Have WeaponID"
			raise Exception()

	#----------------------------------------------------------------------
	def ReformatLocalToClient( self, registry ):
		#return None to force a refresh of the duel object
		return None

	#----------------------------------------------------------------------
	def ClientFetchNeededRemoteObjects( self, phonyModel ):
		"""This function needs to create dummy objects
		in the registry at their appropriate index.  Hopefully the 
		objects can be created with information from the phonyModel 
		passed in as an argument.  Then this function should call
		GetObjectState on the server, which will populate the objects
		so that they are no longer 'dummy' objects, but fully functional
		ones"""
		self.registry = phonyModel.sharedObjs
		duel = self.registry.get( self.duelID )
		if not duel:
			print "This should not have happened."
			print "Maybe the server is being too chatty"
			print "We should already have duel"
			raise Exception()
		#self.registry[ self.duelID ] = duel
		self.phonyModel = phonyModel
		remoteResponse = phonyModel.server.callRemote( "GetObjectState",
		                                               self.duelID )
		remoteResponse.addCallback( phonyModel.ObjStateReturned,
		                            self.ClientFinalize )
	#----------------------------------------------------------------------
	def ClientFinalize( self, *trashVars ):
		"""ClientFinalize will be called by GetAllNeededObjects when all
		the needed objects have been retreived"""
		duel = self.registry[ self.duelID ]

		ev = DuelChangeStepEvent(duel)
		self.phonyModel.ReformattingCallback( ev )
		self.phonyModel = None
		self.registry = None


	#----------------------------------------------------------------------
pb.setUnjellyableForClass(CopyableDuelChangeStepEvent, CopyableDuelChangeStepEvent)
serverToClientEvents.append( CopyableDuelChangeStepEvent )
	#"""..."""
	#def __init__(self, duel):
		#self.name = "Duel Changed Step "+str(duel.step)
		#self.duel = duel
#
#class DuelContinueRequest(Event):
class CopyableDuelContinueRequest( pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name

		#TODO: this is Linear!  make a data structure on the client
		# so that it is O(1)
		self.playerID = None
		for k,v in registry.iteritems():
			if v is event.player:
				self.playerID = k
		if self.playerID is None:
			raise KeyError( 'no key for ', event.player )
		#--------------------end todo

	def ReformatLocalToServer(self, registry):
		player = registry[ self.playerID ]
		ev = DuelContinueRequest( player )
		return ev

pb.setUnjellyableForClass(CopyableDuelContinueRequest, CopyableDuelContinueRequest)
clientToServerEvents.append( CopyableDuelContinueRequest )

	#"""..."""
	#def __init__(self, player):
		#self.name = "Request from Player to goto next Duel step"
		#self.player = player
#
#class DuelTurnFinishedEvent(Event):
	#"""..."""
	#def __init__(self, duel):
		#self.name = "Player's Duel Turn Finished Event"
		#self.duel = duel
#
#class DuelFinishEvent(Event):
class CopyableDuelFinishEvent(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.duelID = id(event.duel)
		#registry should already have duel
		if not registry.has_key(self.duelID):
			print "Server Registry Should Already Have DuelID"
			raise Exception()

	#----------------------------------------------------------------------
	def ReformatLocalToClient( self, registry ):
		#IF the client already has all the needed objects, we can
		# just create a Local-style event and return
		duel = registry.get( self.duelID )
		if not duel:
			print "This should not have happened."
			print "Maybe the server is being too chatty"
			print "We should already have duel"
			raise Exception()
		#clean up and delete the attributes of the duel
		duel.Finish()

		ev = DuelFinishEvent( duel )
		return ev

	#----------------------------------------------------------------------
pb.setUnjellyableForClass(CopyableDuelFinishEvent, CopyableDuelFinishEvent)
serverToClientEvents.append( CopyableDuelFinishEvent )
	#"""..."""
	#def __init__(self, duel):
		#self.name = "Duel Finished Event"
		#self.duel = duel

#
#class DuelFlipCardRequest(Event):
class CopyableDuelFlipCardRequest( pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name

		#TODO: this is Linear!  make a data structure on the client
		# so that it is O(1)
		self.cardID = None
		self.duelID = None
		print "000000000000000000000"
		for k,v in registry.iteritems():
			if v is event.card:
				self.cardID = k
			if v is event.duel:
				self.duelID = k
		if self.cardID is None:
			raise KeyError( 'no key for ', event.card )
		if self.duelID is None:
			raise KeyError( 'no key for ', event.duel )
		#--------------------end todo

	def ReformatLocalToServer(self, registry):
		card = registry[ self.cardID ]
		duel = registry[ self.duelID ]
		ev = DuelFlipCardRequest( card, duel )
		return ev

pb.setUnjellyableForClass(CopyableDuelFlipCardRequest, CopyableDuelFlipCardRequest)
clientToServerEvents.append( CopyableDuelFlipCardRequest )
	#"""..."""
	#def __init__(self, card, duel):
		#self.name = "Charactor Requests FlipCard"
		#self.card = card
		#self.duel = duel
#
#class DuelFlipCardEvent(Event):
class CopyableDuelFlipCardEvent(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.cardID = id(event.card)
		self.duelID = id(event.duel)
		# Client should already have the card obj.  so should registry
		#registry[self.cardID] = event.card

	#----------------------------------------------------------------------
	def ReformatLocalToClient( self, registry ):
		#return None to force a refresh of the duel object
		#pretty much anything could have happened due to a card flip,
		#so refresh all the objects.
		return None

	#----------------------------------------------------------------------
	def ClientFetchNeededRemoteObjects( self, phonyModel ):
		"""This function needs to create dummy objects
		in the registry at their appropriate index.  Hopefully the 
		objects can be created with information from the phonyModel 
		passed in as an argument.  Then this function should call
		GetObjectState on the server, which will populate the objects
		so that they are no longer 'dummy' objects, but fully functional
		ones"""
		#pretty much anything could have happened due to a card flip,
		#so refresh the duel and all the monsters

		self.registry = phonyModel.sharedObjs
		duel = self.registry.get( self.duelID )
		if not duel:
			print "This should not have happened."
			print "Maybe the server is being too chatty"
			print "We should already have duel"
			raise Exception()


		#self.registry[ self.duelID ] = duel
		self.phonyModel = phonyModel

		self.monsters = duel.monsterField[0] + duel.monsterField[1] +\
		           duel.monsterGraveyard[0] + duel.monsterGraveyard[1]
		self.cards = duel.cardField[0] + duel.cardField[1] +\
		           duel.cardGraveyard[0] + duel.cardGraveyard[1]
		#TODO: this is Linear!  make a data structure on the client
		# so that it is O(1)
		#deleteList = []
		#for k,v in self.registry.iteritems():
			#if v in self.monsters:
				#deleteList.append(k)
			#if v in self.cards:
				#deleteList.append(k)
		#for k in deleteList:
			#del self.registry[k]
		#--------------------end todo

		remoteResponse = phonyModel.server.callRemote( "GetObjectState",
		                                               self.duelID )
		remoteResponse.addCallback( phonyModel.ObjStateReturned,
		                            self.ClientFinalize )

		#TODO: this is Linear!  make a data structure on the client
		# so that it is O(1)
		self.monsterIDs = []
		self.cardIDs = []
		for k,v in self.registry.iteritems():
			if v in self.monsters:
				self.monsterIDs.append(k)
			if v in self.cards:
				self.cardIDs.append(k)
		#--------------------end todo
#
		for i in self.monsterIDs + self.cardIDs:
			remoteResponse = phonyModel.server.callRemote(
			                                       "GetObjectState",
		                                               i )
			remoteResponse.addCallback( phonyModel.ObjStateReturned,
		                                    self.ClientFinalize )

	#----------------------------------------------------------------------
	def ClientFinalize( self, someObj ):
		"""ClientFinalize will be called by GetAllNeededObjects when all
		the needed objects have been retreived"""

		#TODO: do i need to check that the duel was retreived?
		#      probably, because it's asynchronus.

		print "Finalize called with", someObj
		if someObj in self.monsters:
			self.monsters.remove( someObj )
		if someObj in self.cards:
			self.cards.remove( someObj )

		if not ( self.cards + self.monsters ):
			duel = self.registry[ self.duelID ]
			card = self.registry[ self.cardID ]

			ev = DuelFlipCardEvent( card, duel )
			self.phonyModel.ReformattingCallback( ev )
			self.phonyModel = None
			self.registry = None
	#----------------------------------------------------------------------
pb.setUnjellyableForClass(CopyableDuelFlipCardEvent, CopyableDuelFlipCardEvent)
serverToClientEvents.append( CopyableDuelFlipCardEvent )
	#"""..."""
	#def __init__(self, card):
		#self.name = "Card Flip"
		#self.card = card
 
 
##------- Player  Events ----------------------

#class PlayerExploreRequest(Event):
class CopyablePlayerExploreRequest( pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name

		#TODO: this is Linear!  make a data structure on the client
		# so that it is O(1)
		self.playerID = None
		for k,v in registry.iteritems():
			if v is event.player:
				self.playerID = k
				break
		if self.playerID is None:
			raise KeyError( 'no key for ', event.player )
		#--------------------end todo

	def ReformatLocalToServer(self, registry):
		print "REG", registry, "\n"
		player = registry[ self.playerID ]
		ev = PlayerExploreRequest( player )
		return ev

pb.setUnjellyableForClass(CopyablePlayerExploreRequest, CopyablePlayerExploreRequest)
clientToServerEvents.append( CopyablePlayerExploreRequest )

#
#class PlayerExplorationEvent(Event):
class CopyablePlayerExplorationEvent(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.playerID = id(event.player)
		# Client should already have the player obj.  so should registry
		#registry[self.playerID] = event.player
		self.turns = event.turns

	#----------------------------------------------------------------------
	def ReformatLocalToClient( self, registry ):
		#IF the client already has all the needed objects, we can
		# just create a Local-style event and return
		player = registry.get( self.playerID )
		if player:
			ev = PlayerExplorationEvent( player, self.turns )
			return ev
		#OTHERWISE, we still need some objects from the remote source
		else:
			print "This should not have happened."
			print "Maybe the server is being too chatty"
			return None

	#----------------------------------------------------------------------
	def ClientFetchNeededRemoteObjects( self, phonyModel ):
		"""This function needs to create dummy objects
		in the registry at their appropriate index.  Hopefully the 
		objects can be created with information from the phonyModel 
		passed in as an argument.  Then this function should call
		GetObjectState on the server, which will populate the objects
		so that they are no longer 'dummy' objects, but fully functional
		ones"""
		print "Again, This should not have happened."
		print "Maybe the server is being too chatty"
	def ClientFinalize( self, *trashVars ):
		pass
	#----------------------------------------------------------------------
pb.setUnjellyableForClass(CopyablePlayerExplorationEvent, CopyablePlayerExplorationEvent)
serverToClientEvents.append( CopyablePlayerExplorationEvent )
#
#class PlayerRetreatRequest(Event):
	#"""..."""
	#def __init__(self, player):
		#self.name = "Player Requests Retreat"
		#self.player = player
#
#class PlayerRetreatEvent(Event):
	#"""..."""
	#def __init__(self, player):
		#self.name = "Player Retreats"
		#self.player = player
#
#
#
##------- Charactor Events ----------------------
#
#class CharactorAttackRequest(Event):
class CopyableCharactorAttackRequest( pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name

		#TODO: this is Linear!  make a data structure on the client
		# so that it is O(1)
		self.attackerID = None
		self.defenderID = None
		for k,v in registry.iteritems():
			if v is event.attacker:
				self.attackerID = k
			elif v is event.defender:
				self.defenderID = k
		if self.attackerID is None or self.defenderID is None:
			raise KeyError( 'no key found ' )
		#--------------------end todo

	def ReformatLocalToServer(self, registry):
		attacker = registry[ self.attackerID ]
		defender = registry[ self.defenderID ]
		ev = CharactorAttackRequest( attacker, defender )
		return ev

pb.setUnjellyableForClass(CopyableCharactorAttackRequest, CopyableCharactorAttackRequest)
clientToServerEvents.append( CopyableCharactorAttackRequest )
#
#------------------------------------------------------------------------------
#class CharactorAttackInitiated(Event):
class CopyableCharactorAttackInitiated(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.attackerID = id(event.attacker)
		#registry should already have attacker
		self.defenderID = id(event.defender)
		#registry should already have defender
		self.weaponID = id(event.weapon)
		registry[self.weaponID] = event.weapon

		self.power = event.power

	#----------------------------------------------------------------------
	def ReformatLocalToClient( self, registry ):
		#IF the client already has all the needed objects, we can
		# just create a Local-style event and return
		attacker = registry.get( self.attackerID )
		defender = registry.get( self.defenderID )
		weapon = registry.get( self.weaponID )
		if attacker and defender and weapon:
			ev = CharactorAttackInitiated( attacker,defender,
			                               weapon, self.power )
			return ev

		elif not attacker or not defender:
			print "This should not have happened."
			print "Maybe the server is being too chatty"
			print "We should already have attacker and defender"
			raise Exception()
		#OTHERWISE, we still need the weapon from the remote source
		else:
			self.attacker = attacker
			self.defender = defender
			return None

	#----------------------------------------------------------------------
	def ClientFetchNeededRemoteObjects( self, phonyModel ):
		"""This function needs to create dummy objects
		in the registry at their appropriate index.  Hopefully the 
		objects can be created with information from the phonyModel 
		passed in as an argument.  Then this function should call
		GetObjectState on the server, which will populate the objects
		so that they are no longer 'dummy' objects, but fully functional
		ones"""
		self.registry = phonyModel.sharedObjs
		weapon = PlaceholderItem( phonyModel.phonyEvManager )
		self.registry[ self.weaponID ] = weapon
		self.phonyModel = phonyModel
		remoteResponse = phonyModel.server.callRemote( "GetObjectState",
		                                               self.weaponID )
		remoteResponse.addCallback( phonyModel.ObjStateReturned,
		                            self.ClientFinalize )
	def ClientFinalize( self, *trashVars ):
		"""ClientFinalize will be called by GetAllNeededObjects when all
		the needed objects have been retreived"""
		self.weapon = self.registry[ self.weaponID ]
		ev = CharactorAttackInitiated( self.attacker,self.defender,
		                               self.weapon, self.power )
		self.phonyModel.ReformattingCallback( ev )
		self.phonyModel = None
		self.registry = None
	#----------------------------------------------------------------------
pb.setUnjellyableForClass(CopyableCharactorAttackInitiated, CopyableCharactorAttackInitiated)
serverToClientEvents.append( CopyableCharactorAttackInitiated )
#


#class CharactorAttackFinished(Event):
class CopyableCharactorAttackFinished(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.attackerID = id(event.attacker)
		#registry should already have attacker
		self.defenderID = id(event.defender)
		#registry should already have defender
		self.weaponID = id(event.weapon)
		if not registry.has_key(self.weaponID):
			print "Registry Should Already Have WeaponID"
			raise Exception()

		self.damage = event.damage

	#----------------------------------------------------------------------
	def ReformatLocalToClient( self, registry ):
		#IF the client already has all the needed objects, we can
		# just create a Local-style event and return
		attacker = registry.get( self.attackerID )
		defender = registry.get( self.defenderID )
		weapon = registry.get( self.weaponID )
		if attacker and defender and weapon:
			#return None because we want to force an update of the
			#defender's new state
			return None
		else:
			print "This should not have happened."
			print "Maybe the server is being too chatty"
			print "We should already have attacker and defender"
			raise Exception()


	#----------------------------------------------------------------------
	def ClientFetchNeededRemoteObjects( self, phonyModel ):
		"""This function needs to create dummy objects
		in the registry at their appropriate index.  Hopefully the 
		objects can be created with information from the phonyModel 
		passed in as an argument.  Then this function should call
		GetObjectState on the server, which will populate the objects
		so that they are no longer 'dummy' objects, but fully functional
		ones"""
		#the defender has just been attacked, therefore his state is
		#changed.  Let's get the updated state.
		self.registry = phonyModel.sharedObjs
		self.phonyModel = phonyModel
		remoteResponse = phonyModel.server.callRemote( "GetObjectState",
		                                               self.defenderID )
		remoteResponse.addCallback( phonyModel.ObjStateReturned,
		                            self.ClientFinalize )

	def ClientFinalize( self, *trashVars ):
		"""ClientFinalize will be called by GetAllNeededObjects when all
		the needed objects have been retreived"""
		attacker = self.registry.get( self.attackerID )
		defender = self.registry.get( self.defenderID )
		weapon = self.registry.get( self.weaponID )

		ev = CharactorAttackFinished( attacker,defender,
		                               weapon, self.damage )
		self.phonyModel.ReformattingCallback( ev )
		self.registry = None
		self.phonyModel = None

	#----------------------------------------------------------------------
pb.setUnjellyableForClass(CopyableCharactorAttackFinished, CopyableCharactorAttackFinished)
serverToClientEvents.append( CopyableCharactorAttackFinished )


#
#class CharactorDeathEvent(Event):
	#def __init__(self, charactor ):
		#self.name = "Charactor Died"
		#self.charactor = charactor
#
#class CharactorPlayCardRequest(Event):
class CopyableCharactorPlayCardRequest( pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name

		#TODO: this is Linear!  make a data structure on the client
		# so that it is O(1)
		self.charactorID = None
		self.cardID = None
		for k,v in registry.iteritems():
			if v is event.charactor:
				self.charactorID = k
			elif v is event.card:
				self.cardID = k
		if self.charactorID is None or self.cardID is None:
			raise KeyError( 'no key found ' )
		#--------------------end todo

	def ReformatLocalToServer(self, registry):
		charactor = registry[ self.charactorID ]
		card = registry[ self.cardID ]
		ev = CharactorPlayCardRequest( charactor, card )
		return ev

pb.setUnjellyableForClass(CopyableCharactorPlayCardRequest, CopyableCharactorPlayCardRequest)
clientToServerEvents.append( CopyableCharactorPlayCardRequest )
	#"""..."""
	#def __init__(self, charactor, card):
		#self.name = "Charactor Requests PlayCard"
		#self.charactor = charactor
		#self.card = card
#
#class CharactorPlayCardEvent(Event):
class CopyableCharactorPlayCardEvent(pb.Copyable, pb.RemoteCopy):
	def __init__(self, event, registry):
		self.name = "Copyable " + event.name
		self.charactorID = id(event.charactor)
		#registry should already have charactor
		self.cardID = id(event.card)
		#registry should already have card

	#----------------------------------------------------------------------
	def ReformatLocalToClient( self, registry ):
		#the client already has all the needed objects, we can
		# just create a Local-style event and return
		charactor = registry.get( self.charactorID )
		card = registry.get( self.cardID )
		if charactor and card:
			#return None because we want to force an update of the
			#card's new state
			ev = CharactorPlayCardEvent( charactor, card )
			return ev
		#OTHERWISE, we still need some objects from the remote source
		else:
			print "This should not have happened."
			print "Maybe the server is being too chatty"
			print "We should already have charactor and card"
			raise Exception()


	#----------------------------------------------------------------------
	def ClientFetchNeededRemoteObjects( self, phonyModel ):
		"""This function needs to create dummy objects
		in the registry at their appropriate index.  Hopefully the 
		objects can be created with information from the phonyModel 
		passed in as an argument.  Then this function should call
		GetObjectState on the server, which will populate the objects
		so that they are no longer 'dummy' objects, but fully functional
		ones"""
		print "Again, This should not have happened."
		print "Maybe the server is being too chatty"

	def ClientFinalize( self, *trashVars ):
		pass

	#----------------------------------------------------------------------
pb.setUnjellyableForClass(CopyableCharactorPlayCardEvent, CopyableCharactorPlayCardEvent)
serverToClientEvents.append( CopyableCharactorPlayCardEvent )
	#"""..."""
	#def __init__(self, charactor, card):
		#self.name = "Charactor Played Card"
		#self.charactor = charactor
		#self.card = card
#
#
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#class ModelEvent(Event): pass
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
#class EventItemUsed(ModelEvent):
	#def __init__(self, userCharactor, item, target=None):
		#self.name = "Item Used"
		#self.user = userCharactor
		#self.item = item
		#self.target = target
##-----------------------------------------------------------------------------
#class EventCharactorTurnFinished(ModelEvent):
	#def __init__(self, userCharactor ):
		#self.name = "Turn Done"
		#self.user = userCharactor
##-----------------------------------------------------------------------------
#class EventPlayerTurnFinished(ModelEvent):
	#def __init__(self, player ):
		#self.name = "Turn Done"
		#self.user = player 
##-----------------------------------------------------------------------------
#class EventInventoryChanged(ModelEvent):
	#def __init__(self, inventory ):
		#self.name = "Inventory Change"
		#self.inventory = inventory
##-----------------------------------------------------------------------------
#class EventFightFinished(ModelEvent):
	#def __init__(self ):
		#self.name = "Fight Done"

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# For any objects that we need to send in our events, we have to give them
# getStateToCopy() and setCopyableState() methods so that we can send a 
# network-friendly representation of them over the network.


#------------------------------------------------------------------------------
class CopyablePlayer:
	def getStateToCopy(self, registry):
		d = self.__dict__.copy()
		del d['evManager']

		gID = id( self.game )
		d['game'] = gID
		registry[gID] = self.game

		charactorIDList = []
		for charactor in self.charactors:
			cID = id( charactor )
			charactorIDList.append( cID )
			registry[cID] = charactor
		d['charactors'] = charactorIDList

		if d['duel'] is not None:
			print "ERROR: don't know what to do with duel"
			d['duel'] = None

		if d.has_key('monster'):
			d['monster'] = id( self.monster )

		if d.has_key('avatar'):
			print "ERROR: don't know what to do with avatar"
			d['avatar'] = id( self.avatar )


		return d

	def setCopyableState(self, stateDict, registry):
		neededObjIDs = []
		success = 1

		self.name = stateDict['name']

		if not registry.has_key( stateDict['game'] ):
			print "Something is very wrong.should already be a game"
			raise Exception()
		else:
			self.game = registry[stateDict['game']]

		aID = stateDict.get( 'avatar' )
		if aID and not registry.has_key( stateDict['avatar'] ):
			aID = stateDict['avatar']
		  	print "==="
			print "Player creating avatar at ID", aID
			registry[ aID ] = PlaceholderCharactor( self.evManager )

			self.avatar = registry[ aID ]
			neededObjIDs.append( aID ) 
			success = 0
		elif aID:
			self.avatar = registry[ aID ]

		mID = stateDict.get( 'monster' )
		if mID and not registry.has_key( mID ):
			registry[ mID ] = PlaceholderCharactor( self.evManager )
			self.monster = registry[ mID ]
			neededObjIDs.append( mID )
			success = 0
		elif mID:
			self.monster = registry[ mID ]
			

		self.charactors = []
		for cID in stateDict['charactors']:
			if registry.has_key( cID ):
				self.charactors.append( registry[cID] )
			else:
				#if the cID is not already in the registry
				# (because it was not found above 
				#  in monster, avatar, etc.)
				# then this is really weird.
				print "ERR: player has extra"

		return [success, neededObjIDs]

MixInClass( Player, CopyablePlayer )

#------------------------------------------------------------------------------
class PlaceholderCharactor(Placeholder):
	#----------------------------------------------------------------------
	def __init__(self, evManager):
		self.evManager = evManager 
		self.finished = 0
		self.targetClassName = 'Charactor'
		self.objDict = {'evManager': self.evManager}

	#----------------------------------------------------------------------
	def ChangeToFullObject(self):
		if not self.finished:
			return None

		#be careful of code-injection here.
		safeClassNames = ['Charactor', 'Avatar', 'Manatee', 'Squirrel']
		if self.targetClassName not in safeClassNames:
			print "ChangeToFullObject Failed"
			print "WARNING: possible code injection"
			raise Exception( "GetFinObj Failed" )
		else:
			import model
			className = getattr( model, self.targetClassName )

		self.__dict__ = self.objDict
		self.__class__ = className

		return self

	#----------------------------------------------------------------------
	def setCopyableState(self, stateDict, registry):
		neededObjIDs = []
		success = 1

		for attr in ['name', 'health', 'maxHealth', ]:
			if stateDict.has_key( attr ):
				self.objDict[attr] = stateDict[attr]

		#sectors aren't really used.  Might want to delete this section
		#eventually.
		if stateDict['sector'] == None:
			self.objDict['sector'] = None
		elif not registry.has_key( stateDict['sector'] ):
			registry[stateDict['sector']] = Sector(self.evManager)
			neededObjIDs.append( stateDict['sector'] )
			success = 0
		else:
			self.objDict['sector'] = registry[stateDict['sector']]

		#grab the game object.  should already have it in registry.
		if not registry.has_key( stateDict['game'] ):
			print "VERY ODD INDEED"
			print stateDict['game'], registry
			raise Exception()
		else:
			self.objDict['game'] = registry[stateDict['game']]

		#grab the player object.  should already have it in registry.
		if not registry.has_key( stateDict['player'] ):
			print "VERY ODD INDEED"
			print stateDict['player'], registry
			raise Exception()
		else:
			self.objDict['player'] = registry[stateDict['player']]

		self.targetClassName = stateDict['copyableClassName']

		if success:
			self.finished = 1
		return [success, neededObjIDs]
		

#------------------------------------------------------------------------------
class CopyableCharactor:
	#----------------------------------------------------------------------
	def getStateToCopy(self, registry):
		d = self.__dict__.copy()
		del d['evManager']

		if self.sector is None:
			sID = None
		else:
			sID = id( self.sector )
		d['sector'] = sID
		registry[sID] = self.sector

		gID = id( self.game )
		d['game'] = gID

		pID = id( self.player )
		d['player'] = pID

		#TODO: do inventory
		iID = id( self.inventory )
		d['inventory'] = iID

		#tell the receiver what the leafclass is so it knows what kind
		#of object to create on the other end.
		d['copyableClassName'] = self.__class__.__name__

		return d

	#----------------------------------------------------------------------
	def setCopyableState(self, stateDict, registry):
		neededObjIDs = []
		success = 1

		for attr in ['name', 'health', 
		             'maxHealth', ]:
			if stateDict.has_key( attr ):
				self.__dict__[attr] = stateDict[attr]

		return [success, neededObjIDs]


MixInClass( Charactor, CopyableCharactor )

#------------------------------------------------------------------------------
class PlaceholderDuel(Placeholder):
	#----------------------------------------------------------------------
	def __init__(self, evManager):
		self.evManager = evManager 
		self.finished = 0
		self.targetClassName = 'Duel'
		self.objDict = {'evManager': self.evManager}

	#----------------------------------------------------------------------
	def ChangeToFullObject(self):
		if not self.finished:
			return None

		self.__dict__ = self.objDict
		self.__class__ = Duel

		return self

	#----------------------------------------------------------------------
	def setCopyableState(self, stateDict, registry):
		neededObjIDs = []
		success = 1

		for attr in ['cardFieldMax', 'monsterFieldMax', 
		             'step', 'activePlayerIndex']:
			if stateDict.has_key( attr ):
				self.objDict[attr] = stateDict[attr]

		#players is 2 Player objects
		self.objDict['players'] = []
		for pID in stateDict['players']:
			if registry.has_key( pID ):
				self.objDict['players'].append( registry[pID] )
			else:
				registry[pID] = Player(self.evManager)
				neededObjIDs.append( pID )
				success = 0

		#decks is 2 lists of Card objects
		self.objDict['decks'] = []
		for i in range( 0, len( stateDict['decks'] ) ):
			cList = []
			for cID in stateDict['decks'][i]:
				if not registry.has_key( cID ):
					registry[cID] = PlaceholderItem(self.evManager)
					neededObjIDs.append( cID )
					success = 0
				elif isinstance(registry[cID], PlaceholderItem):
					print "Will this ever happen?"
					neededObjIDs.append( cID )
					success = 0
				else:
					cList.append( registry[cID] )
			self.objDict['decks'].append( cList )

		#cardField is 2 lists of Card objects
		self.objDict['cardField'] = []
		for i in range( 0, len( stateDict['cardField'] ) ):
			cList = []
			for cID in stateDict['cardField'][i]:
				if registry.has_key( cID ):
					cList.append( registry[cID] )
				else:
					#This should never happen!
					print "cardField has Unknown card!"
					success = 0
					return [success, neededObjIDs]
			self.objDict['cardField'].append( cList )

		#cardGraveyard is 2 lists of Card objects
		self.objDict['cardGraveyard'] = []
		for i in range( 0, len( stateDict['cardGraveyard'] ) ):
			cList = []
			for cID in stateDict['cardGraveyard'][i]:
				if registry.has_key( cID ):
					cList.append( registry[cID] )
				else:
					#This should never happen!
					print "cardGrave has Unknown monster!"
					success = 0
					return [success, neededObjIDs]
			self.objDict['cardGraveyard'].append( cList )

		#monsterField is 2 lists of Monster objects
		self.objDict['monsterField'] = []
		for i in range( 0, len( stateDict['monsterField'] ) ):
			mList = []
			for mID in stateDict['monsterField'][i]:
				if not registry.has_key( mID ):
					registry[mID] = PlaceholderCharactor(self.evManager)
					neededObjIDs.append( mID )
					success = 0
				elif isinstance( registry[mID], PlaceholderCharactor ):
					print "Will this ever happen?"
					neededObjIDs.append( mID )
					success = 0
				else:
					mList.append( registry[mID] )

			self.objDict['monsterField'].append( mList )

		#monsterGraveyard is 2 lists of Monster objects
		self.objDict['monsterGraveyard'] = []
		for i in range( 0, len( stateDict['monsterGraveyard'] ) ):
			mList = []
			for mID in stateDict['monsterGraveyard'][i]:
				if registry.has_key( mID ):
					mList.append( registry[mID] )
				else:
					#This should never happen!
					print "Graveyard has Unknown monster!"
					success = 0
					return [success, neededObjIDs]
			self.objDict['monsterGraveyard'].append( mList )

		#pendingAttack is 2 Monster objects or None
		if stateDict['pendingAttack'] is None:
			pAttack = None
		else:
			pAttack = []
			for mID in stateDict['pendingAttack']:
				if registry.has_key( mID ):
					pAttack.append( registry[mID] )
				else:
					#This should never happen!
					print "pAttack has Unknown monster!"
					success = 0
					return [success, neededObjIDs]
		self.objDict['pendingAttack'] = pAttack

		if success:
			self.finished = 1
		return [success, neededObjIDs]

#------------------------------------------------------------------------------
class CopyableDuel:
	def getStateToCopy(self, registry):
		d = self.__dict__.copy()
		del d['evManager']

		#players is a list of 2 Player Objects
		playerList = []
		for p in self.players:
			pID = id( p )
			playerList.append( pID )
			registry[pID] = p
		d['players'] = playerList

		#decks is 2 lists of Card objects
		decksList = []
		for i in range( 0, len( d['decks'] ) ):
			cList = []
			for card in d['decks'][i]:
				cID = id( card )
				cList.append( cID )
				registry[cID] = card
			decksList.append( cList )
		d['decks'] = decksList

		#cardField is 2 lists of Card objects
		cardFieldList = []
		for i in range( 0, len( d['cardField'] ) ):
			cList = []
			for card in d['cardField'][i]:
				cID = id( card )
				cList.append( cID )
				registry[cID] = card
			cardFieldList.append( cList )
		d['cardField'] = cardFieldList

		#cardGraveyard is 2 lists of Card objects
		cardGraveyardList = []
		for i in range( 0, len( d['cardGraveyard'] ) ):
			cList = []
			for card in d['cardGraveyard'][i]:
				cID = id( card )
				cList.append( cID )
				registry[cID] = card
			cardGraveyardList.append( cList )
		d['cardGraveyard'] = cardGraveyardList

		#monsterField is 2 lists of Monster objects
		monsterFieldList = []
		for i in range( 0, len( d['monsterField'] ) ):
			cList = []
			for monster in d['monsterField'][i]:
				cID = id( monster )
				cList.append( cID )
				registry[cID] = monster
			monsterFieldList.append( cList )
		d['monsterField'] = monsterFieldList

		#monsterGraveyard is 2 lists of Monster objects
		monsterGraveyardList = []
		for i in range( 0, len( d['monsterGraveyard'] ) ):
			cList = []
			for monster in d['monsterGraveyard'][i]:
				cID = id( monster )
				cList.append( cID )
				registry[cID] = monster
			monsterGraveyardList.append( cList )
		d['monsterGraveyard'] = monsterGraveyardList

		#pendingAttack is 2 Monster objects or None
		if d['pendingAttack'] is not None:
			pendingAttackList = []
			try:
				for monster in d['pendingAttack']:
					cID = id( monster )
					pendingAttackList.append( cID )
					registry[cID] = monster
			except:
				print d['pendingAttack']
				print ""
				print ""
				print d
				raise Exception()
			d['pendingAttack'] = pendingAttackList


		return d

	#----------------------------------------------------------------------
	def setCopyableState(self, stateDict, registry):
		neededObjIDs = []
		success = 1

		print "              ----- getting Duel state ----"

		for attr in ['cardFieldMax', 'monsterFieldMax', 
		             'step', 'activePlayerIndex']:
			if stateDict.has_key( attr ):
				self.__dict__[attr] = stateDict[attr]

		#decks is 2 lists of Card objects
		self.decks = []
		for i in range( 0, len( stateDict['decks'] ) ):
			cList = []
			for cID in stateDict['decks'][i]:
				if not registry.has_key( cID ):
					registry[cID] = PlaceholderItem(self.evManager)
					neededObjIDs.append( cID )
					success = 0
				elif isinstance(registry[cID], PlaceholderItem):
					print "Will this ever happen?"
					neededObjIDs.append( cID )
					success = 0
				else:
					cList.append( registry[cID] )
			self.decks.append( cList )

		#cardField is 2 lists of Card objects
		self.cardField = []
		for i in range( 0, len( stateDict['cardField'] ) ):
			cList = []
			for cID in stateDict['cardField'][i]:
				if registry.has_key( cID ):
					cList.append( registry[cID] )
				else:
					registry[cID] = PlaceholderItem(self.evManager)
					neededObjIDs.append( cID )
					success = 0
					#TODO:
					#do i need this here?  if so, this if
					#block can be made simpler.
					cList.append( registry[cID] )

			self.cardField.append( cList )

		#cardGraveyard is 2 lists of Card objects
		self.cardGraveyard = []
		for i in range( 0, len( stateDict['cardGraveyard'] ) ):
			cList = []
			for cID in stateDict['cardGraveyard'][i]:
				if registry.has_key( cID ):
					cList.append( registry[cID] )
				else:
					registry[cID] = PlaceholderItem(self.evManager)
					neededObjIDs.append( cID )
					success = 0
					#TODO:
					#do i need this here?  if so, this if
					#block can be made simpler.
					cList.append( registry[cID] )
			self.cardGraveyard.append( cList )

		#monsterField is 2 lists of Monster objects
		self.monsterField = []
		for i in range( 0, len( stateDict['monsterField'] ) ):
			mList = []
			for mID in stateDict['monsterField'][i]:
				if not registry.has_key( mID ):
					registry[mID] = PlaceholderCharactor(self.evManager)
					neededObjIDs.append( mID )
					success = 0
					#TODO: do i have to add to mList?
				elif isinstance( registry[mID], PlaceholderCharactor ):
					print "Will this ever happen?"
					neededObjIDs.append( mID )
					success = 0
				else:
					mList.append( registry[mID] )

			self.monsterField.append( mList )

		#monsterGraveyard is 2 lists of Monster objects
		self.monsterGraveyard = []
		for i in range( 0, len( stateDict['monsterGraveyard'] ) ):
			mList = []
			for mID in stateDict['monsterGraveyard'][i]:
				if registry.has_key( mID ):
					mList.append( registry[mID] )
				else:
					registry[mID] = PlaceholderCharactor(self.evManager)
					neededObjIDs.append( mID )
					success = 0
					#TODO: do i have to add to mList?
			self.monsterGraveyard.append( mList )

		#pendingAttack is 2 Monster objects or None
		if stateDict['pendingAttack'] is None:
			pAttack = None
		else:
			pAttack = []
			for mID in stateDict['pendingAttack']:
				if registry.has_key( mID ):
					pAttack.append( registry[mID] )
				else:
					#This should never happen!
					print "pAttack has Unknown monster!"
					success = 0
					return [success, neededObjIDs]
		self.pendingAttack = pAttack

		if success:
			self.finished = 1
		return [success, neededObjIDs]

MixInClass( Duel, CopyableDuel )

#------------------------------------------------------------------------------
class PlaceholderItem(Placeholder):
	#----------------------------------------------------------------------
	def __init__(self, evManager):
		Placeholder.__init__( self, evManager )
		self.targetClassName = 'Item'

	#----------------------------------------------------------------------
	def ChangeToFullObject(self):
		if not self.finished:
			return None

		from item import HealthCard

		safeClassNames = ['Item', 'HealthCard',
		                  'DefaultManateeAttack',
		                  'DefaultSquirrelAttack' ]
		if self.targetClassName not in safeClassNames:
			print "ChangeToFullObject Failed"
			print "WARNING: possible code injection"
			raise Exception( "GetFinObj Failed" )
		else:
			import item
			className = getattr( item, self.targetClassName )

		self.__dict__ = self.objDict
		self.__class__ = className

		return self

	#----------------------------------------------------------------------
	def setCopyableState(self, stateDict, registry):
		neededObjIDs = []
		success = 1

		for attr in ['description', 'value', 
		             'isStackable', 'currentPrice',
		             'power', 'facing']:
			if stateDict.has_key( attr ):
				self.objDict[attr] = stateDict[attr]

		aID = stateDict['owner'] 
		if aID is not None:
			if registry.has_key( aID ):
				self.objDict['owner'] = registry[aID]
			else:
				registry[aID] = PlaceholderCharactor(
				                                self.evManager)
				neededObjIDs.append( aID )
				success = 0

		self.targetClassName = stateDict['copyableClassName']

		if success:
			self.finished = 1
		return [success, neededObjIDs]

#------------------------------------------------------------------------------
class CopyableItem:
	def getStateToCopy(self, registry):
		d = self.__dict__.copy()
		del d['evManager']

		del d['barterTarget']

		#owner is a Avatar Object
		if self.owner is not None:
			aID = id( self.owner )
			registry[aID] = self.owner
			d['owner'] = aID

		#tell the receiver what the leafclass is so it knows what kind
		#of object to create on the other end.
		d['copyableClassName'] = self.__class__.__name__


		return d

	#----------------------------------------------------------------------
	def setCopyableState(self, stateDict, registry):
		neededObjIDs = []
		success = 1

		for attr in ['facing', ]:
			if stateDict.has_key( attr ):
				self.attr = stateDict[attr]

		if success:
			self.finished = 1
		return [success, neededObjIDs]


MixInClass( Item, CopyableItem )


#------------------------------------------------------------------------------
class PlaceholderInventory(Placeholder):
	#----------------------------------------------------------------------
	def __init__(self, evManager):
		Placeholder.__init__( self, evManager )
		self.targetClassName = 'Inventory'

	#----------------------------------------------------------------------
	def ChangeToFullObject(self):
		if not self.finished:
			return None

		safeClassNames = ['Inventory']
		if self.targetClassName not in safeClassNames:
			print "ChangeToFullObject Failed"
			print "WARNING: possible code injection"
			raise Exception( "GetFinObj Failed" )
		else:
			import model 
			className = getattr( model, self.targetClassName )

		self.__dict__ = self.objDict
		self.__class__ = className

		return self

	#----------------------------------------------------------------------
	def setCopyableState(self, stateDict, registry):
		neededObjIDs = []
		success = 1

		aID = stateDict['owner'] 
		if aID is not None:
			if registry.has_key( aID ):
				self.objDict['owner'] = registry[aID]
			else:
				registry[aID] = PlaceholderCharactor(
				                                self.evManager)
				neededObjIDs.append( aID )
				success = 0

		#decks is 2 lists of Card objects
		intDict = {}
		for key, val in stateDict['internalDict'].iteritems():
			#one of these dicts has 'item' and 'quantity'
			if type(val) is dict:
				itemID = val['item']
				if not registry.has_key( itemID ):
					registry[itemID] = PlaceholderItem(self.evManager)
					neededObjIDs.append( itemID )
					success = 0
				else:
					intDict[key] = {
					           'item':registry[itemID],
					           'quantity': val['quantity']
					           }
			else:
				#val is an item
				itemID = val
				if not registry.has_key( itemID ):
					registry[itemID] = PlaceholderItem(self.evManager)
					neededObjIDs.append( itemID )
					success = 0
				else:
					intDict[key] = registry[itemID]

		self.objDict['internalDict'] = intDict



		self.targetClassName = stateDict['copyableClassName']

		if success:
			self.finished = 1
		return [success, neededObjIDs]

#------------------------------------------------------------------------------
class CopyableInventory:
	def getStateToCopy(self, registry):
		d = self.__dict__.copy()
		del d['evManager']

		#owner is a Charactor Object
		if self.owner is not None:
			aID = id( self.owner )
			registry[aID] = self.owner
			d['owner'] = aID

		#internalDict is a dictionary of either items or dicts
		for key, val in d['internalDict'].iteritems():
			#one of these dicts has 'item' and 'quantity'
			if type(val) is dict:
				itemID = id( val['item'] )
				registry[itemID] = val['item']
				d['internalDict'][key]['item'] = itemID
			else:
				#val is an item
				itemID = id( val )
				registry[itemID] = val
				d['internalDict'][key] = itemID


		#tell the receiver what the leafclass is so it knows what kind
		#of object to create on the other end.
		d['copyableClassName'] = self.__class__.__name__


		return d

MixInClass( Item, CopyableItem )


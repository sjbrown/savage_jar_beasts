from weakref import WeakKeyDictionary
from events import *

#------------------------------------------------------------------------------
class EventManager:
	"""this object is responsible for coordinating most communication
	between the Model, View, and Controller."""
	def __init__(self ):
		self.listeners = WeakKeyDictionary()
		self.eventQueue= []
		self.pendingGUIBlockers = 0

		self.currEvent = None

	#----------------------------------------------------------------------
	def Debug( self, ev):
		#return
		if isinstance( ev, GUIFocusThisWidgetEvent ):
			return
		if not isinstance( ev, GUIMouseMoveEvent ):
			#print "self", self
			print "   Message: " + ev.name
		if isinstance( ev, CharactorAttackFinished ):
			print "ATT FINISH"
			print ev
			print ev.__dict__

	#----------------------------------------------------------------------
	def RegisterListener( self, listener ):
		#if not hasattr( listener, "Notify" ): raise blah blah...
		self.listeners[ listener ] = 1

	#----------------------------------------------------------------------
	def UnregisterListener( self, listener ):
		if listener in self.listeners.keys():
			del self.listeners[ listener ]
		
	#----------------------------------------------------------------------
	def Tell( self ):
		print "--CURR EVENT: ", self.currEvent

	#----------------------------------------------------------------------
	def Post( self, event ):
		#This method builds up a queue until a Tick event is sent
		#the idea is to avoid mis-ordered events (ACB)
		#this is a quite effective method in the client, because it is
		#always Ticking, but we don't want the server to always tick.
		from copy import copy
		if not isinstance(event, TickEvent): 
			self.eventQueue.append( event )
		else:
			events = copy( self.eventQueue )
			self.eventQueue = []
			while len(events) > 0:
				ev = events.pop(0)
				self.currEvent = ev

				if isinstance( ev, GUIBlockEvent ):
					self.pendingGUIBlockers += 1
				elif isinstance( ev, GUIUnBlockEvent ):
					self.pendingGUIBlockers -= 1

				elif self.pendingGUIBlockers > 0 \
				  and isinstance( ev, GUIEvent ):
					self.eventQueue.append( ev )
					continue

				self.Debug( ev )

				for listener in self.listeners.keys():
					listener.Notify( ev )

			#at the end, notify listeners of the Tick event
			for listener in self.listeners.keys():
				self.currEvent = event
				listener.Notify( event )

			if 0 and self.eventQueue:
				print 'remaining queue:', self.eventQueue



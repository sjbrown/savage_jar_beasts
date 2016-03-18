from events import *
from utils import *
from model import *

import pygame
from pygame.locals import *
from gui import GUIView, SimpleGUIController
from gui_widgets import *

SIZE_RECT = (0,0,800,600)

#------------------------------------------------------------------------------
class ExploreScreenController(SimpleGUIController):
	"""..."""

	MODE_SELECT = 0
	MODE_ACTION = 1

	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.rectOfInterest = pygame.Rect( SIZE_RECT )

		self.mode = ExploreScreenController.MODE_SELECT

	#----------------------------------------------------------------------
	def WantsEvent( self, event ):
		if event.type == MOUSEBUTTONUP \
		  or event.type == MOUSEMOTION \
		  and self.rectOfInterest.collidepoint( event.pos ):
			return 1

		return 0


#------------------------------------------------------------------------------
class ExploreScreen(GUIView):
	"""..."""
	STATE_PREPARING = 0
	STATE_RUNNING = 1
	#----------------------------------------------------------------------
	def __init__(self, evManager, player, turns):
		GUIView.__init__(self, evManager)
		self.state = ExploreScreen.STATE_PREPARING
		self.turns = turns
		self.player = player
		
	#----------------------------------------------------------------------
	def Explore(self):
		print "calling Explore"
		b1= TurnClock( self.evManager, self.turns, container=self )

		self.widgets.append( b1 )

		self.renderGroup.add( self.widgets )

		self.ArrangeWidgets()

	#----------------------------------------------------------------------
 	def GetBackgroundBlit(self):
		bgImg = load_png( 'main_explore_background.png')
		return [ bgImg, self.rect ]

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self):
		xyOffset = ( self.rect.x, self.rect.y )
		self.widgets[0].rect.center = self.rect.center

	#----------------------------------------------------------------------
 	def Notify(self, event):
		GUIView.Notify( self, event )

		if isinstance( event, TickEvent ) \
		  and self.state == ExploreScreen.STATE_PREPARING:
			self.state = ExploreScreen.STATE_RUNNING
			self.Explore()

		#if isinstance( event, PlayerExplorationEvent ):
			#self.Explore( event.player, event.turns )

		if isinstance( event, DuelStartEvent ):
			import gui
			player = gui.playerRef.player
			if player in event.duel.players:
				ev = GUIChangeScreenRequest( 'forest' )
				self.evManager.Post( ev )


#------------------------------------------------------------------------------
class TurnClock(AnimatedWidget):
	def __init__(self, evManager, turns, container=None):
		animation = load_animation( 'turn_clock' )
		AnimatedWidget.__init__( self, evManager, animation, container )


		self.turns = turns
		ev = GUIBlockEvent( )
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def AnimationFinished(self):
		self.turns -= 1
		if self.turns == 0:
			ev = GUIUnBlockEvent()
			self.evManager.Post( ev )
			import gui
			player = gui.playerRef.player
			ev = DuelStartRequest( player, None )
			self.evManager.Post( ev )
		elif self.turns < 0:
			print "turns shouldn't go less than zero"
		else:
			self.animation.first()




if __name__ == "__main__":
	print "that was unexpected"

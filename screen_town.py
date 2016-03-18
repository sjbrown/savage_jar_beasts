from events import *
from utils import *
from model import *

import pygame
from pygame.locals import *
from gui import GUIView, SimpleGUIController
from gui_widgets import *

SIZE_RECT = (0,0,800,600)

#------------------------------------------------------------------------------
class MainTownScreenController(SimpleGUIController):
	"""..."""

	MODE_SELECT = 0
	MODE_ACTION = 1

	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.rectOfInterest = pygame.Rect( SIZE_RECT )

		self.mode = MainTownScreenController.MODE_SELECT

	#----------------------------------------------------------------------
	def WantsEvent( self, event ):
		if event.type == MOUSEBUTTONUP \
		  or event.type == MOUSEMOTION \
		  and self.rectOfInterest.collidepoint( event.pos ):
			return 1

		return 0


#------------------------------------------------------------------------------
class MainTownScreen(GUIView):
	"""..."""
	#----------------------------------------------------------------------
	def Activate( self, renderGroup, rect, evManager=None ):
		GUIView.Activate(self, renderGroup, rect, evManager)
		
		b1= HomeButton( self.evManager, container=self )
		b2= StoreButton( self.evManager, container=self )
		b3= ForestButton( self.evManager, container=self )
		b4= ArenaButton( self.evManager, container=self )

		self.widgets = [ b1,b2,b3,b4 ]

		self.renderGroup.add( self.widgets )

		self.ArrangeWidgets()

	#----------------------------------------------------------------------
 	def GetBackgroundBlit(self):
		bgImg = load_png( 'main_town_background.png')
		return [ bgImg, self.rect ]

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self):
		xyOffset = ( self.rect.x, self.rect.y )
		self.widgets[0].rect.topleft = vectorSum( xyOffset, (50, 400) ) 
		self.widgets[1].rect.topleft = vectorSum( xyOffset, (300, 300) )
		self.widgets[2].rect.topleft = vectorSum( xyOffset, (600, 100) )
		self.widgets[3].rect.topleft = vectorSum( xyOffset, (50, 100) )


#------------------------------------------------------------------------------
class HomeButton(ButtonSprite):
	def __init__(self, evManager, container=None):
		Widget.__init__( self, evManager, container )

		self.image = load_png( 'button_home.png' )
		self.idleImage = self.image
		self.focusedImage = load_png( 'button_home_f.png' )
		self.rect = self.image.get_rect()

		self.onClickEvent = None

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		if self.focused:
			self.image = self.focusedImage
		else:
			self.image = self.idleImage
		self.pos = self.rect.center
		self.rect = self.image.get_rect()
		self.rect.center = self.pos

		self.dirty = 0

#------------------------------------------------------------------------------
class StoreButton(HomeButton):
	def __init__(self, evManager, container=None):
		Widget.__init__( self, evManager, container )

		self.image = load_png( 'button_store.png' )
		self.idleImage = self.image
		self.focusedImage = load_png( 'button_store_f.png' )
		self.rect = self.image.get_rect()

	#----------------------------------------------------------------------
	def Click(self):
		import gui
		player = gui.playerRef.player
		ev = GoToStoreRequest( player )
		self.evManager.Post( ev )
	#----------------------------------------------------------------------
	def Notify(self, event):
		HomeButton.Notify( self, event )

		if isinstance( event, GoToStoreEvent ):
			print "SWITCHING TO STORE"
			from screen_store import StoreScreen, \
			                           StoreScreenController
			from eventmanager import EventManager
			# we don't want the new Gui reacting to events before
			# it is active, so give it a dummy event manager that
			# won't send it anything
			dummyEvManager = EventManager()
			view = StoreScreen( dummyEvManager,
			                      event.player )
			cont = StoreScreenController( self.evManager )
			ev = GUIChangeScreenRequest( ([view], [cont]) )
			self.evManager.Post( ev )



#------------------------------------------------------------------------------
class ArenaButton(StoreButton): pass
#------------------------------------------------------------------------------
class ForestButton(HomeButton):
	def __init__(self, evManager, container=None):
		Widget.__init__( self, evManager, container )

		self.image = load_png( 'button_park.png' )
		self.idleImage = self.image
		self.focusedImage = load_png( 'button_park_f.png' )
		self.rect = self.image.get_rect()

		self.onClickEvent = None
	#----------------------------------------------------------------------
	def Click(self):
		import gui
		player = gui.playerRef.player
		ev = PlayerExploreRequest( player )
		self.evManager.Post( ev )
	#----------------------------------------------------------------------
	def Notify(self, event):
		HomeButton.Notify( self, event )

		if isinstance( event, PlayerExplorationEvent ):
			print "SWITCHING TO EXPLORE"
			from screen_explore import ExploreScreen, \
			                           ExploreScreenController
			from eventmanager import EventManager
			dummyEvManager = EventManager()
			view = ExploreScreen( dummyEvManager,
			                      event.player, event.turns )
			cont = ExploreScreenController( self.evManager )
			ev = GUIChangeScreenRequest( ([view], [cont]) )
			self.evManager.Post( ev )





if __name__ == "__main__":
	print "that was unexpected"

from events import *
from utils import *
from model import *

import pygame
from pygame.locals import *
from gui import GUIView, SimpleGUIController
from gui_widgets import *

SIZE_RECT = (0,0,800,600)

# TODO: this is the same as every other controller.  i should probably
#       consolidate
#------------------------------------------------------------------------------
class StoreScreenController(SimpleGUIController):
	"""..."""

	MODE_SELECT = 0
	MODE_ACTION = 1

	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.rectOfInterest = pygame.Rect( SIZE_RECT )

		self.mode = StoreScreenController.MODE_SELECT

	#----------------------------------------------------------------------
	def WantsEvent( self, event ):
		if event.type == MOUSEBUTTONUP \
		  or event.type == MOUSEMOTION \
		  and self.rectOfInterest.collidepoint( event.pos ):
			return 1

		elif event.type == KEYDOWN \
		     and event.key == K_ESCAPE:
			return 1

		return 0

	#----------------------------------------------------------------------
	def HandlePyGameEvent(self, event):
		ev = None

		if event.type == KEYDOWN \
		     and event.key == K_ESCAPE:
			import gui
			player = gui.playerRef.player
	
			ev = GoToTownRequest( player )

		elif event.type == MOUSEBUTTONUP:
			b = event.button
			if b == 1:
				ev = GUIClickEvent(event.pos)
			else:
				msg = "Button 2 doesn't work"
				ev = GUIDialogAddRequest( 'msgDialog', msg )

		elif event.type == MOUSEMOTION:
			ev = GUIMouseMoveEvent(event.pos)


		if ev:
			self.evManager.Post( ev )


#------------------------------------------------------------------------------
class StoreScreen(GUIView):
	"""This screen often needs to have a little cutscene in front
	that will interrupt."""
	STATE_PREPARING = 0
	STATE_RUNNING = 1
	#----------------------------------------------------------------------
	def __init__(self, evManager, player ):
		GUIView.__init__(self, evManager)
		self.state = StoreScreen.STATE_PREPARING
		self.player = player
		self.selectedItem =  None
		
	#----------------------------------------------------------------------
	def Activate( self, renderGroup, rect, evManager=None ):
		GUIView.Activate(self, renderGroup, rect, evManager)
		self.state = StoreScreen.STATE_RUNNING

		avatar = self.player.avatar
		card = HealthCard( self.evManager )
		buyEvent = BuyItemRequest( avatar, card )
		leaveEvent = GoToTownRequest( self.player )


		self.buttons = {
		                'buy': ['Buy', buyEvent],
		                'leave': ['Leave', leaveEvent],
		               }

		self.widgets = [
		                 ButtonSprite( self.evManager,
		                          self.buttons['buy'][0],
		                          container=self,
		                          onClickEvent=self.buttons['buy'][1],
		                 ),
		                 ButtonSprite( self.evManager,
		                          self.buttons['leave'][0],
		                          container=self,
		                          onClickEvent=self.buttons['leave'][1],
		                 )
		               ]
		self.renderGroup.add( self.widgets )

		self.ArrangeWidgets()

	#----------------------------------------------------------------------
 	def GetBackgroundBlit(self):
		bgImg = load_png( 'main_store_background.png')
		return [ bgImg, self.rect ]

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self):
		xyOffset = ( self.rect.x, self.rect.y )
		self.widgets[0].rect.topleft = 100,100
		self.widgets[1].rect.topleft = (0,0)

	#----------------------------------------------------------------------
 	def Notify(self, event):
		GUIView.Notify( self, event )

		if isinstance( event, GoToTownEvent ):
			ev = GUIChangeScreenRequest( 'town' )
			self.evManager.Post( ev )




if __name__ == "__main__":
	print "that was unexpected"

import pygame
from pygame.locals import *
import string

from gui import *
from events import *
import preferences
from utils import load_png


SIZE_RECT = (37,540,763,49)

#------------------------------------------------------------------------------
class MainGUIController(GUIController):
	"""..."""
	def __init__(self, evManager):
		GUIController.__init__(self, evManager)

		self.rectOfInterest = pygame.Rect( SIZE_RECT )

	#----------------------------------------------------------------------
	def WantsEvent( self, event ):
		if (event.type == KEYDOWN and event.key == K_ESCAPE):
			return 1

		elif ( event.type == MOUSEBUTTONUP \
		  or event.type == MOUSEMOTION ) \
		  and self.rectOfInterest.collidepoint( event.pos ):
			return 1

		return 0

	#----------------------------------------------------------------------
	def HandlePyGameEvent(self, event):
		ev = None

		if event.type == KEYDOWN \
		     and event.key == K_ESCAPE:
			ev = GUIChangeScreenRequest( 'menu' )


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
class MainGUIView(GUIView):
	"""..."""
	clipRect = pygame.Rect( SIZE_RECT )

	#----------------------------------------------------------------------
	def Activate( self, renderGroup, rect, evManager=None ):
		GUIView.Activate(self, renderGroup, rect, evManager)


		playerData = preferences.playerData

		menuEvent = GUIChangeScreenRequest( 'menu' )
		joinEvent = PlayerJoinRequest( playerData )

		b1= ButtonSprite( self.evManager, "End Game", container=self,
		                  onClickEvent=menuEvent )
		#b2= ButtonSprite( self.evManager, "Player Join", container=self,
		                  #onClickEvent=joinEvent)
		#b3= ButtonSprite(evManager, "Place Charactor", container=self )
		#l1= LabelSprite( self.evManager, "Charactor", container=self )
		#cb= CharactorButtons( self.evManager, container=self )

		#self.widgets = [b1,b2,b3,l1,cb]
		self.widgets = [b1]
		self.renderGroup.add( self.widgets )

		self.ArrangeWidgets()

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self):
		xyOffset = ( self.rect.x, self.rect.y )
		self.widgets[0].rect.topleft = vectorSum( xyOffset, (20, 10) ) 
		#self.widgets[1].rect.topleft = vectorSum( xyOffset, (20, 20) )
		#self.widgets[2].rect.topleft = vectorSum( xyOffset, (20, 40) )
		#self.widgets[3].rect.topleft = vectorSum( xyOffset, (250, 0)) 
		#self.widgets[4].rect.topleft = vectorSum( xyOffset, (250, 20)) 

	#----------------------------------------------------------------------
 	def GetBackgroundBlit(self):
		#bgImg = pygame.Surface( (self.rect.width, self.rect.height) )
		#bgImg.fill( (0,100,0) )
		bgImg = load_png( 'main_panel_bg.png' )
		return [bgImg, self.rect]

	#----------------------------------------------------------------------
 	def ConnectButtonsToPlayer(self, player):
		#charactor, sector = player.GetPlaceData( )
		#placeEvent = CharactorPlaceRequest( player, charactor, sector )
		#self.widgets[2].Connect( {'onClickEvent': placeEvent} )
		pass

	#----------------------------------------------------------------------
 	def Notify(self, event):
		GUIView.Notify(self, event)

		if isinstance( event, PlayerJoinEvent ):
			if event.player.name == preferences.playerData['name']:
				self.ConnectButtonsToPlayer( event.player )

#TODO: this is still the old stuff from the Fool The Bar game
#------------------------------------------------------------------------------
class CharactorButtons(WidgetAndContainer):
	def __init__(self, evManager, container=None):
		WidgetAndContainer.__init__( self, evManager, container )

		self.image = pygame.Surface( (100, 100) )
		self.image.fill( (0,0,0) )
		self.background = self.image.convert()
		self.rect = self.image.get_rect()

		self.spriteGroup = pygame.sprite.RenderClear()

		l1 = LabelSprite( self.evManager, '-', container=self )

		self.widgets = [ l1 ]

		self.charactor = None


	#----------------------------------------------------------------------
	def ArrangeWidgets(self):
		WidgetContainer.ArrangeWidgets( self, yPadding=20, xPadding=2 )

	#----------------------------------------------------------------------
	def update(self):
		if self.dirty:
			self.ArrangeWidgets()
			#self.spriteGroup.clear( self.image, self.background )

			#self.spriteGroup.update()

			#self.spriteGroup.draw( self.image )

			self.image.blit( self.background, [0,0] )
			for wid in self.widgets:
				wid.update()
				destpos = [wid.rect.x - self.rect.x,
				           wid.rect.y - self.rect.y ]
				self.image.blit( wid.image, destpos )

			#self.rect = self.image.get_rect()


		self.dirty = 0

	#----------------------------------------------------------------------
	def RefreshCharactor(self):
		self.SetCharactor( self.charactor )
	#----------------------------------------------------------------------
	def SetCharactor(self, charactor):
		self.dirty = 1
		self.charactor = charactor

		if self.charactor is None:
			self.widgets[0].SetText( '-' )
			if len( self.widgets ) >= 2:
				#self.spriteGroup.empty()
				self.widgets = [self.widgets[0]]
				#self.spriteGroup.add( self.widgets )

			return

		self.widgets[0].SetText( self.charactor.name )

		if hasattr( self.charactor, 'drinksReceived' ):

			drinkText = "Drinks: " \
			            + str(self.charactor.drinksReceived)
			if len( self.widgets ) < 2:
				self.widgets.insert(1, LabelSprite( self.evManager, drinkText ) )
				#self.spriteGroup.add( self.widgets[1] )
			else: 
				self.widgets[1].SetText( drinkText )

			orderEvent = CharactorDrinkOrderEvent( self.charactor )
			if len( self.widgets ) < 3:
				self.widgets.insert(2, OrderButtonSprite( self.evManager, 'Order', onClickEvent=orderEvent) )
				#self.spriteGroup.add( self.widgets[2] )
			else: 
				self.widgets[2].Connect( {'onClickEvent': orderEvent} )
		else:
			self.widgets = [self.widgets[0]]


	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, GUICharactorSelectedEvent ):
			self.SetCharactor( event.charactor )
		elif isinstance( event, GUICharactorUnSelectedEvent ) \
		  and self.charactor == event.charactor:
			self.SetCharactor( None )
		elif isinstance( event, ServeDrinkEvent ) \
		  and self.charactor == event.customer:
			self.RefreshCharactor( )
		elif isinstance( event, DenyDrinkEvent ) \
		  and self.charactor == event.customer:
			msg = "Drink Denied!"
			ev = GUIDialogAddRequest( 'msgDialog', msg )
			self.evManager.Post( ev )

		#See if we're dirty
		for wid in self.widgets:
			if wid.dirty:
				self.dirty = 1
				break
			

#------------------------------------------------------------------------------
class OrderButtonSprite(ButtonSprite):
	pass
		



if __name__ == "__main__":
	print "that was unexpected"

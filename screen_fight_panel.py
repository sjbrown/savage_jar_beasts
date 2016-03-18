import pygame
from pygame.locals import *
import string

from gui import *
from events import *
import preferences
from utils import load_png


SIZE_RECT = (300,40,360,50)

#------------------------------------------------------------------------------
class FightPanelController(GUIController):
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
			import gui
			player = gui.playerRef.player
	
			ev = PlayerRetreatRequest( player )


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
class FightPanelView(GUIView):
	"""..."""
	clipRect = pygame.Rect( SIZE_RECT )

	#----------------------------------------------------------------------
	def Activate( self, renderGroup, rect, evManager=None ):
		GUIView.Activate(self, renderGroup, rect, evManager)


		playerData = preferences.playerData

		import gui
		self.player = gui.playerRef.player
		self.duel = self.player.duel

		runEvent = PlayerRetreatRequest( self.player )
		monster = self.player.monster
		opponent = self.duel.GetMonsterTarget( monster )
		hitEvent = CharactorAttackRequest( monster, opponent )
		endEvent = DuelContinueRequest( self.player )
		setEvent = GUIDialogAddRequest( 'cardSel' )


		self.buttons = {
		                'step': ['step', None],
		                'retreat': ['Retreat', runEvent],
		                'pass': ['Next Step', endEvent],
		                'flip1': ['Flip 1', hitEvent],
		                'counterflip1': ['CounterFlip 1', hitEvent],
		                'attack': ['Attack', hitEvent],
		                'counterattack': ['CounterAttack', hitEvent],
		                'set': ['Set Card', setEvent],
		                'flip2': ['Flip 2', hitEvent],
		                'counterflip2': ['CounterFlip 2', hitEvent],
		               }



		self.StepChange()

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self):
		xyOffset = ( self.rect.x, self.rect.y )
		self.widgets[0].rect.topleft = vectorSum( xyOffset, (20, 10) ) 
		if len(self.widgets) == 1:
			return
		#self.widgets[1].rect.topleft = vectorSum( xyOffset, (20, 10) ) 
		self.widgets[1].rect.topleft = (0,500)

		wid3 = self.widgets[2]
		if hasattr( wid3, 'text' ) \
		  and wid3.text == self.buttons['attack'][0]:
			wid3.rect.topleft = (600,100)
		elif hasattr( wid3, 'text' ):
			wid3.rect.topleft = (100,80)
		else:
			wid3.rect.topleft = (0,-150)

		self.widgets[3].rect.topleft = vectorSum( xyOffset, (100, 20) ) 

	#----------------------------------------------------------------------
 	def GetBackgroundBlit(self):
		bgImg = load_png( 'main_panel_bg.png' )
		return [bgImg, self.rect]

	#----------------------------------------------------------------------
 	def StepChange(self):
		if self.duel.state != self.duel.STATE_ACTIVE:
			return
		#TODO: this is implicitly tightly coupled here with Duel
		#      thus, very bad
		steps = ['flip1', 'counterflip1', 'attack', 'counterattack',
		         'set', 'flip2', 'counterflip2' ]
		text = steps[self.duel.step]
		self.buttons['step'][0] = text

		if self.player is self.duel.GetActivePlayer():
			if text == 'set' \
			  and not self.duel.GetDeckForPlayer( self.player ):
				print self.duel.GetDeckForPlayer(self.player),"IS EMPTY"
				print "PLAYER HAD NO DECK. CONTINUE"
				ev = DuelContinueRequest( self.player )
				self.evManager.Post( ev )
				return
			elif text != 'set' and text != 'attack' \
			  and not self.duel.GetCardFieldForPlayer(self.player):
			  	print "\nPLAYER HAD NO FIELD ON ", text
				ev = DuelContinueRequest( self.player )
				self.evManager.Post( ev )
				return

			if self.duel.InFlippingStep():
				#if there are no flippable cards, skip the step
				field = self.duel.GetCardFieldForPlayer(
						                   self.player)
				if not field:
			  		print "\nHAD NO PLAYABLE CARD", text
					ev = DuelContinueRequest( self.player )
					self.evManager.Post( ev )
					return
				else:
					print field

		for w in self.widgets:
			w.kill()
			#self.renderGroup.remove( w )

		if self.player is self.duel.GetActivePlayer():
			b1 = ButtonSprite( self.evManager,
			                self.buttons['step'][0],
			                container=self,
			                onClickEvent=self.buttons['step'][1]
			                )
			b2 = BalloonButton( self.evManager,
			                self.buttons['retreat'][0],
			                container=self,
			                onClickEvent=self.buttons['retreat'][1]
			                )
			b4 = BalloonButton( self.evManager,
			                self.buttons['pass'][0],
			                container=self,
			                onClickEvent=self.buttons['pass'][1]
			                )
			if text[:4] == 'flip' or text == 'counterattack':
				b3 = CardZoneIndicator( self.evManager,
				                        container=self )
			else:
				b3 = BalloonButton( self.evManager,
			                   self.buttons[text][0],
			                   container=self,
			                   onClickEvent=self.buttons[text][1]
			                )

			self.widgets = [b1, b2, b3, b4]
			self.renderGroup.add( self.widgets )
		else:
			b1 = ButtonSprite( self.evManager,
			                self.buttons['step'][0],
			                container=self,
			                onClickEvent=self.buttons['step'][1]
			                )
			self.widgets = [b1]
			self.renderGroup.add( self.widgets )

		self.ArrangeWidgets()

	#----------------------------------------------------------------------
 	def Notify(self, event):
		GUIView.Notify( self, event )

		if isinstance( event, DuelChangeStepEvent ) \
		  and event.duel is self.duel:
			self.StepChange()
		#elif isinstance( event, DuelChangePlayerEvent ) \
		  #and event.duel is self.duel:
			#self.StepChange()

		
from eventmanager import EventManager
#------------------------------------------------------------------------------
class ScrolledIconWindow( WidgetAndContainer, EventManager ):
	#----------------------------------------------------------------------
	def __init__(self, evManager, objects, container=None):
		WidgetAndContainer.__init__( self, evManager, container )
		EventManager.__init__( self )

		self.image = pygame.Surface( (400,130), SRCALPHA )
		self.image.fill( (90,90,90) )
		self.rect = self.image.get_rect()
		#copy the rect
		self.scrollState = self.rect.move( 0,0 )

		leftEvent = GUIScrollRequest( self, -5 )
		rightEvent = GUIScrollRequest( self, 5 )
		self.leftButton = ScrollButton( self, self, leftEvent )
		self.widgets.append( self.leftButton )
		self.rightButton = ScrollButton( self, self, rightEvent )
		self.widgets.append( self.rightButton )

		self.xPadding = 4
		
		maxWidth = len(objects)*(IconSprite.maxWidth+self.xPadding)
		maxHeight = IconSprite.maxHeight
		self.scrollSurface = pygame.Surface((maxWidth, maxHeight), SRCALPHA)
		for obj in objects:
			newSprite = IconSprite( self, obj, self )
			self.widgets.append( newSprite )

		self.ArrangeWidgets()
		self.update()

	#----------------------------------------------------------------------
	def ArrangeWidgets(self):
		self.dirty = 1
		xOffset = 0
		yOffset = 0
		xMax = self.scrollSurface.get_width()
		yMax = self.scrollSurface.get_height()
		xCounter = xOffset

		self.widgets[0].rect.bottomleft = (0,self.rect.height)
		self.widgets[1].rect.bottomright = (self.rect.width,self.rect.height)

		#the first two widgets are the left and right buttons,
		#so we just need to arrange the remainder
		for wid in self.widgets[2:]:
			wid.rect.x = xCounter + self.xPadding
			wid.rect.y = yOffset 
			xCounter = wid.rect.right
			print "put ", wid, "at ", wid.rect.x

			#Check to see if we didn't screw it up...
			if wid.rect.left > xMax \
			  or wid.rect.top > yMax:
				print wid, self
				raise Exception( "ScrolledWindow Wrong Size")


	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		for sprite in self.widgets[2:]:
			sprite.update()
			self.scrollSurface.blit( sprite.image, sprite.rect )

		self.image.blit( self.scrollSurface, (0,0), self.scrollState )
		self.image.blit( self.leftButton.image, self.leftButton.rect )
		self.image.blit( self.rightButton.image, self.rightButton.rect )

	#----------------------------------------------------------------------
	def Scroll( self, amount ):
		self.dirty = 1

		self.scrollState.x += amount
		boundLeft = 0
		boundRight = self.scrollSurface.get_width()
		if self.scrollState.left < boundLeft:
			self.scrollState.left = boundLeft
		if self.scrollState.right > boundRight:
			self.scrollState.right = boundRight

	#----------------------------------------------------------------------
	def Debug(self, ev):
		return
	#----------------------------------------------------------------------
	def Post( self, event):
		self.evManager.Post( event )

	#----------------------------------------------------------------------
	def Notify( self, event ):
		WidgetAndContainer.Notify( self, event )

		if isinstance( event, GUIScrollRequest ) \
		  and event.target is self:
		  	self.Scroll( event.amount )


		#determine what icons are accessible, and send events through
		#to them.
		if isinstance( event, GUIClickEvent ) \
		  or isinstance( event, GUIMouseMoveEvent ):
			if self.rect.collidepoint( event.pos ):
				from copy import copy
				modifiedEvent = copy( event )
				pos = list(event.pos)
				pos[0] = pos[0] - self.rect.x
				pos[1] = pos[1] - self.rect.y
				if pos[1] < self.leftButton.rect.top:
					pos[0] = pos[0] + self.scrollState.x
					pos[1] = pos[1] + self.scrollState.y
				modifiedEvent.pos = ( pos )
				EventManager.Post( self, modifiedEvent )
		else:
			EventManager.Post( self, event )

		

#------------------------------------------------------------------------------
class CardSelDialogView(GUIView):
	"""..."""
	clipRect = pygame.Rect( (20,200,760,210) )

	#----------------------------------------------------------------------
	def Activate( self, renderGroup, rect, evManager=None ):
		GUIView.Activate(self, renderGroup, rect, evManager)

		self.selectedItem = None

		bgSprite = pygame.sprite.Sprite()
		bgSprite.image = load_png( 'cardsel_background.png' )
		bgSprite.rect = self.rect

		import gui
		self.player = gui.playerRef.player
		self.duel = self.player.duel
		deck = self.duel.GetDeckForPlayer( self.player )
		print "this is the deck ", deck
		self.scrollWindow = ScrolledIconWindow( self.evManager, 
		                                        deck, self )

		closeEvent = GUIDialogRemoveRequest( 'cardSel' )
		closeButton = ButtonSprite( self.evManager, "Close", 
		                            container=self, 
		                            onClickEvent=closeEvent )
		self.background = bgSprite
		self.widgets = [ closeButton,
		            LabelSprite(self.evManager, "foo", container=self ),
			    self.scrollWindow
		          ]


		#because this is a Dialog, it should be shown on the topmost
		#layer of the View.
		#the renderGroup here is expected to be a LayeredSpriteGroup
		self.renderGroup.add_top( self.background )
		for wid in self.widgets:
			self.renderGroup.add_top( wid )

		self.ArrangeWidgets()

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self ):
		xyOffset = ( self.rect.x, self.rect.y )
		self.widgets[0].rect.topleft= vectorSum( xyOffset, (700,150) ) 
		self.widgets[1].rect.topleft= vectorSum( xyOffset, (10,20) ) 
		self.widgets[2].rect.topleft= vectorSum( xyOffset, (30,40) ) 
		if len(self.widgets) < 4:
			return
		self.widgets[3].rect.topleft= vectorSum( xyOffset, (450,-25) )
		self.widgets[4].rect.topleft= vectorSum( xyOffset, (700,130) )

	#----------------------------------------------------------------------
 	def kill(self ):
		GUIView.kill( self )
		self.background.kill()
		del self.background

	#----------------------------------------------------------------------
 	def Select(self, item ):
		self.selectedItem = item

		cardSprite = CardSprite( self.evManager, self.selectedItem,
		                         container=self )

		if len( self.widgets ) < 4:
			self.widgets.append( cardSprite )
			self.renderGroup.add_top( cardSprite )
		else:
			self.widgets[3].kill()
			self.renderGroup.remove( self.widgets[3] )
			self.widgets[3] = cardSprite
			self.renderGroup.add( self.widgets[3] )


		#change the event of the "Play" button to use the selected card
		avatar = self.player.avatar
		selEvent = CharactorPlayCardRequest( avatar, self.selectedItem )

		if len( self.widgets ) > 4:
			self.widgets[4].onClickEvent = selEvent
			return

		#if we haven't added the "Play" button, add it
		selButton = ButtonSprite( self.evManager, "Play",
		                                container=self,
		                                onClickEvent=selEvent )
		self.widgets.append( selButton )
		self.renderGroup.add_top( selButton )
		self.ArrangeWidgets()

		
	#----------------------------------------------------------------------
 	def Notify(self, event):
		GUIView.Notify( self, event )

		if isinstance( event, GUISelectItemEvent ):
			self.Select( event.item )

		if isinstance( event, CharactorPlayCardEvent ):
			closeEvent = GUIDialogRemoveRequest( 'cardSel' )
			self.evManager.Post( closeEvent )

#------------------------------------------------------------------------------
class CardZoneIndicator( Widget ):
	"""..."""
	#----------------------------------------------------------------------
	def __init__(self, evManager, container=None ):
		Widget.__init__( self, evManager, container )
		self.zAxis = 0

		self.image = load_png( 'card_zone.png' )
		self.rect = self.image.get_rect()

#------------------------------------------------------------------------------
class BalloonButton(ButtonSprite):
	"""..."""
	#----------------------------------------------------------------------
	def __init__(self, evManager, text, container=None, onClickEvent=None ):
		ButtonSprite.__init__( self, evManager, text, 
		                       container, onClickEvent )
		self.zAxis = 5
		originalImg = self.image
		originalRect = self.rect

		self.image = load_png( 'balloon_button.png' )
		self.rect = self.image.get_rect()

		originalRect.center = self.rect.center

		self.image.blit( originalImg, originalRect )
	#----------------------------------------------------------------------
	def update(self):
		return

#------------------------------------------------------------------------------
class CardSprite(ButtonSprite):
	"""..."""

	#----------------------------------------------------------------------
	def __init__(self, evManager, item, container=None, onClickEvent=None ):
		Widget.__init__( self, evManager, container )

		self.image = load_png( 'card_unknown.png' )
		self.rect = self.image.get_rect()
		self.originalRect = None

		self.font = pygame.font.Font(None, 20) 
		name = item.name 
		textImg = self.font.render( name, 1, (0,0,255) )
		self.image.blit( textImg, (60,180) )

		self.onClickEvent = onClickEvent

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		if self.focused:
			pass
		else:
			pass

		self.dirty = 0

#------------------------------------------------------------------------------
class IconSprite(ButtonSprite):
	"""..."""
	maxWidth = 90
	maxHeight = 110

	#----------------------------------------------------------------------
	def __init__(self, evManager, item, container=None, onClickEvent=None ):
		Widget.__init__( self, evManager, container )

		self.image = load_png( 'icon_unknown.png' )
		self.rect = self.image.get_rect()
		self.originalRect = None

		self.font = pygame.font.Font(None, 20) 
		name = item.name 
		textImg = self.font.render( name, 1, (0,0,255) )
		self.image.blit( textImg, (6,80) )

		#self.onClickEvent = onClickEvent
		self.onClickEvent = GUISelectItemEvent( item )

		self.SanityCheck()

	#----------------------------------------------------------------------
	def SanityCheck(self):
		if self.rect.width > IconSprite.maxWidth \
		  or self.rect.height > IconSprite.maxHeight:
		  	raise Exception( 'Icon Sprite Too Big' )

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		if self.focused:
			if not self.originalRect:
				self.originalRect = self.rect.move( 0,0 )
			self.rect = self.originalRect.move( 2,2 )	
		else:
			if self.originalRect:
				self.rect.topleft = self.originalRect.topleft
				self.originalRect = None

		self.dirty = 0

	#----------------------------------------------------------------------
	#def Notify(self, event):
		#ButtonSprite.Notify(self,event)

#------------------------------------------------------------------------------
class ScrollButton(ButtonSprite):
	"""..."""

	#----------------------------------------------------------------------
	def __init__(self, evManager, container=None, onClickEvent=None ):
		Widget.__init__( self, evManager, container )

		if not isinstance( onClickEvent, GUIScrollRequest ):
			raise Exception("Scroll Button Must have Scroll Event")

		self.onClickEvent = onClickEvent
		self.amount = self.onClickEvent.amount

		if self.amount < 0:
			self.image = load_png( 'scroll_left.png' )
		else:	
			self.image = load_png( 'scroll_right.png' )
		self.rect = self.image.get_rect()

		self.originalRect = None

	#----------------------------------------------------------------------
	def update(self):
		#TODO: update() never gets called.  need to add an update call
		# to the parent
		if not self.dirty:
			return

		if self.focused:
			if not self.originalRect:
				self.originalRect = self.rect.move( 0,0 )
			self.rect = self.originalRect.move( 2,2 )	
		else:
			if self.originalRect:
				self.rect.topleft = self.originalRect.topleft
				self.originalRect = None

		self.dirty = 0



if __name__ == "__main__":
	print "that was unexpected"

from events import *
import pygame
from pygame.locals import *

vectorSum = lambda a,b: (a[0]+b[0], a[1]+b[1])

fontFace = '/a/.fonts/animeace_b.ttf'
fontFace = None
fontSize = 18


#------------------------------------------------------------------------------
class Widget(pygame.sprite.Sprite):
	def __init__(self, evManager, container=None):
		pygame.sprite.Sprite.__init__(self)

		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.container = container
		self.focused = 0
		self.dirty = 1

	#----------------------------------------------------------------------
	def SetFocus(self, val):
		self.focused = val
		self.dirty = 1

	#----------------------------------------------------------------------
 	def kill(self):
		self.container = None
		del self.container
		pygame.sprite.Sprite.kill(self)

	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, GUIFocusThisWidgetEvent ) \
		  and event.widget is self:
			self.SetFocus(1)

		elif isinstance( event, GUIFocusThisWidgetEvent ) \
		  and self.focused:
			self.SetFocus(0)



#------------------------------------------------------------------------------
class LabelSprite(Widget):
	def __init__(self, evManager, text, container=None):
		Widget.__init__( self, evManager, container)

		self.color = (200,200,200)
		self.font = pygame.font.Font(fontFace, fontSize)
		self.__text = text
		self.image = self.font.render( self.__text, 1, self.color)
		self.rect  = self.image.get_rect()

	#----------------------------------------------------------------------
	def SetText(self, text):
		self.__text = text
		self.dirty = 1

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		self.image = self.font.render( self.__text, 1, self.color )
		self.dirty = 0


#------------------------------------------------------------------------------
class ButtonSprite(Widget):
	def __init__(self, evManager, text, container=None, onClickEvent=None ):
		Widget.__init__( self, evManager, container)

		self.font = pygame.font.Font(fontFace, fontSize)
		self.text = text
		self.image = self.font.render( self.text, 1, (255,0,0))
		self.rect  = self.image.get_rect()

		self.onClickEvent = onClickEvent

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		if self.focused:
			color = (255,255,0)
		else:
			color = (255,0,0)
		self.image = self.font.render( self.text, 1, color)
		#self.rect  = self.image.get_rect()

		self.dirty = 0

	#----------------------------------------------------------------------
	def Connect(self, eventDict):
		for key,event in eventDict.iteritems():
			try:
				self.__setattr__( key, event )
			except AttributeError:
				print "Couldn't connect the ", key
				pass


	#----------------------------------------------------------------------
	def Click(self):
		self.dirty = 1
		if self.onClickEvent:
			self.evManager.Post( self.onClickEvent )

	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, GUIPressEvent ) and self.focused:
			self.Click()

		elif isinstance( event, GUIClickEvent ) \
		  and self.rect.collidepoint( event.pos ):
			self.Click()

		elif isinstance( event, GUIMouseMoveEvent ) \
		  and self.rect.collidepoint( event.pos ):
		  	ev = GUIFocusThisWidgetEvent(self)
			self.evManager.Post( ev )

		Widget.Notify(self,event)

			
#------------------------------------------------------------------------------
class TextBoxSprite(Widget):
	def __init__(self, evManager, width, container=None ):
		Widget.__init__( self, evManager, container)

		self.font = pygame.font.Font(fontFace, fontSize)
		linesize = self.font.get_linesize()

		self.rect = pygame.Rect( (0,0,width, linesize +4) )
		boxImg = pygame.Surface( self.rect.size ).convert_alpha()
		color = (0,0,100)
		pygame.draw.rect( boxImg, color, self.rect, 4 )

		self.emptyImg = boxImg.convert_alpha()
		self.image = boxImg

		self.text = ''
		self.textPos = (22, 2)

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		text = self.text
		if self.focused:
			text += '|'

		textColor = (255,0,0)
		textImg = self.font.render( text, 1, textColor )
		self.image.blit( self.emptyImg, (0,0) )
		self.image.blit( textImg, self.textPos )

		self.dirty = 0

	#----------------------------------------------------------------------
	def Click(self):
		self.focused = 1
		self.dirty = 1

	#----------------------------------------------------------------------
	def SetText(self, newText):
		self.text = newText
		self.dirty = 1

	#----------------------------------------------------------------------
 	def Notify(self, event):

		if isinstance( event, GUIPressEvent ) and self.focused:
			self.Click()

		elif isinstance( event, GUIClickEvent ) \
		  and self.rect.collidepoint( event.pos ):
			self.Click()

		elif isinstance( event, GUIClickEvent ) \
		  and self.focused:
			self.SetFocus(0)

		elif isinstance( event, GUIMouseMoveEvent ) \
		  and self.rect.collidepoint( event.pos ):
		  	ev = GUIFocusThisWidgetEvent(self)
			self.evManager.Post( ev )

		elif isinstance( event, GUIKeyEvent ) \
		  and self.focused:
		  	newText = self.text + event.key
			self.SetText( newText )

		elif isinstance( event, GUIControlKeyEvent ) \
		  and self.focused and event.key == K_BACKSPACE:
		  	#strip of last character
		  	newText = self.text[:( len(self.text) - 1 )]
			self.SetText( newText )

		Widget.Notify(self,event)


#------------------------------------------------------------------------------
class WidgetContainer:
	def __init__(self, evManager, rect):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.rect = rect

		self.widgets = [ ]

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self, xPadding=20, yPadding=100):
		xOffset = self.rect.x
		yOffset = self.rect.y

		xStep = 1
		yStep = 1
		for wid in self.widgets:
			wid.rect.x = xOffset + (xPadding*xStep)
			wid.rect.y = yOffset + (yPadding*yStep)

			#Check to see if we didn't screw it up...
			if wid.rect.left > self.rect.right \
			  or wid.rect.top > self.rect.bottom:
				print wid, self
				print wid.rect, self.rect
				raise Exception( "Widget Outside Container")

			yStep += 1
			if yStep*yPadding > self.rect.height:
				yStep = 1
				xStep += 1

	#----------------------------------------------------------------------
 	def ChangeFocusedWidget(self, change):
		i = 0
		for wid in self.widgets:
			if wid.focused:
				break
			i += 1

		currentlyFocused = i
		changeToWidget = i + change

		#no widget was focused
		if currentlyFocused == len( self.widgets ):
			self.widgets[0].SetFocus(1)
			return

		#the desired index is out of range
		elif changeToWidget <= -1  \
		  or changeToWidget >= len( self.widgets ):
			changeToWidget = changeToWidget%len(self.widgets)

		self.widgets[currentlyFocused].SetFocus(0)
		self.widgets[changeToWidget].SetFocus(1)


	#----------------------------------------------------------------------
 	def Notify(self, event):

		if isinstance( event, GUIFocusNextWidgetEvent):
			self.ChangeFocusedWidget(1)

		elif isinstance( event, GUIFocusPrevWidgetEvent):
			self.ChangeFocusedWidget(-1)


	#----------------------------------------------------------------------
 	def kill(self):
		for sprite in self.widgets:
			sprite.kill()
		while len( self.widgets ) > 0:
			wid = self.widgets.pop()
			del wid
		del self.widgets

#------------------------------------------------------------------------------
class WidgetAndContainer( Widget, WidgetContainer ):
	#----------------------------------------------------------------------
	def __init__(self, evManager, container):
		Widget.__init__( self, evManager, container)

		self.widgets = [ ]

	#----------------------------------------------------------------------
 	def kill(self):
		WidgetContainer.kill(self)
		Widget.kill(self)


#------------------------------------------------------------------------------
class TextEntrySprite(WidgetAndContainer):
	def __init__(self, evManager, labelText, container=None ):
		WidgetAndContainer.__init__( self, evManager, container)


		self.widgets = [ LabelSprite( self.evManager, labelText, container=self ),
		                 TextBoxSprite( self.evManager, 200, container=self ),
		               ]
		width = self.widgets[0].rect.width \
		        + self.widgets[1].rect.width + 10
		height = self.widgets[1].rect.height

		self.image = pygame.Surface( (width, height) )
		self.image.fill( (0,0,0) )

		self.background = self.image.convert_alpha()
		self.rect = self.image.get_rect()

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self):
		xyOffset = ( self.rect.x, self.rect.y )
		self.widgets[0].rect.topleft = vectorSum( xyOffset, (0,0) ) 
		x = self.widgets[0].rect.width + 10
		self.widgets[1].rect.topleft = vectorSum( xyOffset, (x,0) ) 

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		self.ArrangeWidgets()

		self.image.blit( self.background, [0,0] )
		for wid in self.widgets:
			wid.update()
			destpos = [wid.rect.x - self.rect.x,
				   wid.rect.y - self.rect.y ]
			self.image.blit( wid.image, destpos )

		self.dirty = 0

	#----------------------------------------------------------------------
 	def Notify(self, event):

		#See if we're dirty
		for wid in self.widgets:
			if wid.dirty:
				self.dirty = 1
				break

#------------------------------------------------------------------------------
class AnimatedWidget(Widget):
	def __init__(self, evManager, animation, container=None):
		Widget.__init__(self, evManager, container)
		self.animation = None

		self.offset = [0,0]

		self.SetAnimation( animation )

		#print self.animation
		frame = self.animation.GetCurrent()
		self.image = frame.image
		self.rect = self.image.get_rect()

	#----------------------------------------------------------------------
 	def kill(self):
		Widget.kill(self)
		self.animation.SetFinishCallback( None )
		del self.animation

	#----------------------------------------------------------------------
 	def SetAnimation(self, newAnim):
		if self.animation: 
			self.animation.SetFinishCallback( None )
		self.animation = newAnim
		self.animation.SetFinishCallback( self.AnimationFinished )

	#----------------------------------------------------------------------
 	def NextFrame(self):
		self.dirty = 1
		self.animation.next()

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		import operator
		frame = self.animation.GetCurrent()
		change = frame.GetOffset( self.offset )
		if change != [0.0]:
			self.rect.move_ip( change )
			self.offset = map( operator.add, self.offset, change )
		self.image = frame.image
		
	#----------------------------------------------------------------------
 	def AnimationFinished(self):
		pass
	#----------------------------------------------------------------------
 	def Notify(self, event):
		Widget.Notify( self, event )

		if isinstance( event, AnimationTickEvent ):
			#print "Animation: tick"
			self.NextFrame()

			

if __name__ == "__main__":
	print "that was unexpected"

import pygame
from pygame.locals import *
import string

from gui import *
from events import *
from utils import load_png
import preferences


#------------------------------------------------------------------------------
class MenuGUIView(GUIView):
	"""..."""
	#----------------------------------------------------------------------
	def Activate( self, renderGroup, rect, evManager=None ):
		GUIView.Activate(self, renderGroup, rect, evManager)
		
		quitEvent = QuitEvent()
		optEvent = GUIChangeScreenRequest( 'options' )
		playEvent = GameStartRequest()

		b1= ButtonSprite( self.evManager, "Quit", container=self, 
		                  onClickEvent=quitEvent )
		b2= ButtonSprite( self.evManager, "Options", container=self,
		                  onClickEvent=optEvent )
		b3= LocalGameButton( self.evManager, container=self )

		self.widgets = [ b1,b2,b3 ]

		self.renderGroup.add( self.widgets )

		self.ArrangeWidgets()

	#----------------------------------------------------------------------
 	def GetBackgroundBlit(self):
		bgImg = pygame.Surface( (self.rect.width, self.rect.height) )
		splashBG = load_png( 'splash_back.png' )
		splashRect = splashBG.get_rect()
		bgRect = bgImg.get_rect()
		splashRect.x = bgRect.width - splashRect.width

		bgImg.fill( (0,0,5) )
		bgImg.blit( splashBG, splashRect )
		return [bgImg, self.rect]

	#----------------------------------------------------------------------
 	def Notify(self, event):
		GUIView.Notify( self, event )


#------------------------------------------------------------------------------
class OptionsGUIView(GUIView):
	"""..."""
	#----------------------------------------------------------------------
	def Activate( self, renderGroup, rect, evManager=None ):
		GUIView.Activate(self, renderGroup, rect, evManager)

		self.xyOffset = ( self.rect.x, self.rect.y )

		menuEvent = GUIChangeScreenRequest( 'menu' )
		b1= ButtonSprite( self.evManager, "Menu", container=self,
		                  onClickEvent=menuEvent)
		pn= PlayerNameSprite( self.evManager, container=self)
		cn= CharactorNameSprite(evManager, container=self )

		self.widgets = [ b1, pn, cn ]
		self.renderGroup.add( self.widgets )

		self.ArrangeWidgets()

	#----------------------------------------------------------------------
 	def GetBackgroundBlit(self):
		bgImg = pygame.Surface( (self.rect.width, self.rect.height) )
		bgImg.fill( (50,0,0) )
		return [bgImg, self.rect]


			
#------------------------------------------------------------------------------
class LocalGameButton(ButtonSprite):
	def __init__(self, evManager, container=None):
		ButtonSprite.__init__( self, evManager, "Start Local Game",
		                       container=container )
	#----------------------------------------------------------------------
	def Click(self):
		self.dirty = 1
		ev = GameStartRequest()
		self.evManager.Post( ev )
		playerData = preferences.playerData
		ev = PlayerJoinRequest( playerData )
		self.evManager.Post( ev )
		ev = GUIChangeScreenRequest( 'town' )
		self.evManager.Post( ev )

#------------------------------------------------------------------------------
class PlayerNameSprite(TextEntrySprite):
	def __init__(self, evManager, container=None):
		TextEntrySprite.__init__( self, evManager, 
		                          "Player Name", container=container )
		self.widgets[1] = PlayerNameTextBoxSprite( self.evManager, 
		                                           200, 
		                                           container=container )

#------------------------------------------------------------------------------
class PlayerNameTextBoxSprite(TextBoxSprite):
	def __init__(self,evManager,width,container=None):
		TextBoxSprite.__init__(self,evManager,width,container=container)
		TextBoxSprite.SetText(self,preferences.playerData['name'])
	#----------------------------------------------------------------------
	def SetText(self, newText):
		self.text = newText
		preferences.playerData['name'] = self.text
		self.dirty = 1

#------------------------------------------------------------------------------
class CharactorNameSprite(TextEntrySprite):
	def __init__(self, evManager, container=None ):
		TextEntrySprite.__init__( self, evManager, 
		                          "Charactor Name", container=container)
		self.widgets[1] = CharactorNameTextBoxSprite( self.evManager, 
		                                           200, 
		                                           container=container )

#------------------------------------------------------------------------------
class CharactorNameTextBoxSprite(TextBoxSprite):
	def __init__(self,evManager,width, container=None):
		TextBoxSprite.__init__(self,evManager,width,container=container)
		TextBoxSprite.SetText(self,preferences.playerData['charactorName'])

	#----------------------------------------------------------------------
	def SetText(self, newText):
		self.text = newText
		preferences.playerData['charactorName'] = self.text
		self.dirty = 1



if __name__ == "__main__":
	print "that was unexpected"

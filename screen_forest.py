from events import *
from utils import *
from model import *

import pygame
from pygame.locals import *
from gui import GUIView, SimpleGUIController
from gui_widgets import *

SIZE_RECT = (0,0,800,600)

#------------------------------------------------------------------------------
class ForestScreenController(SimpleGUIController):
	"""..."""

	MODE_SELECT = 0
	MODE_ACTION = 1

	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.rectOfInterest = pygame.Rect( SIZE_RECT )

		self.mode = ForestScreenController.MODE_SELECT

	#----------------------------------------------------------------------
	def WantsEvent( self, event ):
		if event.type == MOUSEBUTTONUP \
		  or event.type == MOUSEMOTION \
		  and self.rectOfInterest.collidepoint( event.pos ):
			return 1

		return 0


#------------------------------------------------------------------------------
class ForestScreen(GUIView):
	"""..."""
	#----------------------------------------------------------------------
	def Activate( self, renderGroup, rect, evManager=None ):
		GUIView.Activate(self, renderGroup, rect, evManager)

		import gui
		duel = gui.playerRef.player.duel
		self.duel= duel
		
		m1Name = duel.players[0].monster.name
		m2Name = duel.players[1].monster.name
		p1N = LabelSprite( self.evManager, m1Name, self )
		p2N = LabelSprite( self.evManager, m2Name, self )
		h1 = HealthSprite( self.evManager, duel.players[0].monster, self )
		h2 = HealthSprite( self.evManager, duel.players[1].monster, self )

		m1 = MonsterSprite(evManager, duel.players[0].monster, self)
		m2 = MonsterSprite(evManager, duel.players[1].monster, self)

		self.widgets = [ p1N, p2N, h1, h2, m1, m2 ]
		self.cardWidgets = [ [], [] ]

		self.renderGroup.add( self.widgets )

		self.ArrangeWidgets()

	#----------------------------------------------------------------------
 	def kill(self):
		GUIView.kill(self)
		for i in range(2):
			for sprite in self.cardWidgets[i]:
				sprite.kill()
			while len( self.cardWidgets[i] ) > 0:
				wid = self.cardWidgets[i].pop()
				del wid
		del self.cardWidgets

	#----------------------------------------------------------------------
 	def GetBackgroundBlit(self):
		bgImg = load_png( 'main_forest_background.png')
		return [ bgImg, self.rect ]

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self):
		xyOffset = ( self.rect.x, self.rect.y )
		self.widgets[0].rect.topleft = vectorSum( xyOffset, (50, 560) ) 
		self.widgets[1].rect.topleft = vectorSum( xyOffset, (550, 560) )
		self.widgets[2].rect.topleft = vectorSum( xyOffset, (180, 560) )
		self.widgets[3].rect.topleft = vectorSum( xyOffset, (680, 560) )
		self.widgets[4].rect.topleft = vectorSum( xyOffset, (10, 100) )
		self.widgets[5].rect.topleft = vectorSum( xyOffset, (400, 100) )

		for i in range(2):
			x = self.rect.x + (10 + i*390)
			y = self.rect.y + 35
			for wid in self.cardWidgets[i]:
				wid.rect.topleft = (x,y)
				y += 20

	#----------------------------------------------------------------------
 	def CardPlayed(self, charactor, card):
		print "ADDING A CARD"
		cardSprite = CardSprite( self.evManager, card, self )
		if charactor.player is self.duel.players[0]:
			position = 0
		else:
			position = 1
		self.cardWidgets[position].append( cardSprite )
		self.ArrangeWidgets()
		self.renderGroup.add( cardSprite )

	#----------------------------------------------------------------------
 	def Notify(self, event):
		GUIView.Notify( self, event )

		if isinstance( event, DuelFinishEvent ) \
		  and event.duel is self.duel:
			ev = GUIChangeScreenRequest( 'town' )
			self.evManager.Post( ev )

		elif isinstance( event, CharactorPlayCardEvent ) \
		  and event.charactor.player.duel is self.duel:
		  	self.CardPlayed( event.charactor, event.card )
		elif isinstance( event, CharactorPlayCardEvent ):
			print "DUMB STUFF HAPPENS"

#------------------------------------------------------------------------------
class MonsterSprite(AnimatedWidget):
	def __init__(self, evManager, charactor, container=None):
		self.charactor = charactor
		print 'loading anim', self.charactor.name
		self.defAnim = load_animation( self.charactor.name )
		self.attAnim = load_animation( self.charactor.name, 'attack' )
		AnimatedWidget.__init__(self, evManager,self.defAnim, container)

	#----------------------------------------------------------------------
 	def kill(self):
		AnimatedWidget.kill(self)
		del self.charactor

	#----------------------------------------------------------------------
	def AnimationFinished(self):
		pass
		#print "ANI FINISHED DONT KNOW WHAT TO DO"

	#----------------------------------------------------------------------
	def Attack(self):
		self.SetAnimation( self.attAnim )
		self.animation.SetFinishCallback( self.AttackFinished )

	#----------------------------------------------------------------------
	def AttackFinished(self):
		self.attAnim.Reset()
		self.SetAnimation( self.defAnim )

	#----------------------------------------------------------------------
	def Death(self):
		ev = GUIBlockEvent()
		self.evManager.Post( ev )

		newAnim= load_animation( self.charactor.name, 'death' )
		self.SetAnimation( newAnim )
		self.animation.SetFinishCallback( self.DeathFinished )

	#----------------------------------------------------------------------
	def DeathFinished(self):
		ev = GUIUnBlockEvent()
		self.evManager.Post( ev )

	#----------------------------------------------------------------------
	def Notify(self, event):
		if not hasattr( self, "animation"):
			import gc
			print gc.get_referrers(self)
		AnimatedWidget.Notify( self, event )

		if isinstance( event, CharactorDeathEvent ) \
		  and event.charactor is self.charactor:
			self.Death()
		if isinstance( event, CharactorAttackFinished ) \
		  and event.attacker is self.charactor:
			self.Attack()

#------------------------------------------------------------------------------
class CardSprite(ButtonSprite):
	"""..."""

	#----------------------------------------------------------------------
	def __init__(self, evManager, item, container=None, onClickEvent=None ):
		Widget.__init__( self, evManager, container )

		self.image = load_png( 'field_card_unknown.png' )
		self.rect = self.image.get_rect()
		self.originalRect = None
		self.item = item
		#TODO: Delete item on delete

		import gui
		duel = gui.playerRef.player.duel
		self.onClickEvent = DuelFlipCardRequest( item, duel )

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		if self.focused:
			pass
		else:
			pass

		self.dirty = 0
	#----------------------------------------------------------------------
	def Notify(self, event):
		ButtonSprite.Notify( self, event )

		if isinstance( event, DuelFlipCardEvent ) \
		  and self.item is event.card:
			self.image = load_png( 'field_card_flipped.png' )

#------------------------------------------------------------------------------
class HealthSprite(LabelSprite):
	def __init__(self, evManager, charactor, container=None):
		self.charactor = charactor
		text = str(self.charactor.health)
		LabelSprite.__init__(self, evManager, text, container)

	#----------------------------------------------------------------------
	def Notify(self, event):
		LabelSprite.Notify( self, event )

		if isinstance( event, CharactorAttackFinished ) \
		  and self.charactor is event.defender:
			text = str(self.charactor.health)
			self.SetText( text )

		if isinstance( event, DuelFlipCardEvent ):
			print "      000000000000000000000   "
			print "GOT HERE. setting health", self.charactor.health
			text = str(self.charactor.health)
			self.SetText( text )




if __name__ == "__main__":
	print "that was unexpected"

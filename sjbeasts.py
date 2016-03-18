#! /usr/bin/python

from events import *
from utils import *
from gui import *
from model import *
from layeredgroup import LayeredSpriteGroup

from screen_town import MainTownScreenController, MainTownScreen
from screen_main_panel import MainGUIController, MainGUIView
from screen_menus import MenuGUIView, OptionsGUIView
from screen_explore import ExploreScreenController, ExploreScreen
from screen_forest import ForestScreenController, ForestScreen
from screen_fight_panel import FightPanelController, FightPanelView, CardSelDialogView

import pygame
from pygame.locals import *
from weakref import WeakKeyDictionary

from eventmanager import EventManager

#------------------------------------------------------------------------------
class CPUSpinnerController:
	"""..."""
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.clock = pygame.time.Clock()

		self.keepGoing = 1

	#----------------------------------------------------------------------
	def Run(self):
		if not self.keepGoing:
			raise Exception('dead spinner')
		while self.keepGoing:
			self.clock.tick( 48 )
			event = TickEvent()
			self.evManager.Post( event )

	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, QuitEvent ):
			#this will stop the while loop from running
			self.keepGoing = 0

#------------------------------------------------------------------------------
class AnimationTimerController:
	"""..."""
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.count = 0


	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, TickEvent ):
			self.count += 1
			if self.count > 10:
				self.count = 0
				ev = AnimationTickEvent()
				self.evManager.Post( ev )



#------------------------------------------------------------------------------
class PygameMasterController:
	"""..."""
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		#subcontrollers is an ordered list, the first controller in the
		# list is the first to be offered an event
		self.subcontrollers = []

		self.guiClasses = { 'menu': [SimpleGUIController],
		                    'options': [SimpleGUIController],
		                    'town': [MainGUIController, MainTownScreenController],
		                    'explore': [ExploreScreenController],
		                    'forest': [FightPanelController, ForestScreenController],
		                  }
		self.dialogClasses = { 'msgDialog': BlockingDialogController,
		                       'cardSel': FightPanelController,
		                     }
		self.SwitchController( 'menu' )

	#----------------------------------------------------------------------
	def SwitchController(self, newScreen):

		#if it's a tuple
		if isinstance( newScreen, tuple ):
			newConts = newScreen[1]
		#if it's a key
		elif self.guiClasses.has_key( newScreen ):
			newConts = []
			for cClass in self.guiClasses[newScreen]:
				newConts.append( cClass(self.evManager) )
		else:
			raise NotImplementedError

		self.subcontrollers = []

		self.subcontrollers = newConts

	#----------------------------------------------------------------------
	def DialogAdd(self, key):
		#print "Adding Dialog Controllers", key

		if not self.dialogClasses.has_key( key ):
			raise NotImplementedError

		contClass = self.dialogClasses[key]
		newController = contClass(self.evManager)

		self.subcontrollers.insert(0, newController)

	#----------------------------------------------------------------------
	def DialogRemove(self, key):

		if not self.dialogClasses.has_key( key ):
			raise NotImplementedError

		contClass = self.dialogClasses[key]

		if self.subcontrollers[0].__class__ is not contClass:
			print self.subcontrollers
			raise Exception('removing dialog controller not there')

		self.subcontrollers.pop(0)



	#----------------------------------------------------------------------
	def Notify(self, incomingEvent):

		if isinstance( incomingEvent, TickEvent ):
			#Handle Input Events
			for event in pygame.event.get():
				ev = None
				if event.type == QUIT:
					ev = QuitEvent()
					self.evManager.Post( ev )

				elif event.type == KEYDOWN \
				  or event.type == MOUSEBUTTONUP \
				  or event.type == MOUSEMOTION:
					for cont in self.subcontrollers:
						if cont.WantsEvent( event ):
							cont.HandlePyGameEvent(event)
							break

		elif isinstance( incomingEvent, GUIChangeScreenRequest ):
			self.SwitchController( incomingEvent.key )

		elif isinstance( incomingEvent, GUIDialogAddRequest ):
			self.DialogAdd( incomingEvent.key )

		elif isinstance( incomingEvent, GUIDialogRemoveRequest ):
			self.DialogRemove( incomingEvent.key )

#------------------------------------------------------------------------------
class SubEventManager(EventManager):
	#----------------------------------------------------------------------
 	def __init__(self, master):
		EventManager.__init__(self)
		self.masterEvManager = master

	#----------------------------------------------------------------------
 	def Debug(self, ev):
		return
		#if not isinstance( ev, GUIMouseMoveEvent ):
			#print '   Sub  Message: ', ev.name

	#----------------------------------------------------------------------
 	def Post(self, event):
		self.masterEvManager.Post( event )

	#----------------------------------------------------------------------
 	def Notify(self, event):
		EventManager.Post( self, event )

#------------------------------------------------------------------------------
class PygameMasterView:
	"""..."""
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.RegisterListener( self )

		self.subEvManager1 = SubEventManager(self.evManager)
		self.subEvManager2 = SubEventManager(self.evManager)
		self.activeEvManager = self.subEvManager1

		pygame.init()
		self.window = pygame.display.set_mode( (800,600) )
		pygame.display.set_caption( 'Savage Jar Beasts' )
		self.background = pygame.Surface( self.window.get_size() )
		self.background.fill( (0,0,0) )

		self.window.blit( self.background, (0,0) )
		pygame.display.flip()

		self.dialog = None

		self.subviews = []
		self.spriteGroup = LayeredSpriteGroup()

		self.guiClasses = { 'menu': [MenuGUIView],
		                    'options': [OptionsGUIView],
		                    'town': [MainTownScreen, MainGUIView],
		                    'explore': [ExploreScreen],
		                    'forest': [ForestScreen, FightPanelView],
		                  }
		self.dialogClasses = { 'msgDialog': BlockingDialogView,
		                       'cardSel': CardSelDialogView,
		                     }

		#the subviews that make up the current screen.  In order from
		# bottom to top
		#self.subviews = []
		self.SwitchView( 'menu' )


	#----------------------------------------------------------------------
 	def SwitchView(self, newScreen):
		"""newScreen can either be a key to self.guiClasses or it can
		be a tuple containing a list of Views and a 
		list of Controllers"""
		print "Start SwitchView"

		if self.dialog:
			raise Exception('cannot switch view while dialog up')

		#if it's a tuple
		if isinstance( newScreen, tuple ):
			newViews = newScreen[0]
		#if it's a key
		elif self.guiClasses.has_key( newScreen ):
			newViews = []
			for vClass in self.guiClasses[newScreen]:
				newViews.append( vClass(self.activeEvManager) )
		else:
			raise NotImplementedError('master view doesnt have key')

		for view in self.subviews:
			view.kill()
		self.subviews = []

		self.spriteGroup.empty()


		#construct the new master View
		for viewObj in newViews:
			if hasattr( viewObj, 'clipRect' ):
				rect = viewObj.clipRect
			else:
				widthHeight = self.window.get_size() 
				rect = pygame.Rect((0,0), widthHeight )

			viewObj.Activate( self.spriteGroup, rect, 
			                  self.activeEvManager )

			bgBlit = viewObj.GetBackgroundBlit()
			self.background.blit( bgBlit[0], bgBlit[1] )
			self.subviews.append( viewObj )

		#initial blit & flip of the newly constructed background
		self.window.blit( self.background, (0,0) )
		pygame.display.flip()

		print "End SwitchView"

	#----------------------------------------------------------------------
	def DialogAdd(self, key, msg="Error"):

		if self.dialog:
			self.dialog.AddDialogMsg( msg )

		if not self.dialogClasses.has_key( key ):
			raise NotImplementedError('master view doesnt have key')

		rect = pygame.Rect( (0,0), self.window.get_size() )
		dialogClass = self.dialogClasses[key]
		if hasattr( dialogClass, 'clipRect' ):
			rect = dialogClass.clipRect

		self.activeEvManager = self.subEvManager2

		self.dialog = dialogClass( self.activeEvManager )
		self.dialog.Activate( self.spriteGroup, rect )
		if hasattr( self.dialog, 'SetMsg' ):
			self.dialog.SetMsg( msg )

		self.subviews.append( self.dialog )

	#----------------------------------------------------------------------
	def DialogRemove(self, key):

		if not self.dialogClasses.has_key( key ):
			raise NotImplementedError

		if self.dialog.__class__ is not self.dialogClasses[key]:
			raise Exception( 'that dialog is not open' )

		self.activeEvManager = self.subEvManager1

		self.dialog.kill()
		self.subviews.remove( self.dialog )
		self.dialog = None


	#----------------------------------------------------------------------
	def HandleTick(self):
		#Clear, Update, and Draw Everything
		self.spriteGroup.clear( self.window, self.background )

		self.spriteGroup.update()

		dirtyRects = self.spriteGroup.draw( self.window )
		
		pygame.display.update( dirtyRects )


	#----------------------------------------------------------------------
 	def Notify(self, event):
		if isinstance( event, GUIChangeScreenRequest ):
			self.SwitchView( event.key )

		elif isinstance( event, TickEvent ):
			self.HandleTick()

		elif isinstance( event, GUIDialogAddRequest ):
			self.DialogAdd( event.key, event.msg )

		elif isinstance( event, ExceptionEvent):
			ev = GUIDialogAddRequest( 'msgDialog', event.msg )
			self.evManager.Post( ev )

		elif isinstance( event, GUIDialogRemoveRequest ):
			self.DialogRemove( event.key )

		#at the end, handle the event like an EventManager should
		if self.dialog and not isinstance(event, GUIEvent):
			#if not isinstance( event, TickEvent ) and not isinstance(event, GUIMouseMoveEvent):
				#print "case 1"
			self.subEvManager1.Notify( event )
			self.subEvManager2.Notify( event )
		else:
			#if not isinstance( event, TickEvent ) and not isinstance(event, GUIMouseMoveEvent):
				#print "case 2"
			self.activeEvManager.Notify( event )


#------------------------------------------------------------------------------
def main():
	"""..."""
	evManager = EventManager()

	spinner = CPUSpinnerController( evManager )
	animationSpinner = AnimationTimerController( evManager )
	pygameView = PygameMasterView( evManager )
	pygameCont = PygameMasterController( evManager )
	game = Game( evManager )

	import gui
	gui.playerRef = gui.GlobalPlayer( evManager )
	print gui.playerRef
	
	while 1:
		try:
			spinner.Run()
		except NotImplementedError, msg:
			text = "Not Implemented: "+ str(msg)
			ev = ExceptionEvent( text )
			evManager.Post( ev )
		else:
			break;

if __name__ == "__main__":
	main()

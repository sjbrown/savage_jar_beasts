#!/usr/bin/env python
"""
Here's some text to describe the utils module
"""


#Import Modules
import os, pygame
from pygame.locals import *

	

#-----------------------------------------------------------------------------
def DoNothing():
	return

#-----------------------------------------------------------------------------
def load_png(name, extradir=''):
    if isinstance(name, list):
	    fullname = 'data'
	    for component in name:
	    	fullname = os.path.join(fullname, component)
    else:
    	fullname = os.path.join('data', extradir, name)
    try:
        image = pygame.image.load(fullname)
	if image.get_alpha is None:
		image = image.convert()
	else:
		image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    return image

#-----------------------------------------------------------------------------
def load_animation(moduleName, animName='default'):
	anim = None
	moduleName = moduleName.lower()
	exec( 'from data.'+moduleName+'.chardef import '+animName )
	exec( 'anim = '+animName )
	anim.Reset()
	return anim

#this calls the 'main' function when this script is executed
if __name__ == '__main__': print "didn't expect that!"

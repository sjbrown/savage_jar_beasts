from utils import *

right = 0
left = 1

class Frame:
	def __init__(self, dirname, name, 
	             attRect, vulnRect, duration, offset=[0,0]):
		#start out RIGHT-facing
		self.facing = left

		self.leftFacingImg = load_png(name+'.png', dirname)
		self.rect = self.leftFacingImg.get_rect()
		flip = pygame.transform.flip
		self.rightFacingImg = flip(self.leftFacingImg,1,0)
		self.image = self.leftFacingImg


		self.leftFacingOffset = [0,0]
		self.rightFacingOffset = offset
		self.offset = self.leftFacingOffset

		self.duration = duration
		self.counter = 0

		if attRect is None:
			self.attRect = None
		else:
			#print "   --  "
			self.leftAttRect = pygame.Rect( attRect )
			midx = self.rect.midtop[0]
			change = midx - \
			          (self.leftAttRect.right - midx)
			self.rightAttRect = self.leftAttRect.move(0,0)
			self.rightAttRect.left = change

			self.attRect = self.rightAttRect

		if vulnRect is None:
			self.vulnRect = None
		else:
			#print 'rect', self.rect
			self.leftVulnRect = pygame.Rect( vulnRect )
			midx = self.rect.midtop[0]
			change = midx - \
			          (self.leftVulnRect.right - midx)
			self.rightVulnRect = self.leftVulnRect.move(0,0)
			self.rightVulnRect.left = change

			self.vulnRect = self.rightVulnRect
			#print 'L vuln', self.leftVulnRect
			#print 'R vuln', self.rightVulnRect
	
	def Step(self):
		self.counter = self.counter + 1
		if self.counter > self.duration:
			self.counter = 0
			return 0
		return 1

	def SetFacing(self, facing):
		if self.facing is facing:
			return
		if self.facing is right:
			self.facing = left
			self.image = self.leftFacingImg
			self.offset = self.leftFacingOffset
			if self.attRect is not None:
				self.attRect = self.leftAttRect
			if self.vulnRect is not None:
				self.vulnRect = self.leftVulnRect
		elif self.facing is left:
			self.facing = right
			self.image = self.rightFacingImg
			self.offset = self.rightFacingOffset
			if self.attRect is not None:
				self.attRect = self.rightAttRect
			if self.vulnRect is not None:
				self.vulnRect = self.rightVulnRect
	
	def SetMasterRect(self, rect):
		#self.rect = rect.move( self.offset )
		self.rect = rect
		#self.vulnRect.top = rect.top + self.vulnRect.top
		#self.vulnRect.left = rect.left + self.vulnRect.left
	
	def GetOffset( self, currentOffset ):
		#print 'g off', currentOffset, self.offset,
		diff0 = currentOffset[0] - self.offset[0]
		diff1 = currentOffset[1] - self.offset[1]
		change = [-diff0,-diff1]
		#print 'change: ', change
		return change

	def Hit( self, enemy ):
		if self.counter > 1:
			return 0
		if self.attRect is None:
			return 0
		#print self.attRect
		enFr = enemy.GetFrame()
		#print enFr
		#print 'vuln', enFr.vulnRect
		#self.image.fill( (0,0,200), self.attRect )
		#enFr.image.fill( (220,0,0), enFr.vulnRect )
		attackBox = self.attRect.move( self.rect.left, self.rect.top )
		defendBox = enFr.vulnRect.move( enFr.rect.left, enFr.rect.top )
		#print 'hitb', attackBox
		#print 'enem', enemyRect
		return attackBox.colliderect( defendBox )


class Animation:
	def __init__(self, frames, loop=1):
		self.frames = frames
		self.current = 0
		self.currentFrame = self.frames[self.current]
		self.loop = loop
		self.finishCallbackFn = None
	
	def first(self):
		self.Reset()
		self.currentFrame = self.frames[self.current]
		return self.currentFrame

	def next(self):
		#if that was the last step in the frame
		if self.currentFrame.Step() is 0:
			self.current = self.current +1
			#if we just finished our last frame
			if self.current > len(self.frames) - 1:
				if self.loop:
					self.Reset()
				else:
					self.current = len(self.frames) - 1

				if self.finishCallbackFn is not None:
					#this would be weird to do in a looping 
					#animation, but allow it anyway
					self.finishCallbackFn()

			self.currentFrame = self.frames[self.current]
		return self.currentFrame

	def Reset(self):
		self.current = 0

	def GetCurrent(self):
		return self.currentFrame

	def Length(self):
		return len( self.frames )

	def SetFacing(self, facing):
		for frame in self.frames:
			frame.SetFacing( facing )

	def SetMasterRect(self, rect):
		for frame in self.frames:
			frame.SetMasterRect( rect )

	def SetFinishCallback( self, callbackFn ):
		self.finishCallbackFn = callbackFn


class AllAnimations:

	def __init__(self, anims):
		self.anims = anims
		#self.current = anims['rest']
		self.current = self.anims.values()[0]
	def ChangeTo( self, key ):
		if not self.anims.has_key( key ):
			return self.current
		self.current = self.anims[key]
		self.current.first()
		return self.current

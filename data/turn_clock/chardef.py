from animations import *
		
a = {}
b = 'turn_clock'

#---Rest animation ---

#	 name		attack		vulnerable	dur	offset
a['default'] = Animation( [
Frame(b, 'clock01',	None,		(18,0,58,53),	3,	[0,0] ),
Frame(b, 'clock02',	None,		(18,0,58,53),	3,	[0,0] ),
Frame(b, 'clock03',	None,		(18,0,58,53),	3,	[0,0] ),
Frame(b, 'clock04',	None,		(18,0,58,53),	3,	[0,0] ),
 ], loop=0 )




charAnims = AllAnimations( a )

default = a['default']

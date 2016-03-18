from animations import *
		
a = {}
b = 'manatee'

#---Rest animation ---

#	 name		attack		vulnerable	dur	offset
a['fight'] = Animation( [
Frame(b, 'rest01',	None,		None,	6,	[0,0] ),
Frame(b, 'rest02',	None,		None,	3,	[0,0] ),
Frame(b, 'rest03',	None,		None,	3,	[0,0] ),
Frame(b, 'rest02',	None,		None,	3,	[0,0] ),
 ], loop=1 )



#---In-Fight animation ---

#	 name		attack		vulnerable	dur	offset
a['death'] = Animation( [
Frame(b, 'attack01',	None,		None,	6,	[0,0] ),
Frame(b, 'attack02',	None,		None,	6,	[0,0] ),
 ], loop=0 )


#	 name		attack		vulnerable	dur	offset
a['attack'] = Animation( [
Frame(b, 'attack01',	None,		None,	6,	[0,0] ),
Frame(b, 'attack02',	None,		None,	6,	[0,0] ),
 ], loop=0 )

#	 name		attack		vulnerable	dur	offset
a['healthKit'] = Animation( [
Frame(b, 'heal01',	None,		None,	6,	[0,0] ),
Frame(b, 'heal02',	None,		None,	6,	[0,0] ),
Frame(b, 'heal01',	None,		None,	6,	[0,0] ),
 ], loop=0 )

charAnims = AllAnimations( a )

default = a['fight']
death = a['death']
attack = a['attack']

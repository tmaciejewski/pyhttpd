def pierwsze(n):
	potencjalne = range(2, n+1)
	return [ x for x in potencjalne if [dzielnik for dzielnik in range(1, (x+1)/2) if x % dzielnik == 0] == [1] ]

try:
	print pierwsze(int(_GET['i']))
except:
	print 'Podaj i'

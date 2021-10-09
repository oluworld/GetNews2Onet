import time
from etoffiutils2.pkg import xpmt, xmpta


class OpMeasure:
	def __init__(self, f, l, t, c):
		self.f = f
		self.l = l
		self.t = t
		self.c = c
		self.d = time.clock()
	
	def startOp(self, each):
		self.c += 1
		
		x = ('foo', 'bar')
		
		xpmt('%s on %s' % (x[1], x[0]))
		xmpta('%d of %d (%d left) [%d .. %d] (%f%%) %f' % (self.c, self.t,
		                                                   (self.t - self.c), each, self.l + 1,
		                                                   (100 * (float(self.c) / float(self.t))),
		                                                   time.clock() - self.d))
	
	def endOp(self):
		self.d = time.clock()

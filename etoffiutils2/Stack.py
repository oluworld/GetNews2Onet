
class Stack:
	def __init__(self):
		self.storage = []
	def push(self, x):
		self.storage.append(x)
	def pop(self):
		self.storage = self.storage[:-1]
	def top(self):
		return self.storage[-1]
	def tpop(self):
		X=self.top()
		self.pop()
		return X
	def __len__(self):
		return len(self.storage)

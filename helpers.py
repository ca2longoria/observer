
_utab = 1
def tab(i=0,t='  '):
	global _utab
	t = t * _utab
	_utab += i
	return t

def crawl(ob,keys=None,parents=None,capture=None,bubble=None,param=None):
	"""
	Returns what was passed in as param, after crawling through the target
	object's nested structure and firing callbacks at every node in both capture
	and bubble directions.
	
	Parameters:
	ob
		- target dict being crawled through
	parents
		- stack of parent objects to the current object under callback
	keys
		- stack of matching keys resulting in current object under callback in
		  pairing with parents stack
	capture
		- callback function called at every dict moving in the capture direction
		- capture(<dict>,<list>,<list>,<?>)
			- <dict>, current dict
			- <list>, keys stack at state in capture's calling
			- <list>, parents stack at state in capture's calling
			- <?>, optional parameter passed along from crawl(...)
	bubble
		- callback function called at every dict moving in the bubble direction
		- functionally identical to capture, except during the bubble step
	param
		- optional argument passed in as param to capture and bubble callbacks
	"""
	parents = parents if not parents is None else []
	keys    = keys    if not keys    is None else []
	param   = param   if not param   is None else {}
	persist = True
	if capture:
		persist = capture(ob,keys,parents,param=param)
		persist = persist or persist is None
	if persist and hasattr(ob,'__iter__'):
		iter = isinstance(ob,dict) and ob.iteritems() or zip(range(len(ob)),ob)
		for k,v in iter:
			if hasattr(v,'__getitem__'):
				parents.append(ob)
				keys.append(k)
				crawl(v,keys=keys,parents=parents,capture=capture,bubble=bubble,param=param)
				keys.pop()
				parents.pop()
	if bubble:
		bubble(ob,keys,parents,param=param)
	return param

def comparr(a,b):
	la = len(a)
	lb = len(b)
	if la != lb:
		return la - lb
	for x,y in zip(a,b):
		if x == y:
			continue
		if x < y:
			return -1
		if x > y:
			return 1
	return 0

def unwrinkle(d,parents=[],keys=[],res=[]):
	r = []
	def bubble(ob,keys,parents,param):
		p = len(parents) and parents[-1] or None
		k = len(keys) and keys[-1] or None
		r.append((ob,k,len(keys)))
	crawl(d,bubble=bubble,param=r)
	return r
def compcrawl(a,b):
	# Sorting here is hacky.  No guarantee on non-literal value sorts.
	return comparr(unwrinkle(a),unwrinkle(b))

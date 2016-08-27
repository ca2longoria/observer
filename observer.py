
import copy
import json
import types


'''
Notes:
- Should add/remove only fire if the *size* of the list/dict is changed?  That
  might clear up some uncertainty.
- This might require a 'replace' event.

Todo:
- events
	- 1 arg
		- add
		- remove
		- reorder
	- 2 arg
		- set
		- del
		- change
'''


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

def translate(ob,table=None,ignore=None,post=None):
	"""
	Returns yet another mess.  But not as bad as the last.
	"""
	table = table or {}
	ignore = ignore or []
	post = post or {}
	def these(c):
		args = []
		keys = {}
		if hasattr(type(c),'__getitem__'):
			args = [a for a in c if isinstance(a,list) or isinstance(a,tuple)]
			args = len(args) > 0 and args[0] or []
			keys = [a for a in c if isinstance(a,dict)]
			keys = len(keys) > 0 and keys[0] or {}
			c = c[0]
		return c,args,keys
	#def capture(ob,keys,parents,param):
	#	tab(1)
	def bubble(ob,keys,parents,param):
		t = type(ob)
		if t in ignore or not hasattr(ob,'__setitem__') or len(parents) < 1:
			#tab(-1)
			return
		if table.has_key(t):
			c,args,keys2 = these(table[t])
			parents[-1][keys[-1]] = c(ob,*args,**keys2)
			a = parents[-1][keys[-1]]
			if post.has_key(type(a)):
				post[type(a)](a)
		#tab(-1)
	r = [ob]
	crawl(r,bubble=bubble)
	return r[0]

class _Observer(object):
	def __init__(self,classtype=None):
		if hasattr(self,'_etable'):
			return
		# None covers all callbacks without a key.
		self._etable = {None:{}}
		self._ktable = {}
		self._classtype = classtype
		self._silent = False
	
	def _add_events_1(self,*args):
		for a in args:
			self._etable[None][a] = []
	def _add_events_k(self,*args):
		for a in args:
			self._ktable[a] = []
	
	def __parse_on(self,args):
		k = None
		call = None
		if len(args) < 1:
			raise Exception('argument(s) (k,)call is/are necessary')
		# Set k and call.
		if type(args[0]) is types.FunctionType:
			call = args[0]
			args = args[1:]
		else:
			k = args[0]
			call = args[1]
			args = args[2:]
		if call is None:
			raise Exception('Must provide callback')
		return k,call,args
	def on(self,op,*args,**keys):
		try:
			k,call,args = self.__parse_on(args)
		except Exception as e:
			print 'ERROR:',e
			return False
		# This will only fire for 'set' and 'del', assuming a key was
		# appropriately provided.
		if not self._etable.has_key(k):
			self._etable[k] = copy.deepcopy(self._ktable)
		# Add the callback.
		r = self._etable[k][op]
		r.append((call,args,keys))
		return True
	def off(self,op,all=False,*args,**keys):
		try:
			k,call,args = self.__parse_on(args)
		except Exception as e:
			print 'ERROR:',e
			return False
		if not self._etable.has_key(k):
			return False
		r = self._etable[k][op]
		for i in range(len(r)):
			c,ag,kw = r
			if c == call:
				del r[i]
				if not all:
					break
		return True

class _SetDel(_Observer):
	def __init__(self,classtype):
		_Observer.__init__(self,classtype)
		self._add_events_k('set','del')
	# Such a hack...
	def _has_key(self,k):
		return self.has_key(k)
	def __setitem__(self,k,v):
		#print tab(),'setitem',k,v
		old = self._has_key(k) and self[k] or None # Is None "null" enough?
		self._classtype.__setitem__(self,k,v)
		if not self._silent and self._etable.has_key(k):
			r = self._etable[k]['set']
			for call,args,keys in r:
				# new, old, key
				call(v,old,k,*args,**keys)
	def __delitem__(self,k):
		#print 'delitem',k
		old = self[k]
		self._classtype.__delitem__(self,k)
		if not self._silent and self._etable.has_key(k):
			r = self._etable[k]['del']
			for call,args,keys in r:
				call(old,k,*args,**keys)

class _AddRemove(_Observer):
	def __init__(self,classtype):
		_Observer.__init__(self,classtype)
		self._add_events_1('add','remove')
	def _add_call(self,a,*args,**keys):
		#print '_add',a
		if self._silent:
			return
		r = self._etable[None]['add']
		for call,args2,keys2 in r:
			# This differs from key calls, as in _SetDel.  If an index, for
			# example, is provided, then that prepends the args stored under
			# (call,args,keys).
			call(a,*(args+args2),**keys2)
	def _remove_call(self,a,*args,**keys):
		#print '_add',a
		if self._silent:
			return
		r = self._etable[None]['remove']
		for call,args2,keys2 in r:
			# Looks like it ignores keys.
			call(a,*(args+args2),**keys2)

class _Reorder(_Observer):
	def __init__(self,classtype):
		if not hasattr(classtype,'__iter__'):
			raise Exception('Must be based off an iterable class')
		_Observer.__init__(self,classtype)
		self._add_events_1('reorder')
	def _reorder_call(self,*args,**keys):
		if self._silent:
			return
		r = self._etable[None]['reorder']
		for call,args2,keys2 in r:
			call(self,*(args+args2),**keys2)

class _Translate(object):
	def __init__(self,table=None,ignore=None,post=None):
		tabe = table or {}
		ignore = ignore or []
		post = post or {}
		self._table = dict(table)
		self._ignore = set(ignore)
		self._post = post
	def translate(self,k=None):
		# NOTE: This works strangely.  It was supposed to replace without the
		#   return, but instead ended up being used as a kind of customized
		#   translate(...) call.
		ob = self if k is None else self[k]
		#print tab(),'to translate: ob',ob
		return translate(ob,self._table,self._ignore,self._post)


class List(_Translate,_SetDel,_AddRemove,_Reorder,list):
	
	def __init__(self,*args,**keys):
		def def_set_recurse(ob):
			def set_recurse(a):
				a.recurse = ob.recurse
			return set_recurse
		_Translate.__init__(self,{
			tuple:List,
			list:List,
			dict:Dict
		},post={
			List:def_set_recurse(self),
			Dict:def_set_recurse(self)
		})
		_SetDel.__init__(self,list)
		_AddRemove.__init__(self,list)
		_Reorder.__init__(self,list)
		list.__init__(self,*args,**keys)
		self.recurse = False
	def translate(self,k=None):
		v = _Translate.translate(self,k=k)
		if self.recurse and hasattr(v,'recurse'):
			#print tab(),'hasattr recurse',v
			v.recurse = True
		return v
	def _has_key(self,k):
		return 0 <= k <= len(self)
	def __str__(self):
		return '<'+list.__str__(self)+'>'
	def __setitem__(self,i,v):
		_SetDel.__setitem__(self,i,v)
		if self.recurse:
			s = self._silent
			self._silent = True
			list.__setitem__(self,i,self.translate(i))
			self._silent = s
	def __delitem__(self,i):
		v = self[i]
		_SetDel.__delitem__(self,i)
		self._remove_call(v,i)
	def __setslice__(self,a,b,r,*args,**keys):
		#print 'setslice',a,b,r
		old_slice = self[a:b]
		list.__setslice__(self,a,b,r,*args,**keys)
		if self.recurse:
			for i in range(a,a+len(r)):
				s = self._silent
				self._silent = True
				list.__setitem__(self,i,self.translate(i))
				self._silent = s
		# Because the removal and insertion has already occurred, the self
		# passed into the _add_calls will not represent the state of the
		# list at time of insertion.
		for i in range(a,b):
			self._remove_call(old_slice[i-a],i)
		for i in range(a,a+len(r)):
			self._add_call(r[i-a],i,self)
	def __delslice__(self,a,b,*args,**keys):
		#print 'delslice',a,b
		old_slice = self[a:b]
		list.__delslice__(self,a,b,*args,**keys)
		for i in range(a,b):
			if self._etable.has_key(i):
				r = self._etable[i]['del']
				for call,args2,keys2 in r:
					call(old_slice[i-a],i,*args2,**keys2)
			self._remove_call(old_slice[i-a],i)
	def append(self,v,*args,**keys):
		#print 'appending',v
		list.append(self,v)
		if self.recurse:
			#print 'recurse'
			s = self._silent
			self._silent = True
			list.__setitem__(self,-1,self.translate(len(self)-1))
			self._silent = s
			
		self._add_call(v,len(self),self)
	def extend(self,r,*args,**keys):
		old_len = len(self)
		list.extend(self,r,*args,**keys)
		if self.recurse:
			for i in range(old_len,len(self)):
				s = self._silent
				self._silent = True
				self[i] = self.translate(i)
				self._silent = s
		for i in range(old_len,len(self)):
			self._add_call(self[i],old_len+i,self)
	def insert(self,i,v,*args,**keys):
		list.insert(self,i,v,*args,**keys)
		if self.recurse:
			s = self._silent
			self._silent = True
			self[i] = self.translate(i)
			self._silent = s
		self._add_call(v,i,self)
	def remove(self,v,*args,**keys):
		i = self.index(v)
		list.remove(self,v,*args,**keys)
		self._remove_call(v,i,self)
	def pop(self):
		v = list.pop(self)
		self._remove_call(v,len(self),self)
		return v
	def reverse(self,*args,**keys):
		list.reverse(self,*args,**keys)
		self._reorder_call()
	def sort(self,*args,**keys):
		list.sort(self,*args,**keys)
		self._reorder_call()


class Dict(_Translate,_SetDel,_AddRemove,dict):
	def __init__(self,*args,**keys):
		def def_set_recurse(ob):
			def set_recurse(a):
				a.recurse = ob.recurse
			return set_recurse
		_Translate.__init__(self,{
			tuple:List,
			list:List,
			dict:Dict
		},post={
			List:def_set_recurse(self),
			Dict:def_set_recurse(self)
		})
		_SetDel.__init__(self,dict)
		_AddRemove.__init__(self,dict)
		dict.__init__(self,*args,**keys)
		# Observer recursion here, or on every add?
		self.recurse = False
	def translate(self,k=None):
		v = _Translate.translate(self,k=k)
		if self.recurse and hasattr(v,'recurse'):
			#print tab(),'hasattr recurse',v
			v.recurse = True
		return v
	def __setitem__(self,k,v):
		replacing = self.has_key(k)
		a = replacing and self[k] or None
		_SetDel.__setitem__(self,k,v)
		# This comparison will not work in all cases, especially references.
		if replacing and a != v:
			self._remove_call(a,k,self)
		self._add_call(v,k,self)
		if self.recurse:
			s = self._silent
			self._silent = True
			dict.__setitem__(self,k,self.translate(k))
			self._silent = s
	def __delitem__(self,k):
		v = self[k]
		_SetDel.__delitem__(self,k)
		self._remove_call(v,k,self)
	def update(self,a,**keys):
		for k,v in a:
			# This bit is still in the air; should I add a 'replace' event?
			# Also, this fires callbacks before all values are assigned.
			self[k] = v
		if len(keys):
			self.update(keys)
	def pop(self,*args):
		k = args[0]
		v = self[k]
		dict.pop(self,k)
		self._remove_call(v,k,self)
		return v
	def popitem(self):
		p = dict.popitem(self)
		self._remove_call(p[0],p[1],self)
		return p


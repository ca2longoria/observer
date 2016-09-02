
import copy
import observer
import unittest as ut
from helpers import *


class TestObserver(ut.TestCase):
	def setUp(self):
		self.a = [1,2,3,4]
		self.b = {'a':'alpha','b':'beta','c':{1:'one',2:'two'},'d':'ohyouknow'}
		
		self.counts = {'set':0,'del':0,'change':0,'add':0,'remove':0,'reorder':0}
		def these(ob):
			res = {}
			for k in ob.keys():
				def oh(k,ob):
					def a(*args,**keys):
						ob[k] += 1
						return ob[k]
					return a
				res[k] = oh(k,ob)
			return res
		self.count_inc = these(self.counts)
		
		self.list = observer.List(self.a)
		self.dict = observer.Dict(self.b)
	def tearDown(self):
		pass
	

class TestList(TestObserver):
	
	def test_list_init(self):
		self.assertEqual(comparr(self.list,self.a),0)
	
	def test_list_set_del(self):
		self.list.on('set',0,self.count_inc['set'])
		self.list.on('del',0,self.count_inc['del'])
		
		self.list[0] = 0
		self.a[0] = 0
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['set'],1)
		
		del self.list[0]
		del self.a[0]
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['del'],1)
		self.assertEqual(self.counts['set'],1) # unchanged
	
	def test_list_add(self):
		self.list.on('add',self.count_inc['add'])
		
		# Test append
		self.list.append(5)
		self.a.append(5)
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['add'],1)
		
		# Test insert
		self.list.insert(0,0)
		self.a.insert(0,0)
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['add'],2)
		
		# Test extend
		self.list.extend([6,7,8])
		self.a.extend([6,7,8])
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['add'],5)
		
		# Test __setslice__
		self.list[0:3] = [-1,-2]
		self.a[0:3] = [-1,-2]
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['add'],7)
	
	def test_list_remove(self):
		self.list.extend([5,6,7,8])
		self.a.extend([5,6,7,8])
		
		self.list.on('remove',self.count_inc['remove'])
		
		# Test remove
		self.list.remove(1)
		self.a.remove(1)
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['remove'],1)
		
		# Test pop
		self.list.pop()
		self.a.pop()
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['remove'],2)
		
		# Test __delitem__
		del self.list[0]
		del self.a[0]
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['remove'],3)
		
		# Test __setslice__
		self.list[:3] = [-1,-2]
		self.a[:3] = [-1,-2]
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['remove'],6)
		
		# Test __delslice__
		del self.list[:3]
		del self.a[:3]
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['remove'],9)
	
	def test_list_change(self):
		self.list.on('change',self.count_inc['change'])
		
		self.list[0] = 'zero'
		self.a[0] = 'zero'
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['change'],1)
	
	def test_list_reorder(self):
		self.list.on('reorder',self.count_inc['reorder'])
		
		self.a.reverse()
		self.list.reverse()
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['reorder'],1)
		
		self.a.sort()
		self.list.sort()
		self.assertEqual(comparr(self.list,self.a),0)
		self.assertEqual(self.counts['reorder'],2)
	
	def test_list_recurse(self):
		self.a[0] = ['A','B',[0]]
		
		# Test init
		r = observer.List.Recurse(copy.deepcopy(self.a))
		
		#exit(1)
		self.assertEqual(comparr(r,self.a),0)
		self.assertEqual(type(r[0]),observer.List)
		self.assertEqual(type(r[0][-1]),observer.List)
		
		# Recursive init
		r[0][-1].append([])
		self.a[0][-1].append([])
		self.assertEqual(type(r[0][-1][-1]),observer.List)
		
		# Test append
		r[0][-1].on('add',self.count_inc['add'])
		r[0][-1].append(1)
		self.a[0][-1].append(1)
		self.assertEqual(compcrawl(r,self.a),0)
		self.assertEqual(self.counts['add'],1)
		
		# Test insert
		r.on('add',self.count_inc['add'])
		r.insert(0,[[]])
		self.a.insert(0,[[]])
		self.assertEqual(compcrawl(r,self.a),0)
		self.assertEqual(type(r[0][0]),observer.List)
		self.assertEqual(self.counts['add'],2)
		
		# Test extend
		r.extend([1,2,[]])
		self.a.extend([1,2,[]])
		self.assertEqual(compcrawl(r,self.a),0)
		self.assertEqual(type(r[-1]),observer.List)
		self.assertEqual(self.counts['add'],5)
		
		# Test __setslice__
		r[0:2] = [-2,[]]
		self.a[0:2] = [-2,[]]
		self.assertEqual(compcrawl(r,self.a),0)
		self.assertEqual(type(r[0]),int)
		self.assertEqual(type(r[1]),observer.List)
		self.assertEqual(self.counts['add'],7)


class TestDict(TestObserver):
	
	# I've yet to implement the recursive List/Dict-setting, but soon, sooon...
	def test_dict_init(self):
		self.assertEqual(compcrawl(self.dict,self.b),0)
	
	def test_dict_set_del(self):
		self.dict.on('set','a',self.count_inc['set'])
		self.dict.on('set','a',self.count_inc['del'])
		
		self.dict['a'] = 'ALPHARB'
		self.b['a'] = 'ALPHARB'
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(self.counts['set'],1)
		
		del self.dict['a']
		del self.b['a']
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(self.counts['del'],1)
		self.assertEqual(self.counts['set'],1) # unchanged
	
	def test_dict_add(self):
		self.dict.on('add',self.count_inc['add'])
		
		# Test __setitem__
		self.dict['a'] = 'BEHTAR'
		self.b['a'] = 'BEHTAR'
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(self.counts['add'],1)
		
		# Test update
		self.dict.update({'a':0,'x':1,'y':{'z':2}})
		self.b.update({'a':0,'x':1,'y':{'z':2}})
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(self.counts['add'],4)
	
	def test_dict_remove(self):
		self.dict.on('remove',self.count_inc['remove'])
		
		# Test __setitem__
		self.dict['a'] = 'OOHNOO'
		self.b['a'] = 'OOHNOO'
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(self.counts['remove'],1)
		
		# Test __delitem__
		del self.dict['a']
		del self.b['a']
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(self.counts['remove'],2)
		
		# Test pop
		self.dict.pop('b')
		self.b.pop('b')
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(self.counts['remove'],3)
		
		# Test popitem
		self.dict.popitem()
		self.b.popitem()
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(self.counts['remove'],4)
		
		# Test update
	
	def test_dict_change(self):
		self.dict.on('change',self.count_inc['change'])
		
		self.dict['a'] = 'what'
		self.b['a'] = 'what'
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(self.counts['change'],1)
	
	def test_dict_recurse(self):
		self.dict = observer.Dict.Recurse(self.dict)
		
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(type(self.dict['c']),observer.Dict)
		
		# Test __setitem__
		self.dict['a'] = {0:{}}
		self.b['a'] = {0:{}}
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(type(self.dict['a']),observer.Dict)
		self.assertEqual(type(self.dict['a'][0]),observer.Dict)
		
		self.dict['a'][0].on('add',self.count_inc['add'])
		self.dict['a'][0][1] = 5
		self.b['a'][0][1] = 5
		self.assertEqual(compcrawl(self.dict,self.b),0)
		self.assertEqual(self.counts['add'],1)
		

if __name__ == '__main__':
	ut.main()

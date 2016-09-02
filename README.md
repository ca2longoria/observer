# observer
Observer classes extending common types

Events handled:
- add
- remove
- reorder
- set
- del
- change

Two callback types, so far:
- 1-param
  - add
  - remove
  - reorder
- 2-param
  - set
  - del
  - change

### So far
```python
import observer
```
or perhaps now...
```python
import observer.observer
```
- List
- Dict

The attribute `recurse` and method `translate`, used in conjunction, allow for recursively replacing incoming objects' list- and dict-extending values with List and Dict respectively.
```python
{observer-object}.recurse = True
{observer-object}.translate()
```

This is, however, ungainly, and an extending Recurse class per List and Dict has been added as an, at least aesthetically, preferable solution.  The following are equivalent, except for setting `recurse` and running `translate()` after the respective parent class init.

```python
a = List([1,2,3])
a = List.Recurse([1,2,3])

b = Dict({0:1})
b = Dict.Recurse({0:1})
```

### Unit tests
testobserver.py
```shell
python testobserver.py
```

- List
- Dict

### Setting events
```python
def callback(val,*args,**keywords):
  pass

{observer-object}.on('add',callback)
{observer-object}.off('add',callback)

{observer-object}.on('remove',callback)
{observer-object}.off('remove',callback)

{observer-object}.on('reorder',callback)
{observer-object}.off('reorder',callback)

def callback(val,old_val,key,*args,**keywords):
  pass

{observer-object}.on('change',callback)
{observer-object}.off('change',callback)
```

```python
def callback(val,old_val,key,*args,**keywords):
  pass

{observer-object}.on('set','key1',callback)
{observer-object}.off('set','key1',callback)

def callback(val,old_val,*args,**keywords):
  pass

{observer-object}.on('del','key1',callback)
{observer-object}.off('del','key1',callback)
```

It is possible to add default \*args and \*\*keys arguments that append to immediately provided arguments, but I'll cover that later.

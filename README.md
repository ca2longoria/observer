# observer
Observer classes extending common types.

For clarity, this is observer in the sense of adding event handling to otherwise-unsuspecting objects.  In this case, extended are `list` and `dict`.  Working presently on `set`.

Events handled:
- add
- remove
- reorder
- set
- del
- change

Three callback types, so far:
- 1-param
  - add
  - remove
  - reorder
- 2-param
  - del
- 3-param
  - set
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

These are set with one param.

```python
def callback(val, *args, **keywords):
  pass

{observer-object}.on('add',callback)
{observer-object}.off('add',callback)

{observer-object}.on('remove',callback)
{observer-object}.off('remove',callback)

# For reorder, val is simply passed self.
{observer-object}.on('reorder',callback)
{observer-object}.off('reorder',callback)

def callback(val, old_val, key, *args, **keywords):
  pass

{observer-object}.on('change',callback)
{observer-object}.off('change',callback)
```

These are set with 2 params.

```python
def callback(val, old_val, key, *args, **keywords):
  pass

{observer-object}.on('set','key1',callback)
{observer-object}.off('set','key1',callback)

def callback(old_val, key, *args, **keywords):
  pass

{observer-object}.on('del','key1',callback)
{observer-object}.off('del','key1',callback)
```

It is possible to add default \*args and \*\*keys arguments that append to immediately provided arguments, but I'll cover that later.

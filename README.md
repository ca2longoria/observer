# observer
Observer classes extending common types

Events handled:
- add
- remove
- reorder
- set
- del

Events pending:
- change/replace

Two callback types, so far:
- 1-param
  - add
  - remove
  - reorder
- 2-param
  - set
  - del
  - (change/replace?)

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

Note that to recursively replace new list/dict values with List/Dict values, this odd thing must be manually set:
```python
{observer-object}.recurse = True
```
Currently thinking through possible solutions.

### Unit tests
testobserver.py
```shell
python testobserver.py
```

- List
- Dict

### Setting events
```python
{observer-object}.on('add',callback)
{observer-object}.off('add',callback)
```

```python
{observer-object}.on('set','key1',callback)
{observer-object}.off('set','key1',callback)
```

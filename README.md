timeslot
========

Class for working with time slots that have an arbitrary start and end.

Completes the Python datetime module: datetime (a time), timedelta (a duration), timezone (an offset), **timeslot** (a range/interval).

Supports operations such as: overlaps, intersects, contains, intersection, adjacent, gap, union.

Initially developed as part of [aw-core](https://github.com/ActivityWatch/aw-core), and inspired by a [similar library for .NET](http://www.codeproject.com/Articles/168662/Time-Period-Library-for-NET).

You might also be interested in [`pandas.Interval`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Interval.html).


# Usage

```python
from datetime import datetime, timedelta
from timeslot import Timeslot

now = datetime.now()

slot = Timeslot(now, now + timedelta(hours=24)

assert slot.duration == timedelta(hours=24)

slot_large = Timeslot(now, now + timedelta(hours=24)
slot_small = Timeslot(now, now + timedelta(hours=1))

# The events definitely intersect
assert slot_large.intersects(slot_small)

# The larger even contains the smaller!
assert slot_large.contains(slot_small)
assert slot_small in slot_large

# You can also check if a datetime is within the slot
assert slot_large.contains(now)

# The union of a slot and a contained slot is equal to the larger slot
assert slot_large == slot_large.union(slot_small)

# Intersection
# TODO

# Gap
# TODO

# Adjacent
# TODO
```


# Synonyms

 - timerange (the name was already taken on PyPI)
 - timeperiod (already taken on PyPI)
 - time interval

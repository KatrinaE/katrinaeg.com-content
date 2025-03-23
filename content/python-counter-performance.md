Title: Python Counter Performance
Date: Wed 16 April 2014
Author: Katrina Ellison Geltman
Slug: python-counter-performance

Python's Counters are a subclass of dictionaries used for tallying how many
times elements occur in an iterable data structure like a list. I'm writing an
application that makes heavy use of Counters - like creating 10,000,000
counters in one run - and I found that they were a performance chokepoint.

Since each of my counters is very similar to the previous one generated, I
hoped that I could improve performance by continually mutating an existing
counter rather than creating all of them from scratch. I hoped to do this by
creating a Counter with a short list of changes and adding it to my existing
Counter.

### tl;dr

Adding Python Counters takes the same amount of time as creating each of the
addend Counters. There's no performance gain from applying changes to an
existing Counter by adding a second one to it vs. generating a new Counter
from scratch.

### Counter performance vs. dictionary performance

Python advertises Counters as 'fast'. For small _n_ (here, _n_ = 10) creating
one is about 4 times slower than creating a regular dictionary:

    
    >>> import timeit
    >>> from collections import Counter
    
    >>> # Timing dictionary creation
    >>> timeit.timeit("x = { num : 'foo' for num in range(0, 10)}", number=1000)
    0.003952980041503906
    
    >>> # Timing Counter creation
    >>> timeit.timeit("from collections import Counter; x = Counter({ num : 'foo' for num in range(0, 10)})", number=1000)
    0.016061067581176758
    

For larger _n_ , the performance disparity isn't nearly as extreme. Here, _n_
= 1,000,000 and Counter creation is about 35% slower than dictionary creation:

    
    # Timing dictionary creation
    >>> timeit.timeit("x = { num : 'foo' for num in range(0, 1000000)}", number=1000)
    123.48868298530579
    
    # Timing Counter creation
    >>> timeit.timeit("from collections import Counter; x = Counter({ num : 'foo' for num in range(0, 1000000)})", number=1000)
    167.64849400520325
    

### Creating counters

When creating a Counter, you can either create an empty Counter, or you can
pass it an iterable whose items you want to count. If you pass it an iterable,
most of the activity to create the Counter takes place in its `update` method
- `Counter.__init__()` just creates an empty Counter, then updates it with
values from the iterable. For example, here are the interesting parts of
cProfile output on code to create a Counter of 1,500 elements 1,000 times.

ncalls | tottime | percall | cumtime | percall | filename:lineno(function)  
---|---|---|---|---|---  
1000 | 0.957 | 0.001 | 1.201 | 0.001 | collections.py:501(update)  
1575000 | 0.219 | 0.000 | 0.219 | 0.000 | {method 'get' of 'dict' objects}  
36000 | 0.020 | 0.000 | 0.020 | 0.000 | counter-perf-test.py:18()  
1000 | 0.003 | 0.000 | 0.004 | 0.000 | abc.py:128(**instancecheck**)  
1000 | 0.002 | 0.000 | 1.203 | 0.001 | collections.py:438(**init**)  
  
`Counter.update()` takes by far the most time, and on top of that it's what
calls most of the functions below it. What does it look like?

    
    def update(self, iterable=None, **kwds):
        if iterable is not None:
            if isinstance(iterable, Mapping):
                if self:
                    self_get = self.get
                    for elem, count in iterable.iteritems():
                        self[elem] = self_get(elem, 0) + count
                else:
                    super(Counter, self).update(iterable) # fast path when counter is empty
            else:
                self_get = self.get
                for elem in iterable:
                    self[elem] = self_get(elem, 0) + 1
        if kwds:
            self.update(kwds)
    

First, `update` checks to see if the input iterable is a `Mapping` \- a
dictionary or dictionary subclass (like a Counter). This is so it can use the
`update` method of Counter's parent class, `dict`, if the Counter is empty - a
performance enhancement.

If the input iterable is not a `Mapping`, or if the Counter already has stuff
in it, `update` loops through the iterator. Each element in the iterator is a
key in the Counter. As `update` loops, it increments the old value stored in
`self[elem]` by 1.

Finally, `update` updates values passed by keyword argument, like those shown
below:

    
    >>> x = Counter(key1 = 'foo', key2 = 'var')
    >>> print x
    Counter({'key2': 'var', 'key1': 'foo'})
    

The performance hits in `update` are in the time it takes to (1) loop through
the iterator, and (2) `get` the Counter value of each element in the iterator.
So performance is tied almost entirely to the size of the iterator we're
instantiating the Counter with.

### Adding Counters

Given that, adding a short Counter to a large Counter shouldn't degrade
performance at all. Here I profile adding a 25-element Counter to the
1500-element one.

ncalls | tottime | percall | cumtime | percall | filename:lineno(function)  
---|---|---|---|---|---  
2000 | 1.399 | 0.001 | 1.729 | 0.001 | collections.py:501(update)  
1600000 | 0.275 | 0.000 | 0.275 | 0.000 | {method 'get' of 'dict' objects}  
1 | 0.234 | 0.234 | 2.063 | 2.063 | counter-perf-test.py:6(main)  
1035 | 0.046 | 0.000 | 0.060 | 0.000 | random.py:291(sample)  
36000 | 0.040 | 0.000 | 0.040 | 0.000 | counter-perf-test.py:18()  
36000 | 0.032 | 0.000 | 0.032 | 0.000 | counter-perf-test.py:22()  
2000 | 0.007 | 0.000 | 0.013 | 0.000 | abc.py:128(**instancecheck**)  
2000 | 0.007 | 0.000 | 1.736 | 0.001 | collections.py:438(**init**)  
25358 | 0.006 | 0.000 | 0.006 | 0.000 | {method 'add' of 'set' objects}  
  
Why does this lengthen the code's running time by 60%? I was surprised,
because the new Counter is not very big, and I'm not making any copies - I
thought that adding Counters would be quick. Let's look at `Counter__add__()`:

    
    def __add__(self, other):
        if not isinstance(other, Counter):
            return NotImplemented
        result = Counter()
        for elem, count in self.items():
            newcount = count + other[elem]
            if newcount > 0:
                result[elem] = newcount
        for elem, count in other.items():
            if elem not in self and count > 0:
                result[elem] = count
        return result
    

Here's why it takes so long: it creates an entirely new counter (`result`) by
iterating through the items in both of the input Counters (`self.items()` and
`other.items()`). Adding two Counters takes the same amount of time as it took
to instantiate those Counters initially.

Gah. Looks like I'll have to come up with another idea to improve my program's
running time.

* * *
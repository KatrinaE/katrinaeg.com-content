Title: Counting Overlapping Elements in Python
Date: Wed 16 April 2014
Author: Katrina Ellison Geltman
Slug: python-counters

Say you have a list of lists, like:

    
    matrix = [[1, 2, 3], [4, 5, 6], [1, 2, 6]]
    

You want to know how many times pairs of numbers occur in the same list, or
overlap. In the example above, you'd have:

* 1 & 2: paired twice
* 1 & 3: paired once
* 2 & 3: paired once
* 4 & 5: paired once
* 4 & 6: paired once
* 5 & 6: paired once
* 1 & 6: paired once
* 2 & 6: paired once

You'd like some code that tells you that there's one pairing that occur twice
and seven pairings that occur once. [Stack Overflow will tell you how to do
it](http://stackoverflow.com/questions/10844556/python-counting-frequency-of-
pairs-of-elements-in-a-list-of-lists):

    
    from collections import Counter
    from itertools import chain, combinations
    Counter(chain.from_iterable(combinations(row, 2) for row in matrix))
    

That works, but it's completely confusing. I'm going to break down what it's
doing, beginning with `combinations(row, 2)`.

### Producing combinations

`combinations()` produces an iterator containing the pairs in an input
iterable (e.g. a list). The code below uses `combinations` to generate all the
pairs in the matrix's first row. Each tuple represents one pairing; for
example, `(1, 2)` indicates that 1 and 2 were in the same row one time.

    
    >>> x = combinations(matrix[0], 2)
   
    >>> print x
    <itertools.combinations object at 0x10d1719f0>
    
    >>> print list(x)
    [(1, 2), (1, 3), (2, 3)]
    

To find the combinations in all of the rows in the matrix, we apply
`combinations()` to each row through a generator comprehension. A generator
comprehension has the same syntax as a list comprehension but produces a
generator instead of a list.

    
    >>> combos = (combinations(row, 2) for row in matrix)
    
    >>> print combos
    <generator object <genexpr> at 0x10d168f00>
    
    >>> print [list(x) for x in combos]
    [[(1, 2), (1, 3), (2, 3)], [(4, 5), (4, 6), (5, 6)], [(1, 2), (1, 6), (2, 6)]]
    

### Chaining the combinations

Our end goal is to count how many there are of each tuple; we should end up
with one that occurs twice (`(1, 2)`) and seven that occur once. By inspecting
the output above, _we_ can see that this is the case, but Python can't because
the tuples aren't all in the same combinations object. Enter
`chain.from_iterable()`, a function that will combine each of the
`combinations` objects in `combos` into one giant iterator:

    
    >>> chained_combos = chain.from_iterable(combos)
    >>> list(chained_combos)
    [(1, 2), (1, 3), (2, 3), (4, 5), (4, 6), (5, 6), (1, 2), (1, 6), (2, 6)]
    

### Counting the pairs in the chain

Now we can create a `Counter` object to tally the frequency of each pairing. A
`Counter` is a type of dictionary used for creating tallies: the keys are the
items you're counting, and the values are the tallies.

    
    >>> counts = Counter(chained_combos)
    >>> print counts
    Counter({(1, 2): 2, (1, 3): 1, (4, 6): 1, (4, 5): 1, (5, 6): 1, (2, 6): 1, (2, 3): 1, (1, 6): 1})
    >>> print counts.values()
    [2, 1, 1, 1, 1, 1, 1, 1]
    

### Tallying the overall frequencies

Finally, to count the overall frequencies, we use a second counter:

    
    >>> overall_counts = Counter(counts.values())
    >>> print overall_counts
    Counter({1: 7, 2: 1})
    

Ta da! 7 pairs together once, 1 pair together twice.

This can be easily extended from pairs to trios, quartets, and larger groups
by replacing `combinations(row, 2)` with `combinations(row, <your-size>)`.

Finally, an important note: this will only work if the values inside each
tuple are always listed in the same order. `(1, 2)` is not the same as `(2,
1)`.

* * *


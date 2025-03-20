Title: Seating Chart Creator

# Katrina Ellison Geltman

  * [Home]()
  * Pages
  * [About](/pages/about-me.html)
  * [Projects](/pages/projects.html)
  * Links
  * [LinkedIn](http://www.linkedin.com/in/katrinaellison)
  * [GitHub](http://www.github.com/katrinae)
  * [SlideShare](http://www.slideshare.net/kellison00)
  * Monthly Archives
  * [December 2015 (1)](/posts/2015/12/)
  * [May 2014 (2)](/posts/2014/05/)
  * [April 2014 (3)](/posts/2014/04/)
  * [March 2014 (2)](/posts/2014/03/)
  * [February 2014 (2)](/posts/2014/02/)
    * # [Katrina Ellison Geltman](/)

    * [About](/pages/about-me.html)
    * [Projects](/pages/projects.html)
    * [Archives](/archives.html)

## Seating Chart Creator

Seating Chart Creator outputs a third CSV file, `output.csv`. Its form is the
same as that of `people.csv`, but all cells in the days columns contain a
table name.

**_UPDATE SO HEADERS OF PEOPLE.CSV AND OUTPUT.CSV ARE ACTUALLY THE SAME
NAME_**

### Program Overview

Seating Chart Creator **_HAS A GUI??_**

Seating Chart Creator imports `people.csv` and `tables.csv` and from them
creates person and table objects.

A person object has an id, category, first name, and last name, as well as
fields for each day (e.g. `self.Monday`, `self.Tuesday`), which will store the
names of the tables where the person will sit. A table object has a name, day,
capacity, and list of people sitting there. (Except for the head table, this
list is initially empty).

For convenience, a list of days is created from the header row of
`tables.csv`.

The seating chart is created by populating the days' fields in the person
objects and the lists of people in the table objects. An initial, random
solution is generated, and then [simulated annealing](/simulated-
annealing.html) is used to refine that solution until an optimum is reached.
The `anneal` function switches people around, looking for better solutions,
according to specific annealing parameters.

One of those parameters is a variable called `T`, for temperature. `T` starts
out large and is slowly lowered. The annealing algorithm behaves slightly
differently at each value of `T`, helping it find a good solution. Multiple
switches are carried out at each temperature.

After each switch, the cost of that solution is calculated. A set of cost
functions, one for each constraint, is assessed. The total cost of the
solution is the sum of these individual costs.

Just after `T` is lowered, the best solution is saved so that it can be
returned if the algorithm terminates. After that, a progress graph - a
scatterplot showing the best cost found at the end of each iteration - is
updated. Initially, the cost drops quickly; by the end, many iterations need
to be conducted to squeeze out improvements.

In order to update the progress graph, `anneal` is used as a generator. **ADD
MORE**.

When an optimal solution is found or when the temperature reaches a predefined
minimum, the program terminates and outputs the best solution found.

### Program Structure

_Make a pretty tree_

![](/theme/img/headshot.png)

##### Links

[LinkedIn](http://www.linkedin.com/in/katrinaellison)

[GitHub](http://www.github.com/katrinae)

[SlideShare](http://www.slideshare.net/kellison00)

##### Monthly Archives

[December 2015 (1)](/posts/2015/12/)

[May 2014 (2)](/posts/2014/05/)

[April 2014 (3)](/posts/2014/04/)

[March 2014 (2)](/posts/2014/03/)

[February 2014 (2)](/posts/2014/02/)

* * *

Powered by Pelican and based on a theme by [Kenton
Hamaluik](http://hamaluik.com).


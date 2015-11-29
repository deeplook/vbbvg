README
======

This little tool will fetch and display real-time departure times for VBB/BVG 
public transport lines for a single stop in Berlin and Brandenburg, Germany.
Here, VBB is the "Verkehrsverbund Berlin-Brandenburg" and BVG is the "Berliner
Verkehrsbetriebe".


Sample output
-------------

Here is an example output for "Möckernbrücke" (including the optional ``--header``)
on the command-line:

.. code-block:: console

    $ python vbbvg.py --stop Möckernbrücke --header
    Now: 14:06:04
    Stop-Name: U Möckernbrücke (Berlin)
    Stop-ID: 9017104

    Wait    Departure    Line    Destination
    ------  -----------  ------  ----------------------------
    00:48   14:07        U1      U Uhlandstr. (Berlin)
    02:48   14:09        U7      S+U Rathaus Spandau (Berlin)
    02:48   14:09        U1      S+U Warschauer Str. (Berlin)
    04:48   14:11        U7      U Rudow (Berlin)

This shows the departure times from one stop, limited to all earliest unique 
combinations of the *Line* and *Destination* columns. This is usually the only
information one is interested in just "before leaving the office" as a typical
use-case. The waiting time is calculated by this tool and inserted as the
first column.

There are quite a few other command-line options which you can find out more
about by typing ``python vbbvg.py -h``.


Installation and Test
---------------------

There is no support yet to make this tool installable by ``pip`` or 
``distutils`` (like a ``setup.py`` script). Nevertheless, there is a list 
of dependencies in the file ``requirements.txt`` (for more about them 
please read the next section) which you can install with the command 
``pip install -r requirements.txt``. 
Then, in order to use this tool and run it from anywhere, just copy the
files ``vbbvg.py`` and ``vbbvg_stopy.csv`` to the same directory
in your search path, and make it executable.

To run the little "test suite", download and unpack this repository or
clone it and, in the unpacked archive, run the command ``py.test test.py``, 
which of course needs the ``pytest`` package to be available (not listed in 
the requirements, but easy to install with ``pip install pytest``).


Dependencies
------------

This tool was partly developed as an instructive example of using ``Pandas``
for greatly simplifying the code needed for working with tables or
*dataframes* in ``Pandas'`` own parlance.
The ``BeautifulSoup4`` and ``htmlib5`` packages are optional dependencies,
but needed for ``pandas.read_html()`` which will barf if they are not
installed.

Output on the command-line is created by using the ``termcolor`` and 
``tabulate`` packages, saving a great amount of code to write otherwise
oneself.


Implementation
--------------

Since VBB/BVG have no API for real time data access this data is fetched 
(using ``pandas``, yes!) from a web application on http://mobil.bvg.de.
There, as a real person you can enter parts of the destination name and get
a list of matching destinations to chose from, before you get to see the result 
table.

To avoid multi-level scraping, speed things up (and add some more thrills) 
a small part of an existing 
`"Open Data" VBB database <http://daten.berlin.de/kategorie/verkehr>`_, 
published under the 
`CC-BY 3.0 license <http://creativecommons.org/licenses/by/3.0/de/>`_ 
is used to access the stop names and IDs of the VBB/BVG public transport 
network (a simple CSV file named here ``vbbvg_stops.csv``).

The resulting tables are output as "real" tables in various formats on
the command-line.


Usage
-----

Command-Line
............

You can run a few sample command-line calls using the options ``--test`` 
and ``--stop <NAME_ID>`` for a given stop name or ID like this for the 
stop *Möckernbrücke*:

.. code-block:: console

    $ python vbbvg.py --test --stop Möckernbrücke


Programmatic
............

The main function to use programmatically is ``vbbvg.get_next_departures()``,
which returns a Pandas DataFrame object, which you can convert to almost
anything you like this:

.. code-block:: python

    import vbbvg
    # get departures of S7 and S75 from Berlin main station
    df = vbbvg.get_next_departures('9003201', filter_line='S7')
    print(list(df.to_records()))
    ...
    print(df.to_csv())
    ...


Dashboards
..........

When using this tool inside some kind of web-based dashboard like those 
created by http://dashing.io (which was the originally intended use-case) 
one should use a stop's ID to be sure to provide a unique stop on the 
VBB/BVG public transport network. You can find out the IDs by running 
test queries with the ``--header`` option.


Todo
----

Any help is welcome with any of the following items:

- turn this into a real pip-installable package
- make code polyglot, running not only on Python 2.7 but also 3.4/3.5
- test option to filter specific line types like S-Bahn ('S.*') or single 
  lines ('U7')
- use in some real dashboard like those of dhasing.io (the original purpose!)
- mention that case is ignored in the whole tool for all stop names

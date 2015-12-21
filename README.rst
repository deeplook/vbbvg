README
======

This little tool will fetch and display real-time departure times for VBB/BVG 
public transport lines for a single stop in Berlin and Brandenburg, Germany.
Here, VBB_ is the "Verkehrsverbund Berlin-Brandenburg" and BVG_ is the "Berliner
Verkehrsbetriebe".

.. _VBB: http://www.vbb.de/en/index.html
.. _BVG: http://www.bvg.de/en/

This tool was partly developed as an instructive example (although a toy one)
of using Pandas_ and producing some output to be fed into a web-based 
dashboard like those one can create with Dashing_ (to be done). 

.. _Pandas: http://pandas.pydata.org
.. _Dashing: http://dashing.io



Sample output
-------------

Here is an example output for "Möckernbrücke" (including the optional ``--header``)
on the command-line:

.. code-block:: console

    $ vbbvg --stop Möckernbrücke --header
    Now: 14:06:04
    Stop-Name: U Möckernbrücke (Berlin)
    Stop-ID: 9017104

    Wait    Departure    Line    Destination
    ------  -----------  ------  ----------------------------
    00:48   14:07        U1      U Uhlandstr. (Berlin)
    02:48   14:09        U7      S+U Rathaus Spandau (Berlin)
    02:48   14:09        U1      S+U Warschauer Str. (Berlin)
    04:48   14:11        U7      U Rudow (Berlin)

This shows the waiting and departure times (in MM:SS and HH:MM format,
respectively) from one stop, limited to all earliest unique combinations of
the *Line* and *Destination* columns.
This is usually the only information one is interested in just "before
leaving the office" as a typical use-case.
This tool filters these combinations, calculates the waiting times and inserts
them as the first column in the output.
There are quite a few other command-line options which you can find out more
about by typing ``python vbbvg -h``.


Installation and Test
---------------------

You can clone the repository and install it via pip. After
installing, you will have access system wide (or in your virtualenv)
to ``vbbvg`` programmatically or via the CLI.

::

    pip install -e .

There is a list of dependencies in the file ``requirements.txt``
(for more about them please read the next section) which you can install
with the command ``pip install -r requirements.txt``. 

To run the little "test suite", download and unpack this repository or
clone it, and run the command ``python setup.py test`` in the unpacked archive. 
Of course this needs the ``pytest`` package to be available (not listed in 
the requirements, but easy to install with ``pip install pytest``).


Dependencies
------------

This tool was partly developed as an instructive example of using Pandas_ for 
greatly simplifying the code needed for working with tables (``DataFrame``
objects).
The ``BeautifulSoup4`` and ``html5lib`` packages are optional dependencies,
but needed for ``pandas.read_html()`` which will barf if they are not
installed.
Output on the command-line is created by using the ``termcolor`` and 
``tabulate`` packages, saving a great amount of code to write otherwise
oneself.

System Requirements (Linux)
...........................

As a Linux user pointed out: if you are on Linux you might have to install
the following packages manually:

.. code-block:: console

    sudo apt-get install libxml2-dev libxslt1-dev

And if you run into an ``/usr/bin/ld: cannot find -lz`` error consider 
installing this one before running ``pip``, too:

.. code-block:: console

    sudo apt-get install lib32z1-dev


Implementation
--------------

Since VBB/BVG have no API for real time data access this data is fetched 
(scraped using Pandas_, yes!) from a web application on http://mobil.bvg.de.
You can use this page for `testing manually`_ (in English).
There, as a real person, you can enter parts of the destination name and get
a list of matching destinations to chose from, before you get to see the one
result table you are interested in.

.. _testing manually:
    http://mobil.bvg.de/Fahrinfo/bin/stboard.bin/eox?&boardType=depRT

To avoid multi-level scraping, speed things up, and add some more thrills, 
a small part of an existing "Open Data" `VBB database`_, published under the 
`CC-BY 3.0 license <http://creativecommons.org/licenses/by/3.0/de/>`_ 
is used to access the stop names and IDs of the VBB/BVG public transport 
network (a simple CSV file named here ``vbbvg_stops.csv``).

.. _VBB database: http://daten.berlin.de/kategorie/verkehr

The resulting tables are output as "real" tables in various formats on
the command-line, see usage examples below.


Usage
-----

Command-Line
............

You can run a few sample command-line calls using the options ``--test`` 
and ``--stop <NAME_ID>`` for a given stop name or ID like this for the 
stop *Möckernbrücke*:

.. code-block:: console

    $ vbbvg --test --stop Möckernbrücke


Programmatic
............

The main function to use programmatically is ``vbbvg.get_next_departures()``,
which returns a Pandas_ ``DataFrame`` object, which you can convert to almost
anything you like. See the following examples:

Get departures of S7 and S75 from Berlin main station:

.. code-block:: python

    In [1]: import vbbvg
    
    In [2]: df = vbbvg.get_next_departures('9003201', filter_line='S7')
    
    In [3]: df.columns
    Out[3]: Index([u'Wait', u'Departure', u'Line', u'Destination'], dtype='object')

    In [4]: list(df.to_records())
    Out[4]: 
    [(1, '00:00', u'10:01', u'S75 (Gl. 16)', u'S Westkreuz (Berlin)'),
     (4, '01:10', u'10:03', u'S75 (Gl. 15)', u'S Wartenberg (Berlin)'),
     (14, '04:10', u'10:06', u'S7 (Gl. 16)', u'S Potsdam Hauptbahnhof'),
     (24, '07:10', u'10:09', u'S7 (Gl. 15)', u'S Ahrensfelde Bhf (Berlin)'),
     (62, '21:10', u'10:23', u'S75 (Gl. 15)', u'S Ostbahnhof (Berlin)')]
    
    In [5]: print(df.to_csv())
    ,Wait,Departure,Line,Destination
    1,00:00,10:01,S75 (Gl. 16),S Westkreuz (Berlin)
    4,01:10,10:03,S75 (Gl. 15),S Wartenberg (Berlin)
    14,04:10,10:06,S7 (Gl. 16),S Potsdam Hauptbahnhof
    24,07:10,10:09,S7 (Gl. 15),S Ahrensfelde Bhf (Berlin)
    62,21:10,10:23,S75 (Gl. 15),S Ostbahnhof (Berlin)
    

Dashboards
..........

When using this tool inside some kind of web-based dashboard like those 
created by Dashing_ (which was the originally intended use-case) 
one should use a stop's ID to be sure to provide a unique stop on the 
VBB/BVG public transport network. You can find out the IDs by running 
test queries with the ``--header`` option.


Todo
----

- mention http://fahrinfo.vbb.de/bin/stboard.exe/en? (provides some more 
  filtering features)
- add more examples in the Usage section above
- make the code *polyglot*, running not only on Python 2.7 but also 3.4/3.5
- test option to filter specific line types like S-Bahn ('S.*') or single 
  lines ('U7')
- use in some real dashboard like those of dhasing.io (the original purpose!)
- mention that case is ignored in the whole tool for all stop names
- store the last displayed stop (in ~/.vvbvg or so) and reuse when called
  without any args/options
- remove index numbers (leftmost column) from result tables when used
  programmatically

Due to time limitations any help is welcome with any of the items above.

bulma.py
========

.. image:: https://img.shields.io/pypi/l/bulma.py.svg
    :target: https://opensource.org/licenses/MIT
    :alt: Project License

.. image:: https://img.shields.io/pypi/v/bulma.py.svg
    :target: https://pypi.python.org/pypi/bulma.py
    :alt: Library Version

.. image:: https://img.shields.io/pypi/pyversions/bulma.py.svg
    :target: https://pypi.python.org/pypi/bulma.py
    :alt: Required Python Versions

.. image:: https://img.shields.io/pypi/status/bulma.py.svg
    :target: https://github.com/nekitdev/bulma.py
    :alt: Development Status

.. image:: https://img.shields.io/pypi/dw/bulma.py.svg
    :target: https://pypi.python.org/pypi/bulma.py
    :alt: Library Downloads / Week

.. image:: https://app.codacy.com/project/badge/Grade/bc4c4a28974e4eaca0a1930692f64153
    :target: https://app.codacy.com/gh/nekitdev/bulma.py/dashboard
    :alt: Code Quality

bulma.py is a library that provides small and nifty compiler for the Bulma framework and its extensions.

Installing
----------

**Python 3.6 or higher is required**

To install the library, you can just run the following command:

.. code:: sh

    # Linux/OS X
    python3 -m pip install --upgrade bulma.py

    # Windows
    py -3 -m pip install --upgrade bulma.py

Development Version
-------------------

You can install latest development version from GitHub:

.. code:: sh

    $ git clone https://github.com/nekitdev/bulma.py.git
    $ cd bulma.py
    $ python -m pip install --upgrade .

Quick example
-------------

Below is an example of compiling the default theme with all extensions.

.. code:: python

    from bulma import EXPANDED, FIND, Compiler

    folder = "."  # current directory

    compiler = Compiler(
        extensions=FIND,  # find all extensions
        output_style=EXPANDED,  # expand the output
    )

    include = compiler.save(folder)  # compile and save to the folder

    print(f"saved to {include.find_theme_relative()}")

Authors
-------

This project is mainly developed by `nekitdev <https://github.com/nekitdev>`_.

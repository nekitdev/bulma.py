bulma.py
========

.. image:: https://img.shields.io/pypi/l/bulma.py.svg
    :target: https://opensource.org/licenses/MIT
    :alt: Project License

.. image:: https://img.shields.io/pypi/v/bulma.py.svg
    :target: https://pypi.python.org/pypi/bulma.py
    :alt: PyPI Library Version

.. image:: https://img.shields.io/pypi/pyversions/bulma.py.svg
    :target: https://pypi.python.org/pypi/bulma.py
    :alt: Required Python Versions

.. image:: https://img.shields.io/pypi/status/bulma.py.svg
    :target: https://github.com/nekitdev/bulma.py/tree/master/bulma
    :alt: Project Development Status

.. image:: https://img.shields.io/pypi/dw/bulma.py.svg
    :target: https://pypi.python.org/pypi/bulma.py
    :alt: Library Downloads/Week

.. image:: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.herokuapp.com%2Fnekit%2Fpledges
    :target: https://patreon.com/nekit
    :alt: Patreon Page [Support]

bulma.py is a library that provides small and nifty compiler for the Bulma framework and its extensions.

Installing
----------

**Python 3.6 or higher is required**

To install the library, you can just run the following command:

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U bulma.py

    # Windows
    py -3 -m pip install -U bulma.py

Development Version
-------------------

You can install latest development version from GitHub:

.. code:: sh

    $ git clone https://github.com/nekitdev/bulma.py.git
    $ cd bulma.py
    $ python3 -m pip install -U .

Quick example
-------------

Below is an example of compiling the default theme with all extensions.

.. code:: python

    from bulma import EXPANDED, FIND, Compiler

    folder = "."

    compiler = Compiler(
        extensions=FIND, output_style=EXPANDED
    )

    include = compiler.save(folder)

    print(f"saved to {include.find_theme_relative()}")

Authors
-------

This project is mainly developed by `nekitdev <https://github.com/nekitdev>`_.

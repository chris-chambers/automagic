AUTOMAGIC!
==========

Setup
-----

0. Install the `VS Code Extension <https://marketplace.visualstudio.com/items?itemName=python-lyre.lyre>`_
1. Install `Poetry <https://python-poetry.org/docs/#installation>`_
2. Install fswatch native library

   .. code-block:: bash

       brew install fswatch

3. Install this package

   .. code-block:: bash

       poetry install


Use
---

After setup, run the package:

.. code-block:: bash

    poetry shell
    automagic


The VS Code extension should automatically connect, and allow you to evaluate
the current selection (or line if there is no selection) in a Python file with
:code:`ctrl+enter`.

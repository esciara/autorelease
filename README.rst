Autorelease
===========

Installation instructions to contribute
---------------------------------------

``poetry`` must be installed on your system. See
https://poetry.eustace.io/docs/#installation for detailed instructions.

To setup the project on your machine, run the following at your project's level::


    $ poetry install

Then you can enter the virtual environment created by ``poetry`` by typing::

    $ poetry shell

Functional tests can be run by typing::

    poetry_shell$ tox -e bdd


.. note::

    You need to configure an access to a ``gitlab`` instance - either your private server
    or at http://gitlab.com - both for the remote ``git`` repo access and the ``gitlab`` api
    access.

    Please read ``gitlab-access-setup.txt`` in the project root directory for more info.

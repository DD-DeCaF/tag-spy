==============
Docker Tag Spy
==============

.. image:: https://img.shields.io/pypi/v/tag-spy.svg
   :target: https://pypi.org/project/tag-spy/
   :alt: Current PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/tag-spy.svg
   :target: https://pypi.org/project/tag-spy/
   :alt: Supported Python Versions

.. image:: https://img.shields.io/pypi/l/tag-spy.svg
   :target: https://www.apache.org/licenses/LICENSE-2.0
   :alt: Apache Software License Version 2.0

.. image:: https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg
   :target: https://github.com/dd-decaf/tag-spy/blob/master/.github/CODE_OF_CONDUCT.md
   :alt: Code of Conduct

.. image:: https://img.shields.io/travis/dd-decaf/tag-spy/master.svg?label=Travis%20CI
   :target: https://travis-ci.org/dd-decaf/tag-spy
   :alt: Travis CI

.. image:: https://codecov.io/gh/dd-decaf/tag-spy/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/dd-decaf/tag-spy
   :alt: Codecov

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Black

.. image:: https://readthedocs.org/projects/tag-spy/badge/?version=latest
   :target: https://tag-spy.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. summary-start

Identify the latest DD-DeCaF tag on a particular Docker image.

The package was designed to only depend on the standard library in order to not have
any fast moving dependencies. It depends on Python 3.7+ for ``fromisoformat`` date
parsing.

Usage
=====

The main purpose of this package is to provide a command line interface (CLI) for
retrieving the latest of all of a Docker image's tags. The DD-DeCaF organization uses a
particular tag format in order to manage dependencies between Docker images. Take 
``dddecaf/wsgi-base:alpine_2020-04-28_24fe0a0`` as an example, it consists of the base
tag ``alpine``, the date when it was built, and the short hash of the git commit from
which the image was generated. The corresponding "latest" image is
``dddecaf/wsgi-base:alpine``, however, child images should depend on the explicit tag.
In order to manage this more easily, this package provides a script for retrieving the
correct information. Sometimes, multiple images exist for the same date which is why
the label for the exact build timestamp is required. The following command

.. code-block:: console

    tag-spy dddecaf/wsgi-base alpine dk.dtu.biosustain.wsgi-base.alpine.build.timestamp

may result in something like

.. code-block:: console

    alpine_2020-04-28_24fe0a0

For more information, also check out the help.

.. code-block:: console

    tag-spy --help

Install
=======

It's as simple as:

.. code-block:: console

    pip install tag-spy

Copyright
=========

* Copyright © 2020, DD-DeCaF.
* Free software distributed under the `Apache Software License 2.0
  <https://www.apache.org/licenses/LICENSE-2.0>`_.

.. summary-end

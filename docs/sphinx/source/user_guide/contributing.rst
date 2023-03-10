.. _contributing:

Contributing
============

.. note::
        This contributing document is heavily based on pvlib-python 
        contribution guidelines. This is still a work in progress 

Encouraging more people to help develop bifacial_radiance is essential to our
success. Therefore, we want to make it easy and rewarding for you to
contribute.

There is a lot of material in this section, aimed at a variety of
contributors from novice to expert. Don't worry if you don't (yet)
understand parts of it.


Easy ways to contribute
~~~~~~~~~~~~~~~~~~~~~~~

Here are a few ideas for how you can contribute, even if you are new to
bifacial_radiance, git, or Python:

* Ask and answer `bifacial_radiance questions on StackOverflow <http://stackoverflow.com/questions/tagged/bifacial_radiance>`_
  and participate in discussions in the `bifacial_radiance google group <https://groups.google.com/forum/#!forum/bifacial_radiance>`_.
* Make `GitHub issues <https://github.com/NREL/bifacial_radiance/issues>`_
  and contribute to the conversations about how to resolve them.
* Read issues and pull requests that other people created and
  contribute to the conversation about how to resolve them.
* Improve the documentation and the unit tests.
* Improve the IPython/Jupyter Notebook tutorials or write new ones that
  demonstrate how to use bifacial_radiance in your area of expertise.
* Tell your friends and colleagues about bifacial_radiance
* Add your project to our
  `Projects and publications that use bifacial_radiance wiki
  <https://github.com/NREL/bifacial_radiance/wiki>`_.


How to contribute new code
~~~~~~~~~~~~~~~~~~~~~~~~~~

The basics
----------

Contributors to bifacial_radiance use GitHub's pull requests to add/modify
its source code. The GitHub pull request process can be intimidating for
new users, but you'll find that it becomes straightforward once you use
it a few times. Please let us know if you get stuck at any point in the
process. Here's an outline of the process:

#. Create a GitHub issue and get initial feedback from users and
   maintainers. If the issue is a bug report, please include the
   code needed to reproduce the problem.
#. Obtain the latest version of bifacial_radiance: Fork the bifacail_radiance
   project to your GitHub account, ``git clone`` your fork to your computer.
#. Make some or all of your changes/additions and ``git commit`` them to
   your local repository.
#. Share your changes with us via a pull request: ``git push`` your
   local changes to your GitHub fork, then go to GitHub make a pull
   request.

The Pandas project maintains an excellent `contributing page
<http://pandas.pydata.org/pandas-docs/stable/contributing.html>`_ that goes
into detail on each of these steps. Also see GitHub's `Set Up Git
<https://help.github.com/articles/set-up-git/>`_ and `Using Pull
Requests <https://help.github.com/articles/using-pull-requests/>`_.

We strongly recommend using virtual environments for development.
Virtual environments make it trivial to switch between different
versions of software. This `astropy guide
<http://astropy.readthedocs.org/en/latest/development/workflow/
virtual_pythons.html>`_ is a good reference for virtual environments. If
this is your first pull request, don't worry about using a virtual
environment.

You must include documentation and unit tests for any new or improved
code. We can provide help and advice on this after you start the pull
request. See the Testing section below.


.. _pull-request-scope:

Pull request scope
------------------

This section can be summed up as "less is more".

A pull request can quickly become unmanageable if too many lines are
added or changed. "Too many" is hard to define, but as a rule of thumb,
we encourage contributions that contain less than 50 lines of primary code.
50 lines of primary code will typically need at least 250 lines
of documentation and testing. This is about the limit of what the
maintainers can review on a regular basis.

A pull request can also quickly become unmanageable if it proposes
changes to the API in order to implement another feature. Consider
clearly and concisely documenting all proposed API changes before
implementing any code. 

Questions about related issues frequently come up in the process of
addressing implementing code for a pull request. Please try to avoid
expanding the scope of your pull request (this also applies to
reviewers!). We'd rather see small, well-documented additions to the
project's technical debt than see a pull request languish because its
scope expanded beyond what the reviewer community is capable of
processing.

Of course, sometimes it is necessary to make a large pull request. We
only ask that you take a few minutes to consider how to break it into
smaller chunks before proceeding.

bifacial_radiance contains 3 layers of code:
functions, analysis, and ModelChain. We recommend that
contributors focus their work on only one or two of those layers in a
single pull request. 


When should I submit a pull request?
------------------------------------

The short answer: anytime.

The long answer: it depends. If in doubt, go ahead and submit. You do
not need to make all of your changes before creating a pull request.
Your pull requests will automatically be updated when you commit new
changes and push them to GitHub.

There are pros and cons to submitting incomplete pull-requests. On the
plus side, it gives everybody an easy way to comment on the code and can
make the process more efficient. On the minus side, it's easy for an
incomplete pull request to grow into a multi-month saga that leaves
everyone unhappy. If you submit an incomplete pull request, please be
very clear about what you would like feedback on and what we should
ignore. Alternatives to incomplete pull requests include creating a
`gist <https://gist.github.com>`_ or experimental branch and linking to
it in the corresponding issue.

The best way to ensure that a pull request will be reviewed and merged in
a timely manner is to:

#. Start by creating an issue. The issue should be well-defined and
   actionable.
#. Ask the maintainers to tag the issue with the appropriate milestone.
#. Tag bifacial_radiance community members or ``@bifacial_radiance/maintainer`` when the pull
   request is ready for review. (see :ref:`pull-request-reviews`)


.. _pull-request-reviews:

Pull request reviews
--------------------

The bifacial_radiance community and maintainers will review your pull request in a
timely fashion. Please "ping" ``@bifacial_radinace/maintainer`` if it seems that
your pull request has been forgotten at any point in the pull request
process.

Keep in mind that the PV modeling community is diverse and each bifacial_radiance
community member brings a different perspective when reviewing code.
Some reviewers bring years of expertise in the sub-field that your code
contributes to and will focus on the details of the algorithm. Other
reviewers will be more focused on integrating your code with the rest of
bifacial_radiance, ensuring that it is feasible to maintain, that it meets the
:ref:`code style <code-style>` guidelines, and that it is
:ref:`comprehensively tested <testing>`. Limiting the scope of the pull
request makes it much more likely that all of these reviews can be
conducted and any issues can be resolved in a timely fashion.

Sometimes it's hard for reviewers to be immediately available, so the
right amount of patience is to be expected. That said, interested
reviewers should do their best to not wait until the last minute to put
in their two cents.


.. _code-style:

Code style
~~~~~~~~~~

bifacial_radiance python generally follows the `PEP 8 -- Style Guide for Python Code
<https://www.python.org/dev/peps/pep-0008/>`_. Maximum line length for code
is 79 characters.

Code must be compatible with Python 3.5 and above.

bifacial_radiance uses a mix of full and abbreviated variable names. See
:ref:`variables_style_rules`. We could be better about consistency.
Prefer full names for new contributions. This is especially important
for the API. Abbreviations can be used within a function to improve the
readability of formulae.

Set your editor to strip extra whitespace from line endings. This
prevents the git commit history from becoming cluttered with whitespace
changes.

Please see :ref:`Documentation` for information specific to documentation
style.

Remove any ``logging`` calls and ``print`` statements that you added
during development. ``warning`` is ok.

We typically use GitHub's
"`squash and merge <https://help.github.com/articles/about-pull-request-merges/#squash-and-merge-your-pull-request-commits>`_"
feature to merge your pull request into bifacial_radiance. GitHub will condense the
commit history of your branch into a single commit when merging into
bifacial_radiance/master (the commit history on your branch remains
unchanged). Therefore, you are free to make commits that are as big or
small as you'd like while developing your pull request.


.. _documentation:

Documentation
~~~~~~~~~~~~~

Documentation must be written in
`numpydoc format <https://numpydoc.readthedocs.io/>`_ format which is rendered
using the `Sphinx Napoleon extension
<https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_.

The numpydoc format includes a specification for the allowable input
types. Python's `duck typing <https://en.wikipedia.org/wiki/Duck_typing>`_
allows for multiple input types to work for many parameters. bifacial_radiance uses
the following generic descriptors as short-hand to indicate which
specific types may be used:

* dict-like : dict, OrderedDict, pd.Series
* numeric : scalar, np.array, pd.Series. Typically int or float dtype.
* array-like : np.array, pd.Series. Typically int or float dtype.

Parameters that specify a specific type require that specific input type.

Read the Docs will automatically build the documentation for each pull
request. Please confirm the documentation renders correctly by following
the ``continuous-documentation/read-the-docs`` link within the checks
status box at the bottom of the pull request.

To build the docs locally, install the ``doc`` dependencies specified in the
`setup.py <https://github.com/NREL/bifacial_radiance/blob/master/setup.py>`_
file. See :ref:`installation` instructions for more information.

.. _testing:

Testing
~~~~~~~

Developers **must** include comprehensive tests for any additions or
modifications to bifacial_radiance. New unit test code should be placed in the corresponding test module in the bifacial_radiance/test directory.

A pull request will automatically run the tests for you on Linux platform and python versions 2.7 and 3.6. However, it is typically more efficient to run and debug the tests in your own local
environment.

To run the tests locally, install the ``test`` dependencies specified in the
`setup.py <https://github.com/NREL/bifacial_radiance/blob/master/setup.py>`_
file. See :ref:`installation` instructions for more information.i

bifacial_radiance's unit tests can easily be run by executing ``pytest`` on the
bifacial_radiance directory:

``pytest bifacial_radiance``

or, for a single module:

``pytest bifacial_radiance/test/modelchain.py``

or, for a single test:

``pytest bifacial_radiance/test/modelchain.py::runModelChain``

We suggest using pytest's ``--pdb`` flag to debug test failures rather
than using ``print`` or ``logging`` calls. For example:

``pytest bifacial_radiance/test/modelchain.py --pdb``

will drop you into the
`pdb debugger <https://docs.python.org/3/library/pdb.html>`_ at the
location of a test failure. As described in :ref:`code-style`, bifacial_radiance
code does not use ``print`` or ``logging`` calls, and this also applies
to the test suite (with rare exceptions).

This documentation
~~~~~~~~~~~~~~~~~~

If this documentation is unclear, help us improve it! Consider looking
at the `pandas
documentation <http://pandas.pydata.org/pandas-docs/stable/
contributing.html>`_ for inspiration.

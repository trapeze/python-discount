discount
========

This Python package is a ctypes binding of `David Loren`_'s
`Discount`_, a C implementation of `John Gruber`_'s `Markdown`_.

.. contents::


Introduction
------------

Markdown is a text-to-HTML conversion tool for web writers. Markdown
allows you to write using an easy-to-read, easy-to-write plain text
format, then convert it to structurally valid XHTML (or HTML).

The ``discount`` Python module contains two things of interest:

* ``libmarkdown``, a submodule that provides access to the public C
  functions defined by Discount.

* ``Markdown``, a helper class built on top of ``libmarkdown``,
  providing a more familiar Pythonic interface

.. _`David Loren`: http://www.pell.portland.or.us/~orc
.. _`Discount`:    http://www.pell.portland.or.us/~orc/Code/discount/
.. _`John Gruber`: http://daringfireball.net/
.. _`Markdown`:    http://daringfireball.net/projects/markdown


Using the ``Markdown`` class
----------------------------

The ``Markdown`` class wraps the c functions exposed in the
``libmarkdown`` submodule and handles the ctypes leg work for you.  If
you want to use the Discount functions directly, skip to the next
section about ``libmarkdown``.

Let's take a look at a simple example::

    import sys
    import discount

    mkd = discount.Markdown(sys.stdin)
    mkd.write_html_content(sys.stdout)

``Markdown`` takes one required argument, ``input_file_or_string``,
the markdown formatted data.  If this argument is a file-like object,
the file must be a real OS file descriptor, i.e. ``sys.stdin`` yes, a
``StringIO`` object, no.  The argument is otherwise assumed to be a
string-like object.  The same is true for ``Markdown`` methods that
write HTML output to files.

Otherwise, the data is assumed to be string-like.  ``Markdown`` also
has methods for getting the output as a string, instead of writing to
a file-like object.  Let's look at a modified version of the first
example, this time using strings::

    import discout

    mkd = discount.Markdown('`test`')
    print mkd.get_html_content()

The ``Markdown`` class constructor also takes optional boolean keyword
arguments.

  ``toc``
    Generate table-of-contents headers (each generated <h1>, <h2>,
    etc will include a id="name" argument.)  Use ``get_html_toc()``
    or ``write_html_toc()`` to generate the table-of-contents
    itself.

  ``strict``
    Disable relaxed emphasis and superscripts.

  ``autolink``
    Greedily expand links; if a url is encountered, convert it to a
    hyperlink even if it isn't surrounded with ``<>s``.

  ``safelink``
    Be paranoid about how ``[][]`` is expanded into a link - if the
    url isn't a local reference, ``http://``, ``https://``,
    ``ftp://``, or ``news://``, it will not be converted into a
    hyperlink.

  ``ignore_header``
    Do not process the `pandoc document header`_, but treat it like
    regular text.
  
  ``ignore_links``
    Do not allow ``<a`` or expand ``[][]`` into a link.

  ``ignore_images``
    Do not allow ``<img`` or expand ``![][]`` into a image.

  ``ignore_tables``
    Don't process `PHP Markdown Extra`_ tables.

  ``ignore_smartypants``
    Disable `SmartyPants`_ processing.

  ``ignore_embedded_html``
    Disable all embedded HTML by replacing all ``<``'s with
    ``&lt;``.

  ``ignore_pseudo_protocols``
    Do not process `pseudo-protocols`_.

Pandoc header elements can be retrieved with the methods
``get_pandoc_title()``, ``get_pandoc_author()`` and
``get_pandoc_date()``.

The converted HTML document parts can be retrieved as a string
with the ``get_html_css()``, ``get_html_toc()`` and
``get_html_content()`` methods, or written to a file with the
``write_html_css(fp)``, ``write_html_toc(fp)`` and
``write_html_content(fp)`` methods, where ``fp`` is the output file
descriptor.

Under some conditions, the functions in ``libmarkdown`` may return
integer error codes.  These errors are raised as a ``MarkdownError``
exceptions when using the ``Markdown`` class.

.. _`pandoc document header`:
     http://johnmacfarlane.net/pandoc/README.html#title-blocks
.. _`PHP Markdown Extra`:
     http://michelf.com/projects/php-markdown/extra/.
.. _`SmartyPants`:
     http://daringfireball.net/projects/smartypants/
.. _`pseudo-protocols`:
     http://www.pell.portland.or.us/~orc/Code/discount/#pseudo


Using ``libmarkdown``
---------------------

If you are familiar with using the C library and would rather use
Discount's functionality directly, ``libmarkdown`` is what you are
looking for; its simply a thin wrapper around the original C
implementation.  ``libmarkdown`` exposes the public functions and
flags documented on the `Discount homepage`_.

In Python you'll need to do some extra work preparing Python objects
you want to pass to ``libmarkdown``'s functions.

Most of these functions accept ``FILE*`` and ``char**`` types as their
arguments, which require some additional ctypes boilerplate.

To get a ``FILE*`` from a Python file descriptor for use with
``libmarkdown``, use the following pattern::

    i = ctypes.pythonapi.PyFile_AsFile(sys.stdin)
    o = ctypes.pythonapi.PyFile_AsFile(sys.stdout)
    doc = libmarkdown.mkd_in(i)
    libmarkdown.markdown(doc, o)

For ``libmarkdown`` functions to which you pass a ``char**``, use the
following pattern::

    cp = ctypes.c_char_p('')
    ln = libmarkdown.mkd_document(doc, ctypes.byref(cp))
    html_text = cp.value[:ln]

It is important to initialize ``c_char_p`` with an empty string.

.. _`Discount homepage`:
   http://www.pell.portland.or.us/~orc/Code/discount/


Running the test suite
----------------------

Tests are available with the source distibution of ``discount`` in the
``tests.py`` file.  The C shared object should be compiled first::

    python setup.py build_ext

Then you can run the tests::

    python tests.py


Source code and reporting bugs
------------------------------

You can obtain the source code and report bugs on
`GitHub project page`_.

.. _`GitHub project page`:
   http://github.com/trapeze/python-discount/issues


License
-------

See the ``LICENSE`` file in the source distribution for details.


Credits
-------

discount is maintained by [Tamas Kemenczy](tkemenczy@trapeze.com), and
is funded by [Trapeze](http://trapeze.com).  See the ``AUTHORS`` file
for details.

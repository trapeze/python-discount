"""
A Python interface for Discount, the C Markdown parser

This module contains `libmarkdown`, a ctypes binding for Discount,
as well as `Markdown`, a helper class built on top of this library.

Visit the Discount homepage:
http://www.pell.portland.or.us/~orc/Code/discount/

Basic usage examples:

    >>> md = Markdown('`test`')
    >>> md.get_html_content()
    '<p><code>test</code></p>'

    >>> md = Markdown(sys.stdin, autolink=True)
    >>> md.write_html_content(sys.stdout)

See the `Markdown` docstrings for all keyword arguments, or the
docstrings for `libmarkdown` if you want to use the C functions
directly.
"""

import ctypes

import libmarkdown


_KWARGS_TO_LIBMARKDOWN_FLAGS = {
    'toc': libmarkdown.MKD_TOC,
    'strict': libmarkdown.MKD_STRICT,
    'autolink': libmarkdown.MKD_AUTOLINK,
    'safelink': libmarkdown.MKD_SAFELINK,
    'ignore_header': libmarkdown.MKD_NOHEADER,
    'ignore_links': libmarkdown.MKD_NOLINKS,
    'ignore_images': libmarkdown.MKD_NOIMAGE,
    'ignore_tables': libmarkdown.MKD_NOTABLES,
    'ignore_smartypants': libmarkdown.MKD_NOPANTS,
    'ignore_embedded_html': libmarkdown.MKD_NOHTML,
    'ignore_pseudo_protocols': libmarkdown.MKD_NO_EXT,
}


class MarkdownError(Exception):
    """
    Exception raised when a discount c function
    returns an error code, `-1`.
    """
    def __str__(self):
        return '%s failure' % self.args[0]


class Markdown(object):
    """
    Markdown to HTML conversion.

    A single argument is required, `input_file_or_string`, the
    Markdown formatted data.  If this argument is a file-like object,
    the file must be a real OS file descriptor, i.e. `sys.stdin` yes,
    a `StringIO` object, no.  The argument is otherwise assumed to be
    a string-like object.  The same is true for `Markdown` methods
    that write HTML output to files.

    Additional boolean keyword arguments are also accepted:

    * `toc`:
         Generate table-of-contents headers (each generated <h1>,
         <h2>, etc will include a id="name" argument.)  Use
         `get_html_toc()` or `write_html_toc()` to generate the
         table-of-contents itself.

    * `strict`:
         Disable relaxed emphasis and superscripts.

    * `autolink`:
         Greedily expand links; if a url is encountered, convert it to
         a hyperlink even if it isn't surrounded with `<>s`.

    * `safelink`:
         Be paranoid about how `[][]` is expanded into a link - if the
         url isn't a local reference, `http://`, `https://`, `ftp://`,
         or `news://`, it will not be converted into a hyperlink.

    * `ignore_header`:
         Do not process the document header, but treat it like regular
         text.  See http://johnmacfarlane.net/pandoc/README.html#title-blocks

    * `ignore_links`:
         Do not allow `<a` or expand `[][]` into a link.

    * `ignore_images`:
         Do not allow `<img` or expand `![][]` into a image.

    * `ignore_tables`:
         Don't process PHP Markdown Extra tables.  See
         http://michelf.com/projects/php-markdown/extra/.

    * `ignore_smartypants`:
         Disable SmartyPants processing.  See
         http://daringfireball.net/projects/smartypants/.

    * `ignore_embedded_html`:
         Disable all embedded HTML by replacing all `<`'s with `&lt;`.

    * `ignore_pseudo_protocols`:
         Do not process pseudo-protocols.  See
         http://www.pell.portland.or.us/~orc/Code/discount/#pseudo

    Pandoc header elements can be retrieved with the methods
    `get_pandoc_title()`, `get_pandoc_author()` and
    `get_pandoc_date()`.

    The converted HTML document parts can be retrieved as a string
    with the `get_html_css()`, `get_html_toc()` and
    `get_html_content()` methods, or written to a file with the
    `write_html_css(fp)`, `write_html_toc(fp)` and
    `write_html_content(fp)` methods, where `fp` is the output file
    descriptor.
    """
    def __init__(self, input_file_or_string, **kwargs):
        self.input = input_file_or_string

        # Convert a `kwargs` dict to a bitmask of libmarkdown flags.
        # All but one flag is exposed; MKD_1_COMPAT, which, according
        # to the original documentation, is not really useful other
        # than running MarkdownTest_1.0
        flags = 0
        for key in kwargs:
            flags |= _KWARGS_TO_LIBMARKDOWN_FLAGS.get(key, 0)
        self.flags = flags

    def __del__(self):
        try:
            libmarkdown.mkd_cleanup(self._doc)
        except AttributeError:
            pass

    def _get_compiled_doc(self):
        try:
            self._doc
        except AttributeError:
            if hasattr(self.input, 'read'):
                # If the input is file-like
                input_ = ctypes.pythonapi.PyFile_AsFile(self.input)
                self._doc = libmarkdown.mkd_in(input_, self.flags)
            else:
                # Otherwise, treat it as a string
                input_ = ctypes.c_char_p(self.input)
                self._doc = libmarkdown.mkd_string(
                    input_, len(self.input), self.flags)

            ret = libmarkdown.mkd_compile(self._doc, self.flags)
            if ret == -1:
                raise MarkdownError('mkd_compile')

        finally:
            return self._doc

    def _generate_html_content(self, fp=None):
        if fp is not None:
            fp_ = ctypes.pythonapi.PyFile_AsFile(fp)
            ret = libmarkdown.mkd_generatehtml(self._get_compiled_doc(), fp_)
            if ret == -1:
                raise MarkdownError('mkd_generatehtml')
        else:
            sb = ctypes.c_char_p('')
            ln = libmarkdown.mkd_document(self._get_compiled_doc(), ctypes.byref(sb))
            if ln == -1:
                raise MarkdownError('mkd_document')
            else:
                return sb.value[:ln]

    def _generate_html_toc(self, fp=None):
        self.flags |= libmarkdown.MKD_TOC

        if fp is not None:
            fp_ = ctypes.pythonapi.PyFile_AsFile(fp)
            ret = libmarkdown.mkd_generatetoc(self._get_compiled_doc(), fp_)
            if ret == -1:
                raise MarkdownError('mkd_generatetoc')
        else:
            sb = ctypes.c_char_p('')
            ln = libmarkdown.mkd_toc(self._get_compiled_doc(), ctypes.byref(sb))
            if ln == -1:
                raise MarkdownError('mkd_toc')
            else:
                return sb.value[:ln]

    def _generate_html_css(self, fp=None):
        if fp is not None:
            fp_ = ctypes.pythonapi.PyFile_AsFile(fp)
            ret = libmarkdown.mkd_generatecss(self._get_compiled_doc(), fp_)

            # Returns -1 even on success
            # if ret == -1:
            #     raise MarkdownError('mkd_generatecss')
        else:
            sb = ctypes.c_char_p('')
            ln = libmarkdown.mkd_css(self._get_compiled_doc(), ctypes.byref(sb))

            if ln == -1:
                raise MarkdownError('mkd_css')
            else:
                return sb.value[:ln]

    def get_pandoc_title(self):
        """
        Get the document title from the pandoc header.
        """
        return libmarkdown.mkd_doc_title(self._get_compiled_doc())

    def get_pandoc_author(self):
        """
        Get the document author(s) from the pandoc header.
        """
        return libmarkdown.mkd_doc_author(self._get_compiled_doc())

    def get_pandoc_date(self):
        """
        Get the document date from the pandoc header.
        """
        return libmarkdown.mkd_doc_date(self._get_compiled_doc())

    def get_html_content(self):
        """
        Get the document content as HTML.
        """
        return self._generate_html_content()

    def get_html_toc(self):
        """
        Get the document's table of contents as HTML.
        """
        return self._generate_html_toc()

    def get_html_css(self):
        """
        Get any style blocks in the document as HTML.
        """
        return self._generate_html_css()

    def write_html_content(self, fp):
        """
        Write the document content to the file, `fp`.
        """
        self._generate_html_content(fp)

    def write_html_toc(self, fp):
        """
        Write the document's table of contents to the file, `fp`.
        """
        self._generate_html_toc(fp)

    def write_html_css(self, fp):
        """
        Write any style blocks in the document to the file, `fp`.
        """
        self._generate_html_css(fp)

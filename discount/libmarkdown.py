"""
Python bindings for Discount

The `libmarkdown` public functions accept `FILE*` and `char**` types
as their arguments, which require some additional ctypes boilerplate.

To obtain a `FILE*` from a Python file descriptor for use with
`libmarkdown`, use the following pattern:

    i = ctypes.pythonapi.PyFile_AsFile(sys.stdin)
    o = ctypes.pythonapi.PyFile_AsFile(sys.stdout)
    doc = libmarkdown.mkd_in(i)
    libmarkdown.markdown(doc, o)

For `libmarkdown` functions to which you pass a `char**`, use the
following pattern:

    cp = ctypes.c_char_p('')
    ln = libmarkdown.mkd_document(doc, ctypes.byref(cp))
    html_text = cp.value[:ln]

It is important to initialize `c_char_p` with an empty string.
"""

import ctypes
import os


MKD_NOLINKS = 0x0001
MKD_NOIMAGE = 0x0002
MKD_NOPANTS = 0x0004
MKD_NOHTML = 0x0008
MKD_STRICT = 0x0010
MKD_NO_EXT = 0x0040
MKD_NOHEADER = 0x0100
MKD_TABSTOP = 0x0200
MKD_NOTABLES = 0x0400
MKD_TOC = 0x1000
MKD_1_COMPAT = 0x2000
MKD_AUTOLINK =  0x4000
MKD_SAFELINK = 0x8000


_so = ctypes.CDLL(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '_discount.so'
    )
)


markdown_version = (ctypes.c_char * 64).in_dll(_so, 'markdown_version').value


class FILE(ctypes.Structure):
    pass


ctypes.pythonapi.PyFile_AsFile.argtypes = (ctypes.py_object,)

ctypes.pythonapi.PyFile_AsFile.restype = ctypes.POINTER(FILE)


class Cstring(ctypes.Structure):
    _fields_ = [
        ('text', ctypes.c_char_p),
        ('size', ctypes.c_int),
        ('alloc', ctypes.c_int),
    ]


class Line(ctypes.Structure):
    pass

Line._fields_ = [
    ('text', Cstring),
    ('next', ctypes.POINTER(Line)),
    ('dle', ctypes.c_int)
]


class Line_ANCHOR(ctypes.Structure):
    _fields_ = [
        ('text', ctypes.POINTER(Line)),
        ('end', ctypes.POINTER(Line)),
    ]


class Paragraph(ctypes.Structure):
    pass

Paragraph._fields_ = [
    ('next', ctypes.POINTER(Paragraph)),
    ('down', ctypes.POINTER(Paragraph)),
    ('text', ctypes.POINTER(Line)),
    ('ident', ctypes.c_char_p),
    ('typ', ctypes.c_int),
    ('align', ctypes.c_int),
    ('hnumber', ctypes.c_int),
]


class Block(ctypes.Structure):
    _fields_ = [
        ('b_type', ctypes.c_int),
        ('b_count', ctypes.c_int),
        ('b_char', ctypes.c_char),
        ('b_text', Cstring),
        ('b_post', Cstring),
    ]


class Qblock(ctypes.Structure):
    _fields_ = [
        ('text', ctypes.POINTER(Block)),
        ('size', ctypes.c_int),
        ('alloc', ctypes.c_int),
    ]


class Footnote(ctypes.Structure):
    _fields_ = [
        ('tag', Cstring),
        ('link', Cstring),
        ('title', Cstring),
        ('height', ctypes.c_int),
        ('width', ctypes.c_int),
        ('dealloc', ctypes.c_int),
    ]


class Footnote_STRING(ctypes.Structure):
    _fields_ = [
        ('text', ctypes.POINTER(Footnote)),
        ('size', ctypes.c_int),
        ('alloc', ctypes.c_int),
    ]


class MMIOT(ctypes.Structure):
    _fields_ = [
        ('out', Cstring),
        ('in_', Cstring),
        ('Q', Qblock),
        ('isp', ctypes.c_int),
        ('footnotes', ctypes.POINTER(Footnote_STRING)),
        ('flags', ctypes.c_int),
        ('base', ctypes.c_char_p),
    ]


class Document(ctypes.Structure):
    _fields_ = [
        ('headers', ctypes.POINTER(Line)),
        ('content', Line_ANCHOR),
        ('code', ctypes.POINTER(Paragraph)),
        ('compiled', ctypes.c_int),
        ('html', ctypes.c_int),
        ('tabstop', ctypes.c_int),
        ('ctx', ctypes.POINTER(MMIOT)),
        ('base', ctypes.c_char_p),
    ]


mkd_in = _so.mkd_in
mkd_in.argtypes = (
    ctypes.POINTER(FILE),
    ctypes.c_int,
)
mkd_in.restype = ctypes.POINTER(Document)

mkd_string = _so.mkd_string
mkd_string.argtypes = (
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_int,
)
mkd_string.restype = ctypes.POINTER(Document)

markdown = _so.markdown
markdown.argtypes = (
    ctypes.POINTER(Document),
    ctypes.POINTER(FILE),
    ctypes.c_int,
)

mkd_line = _so.mkd_line
mkd_line.argtypes = (
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.c_int,
)

mkd_generateline = _so.mkd_generateline
mkd_generateline.argtypes = (
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.POINTER(FILE),
    ctypes.c_int,
)

mkd_compile = _so.mkd_compile
mkd_compile.argtypes = (
    ctypes.POINTER(Document),
    ctypes.c_int,
)

mkd_generatehtml = _so.mkd_generatehtml
mkd_generatehtml.argtypes = (
    ctypes.POINTER(Document),
    ctypes.POINTER(FILE),
)

mkd_document = _so.mkd_document
mkd_document.argtypes = (
    ctypes.POINTER(Document),
    ctypes.POINTER(ctypes.c_char_p),
)

mkd_css = _so.mkd_css
mkd_css.argtypes = (
    ctypes.POINTER(Document),
    ctypes.POINTER(ctypes.c_char_p),
)

mkd_generatecss = _so.mkd_generatecss
mkd_generatecss.argtypes = (
    ctypes.POINTER(Document),
    ctypes.POINTER(FILE),
)

mkd_toc = _so.mkd_toc
mkd_toc.argtypes = (
    ctypes.POINTER(Document),
    ctypes.POINTER(ctypes.c_char_p),
)

mkd_generatetoc = _so.mkd_generatetoc
mkd_generatetoc.argtypes = (
    ctypes.POINTER(Document),
    ctypes.POINTER(FILE),
)

mkd_dump = _so.mkd_dump
mkd_dump.argtypes = (
    ctypes.POINTER(Document),
    ctypes.POINTER(FILE),
    ctypes.c_int,
    ctypes.c_char_p,
)

mkd_cleanup = _so.mkd_cleanup
mkd_cleanup.argtypes = (ctypes.POINTER(Document),)

mkd_doc_title = _so.mkd_doc_title
mkd_doc_title.argtypes = (ctypes.POINTER(Document),)
mkd_doc_title.restype = ctypes.c_char_p

mkd_doc_author = _so.mkd_doc_author
mkd_doc_author.argtypes = (ctypes.POINTER(Document),)
mkd_doc_author.restype = ctypes.c_char_p

mkd_doc_date = _so.mkd_doc_date
mkd_doc_date.argtypes = (ctypes.POINTER(Document),)
mkd_doc_date.restype = ctypes.c_char_p

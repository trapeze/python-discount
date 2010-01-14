import ctypes
import tempfile
import unittest

from discount import Markdown, libmarkdown


class LibmarkdownTestCase(unittest.TestCase):
    def test_pythonapi(self):
        self.assertEqual(
            ctypes.pythonapi.PyFile_AsFile.argtypes,
            (ctypes.py_object,)
        )

        self.assertEqual(
            ctypes.pythonapi.PyFile_AsFile.restype,
            ctypes.POINTER(libmarkdown.FILE),
        )

    def test_mkd_in(self):
        self.assertEqual(
            libmarkdown.mkd_in.argtypes,
            (ctypes.POINTER(libmarkdown.FILE), ctypes.c_int),
        )

        self.assertEqual(
            libmarkdown.mkd_in.restype,
            ctypes.POINTER(libmarkdown.Document),
        )

        i = tempfile.TemporaryFile('r+w')
        i.write('`test`')
        i.seek(0)
        i_ = ctypes.pythonapi.PyFile_AsFile(i)
        libmarkdown.mkd_in(i_, 0)
        i.close()

    def test_mkd_string(self):
        self.assertEqual(
            libmarkdown.mkd_string.argtypes,
            (ctypes.c_char_p, ctypes.c_int, ctypes.c_int)
        )

        self.assertEqual(
            libmarkdown.mkd_string.restype,
            ctypes.POINTER(libmarkdown.Document)
        )

        text = '`test`'
        cp = ctypes.c_char_p(text)
        libmarkdown.mkd_string(cp, len(text), 0)

    def test_markdown(self):
        self.assertEqual(
            libmarkdown.markdown.argtypes,
            (ctypes.POINTER(libmarkdown.Document),
             ctypes.POINTER(libmarkdown.FILE),
             ctypes.c_int)
        )

        self.assertEqual(
            libmarkdown.markdown.restype,
            ctypes.c_int,
        )

        text = '`test`'
        cp = ctypes.c_char_p(text)
        doc = libmarkdown.mkd_string(cp, len(text), 0)
        out = tempfile.TemporaryFile('r+w')
        ret = libmarkdown.markdown(
            doc, ctypes.pythonapi.PyFile_AsFile(out), 0
        )
        out.seek(0)
        html = out.read()

        self.assertNotEqual(ret, -1)
        self.assertEqual(html, '<p><code>test</code></p>\n')

        out.close()

    def test_mkd_line(self):
        self.assertEqual(
            libmarkdown.mkd_line.argtypes,
            (ctypes.c_char_p,
             ctypes.c_int,
             ctypes.POINTER(ctypes.c_char_p),
             ctypes.c_int),
        )

        self.assertEqual(
            libmarkdown.mkd_line.restype,
            ctypes.c_int,
        )

        text = '`test`'
        cp = ctypes.c_char_p(text)
        sb = ctypes.c_char_p('')
        ret = libmarkdown.mkd_line(cp, len(text), ctypes.byref(sb), 0)

        self.assertNotEqual(ret, -1)
        self.assertEqual(sb.value, '<code>test</code>')

    def test_mkd_generateline(self):
        self.assertEqual(
            libmarkdown.mkd_generateline.argtypes,
            (ctypes.c_char_p,
             ctypes.c_int,
             ctypes.POINTER(libmarkdown.FILE),
             ctypes.c_int),
        )

        self.assertEqual(
            libmarkdown.mkd_generateline.restype,
            ctypes.c_int,
        )

        text = '`test`'
        cp = ctypes.c_char_p(text)
        out = tempfile.TemporaryFile('r+w')
        ret = libmarkdown.mkd_generateline(
            cp, len(text), ctypes.pythonapi.PyFile_AsFile(out), 0
        )

        self.assertNotEqual(ret, -1)

        out.close()

    def test_mkd_compile(self):
        self.assertEqual(
            libmarkdown.mkd_compile.argtypes,
            (ctypes.POINTER(libmarkdown.Document), ctypes.c_int),
        )

        self.assertEqual(
            libmarkdown.mkd_compile.restype,
            ctypes.c_int,
        )

        text = '`test`'
        cp = ctypes.c_char_p(text)
        doc = libmarkdown.mkd_string(cp, len(text), 0)
        ret = libmarkdown.mkd_compile(doc, 0)

        self.assertNotEqual(ret, -1)
        self.assertEqual(doc.contents.compiled, 1)

        libmarkdown.mkd_cleanup(doc)

    def test_mkd_generatehtml(self):
        self.assertEqual(
            libmarkdown.mkd_generatehtml.argtypes,
            (ctypes.POINTER(libmarkdown.Document),
             ctypes.POINTER(libmarkdown.FILE)),
        )

        self.assertEqual(
            libmarkdown.mkd_generatehtml.restype,
            ctypes.c_int,
        )

        text = '`test`'
        cp = ctypes.c_char_p(text)
        out = tempfile.TemporaryFile('r+w')
        doc = libmarkdown.mkd_string(cp, len(text), 0)
        ret = libmarkdown.mkd_compile(doc, 0)

        self.assertNotEqual(ret, -1)

        ret = libmarkdown.mkd_generatehtml(
            doc, ctypes.pythonapi.PyFile_AsFile(out), 0
        )

        self.assertNotEqual(ret, -1)

        out.seek(0)
        html = out.read()

        self.assertEqual(
            html, '<p><code>test</code></p>\n',
        )

        libmarkdown.mkd_cleanup(doc)

        out.close()

    def test_mkd_document(self):
        self.assertEqual(
            libmarkdown.mkd_document.argtypes,
            (ctypes.POINTER(libmarkdown.Document),
             ctypes.POINTER(ctypes.c_char_p)),
        )

        self.assertEqual(
            libmarkdown.mkd_document.restype,
            ctypes.c_int,
        )

        text = '`test`'
        cp = ctypes.c_char_p(text)
        sb = ctypes.c_char_p('')
        doc = libmarkdown.mkd_string(cp, len(text), 0)
        ret = libmarkdown.mkd_compile(doc, 0)

        self.assertNotEqual(ret, -1)

        ret = libmarkdown.mkd_document(doc, ctypes.byref(sb), 0)

        self.assertNotEqual(ret, -1)
        self.assertEqual(
            sb.value[:ret],
            '<p><code>test</code></p>'
        )

    def test_mkd_css(self):
        self.assertEqual(
            libmarkdown.mkd_css.argtypes,
            (ctypes.POINTER(libmarkdown.Document),
             ctypes.POINTER(ctypes.c_char_p)),
        )

        self.assertEqual(
            libmarkdown.mkd_css.restype,
            ctypes.c_int,
        )

        text = '<style>\n  *{color:red}\n</style>\n\n# header-1\n\n`test`'
        cp = ctypes.c_char_p(text)
        sb = ctypes.c_char_p('')
        doc = libmarkdown.mkd_string(cp, len(text), 0)
        ret = libmarkdown.mkd_compile(doc, 0)

        self.assertNotEqual(ret, -1)

        ret = libmarkdown.mkd_css(doc, ctypes.byref(sb))

        self.assertNotEqual(ret, -1)
        self.assertEqual(
            sb.value[:ret],
            '<style>  *{color:red}</style>\n'
        )

    def test_mkd_generatecss(self):
        self.assertEqual(
            libmarkdown.mkd_generatecss.argtypes,
            (ctypes.POINTER(libmarkdown.Document),
             ctypes.POINTER(libmarkdown.FILE)),
        )

        self.assertEqual(
            libmarkdown.mkd_generatecss.restype,
            ctypes.c_int,
        )

        text = '<style>\n  *{color:red}\n</style>\n\n# header-1\n\n`test`'
        cp = ctypes.c_char_p(text)
        out = tempfile.TemporaryFile('r+w')
        doc = libmarkdown.mkd_string(cp, len(text), 0)
        ret = libmarkdown.mkd_compile(doc, 0)

        self.assertNotEqual(ret, -1)

        ret = libmarkdown.mkd_generatecss(
            doc, ctypes.pythonapi.PyFile_AsFile(out)
        )

        # Returns -1 event on success
        # self.assertNotEqual(ret, -1)

        out.seek(0)
        html = out.read()

        self.assertEqual(
            html, '<style>  *{color:red}</style>\n'
        )

        out.close()

    def test_mkd_toc(self):
        self.assertEqual(
            libmarkdown.mkd_toc.argtypes,
            (ctypes.POINTER(libmarkdown.Document),
             ctypes.POINTER(ctypes.c_char_p)),
        )

        self.assertEqual(
            libmarkdown.mkd_toc.restype,
            ctypes.c_int,
        )

        flags = libmarkdown.MKD_TOC
        text = '# header-1\n## header-2\n### header-3'
        cp = ctypes.c_char_p(text)
        sb = ctypes.c_char_p('')
        doc = libmarkdown.mkd_string(cp, len(text), flags)
        ret = libmarkdown.mkd_compile(doc, flags)

        self.assertNotEqual(ret, -1)

        ret = libmarkdown.mkd_toc(doc, ctypes.byref(sb))

        self.assertNotEqual(ret, -1)
        self.assertEqual(
            sb.value[:ret], (
                '\n '
                '<ul>\n <li><a href="#header-1">header-1</a>\n  '
                '<ul>\n  <li><a href="#header-2">header-2</a>\n   '
                '<ul>\n   <li><a href="#header-3">header-3</a>   </li>\n   '
                '</ul>\n  </li>\n  </ul>\n </li>\n </ul>\n'
            )
        )

    def test_mkd_generatetoc(self):
        self.assertEqual(
            libmarkdown.mkd_generatetoc.argtypes,
            (ctypes.POINTER(libmarkdown.Document),
             ctypes.POINTER(libmarkdown.FILE)),
        )

        self.assertEqual(
            libmarkdown.mkd_generatetoc.restype,
            ctypes.c_int,
        )

        flags = libmarkdown.MKD_TOC
        text = '# header-1\n## header-2\n### header-3'
        cp = ctypes.c_char_p(text)
        out = tempfile.TemporaryFile('r+w')
        doc = libmarkdown.mkd_string(cp, len(text), flags)
        ret = libmarkdown.mkd_compile(doc, flags)

        self.assertNotEqual(ret, -1)

        ret = libmarkdown.mkd_generatetoc(
            doc, ctypes.pythonapi.PyFile_AsFile(out)
        )

        self.assertNotEqual(ret, -1)

        out.seek(0)
        html = out.read()

        self.assertEqual(
            html, (
                '\n '
                '<ul>\n <li><a href="#header-1">header-1</a>\n  '
                '<ul>\n  <li><a href="#header-2">header-2</a>\n   '
                '<ul>\n   <li><a href="#header-3">header-3</a>   </li>\n   '
                '</ul>\n  </li>\n  </ul>\n </li>\n </ul>\n'
            )
        )

        out.close()

    def test_mkd_dump(self):
        self.assertEqual(
            libmarkdown.mkd_dump.argtypes,
            (ctypes.POINTER(libmarkdown.Document),
             ctypes.POINTER(libmarkdown.FILE),
             ctypes.c_int,
             ctypes.c_char_p),
        )

        self.assertEqual(
            libmarkdown.mkd_dump.restype,
            ctypes.c_int,
        )

        text = (
            '# header-1\n'
            '`test`\n'
        )

        cp = ctypes.c_char_p(text)

        doc = libmarkdown.mkd_string(cp, len(text), 0)
        ret = libmarkdown.mkd_compile(doc, 0)

        self.assertNotEqual(ret, -1)

        out = tempfile.TemporaryFile('r+w')

        libmarkdown.mkd_dump(
            doc, ctypes.pythonapi.PyFile_AsFile(out),
            0, ctypes.c_char_p('title')
        )

        out.seek(0)
        dump = out.read()

        self.assertEqual(
            dump, (
                'title-----[source]--+--[header, <P>, 1 line]\n'
                '                    `--[markup, <P>, 1 line]\n'
            )
        )

        out.close()

    def test_mkd_cleanup(self):
        self.assertEqual(
            libmarkdown.mkd_cleanup.argtypes,
            (ctypes.POINTER(libmarkdown.Document),)
        )

        self.assertEqual(
            libmarkdown.mkd_cleanup.restype,
            ctypes.c_int,
        )

        text = '`test`'
        cp = ctypes.c_char_p(text)
        doc = libmarkdown.mkd_string(cp, len(text), 0)
        libmarkdown.mkd_compile(doc, 0)

        self.assertEqual(doc.contents.compiled, 1)

        libmarkdown.mkd_cleanup(doc)

        self.assertNotEqual(doc.contents.compiled, 1)

    def test_mkd_doc_title(self):
        self.assertEqual(
            libmarkdown.mkd_doc_title.argtypes,
            (ctypes.POINTER(libmarkdown.Document),)
        )

        self.assertEqual(
            libmarkdown.mkd_doc_title.restype,
            ctypes.c_char_p,
        )

        text = '% title\n% author\n% date\n'
        cp = ctypes.c_char_p(text)
        doc = libmarkdown.mkd_string(cp, len(text), 0)
        ret = libmarkdown.mkd_compile(doc, 0)

        self.assertNotEqual(ret, -1)

        v = libmarkdown.mkd_doc_title(doc)

        self.assertEqual(v, 'title')

    def test_mkd_doc_author(self):
        self.assertEqual(
            libmarkdown.mkd_doc_author.argtypes,
            (ctypes.POINTER(libmarkdown.Document),)
        )

        self.assertEqual(
            libmarkdown.mkd_doc_author.restype,
            ctypes.c_char_p,
        )

        text = '% title\n% author\n% date\n'
        cp = ctypes.c_char_p(text)
        doc = libmarkdown.mkd_string(cp, len(text), 0)
        ret = libmarkdown.mkd_compile(doc, 0)

        self.assertNotEqual(ret, -1)

        v = libmarkdown.mkd_doc_author(doc)

        self.assertEqual(v, 'author')

    def test_mkd_doc_date(self):
        self.assertEqual(
            libmarkdown.mkd_doc_date.argtypes,
            (ctypes.POINTER(libmarkdown.Document),)
        )

        self.assertEqual(
            libmarkdown.mkd_doc_date.restype,
            ctypes.c_char_p,
        )

        text = '% title\n% author\n% date\n'
        cp = ctypes.c_char_p(text)
        doc = libmarkdown.mkd_string(cp, len(text), 0)
        ret = libmarkdown.mkd_compile(doc, 0)

        self.assertNotEqual(ret, -1)

        v = libmarkdown.mkd_doc_date(doc)

        self.assertEqual(v, 'date')

    # The following flag tests just ensure that the flags bits are
    # correct and enable/disable the appropriate output features.

    def _test_flag(self, i, o, f):
        text = i
        cp = ctypes.c_char_p(text)

        doc = libmarkdown.mkd_string(
            cp, len(text), f
        )
        libmarkdown.mkd_compile(doc, f)

        sb = ctypes.c_char_p('')
        ret = libmarkdown.mkd_document(doc, ctypes.byref(sb))

        self.assertEqual(
            sb.value[:ret],
            o,
        )

    def test_MKD_NOLINKS(self):
        self._test_flag(
            '<a href="a">a</a>',
            '<p><a href="a">a</a></p>',
            0
        )

        self._test_flag(
            '<a href="a">a</a>',
            '<p>&lt;a href="a">a</a></p>',
            libmarkdown.MKD_NOLINKS
        )

    def test_MKD_NOIMAGE(self):
        self._test_flag(
            '<img src="test.png" />',
            '<p><img src="test.png" /></p>',
            0
        )

        self._test_flag(
            '<img src="test.png" />',
            '<p>&lt;img src="test.png" /></p>',
            libmarkdown.MKD_NOIMAGE
        )

    def test_MKD_NOHTML(self):
        self._test_flag(
            '<div>test</div>',
            '<div>test</div>\n',
            0
        )

        self._test_flag(
            '<div>test</div>',
            '<p>&lt;div>test&lt;/div></p>',
            libmarkdown.MKD_NOHTML
        )

    def test_MKD_NOPANTS(self):
        self._test_flag(
            (
                '"test"\n'
                '``test''\n'
                'a -- b\n'
                'a --- b\n'
                'a ... b\n'
            ),
            '<p>&ldquo;test&rdquo;\n``test\na &mdash; b\n'
            'a &mdash;&ndash; b\na &hellip; b</p>',
            0
        )

        self._test_flag(
            (
                '"test"\n'
                '``test''\n'
                'a -- b\n'
                'a --- b\n'
                'a ... b\n'
            ),
            '<p>"test"\n``test\na -- b\na --- b\na ... b</p>',
            libmarkdown.MKD_NOPANTS
        )

    def test_MKD_NOHEADER(self):
        self._test_flag(
            (
                '%s title\n'
                '%s author(s)\n'
                '%s date\n'
                '`test`\n'
            ),
            '<p><code>test</code></p>',
            0
        )

        self._test_flag(
            (
                '%s title\n'
                '%s author(s)\n'
                '%s date\n'
                '`test`\n'
            ),
            '<p>%s title\n%s author(s)\n%s date\n<code>test</code></p>',
            libmarkdown.MKD_NOHEADER
        )

    def test_MKD_AUTOLINK(self):
        self._test_flag(
            'http://example.com',
            '<p>http://example.com</p>',
            0
        )

        self._test_flag(
            'http://example.com',
            '<p><a href="http://example.com">http://example.com</a></p>',
            libmarkdown.MKD_AUTOLINK
        )

    def test_MKD_SAFELINK(self):
        self._test_flag(
            (
                '[a][x]\n\n'
                '[x]: file://test "Some title"'
            ),
            '<p><a href="file://test" title="Some title">a</a></p>',
            0
        )

        self._test_flag(
            (
                '[a][x]\n\n'
                '[x]: file://test "Some title"'
            ),
            '<p>[a][x]</p>',
            libmarkdown.MKD_SAFELINK
        )

    def test_MKD_NOTABLES(self):
        self._test_flag(
            'a  | b\n'
            '-- | -\n'
            '1  | 2\n',
            '<table>\n<thead>\n<tr>\n<th>a  </th>\n'
            '<th> b</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n'
            '<td>1  </td>\n<td> 2</td>\n</tr>\n</tbody>\n</table>\n',
            0
        )

        self._test_flag(
            'a  | b\n'
            '-- | -\n'
            '1  | 2\n',
            '<p>a  | b\n&mdash; | &ndash;\n1  | 2</p>',
            libmarkdown.MKD_NOTABLES
        )

    def test_MKD_NO_EXT(self):
        self._test_flag(
            '[foo](class:bar)\n',
            '<p><span class="bar">foo</span></p>',
            0
        )

        self._test_flag(
            '[foo](class:bar)\n',
            '<p>[foo](class:bar)</p>',
            libmarkdown.MKD_NO_EXT
        )

    def test_MKD_STRICT(self):
        self._test_flag(
            'A^B\n',
            '<p>A<sup>B</sup></p>',
            0
        )

        self._test_flag(
            'A^B\n',
            '<p>A^B</p>',
            libmarkdown.MKD_STRICT
        )

    def test_MKD_TOC(self):
        self._test_flag(
            '# header-1\n'
            '## header-2\n',
            '<h1>header-1</h1>\n\n<h2>header-2</h2>',
            0
        )

        self._test_flag(
            '# header-1\n'
            '## header-2\n',
            '<h1 id="header-1">header-1</h1>\n\n'
            '<h2 id="header-2">header-2</h2>',
            libmarkdown.MKD_TOC
        )


class MarkdownClassTestCase(unittest.TestCase):
    def test_fails_without_args(self):
        self.assertRaises(TypeError, Markdown)

    def test__accepts_string_arg(self):
        md = Markdown('`test`')

    def test_accepts_file_arg(self):
        i = tempfile.TemporaryFile('r+w')
        md = Markdown(i)
        i.close()

    def test_kwargs_generates_valid_bitmask(self):
        md = Markdown('`test`')
        self.assertEqual(md.flags, 0)

        md = Markdown('`test`', strict=True)
        self.assertEqual(md.flags, libmarkdown.MKD_STRICT)

        md = Markdown('`test`', autolink=True)
        self.assertEqual(md.flags, libmarkdown.MKD_AUTOLINK)

        md = Markdown('`test`', safelink=True)
        self.assertEqual(md.flags, libmarkdown.MKD_SAFELINK)

        md = Markdown('`test`', ignore_header=True)
        self.assertEqual(md.flags, libmarkdown.MKD_NOHEADER)

        md = Markdown('`test`', ignore_links=True)
        self.assertEqual(md.flags, libmarkdown.MKD_NOLINKS)

        md = Markdown('`test`', ignore_images=True)
        self.assertEqual(md.flags, libmarkdown.MKD_NOIMAGE)

        md = Markdown('`test`', ignore_tables=True)
        self.assertEqual(md.flags, libmarkdown.MKD_NOTABLES)

        md = Markdown('`test`', ignore_smartypants=True)
        self.assertEqual(md.flags, libmarkdown.MKD_NOPANTS)

        md = Markdown('`test`', ignore_embedded_html=True)
        self.assertEqual(md.flags, libmarkdown.MKD_NOHTML)

        md = Markdown('`test`', ignore_pseudo_protocols=True)
        self.assertEqual(md.flags, libmarkdown.MKD_NO_EXT)

    def test_input_string_get_pandoc_title(self):
        md = Markdown('`test`')
        self.assertEqual(md.get_pandoc_title(), None)

        md = Markdown('% abc\n')
        self.assertEqual(md.get_pandoc_title(), None)

        md = Markdown('% abc\n% def')
        self.assertEqual(md.get_pandoc_title(), None)

        md = Markdown('% abc\n% def\n% jhi\n')
        self.assertEqual(md.get_pandoc_title(), 'abc')

    def test_input_string_get_pandoc_author(self):
        md = Markdown('`test`')
        self.assertEqual(md.get_pandoc_author(), None)

        md = Markdown('% abc\n')
        self.assertEqual(md.get_pandoc_author(), None)

        md = Markdown('% abc\n% def')
        self.assertEqual(md.get_pandoc_author(), None)

        md = Markdown('% abc\n% def\n% jhi\n')
        self.assertEqual(md.get_pandoc_author(), 'def')

    def test_input_string_get_pandoc_date(self):
        md = Markdown('`test`')
        self.assertEqual(md.get_pandoc_date(), None)

        md = Markdown('% abc\n')
        self.assertEqual(md.get_pandoc_date(), None)

        md = Markdown('% abc\n% def')
        self.assertEqual(md.get_pandoc_date(), None)

        md = Markdown('% abc\n% def\n% jhi\n')
        self.assertEqual(md.get_pandoc_date(), 'jhi')

    def test_input_string_get_html_css(self):
        md = Markdown(
            '<style>\n  *{color:red}\n</style>\n\n# header-1\n\n`test`')

        style = md.get_html_css()

        self.assertEqual(style, '<style>  *{color:red}</style>\n')

    def test_input_string_get_html_toc(self):
        md = Markdown('# header-1\n## header-2\n### header-3')
        html = md.get_html_toc()

        self.assertEqual(
            html, (
                '\n '
                '<ul>\n <li><a href="#header-1">header-1</a>\n  '
                '<ul>\n  <li><a href="#header-2">header-2</a>\n   '
                '<ul>\n   <li><a href="#header-3">header-3</a>   </li>\n   '
                '</ul>\n  </li>\n  </ul>\n </li>\n </ul>\n'
            )
        )

    def test_input_string_get_html_content(self):
        md = Markdown('`test`')

        html = md.get_html_content()

        self.assertEqual(html, '<p><code>test</code></p>')

    def test_input_string_write_html_css(self):
        o = tempfile.TemporaryFile('r+w')
        md = Markdown(
            '<style>\n  *{color:red}\n</style>\n\n# header-1\n\n`test`')
        md.write_html_css(o)

        o.seek(0)
        style = o.read()
        o.close()

        self.assertEqual(style, '<style>  *{color:red}</style>\n')

    def test_input_string_write_html_toc(self):
        o = tempfile.TemporaryFile('r+w')
        md = Markdown('# header-1\n## header-2\n### header-3')
        md.write_html_toc(o)

        o.seek(0)
        html = o.read()
        o.close()

        self.assertEqual(
            html, (
                '\n '
                '<ul>\n <li><a href="#header-1">header-1</a>\n  '
                '<ul>\n  <li><a href="#header-2">header-2</a>\n   '
                '<ul>\n   <li><a href="#header-3">header-3</a>   </li>\n   '
                '</ul>\n  </li>\n  </ul>\n </li>\n </ul>\n'
            )
        )

    def test_input_string_write_html_content(self):
        o = tempfile.TemporaryFile('r+w')
        md = Markdown('`test`')
        md.write_html_content(o)

        o.seek(0)
        html = o.read()
        o.close()

        self.assertEqual(html, '<p><code>test</code></p>\n')

    def test_input_file_get_pandoc_title(self):
        i = tempfile.TemporaryFile('r+w')
        i.write('`test`')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_title(), None)
        i.close()

        i = tempfile.TemporaryFile('r+w')
        i.write('% abc\n')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_title(), None)
        i.close()

        i = tempfile.TemporaryFile('r+w')
        i.write('% abc\n% def')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_title(), None)
        i.close()

        i = tempfile.TemporaryFile('r+w')
        i.write('% abc\n% def\n% jhi\n')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_title(), 'abc')
        i.close()

    def test_input_file_get_pandoc_author(self):
        i = tempfile.TemporaryFile('r+w')
        i.write('`test`')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_author(), None)
        i.close()

        i = tempfile.TemporaryFile('r+w')
        i.write('% abc\n')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_author(), None)
        i.close()

        i = tempfile.TemporaryFile('r+w')
        i.write('% abc\n% def')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_author(), None)
        i.close()

        i = tempfile.TemporaryFile('r+w')
        i.write('% abc\n% def\n% jhi\n')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_author(), 'def')
        i.close()

    def test_input_file_get_pandoc_date(self):
        i = tempfile.TemporaryFile('r+w')
        i.write('`test`')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_date(), None)
        i.close()

        i = tempfile.TemporaryFile('r+w')
        i.write('% abc\n')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_date(), None)
        i.close()

        i = tempfile.TemporaryFile('r+w')
        i.write('% abc\n% def')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_date(), None)
        i.close()

        i = tempfile.TemporaryFile('r+w')
        i.write('% abc\n% def\n% jhi\n')
        i.seek(0)
        md = Markdown(i)
        self.assertEqual(md.get_pandoc_date(), 'jhi')
        i.close()

    def test_input_file_get_html_css(self):
        i = tempfile.TemporaryFile('r+w')
        i.write('<style>\n  *{color:red}\n</style>\n\n# header-1\n\n`test`')
        i.seek(0)
        md = Markdown(i)

        style = md.get_html_css()

        self.assertEqual(style, '<style>  *{color:red}</style>\n')

    def test_input_file_get_html_toc(self):
        i = tempfile.TemporaryFile('r+w')
        i.write('# header-1\n## header-2\n### header-3')
        i.seek(0)
        md = Markdown(i)
        html = md.get_html_toc()
        i.close()

        self.assertEqual(
            html, (
                '\n '
                '<ul>\n <li><a href="#header-1">header-1</a>\n  '
                '<ul>\n  <li><a href="#header-2">header-2</a>\n   '
                '<ul>\n   <li><a href="#header-3">header-3</a>   </li>\n   '
                '</ul>\n  </li>\n  </ul>\n </li>\n </ul>\n'
            )
        )

    def test_input_file_get_html_content(self):
        i = tempfile.TemporaryFile('r+w')
        i.write('`test`')
        i.seek(0)
        md = Markdown(i)
        html = md.get_html_content()
        i.close()

        self.assertEqual(html, '<p><code>test</code></p>')

    def test_input_file_write_html_css(self):
        i = tempfile.TemporaryFile('r+w')
        i.write('<style>\n  *{color:red}\n</style>\n\n# header-1\n\n`test`')
        i.seek(0)
        o = tempfile.TemporaryFile('r+w')
        md = Markdown(i)
        md.write_html_css(o)

        o.seek(0)
        style = o.read()

        o.close()
        i.close()

        self.assertEqual(style, '<style>  *{color:red}</style>\n')

    def test_input_file_write_html_toc(self):
        i = tempfile.TemporaryFile('r+w')
        i.write('# header-1\n## header-2\n### header-3')
        i.seek(0)
        o = tempfile.TemporaryFile('r+w')
        md = Markdown(i)
        md.write_html_toc(o)

        o.seek(0)
        html = o.read()

        i.close()
        o.close()

        self.assertEqual(
            html, (
                '\n '
                '<ul>\n <li><a href="#header-1">header-1</a>\n  '
                '<ul>\n  <li><a href="#header-2">header-2</a>\n   '
                '<ul>\n   <li><a href="#header-3">header-3</a>   </li>\n   '
                '</ul>\n  </li>\n  </ul>\n </li>\n </ul>\n'
            )
        )

    def test_input_file_write_html_content(self):
        i = tempfile.TemporaryFile('r+w')
        i.write('`test`')
        i.seek(0)
        o = tempfile.TemporaryFile('r+w')
        md = Markdown(i)
        md.write_html_content(o)

        o.seek(0)
        html = o.read()

        i.close()
        o.close()

        self.assertEqual(html, '<p><code>test</code></p>\n')


if __name__ == '__main__':
    unittest.main()

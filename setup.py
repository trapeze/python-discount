import os
import posixpath
import shutil
import subprocess
import urllib2

from distutils.command.build_ext import build_ext as _build_ext
from distutils.core import setup, Extension


DISCOUNT_VERSION = '1.5.8'

DISCOUNT_CONFIGURATION = (
    # Use pandoc-style header blocks
    '--enable-pandoc-header',

    # A^B becomes A<sup>B</sup>
    '--enable-superscript',

    # underscores aren'\''t special in the middle of words
    '--relaxed-emphasis',

    # Set tabstops to N characters (default is 4)
    '--with-tabstops=4',

    # Enable >%id% divisions
    '--enable-div',

    # Enable (a)/(b)/(c) lists
    '--enable-alpha-list',

    # Enable memory allocation debugging
    # '--enable-amalloc',

    # Turn on all stable optional features
    # '--enable-all-features',
)

# TODO: host on pypi
DISCOUNT_DOWNLOAD_URL = (
    'http://www.pell.portland.or.us/'
    '~orc/Code/discount/discount-%s.tar.gz'
) % DISCOUNT_VERSION


class build_ext(_build_ext):
    user_options = _build_ext.user_options + [
        ('discount-src-path=', None,
         'User-defined path to discount source files.'),
    ]

    def initialize_options(self):
        _build_ext.initialize_options(self)
        self.discount_src_path = None

    def build_extension(self, ext):
        if ext.name == '_discount':
            self.build_extension_discount(ext)
        else:
            _build_ext.build_extension(self, ext)

    def build_extension_discount(self, ext):
        if self.discount_src_path is None:
            filepath = os.path.join(
                self.build_temp,
                posixpath.basename(DISCOUNT_DOWNLOAD_URL)
            )
            if not os.path.lexists(self.build_temp):
                os.makedirs(self.build_temp)

            if not os.path.exists(filepath):
                print 'Downloading %s...' % DISCOUNT_DOWNLOAD_URL

                data = urllib2.urlopen(DISCOUNT_DOWNLOAD_URL)
                fp = open(filepath, 'wb')
                fp.write(data.read())
                fp.close()

                print 'Extracting %s...' % filepath

                subprocess.call(
                    ['tar', 'xzf', filepath, '-C', self.build_temp]
                )

            discount_src_path = filepath[:-len('.tar.gz')]

        else:
            discount_src_path = self.discount_src_path

        if not os.path.exists(
            os.path.join(discount_src_path, 'config.h')):
            current_dir = os.getcwd()
            os.chdir(discount_src_path)
            subprocess.call(
                ('./configure.sh',) + DISCOUNT_CONFIGURATION,
                env=os.environ
            )
            os.chdir(current_dir)

        ext.sources = [
            os.path.join(discount_src_path, s) for s in ext.sources
        ]
        ext.extra_compile_args += [
            '-I%s' % discount_src_path,
        ]

        _build_ext.build_extension(self, ext)

        ext_filename = self.get_ext_filename(ext.name)

        if not os.path.exists(ext_filename):
            # Copy the shared library to same dir as setup.py for
            # convenience, helpful for running test suite without
            # installing package.
            shutil.copy(
                os.path.join(self.build_lib, ext_filename),
                ext_filename
            )


setup(
    name='discount',
    license='BSD',
    version='0.1.0BETA',

    author='Trapeze Media',
    author_email='technology@trapeze.com',
    url="http://github.com/trapeze/python-discount",
    download_url='http://pypi.python.org/pypi/discount',
    description='A Python interface for Discount, the C Markdown parser',
    long_description=open('README.rst').read(),
    keywords='markdown discount ctypes',

    provides=[
        'discount',
    ],

    py_modules=[
        'discount',
        'discount.libmarkdown',
    ],

    ext_modules=[
        Extension(
            '_discount',
            extra_compile_args=[
                '-DVERSION="%s"' % DISCOUNT_VERSION,
            ],
            sources=[
                'Csio.c',
                'amalloc.c',
                'css.c',
                'docheader.c',
                'dumptree.c',
                'generate.c',
                'markdown.c',
                'mkdio.c',
                'resource.c',
                'theme.c',
                'toc.c',
                'version.c',
                'xml.c',
                'xmlpage.c',
            ],
        )
    ],

    cmdclass={
        'build_ext': build_ext
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Markup'
    ],
)

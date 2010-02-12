import os
import posixpath
import shutil
import subprocess
import urllib2

from distutils.command.build_ext import build_ext as _build_ext
from distutils.core import setup, Extension


DEFAULT_DISCOUNT_VERSION = '1.6.1'


DEFAULT_DISCOUNT_DOWNLOAD_URL = (
    # 'http://www.pell.portland.or.us/~orc/Code/discount/'
    'http://packages.python.org/discount/'
    'discount-%s.tar.gz'
) % DEFAULT_DISCOUNT_VERSION


DEFAULT_DISCOUNT_CONFIGURE_OPTS = (
    # Use pandoc-style header blocks
    '--enable-pandoc-header '

    # A^B becomes A<sup>B</sup>
    '--enable-superscript '

    # underscores aren'\''t special in the middle of words
    '--relaxed-emphasis '

    # Set tabstops to N characters (default is 4)
    '--with-tabstops=4 '

    # Enable >%id% divisions
    '--enable-div '

    # Enable (a)/(b)/(c) lists
    '--enable-alpha-list '

    # Enable memory allocation debugging
    # '--enable-amalloc '

    # Turn on all stable optional features
    # '--enable-all-features '
)


class build_ext(_build_ext):
    user_options = _build_ext.user_options + [
        ('discount-src-path=', None,
         'Path to discount source files.'),

        ('discount-download-url=', None,
         'Download url of the discount source files.'),

        ('discount-configure-opts=', None,
         'Default options passed to ./configure.sh'),
    ]

    def initialize_options(self):
        _build_ext.initialize_options(self)
        self.discount_src_path = None
        self.discount_download_url = DEFAULT_DISCOUNT_DOWNLOAD_URL
        self.discount_configure_opts = DEFAULT_DISCOUNT_CONFIGURE_OPTS

    def build_extension(self, ext):
        if self.discount_src_path is None:
            filepath = os.path.join(
                self.build_temp,
                posixpath.basename(self.discount_download_url)
            )
            if not os.path.lexists(self.build_temp):
                os.makedirs(self.build_temp)

            if not os.path.exists(filepath):
                print 'Downloading %s...' % self.discount_download_url

                data = urllib2.urlopen(self.discount_download_url)
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
                ['./configure.sh',] + self.discount_configure_opts.split(),
                env=os.environ
            )
            os.chdir(current_dir)

        ext.sources = [
            os.path.join(discount_src_path, s) for s in ext.sources
        ]

        ext.extra_compile_args += [
            '-I%s' % discount_src_path,
            '-DVERSION="%s"' % open(
                os.path.join(discount_src_path, 'VERSION')
            ).read().strip()
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
    version='0.2.0ALPHA',

    author='Trapeze',
    author_email='tkemenczy@trapeze.com',
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
            sources=[
                'amalloc.c', 'Csio.c', 'css.c', 'docheader.c',
                'dumptree.c', 'generate.c', 'markdown.c', 'mkdio.c',
                'resource.c', 'toc.c', 'version.c', 'xml.c', 'xmlpage.c',
                'basename.c',
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

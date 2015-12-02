import setuptools
import distutils.core


class PyTest(distutils.core.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call([sys.executable, 'test/runtests.py'])
        raise SystemExit(errno)


setuptools.setup(
    name='vbbvg',
    version='0.0.1',
    author='Dinu Gherman',
    author_email='gherman@darwin.in-berlin.de',
    description='Fetch and display real-time departure times for VBB/BVG public transport',
    license='GPL',
    keywords='real-time, transport-data',
    url='https://github.com/deeplook/vbbvg',
    packages=setuptools.find_packages(exclude='test'),
    long_description=open('README.rst').read(),
    install_requires=[
        'six',
        'pandas',
        'BeautifulSoup4',
        'html5lib',
        'tabulate',
        'termcolor',
        'lxml'
    ],
    entry_points={
        'console_scripts': ['vbbvg=vbbvg.__main__:main']
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License (GPL)'
    ],
    cmdclass={'test': PyTest},
    package_data={
        'vbbvg': ['vbbvg_stops.csv'],
    },
)

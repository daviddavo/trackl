from setuptools import setup, find_packages

try:
    LONG_DESCRIPTION = open("README.rst").read()
except IOError:
    LONG_DESCRIPTION = __doc__

NAME = "Trackl"
VERSION = "0.1"
REQUIREMENTS = [
"guessit",
"notify2"
]
EXTRA_REQUIREMENTS = { #Here goes Gtk, Qt or whatever
}

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(),

    install_requires=REQUIREMENTS,
    extras_require=EXTRA_REQUIREMENTS,
    package_data={"trackl": ["resources/*", ".api"]},

    author="David Davó",
    author_email="david@ddavo.me",
    description="Open simkl tracker and manager",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/daviddavo/trackl",
    keywords="tracker, cli, simkl, manager",
    license="GPL-3",
    entry_points={
        "console_scripts": [
            "trackl-beta = trackl.ui.cli:main"
        ]
    },
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Operating System :: POSIX"
    ]
)
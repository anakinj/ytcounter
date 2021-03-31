from setuptools import setup, find_packages
from ytcounter import __version__

setup(
    name="ytcounter",
    version=__version__,
    description="Displays subscription and view counts on a matrix display",
    url="https://github.com/anakinj/ytcounter",
    author="Joakim antman",
    author_email="antmanj@gmail.com",
    license="MIT",
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires= ['requests','luma.core', 'luma.led_matrix'],
    extras_require = {
        'test': ['luma.emulator']
    },
    include_package_data=True,
    entry_points= {
      "console_scripts": [
        "ytcounter=ytcounter.cli:main"
      ]
    }
)
import os
import re

from setuptools import setup, find_packages


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
    init_py = os.path.join(os.path.dirname(__file__),
                           'x_project_cdn_watcher', '__init__.py')
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        else:
            msg = 'Cannot find version in x_project_cdn_watcher/__init__.py'
            raise RuntimeError(msg)


install_requires = ['aiohttp==2.3.10',
                    'aiodns==2.0.0',
                    'ujson',
                    'trafaret-config',
                    'pytz',
                    'uvloop==0.13.0',
                    'requests',
                    'python-magic'
                    ]

setup(
    name="x_project_cdn_watcher",
    version=read_version(),
    url="",
    packages=find_packages(),
    package_data={

    },
    install_requires=install_requires,
    zip_safe=False,
    entry_points={
        'console_scripts': [
        ],
    }
)

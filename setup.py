try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

config = {
    'name': 'influence api'
    'version': '0.1',
    'packages': find_packages[],
    'install_requires': ['nose', 'Flask', 'pymongo', 'networkx', 'tornado'],
    'description': 'description',
    'author': 'Michael Kerr',
    'author_email': 'mkerr09@gmail.com',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'scripts': [],
    include_package_data = True
}

setup(**config)
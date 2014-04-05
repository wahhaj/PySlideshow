try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Photo slideshow',
    'author': 'Wahhaj Ali',
    'url': 'www.wahhajali.com',
    'download_url': 'Where to download it.',
    'author_email': 'wahhajj@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'slideshow'
}

setup(**config)
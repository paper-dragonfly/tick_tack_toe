try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Tick Tack Toe Game',
    'author': 'PaperDragonfly',
    'url': 'URL to get it at.',
    'download_url':'Where to download it.',
    'author_email':'My email.',
    'version': '0.1',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['ttt'],
    'scripts':[],
    'name':'tick_tack_toe'
}

setup(**config)


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

long_desc = '''Something like print, but for images...
If your terminal supports iTerm image protocol then the images shown will be of high resolution. 
Otherwise prints the image to the terminal by printing colored characters.
'''



# python setup.py register -r pypi
# python3 setup.py sdist upload -r pypi
setup(
    name='pycat-real',
    version='0.05',

    packages=['pycat'],
    url='https://github.com/PiotrDabkowski/pycat',
    install_requires = ['PIL', 'numpy', 'six'],
    license='MIT',
    author='Piotr Dabkowski',
    author_email='piodrus@gmail.com',
    description='Something like print, but for images...',
    long_description=long_desc
)
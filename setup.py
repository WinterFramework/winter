import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, 'winter', '__version__.py')) as f:
    exec(f.read(), about)


setup(name='winter',
      version=about['__version__'],
      description='Web Framerowk inspired by Spring Framework',
      url='https://github.com/mofr/winter',
      author='Alexander Egorov',
      author_email='mofr@zond.org',
      license='MIT',
      packages=['winter'],
      install_requires=['djangorestframework>=3.9.0',
                        'Django>=1.11.16',
                        'dataclasses>=0.6',
                        'pydantic>=0.15',
                        'drf-yasg>=1.11.0',
                        'docstring_parser>=0.1'])

import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, 'winter', '__version__.py')) as f:
    exec(f.read(), about)


def read_requirements(req_file):
    with open(os.path.join('requirements', req_file)) as req:
        return [line.strip() for line in req.readlines() if line.strip() and not line.strip().startswith('#')]


requirements = read_requirements('base.txt')

setup(
    name='winter',
    packages=find_packages(),
    include_package_data=True,
    version=about['__version__'],
    description='Web Framework inspired by Spring Framework',
    url='https://github.com/mofr/winter',
    author='Alexander Egorov',
    author_email='mofr@zond.org',
    license='MIT',
    install_requires=requirements,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
)

from setuptools import setup, find_packages

setup(
        name='firepy',
        version='0.1.4',
        description='FirePHP for Python',
        long_description=('This is a python server library for FirePHP '
                          'supporting python built-in logging facility '
                          'and Django.'),
        author='Sung-jin Hong',
        author_email='serialx@serialx.net',
        license='MIT',
        url='http://code.google.com/p/firepy/',
        download_url='http://code.google.com/p/firepy/downloads/list',
        packages=find_packages(),
        zip_safe=False,
        )

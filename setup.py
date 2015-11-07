from setuptools import setup


setup(
    name='aiohttp_exc_handlers',
    version='0.1',
    description='Bind views to exceptions for aiohttp',
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP",
    ],
    author='Alexander Zelenyak',
    author_email='zzz.sochi@gmail.com',
    license='BSD',
    url='https://github.com/zzzsochi/aiohttp_ext_handlers',
    keywords=['asyncio', 'aiohttp'],
    py_modules=['aiohttp_ext_handlers'],
    install_requires=[
        'aiohttp',
        'resolver_deco',
        'zope.dottedname',
    ],
    tests_require=['pytest']
),

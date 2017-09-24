from setuptools import setup
from distutils.core import Extension

bnb_module = Extension(

        'cia', 
        extra_compile_args=['-O3'],
        sources = ["cia.cpp"]
    )

setup(

    name='cia',
    version='0.1',

    author='Adrian Buerger, Clemens Zeile',
    author_email='adrian.buerger@hs-karlsruhe.de, clemens.zeile@ovgu.de',
    
    ext_modules=[Extension('cia', ['cia.cpp'])]

    )

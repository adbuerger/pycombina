from setuptools import setup
from distutils.core import Extension

bnb_module = Extension(

        'cia_bnb', 
        extra_compile_args=['-O3'],
        sources = ["cia_bnb.cpp"]
    )

setup(

    name='cia_bnb',
    version='0.1',

    author='Adrian Buerger, Clemens Zeile',
    author_email='adrian.buerger@hs-karlsruhe.de, clemens.zeile@ovgu.de',
    
    ext_modules=[Extension('cia_bnb', ['cia_bnb.cpp'])]

    )

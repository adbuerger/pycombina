from setuptools import setup
from distutils.core import Extension

bnb_module = Extension(

        'bnb_jung', 
        extra_compile_args=['-O3'],
        sources = ["bnb_jung.cpp"]
    )

setup(

    name='bnb_jung',
    version='0.1',

    author='Adrian Buerger',
    author_email='adrian.buerger@hs-karlsruhe.de',
    
    ext_modules=[Extension('bnb_jung', ['bnb_jung.cpp'])]

    )

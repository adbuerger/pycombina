#cython: boundscheck=False, wraparound=False, nonecheck=False, profile=True,linetrace=True

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

extensions=[ Extension("bnb_jung",
              ["bnb_jung.pyx"],
              libraries=["m"],
              extra_compile_args = ["-ffast-math", "-O3"])]

setup(name="bnb_jung", \
    cmdclass = {"build_ext": build_ext}, \
    ext_modules=extensions)
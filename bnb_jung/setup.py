#cython: boundscheck=False, wraparound=False, nonecheck=False, profile=True,linetrace=True

from distutils.core import setup
from distutils.extension import Extension
# from Cython.Distutils import build_ext
from Cython.Build import cythonize

from Cython.Compiler.Options import get_directive_defaults

directive_defaults = get_directive_defaults()

directive_defaults['linetrace'] = True
directive_defaults['binding'] = True
directive_defaults['profile'] = True

extensions=[ Extension("bnb_jung",
              ["bnb_jung.pyx"],
              libraries=["m"],
              extra_compile_args = ["-ffast-math"], 
              define_macros=[('CYTHON_TRACE', '1')])]

setup(name="bnb_jung", \
    # cmdclass = {"build_ext": build_ext}, \
    ext_modules=cythonize(extensions, \
        compiler_directives=directive_defaults))
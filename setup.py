import glob

from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup

# Set up extension module.
setup(
    ext_modules=[
        Pybind11Extension(
            name='pycombina._combina_bnb_solver',
            sources=[
                *glob.glob('src/combina_bnb_solver/*.cpp'),
                *glob.glob('src/combina_bnb_solver/**/*.cpp'),
            ]
        ),
    ]
)

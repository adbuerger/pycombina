# -*- coding: utf-8 -*-
#
# This file is part of pycombina.
#
# Copyright 2017-2018 Adrian Bürger, Clemens Zeile, Sebastian Sager, Moritz Diehl
#
# pycombina is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pycombina is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pycombina. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import platform
import subprocess

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

# This installation script is based on:
# - https://github.com/benjaminjack/python_cpp_example

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        if sys.version_info < (3,5):
            raise RuntimeError(
                "Python 3.5 or higher is required for using pycombina.")            
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the BnB solver extension")

        for ext in self.extensions:
            self.build_extension(ext)


    def build_extension(self, ext):
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)))

        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(
                cfg.upper(),
                extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''),
            self.distribution.get_version())

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args,
                              cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args,
                              cwd=self.build_temp)
        print()  # Add an empty line for cleaner output


setup(

    name='pycombina',
    version='0.2',

    author='Adrian Buerger, Clemens Zeile',
    author_email='adrian.buerger@hs-karlsruhe.de, clemens.zeile@ovgu.de',
    
    description='Python module for solving Combinatorial Integral Approximation problems',

    long_description='',
    
    ext_modules=[CMakeExtension('pycombina/_combina_bnb')],

    packages = find_packages(),

    install_requires=["numpy>=1.13"],

    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
    test_suite="test",
    )

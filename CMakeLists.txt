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

cmake_minimum_required(VERSION 2.8.12)
project(combina_bnb_solver)

# Set source directory
set(SOURCE_DIR "src/combina_bnb_solver")

# Tell CMake that headers are also in SOURCE_DIR
include_directories(${SOURCE_DIR})
file(GLOB SOURCES ${SOURCE_DIR}/*.cpp)
set(${SOURCES})

# Generate Python module
add_subdirectory(src/pybind11)
pybind11_add_module(_combina_bnb_solver ${SOURCES} "${SOURCE_DIR}/PythonBindings.cpp")

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# set(CMAKE_CXX_FLAGS "-O3 -Wpedantic -Wextra -I/usr/include/python3.6m")
IF (WIN32)
    set(CMAKE_CXX_FLAGS "/O2")
ELSE()
    set(CMAKE_CXX_FLAGS "-O3 -Wpedantic -Wextra")
ENDIF()

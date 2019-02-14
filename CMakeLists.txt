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

# Export compile commands for autocompletion and linting
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Find (optional) boost libraries
find_package(Boost 1.44.0 COMPONENTS iostreams)
if(Boost_FOUND)
  include_directories(${Boost_INCLUDE_DIRS})
  link_directories(${Boost_LIBRARY_DIRS})
endif()

# Set source directory
set(SOURCE_DIR "src/combina_bnb_solver")

# Tell CMake that headers are also in SOURCE_DIR
include_directories(${SOURCE_DIR})
file(GLOB_RECURSE SOURCES ${SOURCE_DIR}/*.cpp)
set(${SOURCES})

# Configure config.hpp.in
configure_file(${SOURCE_DIR}/config.hpp.in ${SOURCE_DIR}/config.hpp)
include_directories(${CMAKE_BINARY_DIR}/${SOURCE_DIR})

# Generate Python module
add_subdirectory(src/pybind11)
pybind11_add_module(_combina_bnb_solver ${SOURCES} "${SOURCE_DIR}/PythonBindings.cpp")
if(Boost_FOUND)
  target_link_libraries(_combina_bnb_solver PRIVATE Boost::iostreams)
endif()

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

IF (WIN32)
    set(CMAKE_CXX_FLAGS "/O2")
ELSE()
    set(CMAKE_CXX_FLAGS "-O3 -Wpedantic -Wextra")
ENDIF()

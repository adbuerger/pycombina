cmake_minimum_required(VERSION 2.8.12)
project(cia)

# Set source directory
set(SOURCE_DIR "pycombina/src")

# Tell CMake that headers are also in SOURCE_DIR
include_directories(${SOURCE_DIR})
file(GLOB SOURCES ${SOURCE_DIR}/*.cpp)
set(${SOURCES})

# Generate Python module
add_subdirectory(lib/pybind11)
pybind11_add_module(_combina_bnb_solver ${SOURCES} "${SOURCE_DIR}/PythonBindings.cpp")

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS "-Wall -Wextra -O3")

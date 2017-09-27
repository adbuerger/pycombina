# pycombina - Combinatorial Integral Approximation

Python module containing a Combinatorial Integral Approximation algorithm

## Prerequisites

### Python modules

In order to install pycombina, you need

```
setuptools

```

to be installed If you want to run the automated tests, you also need

```
unittest2

```

The module has been tested with Python2, but should also work with Python3.

### Other software

The (major) C++ part of pycombina is built using

```
g++
cmake
```

**Please note:** pycombina uses features available only from C++11 on and uses [pybind11](https://github.com/pybind/pybind11) (a copy is shipped with pycombina).


## How to install


For system-wide installation of the Python module, run

```
sudo python setup.py install
```

If you're working on the module, it's better to just set a link
to the containing folder, which can be done by running

```
sudo python setup.py develop
```

To use the automated tests, run

```
sudo python setup.py test
```

## How to use


For examples on how to use the module, please refer to the tests.

.. This file is part of pycombina.
..
.. Copyright 2017-2018 Adrian Bürger, Clemens Zeile, Sebastian Sager, Moritz Diehl
..
.. pycombina is free software: you can redistribute it and/or modify
.. it under the terms of the GNU Lesser General Public License as published by
.. the Free Software Foundation, either version 3 of the License, or
.. (at your option) any later version.
..
.. pycombina is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
.. GNU Lesser General Public License for more details.
..
.. You should have received a copy of the GNU Lesser General Public License
.. along with pycombina. If not, see <http://www.gnu.org/licenses/>.


How to install
==============

The following sections exemplify how pycombina can be installed on Ubuntu 18.04 / Debian 10 or Windows 10. Depending on your local setup, however, these instructions might need to be adapted.


Install on Ubuntu 18.04 / Debian 9
----------------------------------

First, install the following packages via apt (to install packages via apt, you might need root priviliges):

.. code:: Bash

    apt install python3-pip python3-dev cmake g++ git
    
Please note: Python version >= 3.5 is required to use pycombina. It is also possible to install pycombina in a Python virtual environment. 

Afterwards, clone the pycombina repository and the contained submodules by running: 

.. code:: Bash

    git clone https://github.com/adbuerger/pycombina.git
    cd pycombina
    git submodule init
    git submodule update

Finally, pycombina can be installed for your user by running

.. code:: Bash

    python3 setup.py install --user

from within the pycombina folder, which will also attempt to install package dependecies (numpy>=1.13) if not present, and build the BnB solver extension.

Please note: pycombina uses features available only from C++11 on and uses pybind11 [#f5]_ .

For using the MILP-based combinatorial integral approximation solver ``pycombina.CombinaMILP``, Gurobi and it's Python interface [#f4]_ must be available.

For running the webservice-example in ``examples/webservice_example.py``, Flask [#f9]_ is required.


Install on Windows 10
---------------------

For obtaining Python 3 on Windows, Anaconda [#f7]_ can be used. For building the C++ extensions of pycombina, a 64 bit Visual C++ compiler is required, which can be obtained, e. g., within Visual Studio Community [#f8]_, which is free for private and/or academic use.

After that, clone the pycombina repository from https://github.com/adbuerger/pycombina as described above, open an Anaconda Prompt, and run 

.. code:: Bash

    python setup.py install

from within the pycombina folder, which will also attempt to install package dependecies (numpy>=1.13) if not present, and build the BnB solver extension.

Please note: pycombina uses features available only from C++11 on and uses pybind11 [#f5]_ .

For using the MILP-based combinatorial integral approximation solver ``pycombina.CombinaMILP``, Gurobi and it's Python interface [#f4]_ must be available.


.. [#f5] |linkf5|_

.. _linkf5: https://github.com/pybind/pybind11

.. |linkf5| replace:: pybind11 at Github


.. [#f4] |linkf4|_

.. _linkf4: https://www.gurobi.com/

.. |linkf4| replace:: Gurobi website

.. [#f7] |linkf7|_


.. _linkf7: https://www.anaconda.com/

.. |linkf7| replace:: Anaconda website


.. [#f8] |linkf8|_

.. _linkf8: https://visualstudio.microsoft.com/

.. |linkf8| replace:: Visual Studio website


.. [#f9] |linkf9|_

.. _linkf9: https://github.com/pallets/flask

.. |linkf9| replace:: Flask at Github


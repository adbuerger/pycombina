#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of pycombina.
#
# Copyright 2017-2020 Adrian Bürger, Clemens Zeile, Sebastian Sager, Moritz Diehl
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
from flask import Flask, request, jsonify

import pycombina

class InvalidUsage(Exception):

    status_code = 400

    def __init__(self, message, status_code = None, payload = None):
        
        Exception.__init__(self)
        
        self.message = message
        
        if status_code is not None:
            self.status_code = status_code
        
        self.payload = payload


pycombina_service = Flask(__name__)

@pycombina_service.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    
    response = jsonify({ \
        'solver': None, \
        'solver_status': None, \
        'b_bin': None, \
        'eta': None, \
        'errors': error.message})

    response.status_code = error.status_code

    return response


def initialize_binapprox(problem_definition):

    t = problem_definition["t"]
    b_rel = problem_definition["b_rel"]

    binapprox_init_optional_args = {}

    try:
        binapprox_init_optional_args["binary_threshold"] = \
            problem_definition["binary_threshold"]
    except KeyError:
        pass

    try:
        binapprox_init_optional_args["reduce_problem_size_before_solve"] = \
            problem_definition["reduce_problem_size_before_solve"]
    except KeyError:
        pass

    try:
        binapprox = pycombina.BinApprox(t = t, b_rel = b_rel, **binapprox_init_optional_args)
    except Exception as e:
        raise InvalidUsage(str(e), status_code = 500)

    return binapprox


def set_binapprox_options(binapprox, problem_definition):

    try:
        binapprox.set_n_max_switches(problem_definition["n_max_switches"])
    except KeyError:
        pass
    except Exception as e:
        raise InvalidUsage(str(e), status_code = 500)

    try:
        binapprox.set_min_up_times(problem_definition["min_up_times"])
    except KeyError:
        pass
    except Exception as e:
        raise InvalidUsage(str(e), status_code = 500)

    try:
        binapprox.set_min_down_times(problem_definition["min_down_times"])
    except KeyError:
        pass
    except Exception as e:
        raise InvalidUsage(str(e), status_code = 500)

    try:
        binapprox.set_max_up_times(problem_definition["max_up_times"])
    except KeyError:
        pass
    except Exception as e:
        raise InvalidUsage(str(e), status_code = 500)

    try:
        binapprox.set_total_max_up_times(problem_definition["total_max_up_times"])
    except KeyError:
        pass
    except Exception as e:
        raise InvalidUsage(str(e), status_code = 500)

    try:
        binapprox.set_b_bin_pre(problem_definition["b_bin_pre"])
    except KeyError:
        pass
    except Exception as e:
        raise InvalidUsage(str(e), status_code = 500)

    try:
        if ("b_bin_valid" in problem_definition.keys()) or ("dt" in problem_definition.keys()):
            raise NotImplementedError( \
                "Using set_valid_controls_for_interval not yet supported in service application.")

        if ("b_i" in problem_definition.keys()) or ("b_valid_upcoming" in problem_definition.keys()):
            raise NotImplementedError( \
                "Using set_valid_control_transitions not yet supported in service application.")

    except Exception as e:
        raise InvalidUsage(str(e), status_code = 500)

    return binapprox


def setup_solver(problem_definition):

    if not "solver" in problem_definition.keys():
        return pycombina.CombinaBnB

    else:
        if problem_definition["solver"] == "CombinaMILP":
            return pycombina.CombinaMILP
        
        elif problem_definition["solver"] == "CombinaSUR":
            return pycombina.CombinaSUR

        else:
            return pycombina.CombinaBnB


@pycombina_service.route('/api/solve/', methods=['GET', 'POST'])
def solve():

    problem_definition = request.json

    binapprox = initialize_binapprox(problem_definition)
    binapprox = set_binapprox_options(binapprox, problem_definition)

    solver = setup_solver(problem_definition)(binapprox)
    solver.solve()

    response = jsonify({ \
        'solver': type(solver).__name__, \
        'solver_status': solver.status, \
        'b_bin': binapprox.b_bin.tolist(), \
        'eta': binapprox.eta, \
        'errors': None})

    return response

if __name__ == '__main__':
    
    pycombina_service.run(host= '0.0.0.0', port=6789, debug=True)

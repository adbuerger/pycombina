import os
from flask import Flask, request, jsonify

from pycombina import BinApprox, CombinaBnB, CombinaMILP, CombinaSUR

import ipdb

class InvalidUsage(Exception):

    status_code = 400

    def __init__(self, message, status_code = None, payload = None):
        
        Exception.__init__(self)
        
        self.message = message
        
        if status_code is not None:
            self.status_code = status_code
        
        self.payload = payload

    def to_dict(self):
        
        rv = dict(self.payload or ())
        rv['Error'] = self.message
        
        return rv


pycombina_server = Flask(__name__)

@pycombina_server.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    
    response = jsonify(error.to_dict())
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
        binapprox_init_optional_args["off_state_included"] = \
            problem_definition["off_state_included"]
    except KeyError:
        pass

    try:
        binapprox_init_optional_args["reduce_problem_size_before_solve"] = \
            problem_definition["reduce_problem_size_before_solve"]
    except KeyError:
        pass

    try:
        binapprox = BinApprox(t = t, b_rel = b_rel, **binapprox_init_optional_args)
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

    return binapprox


def setup_solver(problem_definition):

    if not "solver" in problem_definition.keys():

        return CombinaBnB

    else:

        if problem_definition["solver"] == "CombinaMILP":

            return CombinaMILP
        
        elif problem_definition["solver"] == "CombinaSUR":

            return CombinaSUR

        else:

            return CombinaBnB


@pycombina_server.route('/api/solve/', methods=['GET', 'POST'])
def solve():

    problem_definition = request.json

    binapprox = initialize_binapprox(problem_definition)
    binapprox = set_binapprox_options(binapprox, problem_definition)

    solver = setup_solver(problem_definition)(binapprox)
    solver.solve()

    result = {"solver": str(type(solver)), "b_bin": binapprox.b_bin.tolist(), \
        "eta": binapprox.eta}

    return str((result))

if __name__ == '__main__':
    
    pycombina_server.run(host= '0.0.0.0', port=1234, debug=True)

from pycombina import BinApprox
from flask import Flask, request, jsonify

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
        rv['message'] = self.message
        
        return rv


app = Flask(__name__)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response


@app.route('/api/solve/', methods=['GET', 'POST'])
def solve():

    content = request.json

    # raise InvalidUsage('This view is gone', status_code=500)

    t = content["t"]
    b_rel = content["b_rel"]

    try:
        tol = content["tol"]

    binaapprox = BinApprox(t = t, b_rel = b_rel, )

    return str((t, b_rel))

if __name__ == '__main__':
    
    app.run(host= '0.0.0.0', port=1234)

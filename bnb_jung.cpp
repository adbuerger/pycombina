#include <Python.h>
#include <bnbjung.cpp>

static PyObject* py_run_bnb_jung(PyObject* self, PyObject* args){

    PyObject *b_init_py;
    PyObject *b_py;
    int n_b;
    int sigma_max;

    PyArg_ParseTuple(args, "Oii", &b_init_py, &n_b, &sigma_max);

    double *b_init;
    b_init = (double *) malloc(n_b * sizeof(double));

    int j;

    for (j = 0; j < n_b; j++){

        b_py = PySequence_GetItem(b_init_py, j);
        b_init[j] = PyFloat_AsDouble(b_py);
    }

    bnb_input bnb_input_data;
    bnb_output bnb_output_data;

    bnb_input_data.b_data = b_init;
    bnb_input_data.n_b = n_b;
    bnb_input_data.sigma_max = sigma_max;

    bnb_jung(&bnb_input_data, &bnb_output_data);


    PyObject *b_opt_by = PyList_New(n_b);

    for(int j = 0; j < n_b; j++){

        PyObject *b = PyInt_FromLong(bnb_output_data.b_data[j]);
        PyList_SET_ITEM(b_opt_by, j, b);
    }
    
    return b_opt_by;

}

static PyMethodDef bnbJungModule_methods[] = {
  {"run_bnb_jung", py_run_bnb_jung, METH_VARARGS},
  {NULL, NULL}
};


extern "C" void initbnb_jung(void)
{
  (void) Py_InitModule("bnb_jung", bnbJungModule_methods);
}


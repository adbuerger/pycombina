#include <cia.hpp>

#include <Python.h>

#include <queue>
#include <vector>
#include <iostream>
#include <iomanip>
#include <cmath>
#include <map>
#include <algorithm>
#include <iterator>
#include <ctime>

using namespace std;

bool node_comparison::operator()(const node& node_1, const node& node_2){

    if (node_1.priority != node_2.priority){

        return node_1.priority > node_2.priority;
    }

    else{

        if (node_1.d != node_2.d) {

            return node_1.d < node_2.d;
        }
        else{

            return node_1.k > node_2.k;
        }
    }
}


void cia(const bnb_input &bnb_data_init, bnb_output *bnb_output_data){

    int i;

    vector<int> b_opt_bin;
    vector<int>::iterator it_b_opt_bin;

    int b_opt[bnb_data_init.n_b];

    double priority_k;
    int d_k = 0;

    int k = -1;
    double eta_k;
    int k_prev = -1;

    int p_k;
    int sigma_k;

    int n_bnb_iterations = 0;

    clock_t t_start;
    clock_t t_end;

    t_start = clock();

    double delta_b_opt_p_k_true [bnb_data_init.n_b];
    double delta_b_opt_p_k_false [bnb_data_init.n_b];

    cout << setprecision(15) << "\n-----------------------------------------------------------\n";
    cout << setprecision(15) << "|                                                         |\n";
    cout << setprecision(15) << "| Combinatorial Integral Approximation - Branch and Bound |\n";
    cout << setprecision(15) << "|                                                         |\n";
    cout << setprecision(15) << "-----------------------------------------------------------\n";

    cout << setprecision(15) << "\nRunning Combinatorial Integral Approximation ...\n";


    cout << setprecision(15) << "\n- Running preparation phase ...\n";

    delta_b_opt_p_k_true[bnb_data_init.n_b-1] = 
        bnb_data_init.b_data[bnb_data_init.n_b-1] - 1;
    delta_b_opt_p_k_false[bnb_data_init.n_b-1] =
        bnb_data_init.b_data[bnb_data_init.n_b-1];

    for (i = bnb_data_init.n_b-2; i >=0; i--){
        delta_b_opt_p_k_true[i] = delta_b_opt_p_k_true[i+1] + bnb_data_init.b_data[i] - 1;
        delta_b_opt_p_k_false[i] = delta_b_opt_p_k_false[i+1] + bnb_data_init.b_data[i];
    }


    priority_queue<node, vector<node>, node_comparison> q;

    map<int, node> q_selected;
    map<int, node>::iterator it_q_selected;

    node a;

    for (p_k = 0; p_k <= 1; p_k++){

        k++;

        eta_k = bnb_data_init.b_data[d_k] - p_k;
        priority_k = fmax(0.0, fabs(eta_k));

        sigma_k = 0;

        q.push({priority_k, d_k, k, eta_k, k_prev, p_k, sigma_k});

    }

    t_end = clock();

    cout << setprecision(15) << "  Preparation phase finished after " << double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";


    cout << setprecision(15) << "\n- Running Branch and Bound ...\n";

    t_start = clock();

    while(!q.empty()){

        n_bnb_iterations++;

        a = q.top();
        q.pop();

        q_selected.insert(std::pair<int, node>(a.k, a));

        if (a.d == bnb_data_init.n_b){

            t_end = clock();

            cout << setprecision(15) << "  Branch and bound finished after " << double(t_end - t_start) / CLOCKS_PER_SEC << " s\n\n";

            cout << "  * Number of iterations: " << n_bnb_iterations << "\n";
            cout << "  * Number of nodes produced: " << k << "\n";
            cout << "  * eta: " << a.eta << "\n";

            cout << setprecision(15) << "\n- Retrieve solution from nodes ...\n";

            t_start = clock();

            b_opt_bin.insert(b_opt_bin.begin(), a.p);
            k_prev = a.k_prev;

            i = bnb_data_init.n_b-1;

            while (k_prev != -1){

                it_q_selected = q_selected.find(k_prev);
                a = it_q_selected->second;

                i--;
                b_opt_bin.insert(b_opt_bin.begin(), a.p);
                k_prev = a.k_prev;

            }

            while (i > 0){

                b_opt_bin.insert(b_opt_bin.end(), a.p);
                i--;
            }

            i = 0;


            for(it_b_opt_bin = b_opt_bin.begin(); it_b_opt_bin < b_opt_bin.end(); it_b_opt_bin++){

                b_opt[i] = *it_b_opt_bin;
                i++;
            }


            for(i = 0; i < bnb_data_init.n_b; i++){

                bnb_output_data->b_data[i] = b_opt[i];
            }

            t_end = clock();

            cout << setprecision(15) << "  Retrieving finished after " << double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";
        
            cout << setprecision(15) << "\nCombinatorial Integral Approximation finished.\n\n";
        
            break;
        }

        else {

            for (p_k = 0; p_k <= 1; p_k++){

                k++;
                d_k = a.d + 1;

                eta_k = a.eta + (bnb_data_init.b_data[d_k] - p_k);

                sigma_k = a.sigma + abs(a.p - p_k);

                if (sigma_k == bnb_data_init.sigma_max){

                    if (p_k == 0){

                        eta_k = eta_k + delta_b_opt_p_k_false[d_k+1];
                    }
                    else if (p_k == 1){

                        eta_k = eta_k + delta_b_opt_p_k_true[d_k+1];
                    }

                    d_k = bnb_data_init.n_b;
                }

                priority_k = fmax(a.priority, fabs(eta_k));
                q.push({priority_k, d_k, k, eta_k, a.k, p_k, sigma_k});
            }
        }
    }
};


static PyObject* py_run_cia(PyObject* self, PyObject* args){

    PyObject *b_init_py;
    PyObject *b_py;
    int n_b;
    int sigma_max;

    PyArg_ParseTuple(args, "Oii", &b_init_py, &n_b, &sigma_max);

    double *b_init = new double[n_b];

    for (int j = 0; j < n_b; j++){

        b_py = PySequence_GetItem(b_init_py, j);
        b_init[j] = PyFloat_AsDouble(b_py);
    }

    bnb_input bnb_input_data;
    bnb_output bnb_output_data;

    bnb_input_data.b_data = b_init;
    bnb_input_data.n_b = n_b;
    bnb_input_data.sigma_max = sigma_max;

    bnb_output_data.b_data = new int[n_b];

    cia(bnb_input_data, &bnb_output_data);


    PyObject *b_opt_py = PyList_New(n_b);

    for(int j = 0; j < n_b; j++){

        PyObject *b = PyInt_FromLong(bnb_output_data.b_data[j]);
        PyList_SET_ITEM(b_opt_py, j, b);
    }
    
    delete[] b_init;
    delete[] bnb_output_data.b_data;

    return b_opt_py;

}

static PyMethodDef ciaModule_methods[] = {
  {"run_cia", py_run_cia, METH_VARARGS},
  {NULL, NULL}
};


extern "C" void initcia(void)
{
  (void) Py_InitModule("cia", ciaModule_methods);
}


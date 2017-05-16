#include <queue>
#include <vector>
#include <iostream>
#include <iomanip>
#include <cmath>
#include <map>
#include <algorithm>
#include <iterator>
#include <ctime>



class BnBJung{

private:
    double *b_init;
    int n_b;
    int sigma_max;
    double *b_opt;
    
public:
    struct node;
    struct compare_nodes;

    void run_bnb();
    BnBJung(double *b_init, int n_b, int sigma_max);
    ~BnBJung();
};

struct BnBJung::node{

    double priority;
    int d;
    int k;

    double eta;
    int k_prev;
    
    int p;
    int sigma;

};

struct compare_nodes{

    bool operator()(const node& node_1, const node& node_2){

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
};


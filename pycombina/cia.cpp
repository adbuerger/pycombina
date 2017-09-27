// cia.cpp

#include <cia.hpp>

#ifndef VECTOR_H
#define VECTOR_H
#include <vector>
#endif

#include <iostream>
#include <queue>
#include <algorithm>


std::vector<int> cia(const std::vector<double>& b_rel, const int& sigma_max){

    std::vector<double> delta_b_bin_p_k_true (b_rel.size());
    std::vector<double> delta_b_bin_p_k_false (b_rel.size());

    bnb_tree_map bnb_tree;

    std::vector<int> b_bin;

    input_validation(b_rel);

    welcome_prompt();

    cia_preparation_phase(b_rel, delta_b_bin_p_k_true, delta_b_bin_p_k_false);    

    cia_main_phase(b_rel, sigma_max, delta_b_bin_p_k_true, delta_b_bin_p_k_false, bnb_tree);

    cia_postprocessing_phase(bnb_tree, b_bin);

    return b_bin;

};


void input_validation(const std::vector<double>& b_rel){

    for(double b : b_rel){

        if (0.0 > b || b > 1.0){

            throw std::invalid_argument("For all entries b in b_rel it must hold that 0 <= b <= 1.");

        }

    }

};


void welcome_prompt(){

    std::cout << "\n-----------------------------------------------------------\n";
    std::cout << "|                                                         |\n";
    std::cout << "|    pycombina -- Combinatorial Integral Approximation    |\n";
    std::cout << "|                                                         |\n";
    std::cout << "-----------------------------------------------------------\n";

};


void cia_preparation_phase(const std::vector<double>& b_rel, 
    std::vector<double>& delta_b_bin_p_k_true, 
    std::vector<double>& delta_b_bin_p_k_false){
    
    clock_t t_start;
    clock_t t_end;

    std::cout << "\n- Running preparation phase ...\n";

    t_start = clock();

    delta_b_bin_p_k_true.at(delta_b_bin_p_k_true.size() - 1) = 
        b_rel.at(b_rel.size() - 1) - 1;

    delta_b_bin_p_k_false.at(delta_b_bin_p_k_false.size() - 1) = 
        b_rel.at(b_rel.size() - 1);

    for(int i = b_rel.size() - 2; i >= 0; i--){

        delta_b_bin_p_k_true.at(i) = delta_b_bin_p_k_true.at(i+1) + b_rel.at(i) - 1;
        delta_b_bin_p_k_false.at(i) = delta_b_bin_p_k_false.at(i+1) + b_rel.at(i);

    }

    t_end = clock();

    std::cout << "  Preparation phase finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";

};


void cia_main_phase(const std::vector<double>& b_rel, const int& sigma_max,
    const std::vector<double>& delta_b_bin_p_k_true, 
    const std::vector<double>& delta_b_bin_p_k_false, 
    bnb_tree_map& bnb_tree){

    clock_t t_start;
    clock_t t_end;

    double priority_k;
    short unsigned int d_k = 0;

    int k = -1;
    double eta_k;
    int k_prev = -1;

    short unsigned int p_k;
    short unsigned int sigma_k;

    int n_bnb_iterations = 0;

    std::priority_queue<bnb_node, std::vector<bnb_node>, 
        bnb_node_priority_comparison> bnb_queue;

    bnb_node a;

    std::cout << "\n- Running Combinatorial Integral Approximation ...\n";

    t_start = clock();

    for (p_k = 0; p_k <= 1; p_k++){

        k++;

        eta_k = b_rel.at(d_k) - p_k;
        priority_k = fmax(0.0, fabs(eta_k));

        sigma_k = 0;

        bnb_queue.push({priority_k, d_k, k, eta_k, k_prev, p_k, sigma_k});

    }


    while(!bnb_queue.empty()){

        n_bnb_iterations++;

        a = bnb_queue.top();
        bnb_queue.pop();

        bnb_tree.insert(std::pair<int, bnb_node>(a.k, a));

        if (a.d == b_rel.size()){

            break;

        }

        else {

            for (p_k = 0; p_k <= 1; p_k++){

                k++;
                d_k = a.d + 1;

                eta_k = a.eta + (b_rel.at(d_k) - p_k);

                sigma_k = a.sigma + abs(a.p - p_k);

                if (sigma_k == sigma_max){

                    if (p_k == 0){

                        eta_k += delta_b_bin_p_k_false[d_k+1];
                    }
                    else if (p_k == 1){

                        eta_k += delta_b_bin_p_k_true[d_k+1];
                    }

                    d_k = b_rel.size();
                }

                priority_k = fmax(a.priority, fabs(eta_k));
                bnb_queue.push({priority_k, d_k, k, eta_k, a.k, p_k, sigma_k});
            }
        }
    }


    t_end = clock();

    std::cout << "  Branch and bound finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n\n";

    std::cout << "  * Number of iterations: " << n_bnb_iterations << "\n";
    std::cout << "  * Number of BnB nodes produced: " << k << "\n";
    std::cout << "  * eta: " << a.eta << "\n";

};


void cia_postprocessing_phase(bnb_tree_map& bnb_tree, 
    std::vector<int>& b_bin){

    int n_b;

    bnb_node a;

    bnb_tree_map::iterator it_bnb_tree;

    clock_t t_start;
    clock_t t_end;

    std::cout << "\n- Running post-processing phase ...\n";

    t_start = clock();

    bnb_tree_map::iterator final_node_entry = std::max_element(
        bnb_tree.begin(), bnb_tree.end(), bnb_queue_order_comparison);

    a = final_node_entry->second;

    b_bin.insert(b_bin.begin(), a.p);
    
    n_b = a.d;

    while(a.k_prev != -1){
    
        it_bnb_tree = bnb_tree.find(a.k_prev);
        a = it_bnb_tree->second;
        b_bin.insert(b_bin.begin(), a.p);

    }

    while(b_bin.size() < n_b) {

        b_bin.insert(b_bin.end(), a.p);

    }

    t_end = clock();

    std::cout << "  Post-processing finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";

};


bool bnb_queue_order_comparison(const std::pair<int, bnb_node>& pair_a, 
    const std::pair<int, bnb_node>& pair_b){

    return pair_a.second.d < pair_b.second.d;
};


bool bnb_node_priority_comparison::operator()(const bnb_node& node_a, const bnb_node& node_b){

    if (node_a.priority != node_b.priority){

        return node_a.priority > node_b.priority;
    }

    else{

        if (node_a.d != node_b.d) {

            return node_a.d < node_b.d;
        }
        else{

            return node_a.k > node_b.k;
        }
    }
}

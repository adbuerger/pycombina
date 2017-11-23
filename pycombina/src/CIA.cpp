/*
 *
 * CIA.cpp
 *
 */

#include <iostream>

#ifndef ALGORITHM_H
#define ALGORITHM_H
#include <algorithm>
#endif

#ifndef BNB_NODE_H
#define BNB_NODE_H
#include "BnBNode.hpp"
#endif

#include "CIA.hpp"


CIA::CIA(const std::vector<double>& T, const std::vector<std::vector<double>>& b_rel)

    : T(T), 
      b_rel(b_rel),

      N_c(0),
      N_b(0),

      eta(0.0),
      Tg(T.size()-1),

      ptr_bnb_node_queue(new std::priority_queue<BnBNode*, std::vector<BnBNode*>,
        BnBNodeComparison>()),
      ptr_best_node(NULL),

      b_bin(b_rel[0].size()),

      eta_node(b_rel.size()),
      
      eta_parent(b_rel.size()),
      sigma_node(b_rel.size()),

      sum_eta(2, std::vector<std::vector<double>> (b_rel.size(), std::vector<double> (b_rel[0].size())))

{

    welcome_prompt();
    validate_input_data();

}


CIA::~CIA(){

}


void CIA::welcome_prompt(){

    std::cout << "\n-----------------------------------------------------------\n";
    std::cout << "|                                                         |\n";
    std::cout << "|    pycombina -- Combinatorial Integral Approximation    |\n";
    std::cout << "|                                                         |\n";
    std::cout << "-----------------------------------------------------------\n";

}


void CIA::validate_input_data() {

    determine_number_of_controls();
    determine_number_of_control_intervals();
    validate_input_dimensions();
    validate_input_values();
}


void CIA::determine_number_of_controls() {

    N_c = b_rel.size();
}


void CIA::determine_number_of_control_intervals() {

    N_b = T.size() - 1;
}


void CIA::validate_input_dimensions() {

    for(std::vector<double> b_rel_i: b_rel) {

        if (b_rel_i.size() != N_b) {

            throw std::invalid_argument("All elements in b_rel must contain one more entry that T.");

        }

    }
}


void CIA::validate_input_values() {

    validate_input_values_T();
    validate_input_values_b_rel();

}


void CIA::validate_input_values_T() {

    for(unsigned int i = 1; i < T.size(); i++) {

        if((T[i] - T[i-1]) <= 0.0) {

            throw std::invalid_argument("Values in T must be strictly increasing.");

        }
    }
}


void CIA::validate_input_values_b_rel() {

    for(std::vector<double> b_rel_i: b_rel){

        for(double b: b_rel_i) {

            if(b < 0.0 || b > 1.0) {

                throw std::invalid_argument("All elements of the relaxed binary input must be 0 <= b <= 1.");

            }
        }

    }
}


void CIA::run_cia(std::vector<unsigned int> n_max_switches) {

    set_sigma_max(n_max_switches);
    prepare_bnb_data();
    initialize_bnb_queue();
    run_bnb();
    retrieve_solution();

}


void CIA::set_sigma_max(std::vector<unsigned int> n_max_switches) {

    sigma_max = n_max_switches;
}


void CIA::prepare_bnb_data() {

    clock_t t_start;
    clock_t t_end;

    std::cout << "\n- Preparing data for Branch and Bound ...\n";

    t_start = clock();


    compute_time_grid_from_time_points();
    compute_initial_upper_bound();
    precompute_sum_of_etas();


    t_end = clock();

    std::cout << "  Preparation phase finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";

}


void CIA::compute_time_grid_from_time_points() {

    for(unsigned int i = 1; i < N_b+1; i++) {

        Tg[i-1] = T[i] - T[i-1];
    }
}


void CIA::compute_initial_upper_bound() {

    for(unsigned int i = 0; i < N_b; i++) {

        eta += Tg[i];
    }
}


void CIA::precompute_sum_of_etas() {

    for(unsigned int i = 0; i < N_c; i++) {

        sum_eta[0][i][N_b-1] = Tg[N_b-1] * (b_rel[i][N_b-1]);
        sum_eta[1][i][N_b-1] = Tg[N_b-1] * (b_rel[i][N_b-1] - 1);

        for(int j = N_b-2; j >= 0; j--) {

            sum_eta[0][i][j] = sum_eta[0][i][j+1] + Tg[j] * b_rel[i][j];
            sum_eta[1][i][j] = sum_eta[1][i][j+1] + Tg[j] * (b_rel[i][j] - 1);
        }
    }
}


void CIA::initialize_bnb_queue() {

    clock_t t_start;
    clock_t t_end;

    std::cout << "\n- Initializing Branch and Bound queue ...\n";

    t_start = clock();

    add_initial_nodes_to_bnb_queue();

    t_end = clock();

    std::cout << "  Initialization finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";
}


void CIA::add_initial_nodes_to_bnb_queue() {

    std::fill(eta_parent.begin(), eta_parent.end(), 0);
    lb_parent = 0.0;

    active_control = 0;

    while(active_control <= N_c) {

        depth_node = 1;

        compute_eta_of_current_node();
        compute_lower_bound_of_node();
        add_node_to_bnb_queue(NULL);

        active_control++;
    }
}


void CIA::compute_eta_of_current_node() {

    for(unsigned int i = 0; i < N_c; i++){

        eta_node[i] = eta_parent[i] + Tg[depth_node - 1] * 
            (b_rel[i][depth_node - 1] - double(active_control == i));
    }
}


void CIA::compute_lower_bound_of_node() {

    lb_node = 0.0;

    for(unsigned int j = 0; j < N_c; j++){

        lb_node = fmax(lb_node, fabs(eta_node[j]));
    }

    lb_node = fmax(lb_parent, fabs(lb_node));
}


void CIA::add_node_to_bnb_queue(BnBNode * ptr_parent_node) {

    BnBNode * ptr_child_node = NULL;

    if(lb_node < eta) {

        ptr_child_node = new BnBNode(ptr_parent_node, active_control, 
            sigma_node, depth_node, eta_node, lb_node);
        ptr_bnb_node_queue->push(ptr_child_node);
    }
}


void CIA::run_bnb() {

    clock_t t_start;
    clock_t t_end;

    unsigned int n_iterations = 0;

    std::cout << "\n- Running Branch and Bound ...\n";

    t_start = clock();


    BnBNode * ptr_active_node;

    while (!ptr_bnb_node_queue->empty()) {

        n_iterations++;

        ptr_active_node = ptr_bnb_node_queue->top();
        ptr_bnb_node_queue->pop();

        if(ptr_active_node->get_eta_branch() < eta) {

            if(ptr_active_node->get_depth() == N_b) {     
                
                update_best_solution(ptr_active_node);
                break;
            }

            else {

                add_child_nodes_to_bnb_queue(ptr_active_node);
            }
        }

        else {

            delete_node(ptr_active_node);

        }
    }

    t_end = clock();

    std::cout << "  Branch and Bound finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";
}


void CIA::update_best_solution(BnBNode * ptr_active_node) {

    if (ptr_best_node != NULL) {

        delete_node(ptr_best_node);
    }

    ptr_best_node = ptr_active_node;
    eta = ptr_best_node->get_eta_branch();

    display_solution_update(ptr_best_node);

}


void CIA::display_solution_update(BnBNode * ptr_best_node) {

    std::cout << "  Found solution with eta = " 
        << ptr_best_node->get_eta_branch() << "\n";

}


void CIA::add_child_nodes_to_bnb_queue(BnBNode * ptr_parent_node) {
    
    eta_parent = ptr_parent_node->get_eta_node();
    lb_parent = ptr_parent_node->get_eta_branch();

    active_control = 0;

    while(active_control <= N_c) {

        depth_node = ptr_parent_node->get_depth() + 1;

        compute_eta_of_current_node();
        increment_sigma_on_active_control_change(ptr_parent_node);
        compute_lower_bound_of_node();
        add_node_to_bnb_queue(ptr_parent_node);

        active_control++;
    }
}


void CIA::increment_sigma_on_active_control_change(BnBNode * ptr_parent_node) {

    sigma_node = ptr_parent_node->get_sigma();

    if(active_control != ptr_parent_node->get_active_control()){

        if(ptr_parent_node->get_active_control() != N_c){

            sigma_node[ptr_parent_node->get_active_control()]++;
        }

        if(active_control != N_c){

            sigma_node[active_control]++;
        }

        for(unsigned int i = 0; i < N_c; i++){

            if(sigma_node[i] == sigma_max[i]){

                for(unsigned int j = 0; j < N_c; j++){

                    eta_node[j] +=  sum_eta[int(active_control == j)][j][depth_node];                              
                }

                depth_node = N_b;

                break;
            }
        }
    }
}


void CIA::delete_node(BnBNode * ptr_active_node) {

    delete ptr_active_node;
}


void CIA::retrieve_solution() {

    clock_t t_start;
    clock_t t_end;

    int node_range_end;
    int node_range_begin;

    std::cout << "\n- Retrieving Branch and Bound solution ...\n";

    t_start = clock();

    BnBNode * ptr_active_node = ptr_best_node;

    while(ptr_active_node != NULL){

        node_range_end = (ptr_active_node->get_depth() - 1);
        BnBNode * ptr_preceding_node = ptr_active_node->get_ptr_parent_node();

        if(ptr_preceding_node != NULL) {

            node_range_begin = ptr_preceding_node->get_depth();
        }

        else {
        
            node_range_begin = 0;
        }

        for(int i = node_range_end; i >= node_range_begin; i--) {

            b_bin[i] = ptr_active_node->get_active_control();
        }

        ptr_active_node = ptr_active_node->get_ptr_parent_node();
    }


    t_end = clock();

    std::cout << "  Reconstructing the solution finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";

}


// get-functions

std::vector<double> CIA::get_T() {

    return T;
}


std::vector<std::vector<double>> CIA::get_b_rel() {

    return b_rel;
}


std::vector<unsigned int> CIA::get_sigma_max() {

    return sigma_max;
}


std::vector<double> CIA::get_Tg() {

    return Tg;
}


double CIA::get_eta() {

    return eta;
}


std::vector<unsigned int> CIA::get_b_bin() {

    return b_bin;
}


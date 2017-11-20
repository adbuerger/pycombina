/*
 *
 * CIA.cpp
 *
 */

#include <iostream>
#include <algorithm>

#ifndef BNB_NODE_H
#define BNB_NODE_H
#include "BnBNode.hpp"
#endif

#include "CIA.hpp"


CIA::CIA(const std::vector<double>& T, const std::vector<double>& b_rel)

    : T(T), 
      b_rel(b_rel),

      N(0),
      eta(0.0),
      Tg(T.size()-1),

      ptr_bnb_node_queue(new std::priority_queue<BnBNode*, std::vector<BnBNode*>,
        BnBNodeComparison>()),
      ptr_best_node(NULL),

      b_bin(b_rel.size())

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

    validate_input_dimensions();
    validate_input_values();
}


void CIA::validate_input_dimensions() {

    if (T.size() != b_rel.size()+1) {

        throw std::invalid_argument("T must contain one element more than b_rel.");

    }
}


void CIA::validate_input_values() {

    validate_input_values_T();
    validate_input_values_b_rel();

}


void CIA::validate_input_values_T() {

    for(unsigned int i = 1; i < T.size(); i++) {

        if((T.at(i) - T.at(i-1)) <= 0.0) {

            throw std::invalid_argument("Values in T must be strictly increasing.");

        }
    }
}


void CIA::validate_input_values_b_rel() {

    for(double b: b_rel) {

        if(b < 0.0 || b > 1.0) {

            throw std::invalid_argument("All elements b of the relaxed binary input must be 0 <= b <= 1.");

        }
    }
}


void CIA::run_cia(int n_max_switches) {

    set_sigma_max(n_max_switches);
    prepare_bnb_data();
    initialize_bnb_queue();
    run_bnb();
    retrieve_solution();

}


void CIA::set_sigma_max(int n_max_switches) {

    sigma_max = n_max_switches;
}


void CIA::prepare_bnb_data() {

    clock_t t_start;
    clock_t t_end;

    std::cout << "\n- Preparing data for Branch and Bound ...\n";

    t_start = clock();


    determine_number_of_control_intervals();
    compute_time_grid_from_time_points();
    compute_initial_upper_bound();


    t_end = clock();

    std::cout << "  Preparation phase finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";

}


void CIA::determine_number_of_control_intervals() {

    N = b_rel.size();
}


void CIA::compute_time_grid_from_time_points() {

    for(unsigned int i = 1; i < N+1; i++) {

        Tg.at(i-1) = T.at(i) - T.at(i-1);
    }
}


void CIA::compute_initial_upper_bound() {

    for(unsigned int i = 0; i < N; i++) {

        eta += Tg.at(i);
    }
}


void CIA::initialize_bnb_queue() {

    clock_t t_start;
    clock_t t_end;

    std::cout << "\n- Initializing Branch and Bound queue ...\n";

    t_start = clock();


    BnBNode * ptr_parent_node = NULL;

    add_nodes_to_bnb_queue(ptr_parent_node);


    t_end = clock();

    std::cout << "  Initialization finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";

}


void CIA::add_nodes_to_bnb_queue(BnBNode * ptr_parent_node) {

    BnBNode * ptr_child_node = NULL;

    int sigma_node;
    unsigned int depth_node;
    double eta_node;
    double lb_node;
    double lb_parent;

    for(unsigned int b = 0; b <= 1; b++) {

        if (ptr_parent_node != NULL) {

            depth_node = ptr_parent_node->get_depth() + 1;

            eta_node = ptr_parent_node->get_eta_node() + 
                Tg.at(depth_node - 1) * (b_rel.at(depth_node - 1) - b);
            
            sigma_node = ptr_parent_node->get_sigma() +
                abs(ptr_parent_node->get_b() - b);

            lb_parent = ptr_parent_node->get_eta_branch();
        }

        else {

            sigma_node = 0;
            depth_node = 1;

            eta_node = Tg.at(depth_node - 1) * (b_rel.at(depth_node - 1) - b);
            lb_parent = 0.0;
        }

        if((sigma_max > 0) && (sigma_node == sigma_max) && (depth_node < N)) {

            for(unsigned int i = depth_node; i < N; i++){

                eta_node += Tg.at(i) * (b_rel.at(i) - b);
            }

            depth_node = N;
        }

        lb_node = fmax(lb_parent, fabs(eta_node));

        if(lb_node < eta) {

            ptr_child_node = new BnBNode(ptr_parent_node, b, 
                sigma_node, depth_node, eta_node, lb_node);
            ptr_bnb_node_queue->push(ptr_child_node);
        }
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

            if(ptr_active_node->get_depth() == N) {     
                
                update_best_solution(ptr_active_node);
                // break;
            }

            else {

                create_new_child_nodes(ptr_active_node);
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


void CIA::create_new_child_nodes(BnBNode * ptr_parent_node) {
    
    add_nodes_to_bnb_queue(ptr_parent_node);
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

            b_bin.at(i) = ptr_active_node->get_b();
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


std::vector<double> CIA::get_b_rel() {

    return b_rel;
}


int CIA::get_sigma_max() {

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


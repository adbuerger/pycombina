/*
 *
 * CombinaBnBSolver.cpp
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

#include "CombinaBnBSolver.hpp"


CombinaBnBSolver::CombinaBnBSolver(const std::vector<double>& Tg, 
        const std::vector<std::vector<double>>& b_rel,
        const unsigned int& N_c, const unsigned int& N_b)

    : Tg(Tg),
      b_rel(b_rel),

      N_c(N_c),
      N_b(N_b),

      eta_max(0.0),

      ptr_best_node(NULL),

      b_bin(b_rel.size(), std::vector<unsigned int>(b_rel[0].size(), 0)),

      eta_node(b_rel.size()),
      
      eta_parent(b_rel.size()),
      sigma_node(b_rel.size()),

      sum_eta(2, std::vector<std::vector<double>> (b_rel.size(), std::vector<double> (b_rel[0].size()))),

      n_iterations(0)

{

}


CombinaBnBSolver::~CombinaBnBSolver(){

    delete ptr_best_node;
}


void CombinaBnBSolver::run(std::vector<unsigned int> max_switches, 
    std::vector<double> min_up_time) {

    set_sigma_max(max_switches);
    set_dwell_time(min_up_time);
    prepare_bnb_data();
    initialize_bnb_queue();
    run_bnb();
    retrieve_solution();
}


void CombinaBnBSolver::set_sigma_max(std::vector<unsigned int> n_max_switches) {

    sigma_max = n_max_switches;
}


void CombinaBnBSolver::set_dwell_time(std::vector<double> min_up_time) {

    dwell_time = min_up_time;
}


void CombinaBnBSolver::prepare_bnb_data() {

    clock_t t_start;
    clock_t t_end;

    std::cout << "\n- Preparing data for Branch and Bound ...\n";

    t_start = clock();

    compute_initial_upper_bound();
    precompute_sum_of_etas();

    t_end = clock();

    std::cout << "  Preparation phase finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";

}


void CombinaBnBSolver::compute_initial_upper_bound() {

    for(unsigned int i = 0; i < N_b; i++) {

        eta_max += Tg[i];
    }
}


void CombinaBnBSolver::precompute_sum_of_etas() {

    for(unsigned int i = 0; i < N_c; i++) {

        sum_eta[0][i][N_b-1] = Tg[N_b-1] * (b_rel[i][N_b-1]);
        sum_eta[1][i][N_b-1] = Tg[N_b-1] * (b_rel[i][N_b-1] - 1.0);

        for(int j = N_b-2; j >= 0; j--) {

            sum_eta[0][i][j] = sum_eta[0][i][j+1] + Tg[j] * b_rel[i][j];
            sum_eta[1][i][j] = sum_eta[1][i][j+1] + Tg[j] * (b_rel[i][j] - 1.0);
        }
    }
}


void CombinaBnBSolver::initialize_bnb_queue() {

    clock_t t_start;
    clock_t t_end;

    std::cout << "\n- Initializing Branch and Bound queue ...\n";

    t_start = clock();

    add_initial_nodes_to_bnb_queue();

    t_end = clock();

    std::cout << "  Initialization finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";
}


void CombinaBnBSolver::add_initial_nodes_to_bnb_queue() {

    std::fill(eta_parent.begin(), eta_parent.end(), 0);
    lb_parent = 0.0;

    active_control = 0;

    while(active_control <= N_c) {

        depth_node = 0;

        compute_eta_of_current_node(NULL);
        set_lower_bound_of_branch();
        add_node_to_bnb_queue(NULL);

        active_control++;
    }
}


void CombinaBnBSolver::compute_eta_of_current_node(BnBNode * ptr_parent_node) {

    double time_step(0.0);

    if (ptr_parent_node) {

        if(active_control == ptr_parent_node->get_active_control()){

            time_step = *std::max_element(dwell_time.begin(), dwell_time.end());
        }
    }

    eta_node = eta_parent;

    do {

        increas_eta_node();
        time_step += Tg[depth_node];

    } while((!std::all_of(dwell_time.begin(), dwell_time.end(), 
            [=](double dt){return dt <= time_step;})) && (depth_node < N_b));
}


void CombinaBnBSolver::increas_eta_node() {

    for(unsigned int i = 0; i < N_c; i++){

        if(sigma_node[i] < sigma_max[i]) {
        
            eta_node[i] += Tg[depth_node] * 
                (b_rel[i][depth_node] - double(active_control == i));
        }
    }

    depth_node++;
}


void CombinaBnBSolver::set_lower_bound_of_branch() {

    lb_node = 0.0;

    for(unsigned int j = 0; j < N_c; j++){

        lb_node = fmax(lb_node, fabs(eta_node[j]));
    }

    lb_node = fmax(lb_parent, fabs(lb_node));
}


void CombinaBnBSolver::add_node_to_bnb_queue(BnBNode * ptr_parent_node) {

    BnBNode * ptr_child_node = NULL;

    if(lb_node < eta_max) {

        ptr_child_node = new BnBNode(ptr_parent_node, active_control, 
            sigma_node, depth_node, eta_node, lb_node);
        bnb_node_queue.push(ptr_child_node);
    }
}


void CombinaBnBSolver::run_bnb() {

    clock_t t_start;
    clock_t t_end;

    std::cout << "\n- Running Branch and Bound ...\n";

    t_start = clock();


    BnBNode * ptr_active_node;

    while (!bnb_node_queue.empty()) {

        n_iterations++;

        ptr_active_node = bnb_node_queue.top();
        bnb_node_queue.pop();

        if(ptr_active_node->get_lb_branch() < eta_max) {

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


void CombinaBnBSolver::update_best_solution(BnBNode * ptr_active_node) {

    set_new_best_node(ptr_active_node);
    display_solution_update();
}


void CombinaBnBSolver::set_new_best_node(BnBNode * ptr_active_node) {

    if (ptr_best_node) {

        delete_node(ptr_best_node);
    }

    ptr_best_node = ptr_active_node;
    eta_max = ptr_best_node->get_lb_branch();

}


void CombinaBnBSolver::display_solution_update() {

    std::cout << "  Solution with eta_max = " 
        << ptr_best_node->get_lb_branch() << 
        " at iteration " << n_iterations << "\n";
}


void CombinaBnBSolver::add_child_nodes_to_bnb_queue(BnBNode * ptr_parent_node) {
    
    eta_parent = ptr_parent_node->get_eta_node();
    lb_parent = ptr_parent_node->get_lb_branch();

    active_control = 0;

    while(active_control < N_c) {

        sigma_node = ptr_parent_node->get_sigma();

        if(sigma_node[active_control] < sigma_max[active_control]) {

            depth_node = ptr_parent_node->get_depth();

            compute_eta_of_current_node(ptr_parent_node);
            increment_sigma_and_eta_on_active_control_change(ptr_parent_node);
            set_lower_bound_of_branch();
            add_node_to_bnb_queue(ptr_parent_node);

        }
        
        active_control++;
    }

    sigma_node = ptr_parent_node->get_sigma();

    if(sigma_node != sigma_max) {

        active_control = N_c;

        depth_node = ptr_parent_node->get_depth();

        compute_eta_of_current_node(ptr_parent_node);
        increment_sigma_and_eta_on_active_control_change(ptr_parent_node);
        set_lower_bound_of_branch();
        add_node_to_bnb_queue(ptr_parent_node);
    }
}


void CombinaBnBSolver::increment_sigma_and_eta_on_active_control_change(BnBNode * ptr_parent_node) {

    if(active_control != ptr_parent_node->get_active_control()){

        increment_sigma_and_eta(ptr_parent_node->get_active_control(), 0);
        increment_sigma_and_eta(active_control, 1);

        if(sigma_node == sigma_max) {

            depth_node = N_b;
        }
    }
}


void CombinaBnBSolver::increment_sigma_and_eta(unsigned int switched_control, unsigned int control_status) {

    if(switched_control != N_c){

        sigma_node[switched_control]++;

        if(sigma_node[switched_control] == sigma_max[switched_control]) {

            eta_node[switched_control] += sum_eta[control_status][switched_control][depth_node];
        }
    }
}


void CombinaBnBSolver::delete_node(BnBNode * ptr_active_node) {

    delete ptr_active_node;
    ptr_active_node = NULL;
}


void CombinaBnBSolver::retrieve_solution() {

    clock_t t_start;
    clock_t t_end;

    int node_range_end;
    int node_range_begin;

    std::cout << "\n- Retrieving Branch and Bound solution ...\n";

    t_start = clock();

    BnBNode * ptr_active_node = ptr_best_node;

    while(ptr_active_node){

        node_range_end = (ptr_active_node->get_depth() - 1);
        BnBNode * ptr_preceding_node = ptr_active_node->get_ptr_parent_node();

        if(ptr_preceding_node) {

            node_range_begin = ptr_preceding_node->get_depth();
        }

        else {
        
            node_range_begin = 0;
        }

        if(ptr_active_node->get_active_control() != N_c) {

            for(int i = node_range_end; i >= node_range_begin; i--) {

                b_bin[ptr_active_node->get_active_control()][i] = 1;
            }
        }

        ptr_active_node = ptr_preceding_node;
    }


    t_end = clock();

    std::cout << "  Reconstructing the solution finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";

}


// get-functions

double CombinaBnBSolver::get_eta() {

    return eta_max;
}


std::vector<std::vector<unsigned int>> CombinaBnBSolver::get_b_bin() {

    return b_bin;
}

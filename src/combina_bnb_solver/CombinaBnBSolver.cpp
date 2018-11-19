/*
 *
 * CombinaBnBSolver.cpp
 *
 * This file is part of pycombina.
 *
 * Copyright 2017-2018 Adrian Bürger, Clemens Zeile, Sebastian Sager, Moritz Diehl
 *
 * pycombina is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * pycombina is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with pycombina. If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include "CombinaBnBSolver.hpp"

namespace py = pybind11;

#ifndef NDEBUG
unsigned int Node::n_add = 0;
unsigned int Node::n_delete_self = 0;
unsigned int Node::n_delete_other = 0;
#endif

CombinaBnBSolver::CombinaBnBSolver(std::vector<double> const & dt, 
                       std::vector<std::vector<double>> const & b_rel,
                       
                       unsigned int const & n_c,
                       unsigned int const & n_t,

                       std::vector<unsigned int> const & n_max_switches,
                       std::vector<double> const & min_up_time,
                       std::vector<double> const & min_down_time,
                       std::vector<std::vector<unsigned int>> const & b_valid,

                       std::vector<double> const & min_down_time_pre,
                       unsigned int const & b_active_pre)

    : dt(dt),
      b_rel(b_rel),

      n_c(n_c),
      n_t(n_t),

      n_max_switches(n_max_switches),
      min_up_time(min_up_time),
      min_down_time(min_down_time),
      b_valid(b_valid),

      min_down_time_pre(min_down_time_pre),
      b_active_pre(b_active_pre),

      sum_eta(2, std::vector<std::vector<double>> (b_rel.size(), 
        std::vector<double> (b_rel[0].size()))),

      best_node(nullptr),
      ub_bnb(0.0),

      b_bin(b_rel.size(), std::vector<unsigned int>(b_rel[0].size(), 0)),
  
      n_iter(0),
      n_print(0),

      terminate(false),
      user_interrupt(false)

{

    prepare_bnb();

}


CombinaBnBSolver::~CombinaBnBSolver(){

}


void CombinaBnBSolver::prepare_bnb() {

    compute_initial_upper_bound();
    precompute_sum_of_etas();

}


void CombinaBnBSolver::compute_initial_upper_bound() {

    for(unsigned int i = 0; i < n_t; i++) {

        ub_bnb += dt[i];
    }
}


void CombinaBnBSolver::precompute_sum_of_etas() {

    for(unsigned int i = 0; i < n_c; i++) {

        sum_eta[0][i][n_t-1] = dt[n_t-1] * (b_rel[i][n_t-1]);
        sum_eta[1][i][n_t-1] = dt[n_t-1] * (b_rel[i][n_t-1] - 1.0);

        for(int j = n_t-2; j >= 0; j--) {

            sum_eta[0][i][j] = sum_eta[0][i][j+1] + dt[j] * b_rel[i][j];
            sum_eta[1][i][j] = sum_eta[1][i][j+1] + dt[j] * (b_rel[i][j] - 1.0);
        }
    }
}


void CombinaBnBSolver::set_solver_settings(std::map<std::string, double> bnb_opts) {

    max_iter = (long)bnb_opts["max_iter"];
    max_cpu_time = bnb_opts["max_cpu_time"];
}


void CombinaBnBSolver::run(bool use_warm_start, 
    std::map<std::string, double> bnb_opts) {

    set_solver_settings(bnb_opts);
    add_initial_nodes_to_queue();
    run_bnb();
    retrieve_solution();

}

void CombinaBnBSolver::add_initial_nodes_to_queue() {

    unsigned int b_active_parent(b_active_pre);
    double lb_parent(0.0);

    for(unsigned int b_active_child = 0; b_active_child < n_c; b_active_child++) {

        std::vector<double> eta_child(n_c, 0.0);
        std::vector<unsigned int> sigma_child(n_c, 0);
        std::vector<double> min_down_time_child = min_down_time_pre;
        unsigned int depth_child(0);
        double lb_child(0.0);

        if (!control_activation_forbidden(b_active_child, b_active_parent, 
            sigma_child, min_down_time_child)) {

            compute_child_node_properties(b_active_child, b_active_parent, 
                eta_child, sigma_child, min_down_time_child,
                lb_parent, &lb_child, &depth_child);

            add_child_node_to_queue(nullptr, b_active_child, sigma_child, 
                min_down_time_child, depth_child, eta_child, lb_child);
        }
    }
}


bool CombinaBnBSolver::control_activation_forbidden(
    unsigned int const b_active_child, unsigned int const b_active_parent,
    std::vector<unsigned int> const & sigma_child,
    std::vector<double> const & min_down_time_parent) {

    return (sigma_child[b_active_child] >= n_max_switches[b_active_child] ||
        (b_active_parent < n_c && sigma_child[b_active_parent] >= n_max_switches[b_active_parent]) ||
        min_down_time_parent[b_active_child] > 0.0);
}


void CombinaBnBSolver::compute_child_node_properties(
    unsigned int const b_active_child, unsigned int const b_active_parent,
    std::vector<double> & eta_child, std::vector<unsigned int> & sigma_child,
    std::vector<double> & min_down_time_child,
    double const lb_parent, double* lb_child, unsigned int* depth_child) {

    double min_up_time_fulfilled(0.0);

    if (b_active_child == b_active_parent) {
        min_up_time_fulfilled = min_up_time[b_active_child];
    }

    do {

        for(unsigned int i = 0; i < n_c; i++){

            if(sigma_child[i] < n_max_switches[i]) {
            
                eta_child[i] += dt[*depth_child] * 
                    (b_rel[i][*depth_child] - double(b_active_child == i));
                
            }

            min_down_time_child[i] -= dt[*depth_child];
        }

        min_up_time_fulfilled += dt[*depth_child];
        (*depth_child)++;


    } while((min_up_time[b_active_child] > min_up_time_fulfilled) && (*depth_child < n_t));


    if ((b_active_child != b_active_parent) && (b_active_parent < n_c)) {

        sigma_child[b_active_parent]++;
        sigma_child[b_active_child]++;

        if (sigma_child[b_active_parent] == n_max_switches[b_active_parent]) {

            eta_child[b_active_parent] += sum_eta[0][b_active_parent][*depth_child];
        }

        if (sigma_child[b_active_child] == n_max_switches[b_active_child]) {

            eta_child[b_active_child] += sum_eta[1][b_active_child][*depth_child];
        }

        if (sigma_child == n_max_switches) {

            *depth_child = n_t;
        }
    }

    for(unsigned int j = 0; j < n_c; j++){

        *lb_child = fmax(*lb_child, fabs(eta_child[j]));
    }

    *lb_child = fmax(lb_parent, fabs(*lb_child));
}


bool CombinaBnBSolver::add_child_node_to_queue(Node* parent_node, 
    unsigned int const b_active_child, std::vector<unsigned int> const & sigma_child,
    std::vector<double> const & min_down_time_child, double const depth_child,
    std::vector<double> const & eta_child, double const lb_child) {

    Node* child_node(nullptr);

    for (unsigned int i = 0; i < n_c; i++) {

        if(sigma_child[i] > n_max_switches[i]) {

            throw std::runtime_error( 
                std::string("Node switches exceeds n_max-switches, this should not happen.") 
                + std::string("\n Please contact the developers."));
        }
    }

    if(lb_child < ub_bnb) {

        child_node = new Node(parent_node, b_active_child, n_c, sigma_child,
            min_down_time_child, depth_child, eta_child, lb_child);

        node_queue.push(child_node);

        #ifndef NDEBUG
        Node::n_add++;
        #endif

        return true;
    }

    return false;
}


void CombinaBnBSolver::run_bnb() {

    clock_t t_start;
    clock_t t_update;
    clock_t t_current;
    clock_t t_end;
    
    py::print("-----------------------------------------------------------");
    py::print("                                                           ");
    py::print("                 pycombina Branch and Bound                ");
    py::print("                                                           ");

    t_start = clock();

    Node * active_node;

    while (!node_queue.empty()) {

        check_it_termination_criterion_reached(n_iter, t_start);
        
        if  (!terminate) {

            n_iter++;
        }

        active_node = node_queue.top();
        node_queue.pop();

        if(!terminate && (active_node->get_lb() < ub_bnb)) {

            if(active_node->get_depth() == n_t) {     
                
                t_update = clock();
                set_new_best_node(active_node); 
                display_solution_update(true, double(t_update - t_start) / CLOCKS_PER_SEC);
            }

            else {

                add_nodes_to_queue(active_node);
            }
        }

        else {

            delete_node(active_node);
        }

        if (!terminate && (n_iter % (int)1e6 == 0)) {

            t_current = clock();
            display_solution_update(false, double(t_current - t_start) / CLOCKS_PER_SEC);
        }
    }

    t_end = clock();


    std::string s_n_iter = std::to_string(n_iter);
    s_n_iter.insert(0, 12 - s_n_iter.length(), ' ');

    std::ostringstream streamObj;

    streamObj << std::scientific << "\n    Best solution:    " << ub_bnb
        << "\n    Total iterations: " << s_n_iter 
        << "\n    Total runtime:    " << double(t_end - t_start) / CLOCKS_PER_SEC
        << " s\n";

    if (n_iter >= max_iter) {

        streamObj << "\n    --> Maximum number of iterations exceeded";

    } else if ((double(t_end- t_start) / CLOCKS_PER_SEC) >= max_cpu_time) {

        streamObj << "\n    --> Maximum CPU time exceeded";

    } else if (user_interrupt) {

        streamObj << "\n    --> User interrupt";

    } else {

        streamObj << "\n    --> Optimal solution found";
    }

    py::print(streamObj.str());
    py::print("\n-----------------------------------------------------------");

    /*

    Restart is still bugyy and therefore disabled for now

    user_interrupt = false;
    terminate = false;
    n_print = 0;
    
    */

}


void CombinaBnBSolver::check_it_termination_criterion_reached(int n_iter, clock_t t_start) {

    if (!terminate) {

        clock_t t_current = clock();

        terminate = ((n_iter >= max_iter) || 
            ((double(t_current - t_start) / CLOCKS_PER_SEC) >= max_cpu_time) ||
            user_interrupt);

    }
}


void CombinaBnBSolver::set_new_best_node(Node* active_node) {

    if (best_node) {

        delete_node(best_node);
    }

    best_node = active_node;
    ub_bnb = best_node->get_lb();

}


void CombinaBnBSolver::display_solution_update(bool solution_update, double runtime) {

    if (n_print++ % 10 == 0) {

        py::print("-----------------------------------------------------------");
        py::print("    Iteration |  Upper bound |  Branches  |  Runtime (s)   ");
        py::print("-----------------------------------------------------------");
    }

    std::string s_n_iter = std::to_string(n_iter);
    s_n_iter.insert(0, 10 - s_n_iter.length(), ' ');

    std::string s_node_queue_size = std::to_string(node_queue.size());
    s_node_queue_size.insert(0, 10 - s_node_queue_size.length(), ' ');

    std::ostringstream streamObj;

    streamObj << std::scientific;

    if (solution_update) {
        
        streamObj << " U ";

    } else {

        streamObj << "   ";
    }

    streamObj << s_n_iter
        << " | " << ub_bnb << " | "
        << s_node_queue_size << " | " << runtime;
    
    py::print(streamObj.str());

}


void CombinaBnBSolver::add_nodes_to_queue(Node* parent_node) {

    unsigned int b_active_parent = parent_node->get_b_active();
    double lb_parent = parent_node->get_lb();
    bool has_children(false);

    for(unsigned int b_active_child = 0; b_active_child < n_c; b_active_child++){

        std::vector<double> eta_child = parent_node->get_eta();
        std::vector<unsigned int> sigma_child = parent_node->get_sigma();
        std::vector<double> min_down_time_child = parent_node->get_min_down_time();
        unsigned int depth_child = parent_node->get_depth();
        double lb_child = parent_node->get_lb();

        bool child_added(false);

        if (!control_activation_forbidden(b_active_child,
            b_active_parent, sigma_child, min_down_time_child)) {

            compute_child_node_properties(b_active_child, b_active_parent, 
                eta_child, sigma_child, min_down_time_child,
                lb_parent, &lb_child, &depth_child);

            child_added = add_child_node_to_queue(parent_node, b_active_child, sigma_child, 
                min_down_time_child, depth_child, eta_child, lb_child);

        }

        if (child_added) {

            has_children = true;
        }
    }

    if (!has_children) {

        delete_node(parent_node);
    }
}


void CombinaBnBSolver::retrieve_solution() {

    int node_range_end;
    int node_range_begin;

    Node* active_node = best_node;

    while(active_node){

        node_range_end = (active_node->get_depth() - 1);
        Node* preceding_node = active_node->get_parent();

        if(preceding_node) {

            node_range_begin = preceding_node->get_depth();
        }

        else {
        
            node_range_begin = 0;
        }

        for(int i = node_range_end; i >= node_range_begin; i--) {

            b_bin[active_node->get_b_active()][i] = 1;
        }

        active_node = preceding_node;
    }
    
    delete_node(best_node);
    best_node = nullptr;


    #ifndef NDEBUG
    py::print("Debug information:");
    py::print("Nodes added:", Node::n_add);
    py::print("Nodes deleted:", Node::n_delete_self + Node::n_delete_other);
    py::print("Nodes not deleted:", Node::n_add - (Node::n_delete_self + Node::n_delete_other));
    py::print("Nodes deleted by themselves:", Node::n_delete_self);
    py::print("Nodes deleted by BnB:", Node::n_delete_other);
    #endif

}


void CombinaBnBSolver::delete_node(Node *& active_node) {

    delete active_node;
    active_node = nullptr;

    #ifndef NDEBUG
    Node::n_delete_other++; 
    #endif
}


void CombinaBnBSolver::stop() {

    // very dirty hack, should be improved

    user_interrupt = true;

    run_bnb();
    retrieve_solution();
}


double CombinaBnBSolver::get_eta() {

    return ub_bnb;
}


std::vector<std::vector<unsigned int>> CombinaBnBSolver::get_b_bin() {

    return b_bin;
}

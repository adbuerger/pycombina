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

#include <algorithm>
#include <queue>
#include <iostream>
#include <sstream>
#include <string>
#include <stdexcept>

#include <pybind11/pybind11.h>

#include "CombinaBnBSolver.hpp"
#include "Monitor.hpp"
#include "Node.hpp"
#include "NodeQueue.hpp"

namespace py = pybind11;

#ifndef NDEBUG
unsigned int Node::n_add = 0;
unsigned int Node::n_delete = 0;
#endif


template <class Map, class Key = typename Map::key_type, class Value = typename Map::mapped_type>
static Value get_with_default(const Map& map, const Key& key, const Value& def) {
    auto it = map.find(key);
    if(it != map.end()) {
        return (Value)it->second;
    }
    else {
        return def;
    }
}


CombinaBnBSolver::CombinaBnBSolver(std::vector<double> const & dt, 
                       std::vector<std::vector<double>> const & b_rel,
                       
                       unsigned int const & n_c,
                       unsigned int const & n_t,

                       std::vector<unsigned int> const & n_max_switches,
                       std::vector<double> const & min_up_time,
                       std::vector<double> const & min_down_time,
                       std::vector<double> const & max_up_time,
                       std::vector<double> const & total_max_up_time,

                       std::vector<std::vector<unsigned int>> const & b_valid,
                       std::vector<std::vector<unsigned int>> const & b_adjacencies,

                       unsigned int const & b_active_pre)

    : dt(dt),
      b_rel(b_rel),

      n_c(n_c),
      n_t(n_t),

      n_max_switches(n_max_switches),
      min_up_time(min_up_time),
      min_down_time(min_down_time),
      max_up_time(max_up_time),
      total_max_up_time(total_max_up_time),

      b_valid(b_valid),
      b_adjacencies(b_adjacencies),

      b_active_pre(b_active_pre),

      sum_eta(2, std::vector<std::vector<double>> (b_rel.size(), 
        std::vector<double> (b_rel[0].size()))),

      node_queue(nullptr),
      best_node(nullptr),
      ub_bnb(0.0),

      b_bin(b_rel.size(), std::vector<unsigned int>(b_rel[0].size(), 0)),
  
      n_iter(0),
      n_print(0),

      n_sol(0),

      max_iter(5000000),
      max_cpu_time(3e2),
      verbosity(2),
      solution_time(0.0),

      user_interrupt(false),

      status(1),
      monitor_(),
      nodeseq(0)

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


void CombinaBnBSolver::run(bool use_warm_start) {

    if(!node_queue) {
        node_queue = NodeQueue::create(this);
    }

    if(monitor_) {
        monitor_->on_start_search();
    }

    add_nodes_to_queue(nullptr);
    run_bnb();

    if(monitor_) {
        monitor_->on_stop_search();
    }

    retrieve_solution();
}

bool CombinaBnBSolver::control_activation_forbidden(
    unsigned int const b_active_child, unsigned int const b_active_parent,
    std::vector<unsigned int> const & sigma_child,
    std::vector<double> const & min_down_time_parent,
    std::vector<double> const & up_time_parent,
    std::vector<double> const & total_up_time_parent,
    unsigned int const depth_child) {

    double min_up_time_fulfilled(0.0);
    std::vector<double> up_time_child_test(up_time_parent);
    std::vector<double> total_up_time_child_test(total_up_time_parent);
    unsigned int depth_child_test(depth_child);

    if (sigma_child[b_active_child] >= n_max_switches[b_active_child]) {

        return true;
    }
        
    if ((b_active_parent < n_c) && (sigma_child[b_active_parent] >= n_max_switches[b_active_parent])) {

        return true;
    }
        

    if (min_down_time_parent[b_active_child] > 0.0) {

        return true;
    }
        
    if ((b_active_parent < n_c) && (b_adjacencies[b_active_child][b_active_parent] == 0)) {

        return true;
    }

    do {

        if (b_valid[b_active_child][depth_child_test] != 1) {

            return true;
        }
        
        min_up_time_fulfilled += dt[depth_child_test];
        up_time_child_test[b_active_child] += dt[depth_child_test];
        total_up_time_child_test[b_active_child] += dt[depth_child_test];
        depth_child_test++;

    } while((min_up_time[b_active_child] > min_up_time_fulfilled) && (depth_child_test < n_t));

    return (up_time_child_test[b_active_child] > max_up_time[b_active_child] ||
        total_up_time_child_test[b_active_child] > total_max_up_time[b_active_child]);
}


void CombinaBnBSolver::compute_child_node_properties(
    unsigned int const b_active_child, unsigned int const b_active_parent,
    std::vector<double> & eta_child, std::vector<unsigned int> & sigma_child,
    std::vector<double> & min_down_time_child, std::vector<double> & up_time_child,
    std::vector<double> & total_up_time_child,
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

            min_down_time_child[i] = fmax(0, min_down_time_child[i] - dt[*depth_child]);
        }

        min_up_time_fulfilled += dt[*depth_child];
        up_time_child[b_active_child] += dt[*depth_child];
        total_up_time_child[b_active_child] += dt[*depth_child];
        
        (*depth_child)++;


    } while((min_up_time[b_active_child] > min_up_time_fulfilled) && (*depth_child < n_t));


    if ((b_active_child != b_active_parent) && (b_active_parent < n_c)) {

        sigma_child[b_active_parent]++;
        sigma_child[b_active_child]++;
        min_down_time_child[b_active_parent]= fmax(0, min_down_time[b_active_parent] - dt[*depth_child]);

        if (sigma_child[b_active_parent] == n_max_switches[b_active_parent]) {

            eta_child[b_active_parent] += sum_eta[0][b_active_parent][*depth_child];
        }

        if (sigma_child[b_active_child] == n_max_switches[b_active_child]) {

            eta_child[b_active_child] += sum_eta[1][b_active_child][*depth_child];

            for (unsigned int i = 0; i < n_c; i++) {

                if (sigma_child[i] < n_max_switches[i]) {

                    eta_child[i] += sum_eta[0][i][*depth_child];
                }
            }

            *depth_child = n_t;
        }
    }


    for(unsigned int j = 0; j < n_c; j++){

        *lb_child = fmax(*lb_child, fabs(eta_child[j]));
    }

    *lb_child = fmax(lb_parent, fabs(*lb_child));
}


NodePtr CombinaBnBSolver::create_or_fathom_child_node(const NodePtr& parent_node, 
    unsigned int const b_active_child, std::vector<unsigned int> const & sigma_child,
    std::vector<double> const & min_down_time_child,
    std::vector<double> const & up_time_child,
    std::vector<double> const & total_up_time_child, double const depth_child,
    std::vector<double> const & eta_child, double const lb_child) {

    NodePtr child_node(nullptr);

    for (unsigned int i = 0; i < n_c; i++) {

        if(sigma_child[i] > n_max_switches[i]) {

            throw std::runtime_error( 
                std::string("Node switches exceeds n_max-switches, this should not happen.") 
                + std::string("\n Please contact the developers."));
        }
    }

    if(lb_child < ub_bnb) {
        return std::make_shared<Node>(parent_node, nodeseq++,
            b_active_child, sigma_child, min_down_time_child,
            up_time_child, total_up_time_child, depth_child,
            eta_child, lb_child);
    }
    else {
        return nullptr;
    }
}


void CombinaBnBSolver::run_bnb() {

    clock_t t_start;
    clock_t t_update;
    clock_t t_current;
    clock_t t_end;
    
    if (verbosity > 0) {
        py::gil_scoped_acquire lock;
        py::print("Running Branch and Bound ... ");
        py::print("");
    }

    t_start = clock();

    NodePtr active_node;

    while(!node_queue->empty() && !termination_criterion_reached(n_iter, t_start)) {

        ++n_iter;

        active_node = node_queue->top();
        node_queue->pop();

        if(monitor_) {
            monitor_->on_select(active_node);
        }

        if(active_node->get_lb() < ub_bnb) {

            if(active_node->get_depth() == n_t) {

                t_update = clock();
                set_new_best_node(active_node);
                display_solution_update(true, double(t_update - t_start) / CLOCKS_PER_SEC);

                if(monitor_) {
                    monitor_->on_change(active_node, NODE_INTEGER);
                }
            }
            else {

                add_nodes_to_queue(active_node);
            }
        }
        else {

            if(monitor_) {
                monitor_->on_change(active_node, NODE_FATHOMED);
            }
        }

        if (n_iter % (int)1e6 == 0) {

            t_current = clock();
            display_solution_update(false, double(t_current - t_start) / CLOCKS_PER_SEC);
        }
    }

    node_queue->clear();

    t_end = clock();
    solution_time = double(t_end- t_start) / CLOCKS_PER_SEC;

    std::string s_n_iter = std::to_string(n_iter);
    s_n_iter.insert(0, 12 - s_n_iter.length(), ' ');

    std::ostringstream streamObj;

    if (n_iter >= max_iter) {

        streamObj << "\n    Maximum number of iterations exceeded";
        status = 3;

    } else if (solution_time >= max_cpu_time) {

        streamObj << "\n    Maximum CPU time exceeded";
        status = 4;

    } else if (user_interrupt) {

        streamObj << "\n    User interrupt";
        status = 5;

    } else {

        streamObj << "\n    Optimal solution found";
        status = 2;
    }

    streamObj << std::scientific << "\n\n    Best solution:    " << ub_bnb
        << "\n    Total iterations: " << s_n_iter 
        << "\n    Total runtime:    " << solution_time
        << " s";

    if (verbosity > 0) {
        py::gil_scoped_acquire lock;
        py::print(streamObj.str());
        py::print("\n");
    }

    /*

    Restart is still bugyy and therefore disabled for now

    user_interrupt = false;
    terminate = false;
    n_print = 0;
    
    */

}


bool CombinaBnBSolver::termination_criterion_reached(int n_iter, clock_t t_start) {

    clock_t t_current = clock();

    return ((n_iter >= max_iter) || 
        ((double(t_current - t_start) / CLOCKS_PER_SEC) >= max_cpu_time) ||
        user_interrupt);
}


void CombinaBnBSolver::set_new_best_node(const NodePtr& active_node) {
    best_node = active_node;
    ub_bnb = best_node->get_lb();
    ++n_sol;
}


void CombinaBnBSolver::display_solution_update(bool solution_update, double runtime) {
    py::gil_scoped_acquire lock;

    if ((verbosity > 1) && (n_print++ % 10 == 0)) {

        py::print("    Iteration   Upper bound    Branches     Runtime (s)    ");
    }

    std::string s_n_iter = std::to_string(n_iter);
    s_n_iter.insert(0, 10 - s_n_iter.length(), ' ');

    std::string s_node_queue_size = std::to_string(node_queue->size());
    s_node_queue_size.insert(0, 10 - s_node_queue_size.length(), ' ');

    std::ostringstream streamObj;

    streamObj << std::scientific;

    if (solution_update) {
        
        streamObj << " U ";

    } else {

        streamObj << "   ";
    }

    streamObj << s_n_iter
        << "   " << ub_bnb << "   "
        << s_node_queue_size << "   " << runtime;
    
    if (verbosity > 1) {
     
        py::print(streamObj.str());
    }

}


void CombinaBnBSolver::add_nodes_to_queue(const NodePtr& parent_node) {
    std::vector<NodePtr> children;
    unsigned int b_active_parent;
    double lb_parent;
    bool node_feasible = false;

    if(parent_node) {
        b_active_parent = parent_node->get_b_active();
        lb_parent = parent_node->get_lb();
    }
    else {
        b_active_parent = b_active_pre;
        lb_parent = 0.0;
    }

    for(unsigned int b_active_child = 0; b_active_child < n_c; b_active_child++){

        std::vector<double> eta_child;
        std::vector<unsigned int> sigma_child;
        std::vector<double> min_down_time_child;
        std::vector<double> up_time_child;
        std::vector<double> total_up_time_child;
        unsigned int depth_child;
        double lb_child = lb_parent;

        if(parent_node) {
            eta_child = parent_node->get_eta();
            sigma_child = parent_node->get_sigma();
            min_down_time_child = parent_node->get_min_down_time();
            up_time_child = parent_node->get_up_time();
            total_up_time_child = parent_node->get_total_up_time();
            depth_child = parent_node->get_depth();
        }
        else {
            eta_child = std::vector<double>(n_c, 0.0);
            sigma_child = std::vector<unsigned int>(n_c, 0);
            min_down_time_child = std::vector<double>(n_c, 0.0);
            up_time_child = std::vector<double>(n_c, 0.0);
            total_up_time_child = std::vector<double>(n_c, 0.0);
            depth_child = 0;
        }

        if (!control_activation_forbidden(b_active_child,
            b_active_parent, sigma_child, min_down_time_child,
            up_time_child, total_up_time_child, depth_child)) {

            node_feasible = true;

            compute_child_node_properties(b_active_child, b_active_parent,
                eta_child, sigma_child, min_down_time_child, up_time_child,
                total_up_time_child, lb_parent, &lb_child, &depth_child);

            NodePtr child = create_or_fathom_child_node(parent_node, b_active_child, sigma_child,
                min_down_time_child, up_time_child, total_up_time_child,
                depth_child, eta_child, lb_child);

            if(child) {

                if(monitor_) {

                    monitor_->on_create(child);
                }

                children.emplace_back(std::move(child));
            }
	    }
    }

    node_queue->push(children);

    #ifndef NDEBUG
    Node::n_add += children.size();
    #endif

    if(parent_node && monitor_) {
        if(!node_feasible) {
            monitor_->on_change(parent_node, NODE_INFEASIBLE);
        }
        else if(children.empty()) {
            monitor_->on_change(parent_node, NODE_FATHOMED);
        }
        else {
            monitor_->on_change(parent_node, NODE_SOLVED);
        }
    }
}


void CombinaBnBSolver::retrieve_solution() {
    size_t node_range_begin;

    NodePtr active_node = best_node;

    while(active_node) {
        NodePtr parent_node = active_node->get_parent();
        node_range_begin = parent_node ? parent_node->get_depth() : 0;

        const size_t b_active = active_node->get_b_active();
        size_t idx = active_node->get_depth() - 1;
        do {
            b_bin[b_active][idx] = 1;
        } while(idx-- > node_range_begin);

        active_node = std::move(parent_node);
    }
   
    best_node.reset();

    #ifndef NDEBUG
    py::print("Debug information:");
    py::print("Nodes added:", Node::n_add);
    py::print("Nodes deleted:", Node::n_delete);
    py::print("Nodes not deleted:", Node::n_add - Node::n_delete);
    #endif

}


void CombinaBnBSolver::stop() {

    // very dirty hack, should be improved

    user_interrupt = true;

    run_bnb();
    retrieve_solution();
}


double CombinaBnBSolver::get_eta() const {

    return ub_bnb;
}


const std::vector<double>& CombinaBnBSolver::get_dt() const {
    return dt;
}


std::vector<std::vector<unsigned int>> CombinaBnBSolver::get_b_bin() const {

    return b_bin;
}


unsigned int CombinaBnBSolver::get_status() const {

    return status;
}


unsigned long CombinaBnBSolver::get_num_sol() const {
    return n_sol;
}


unsigned int CombinaBnBSolver::get_num_time() const {
    return n_t;
}


unsigned int CombinaBnBSolver::get_num_ctrl() const {
    return n_c;
}


const std::vector<unsigned int>& CombinaBnBSolver::get_num_max_switches() const {
    return n_max_switches;
}

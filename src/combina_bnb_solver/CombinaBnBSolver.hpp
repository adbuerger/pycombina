/*
 *
 * CombinaBnBSolver.hpp
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

#ifndef VECTOR_H
#define VECTOR_H
#include <vector>
#endif
 
#include <queue>

#ifndef BNB_NODE_H
#define BNB_NODE_H
#include "BnBNode.hpp"
#endif

#ifndef PYBIND11
#define PYBIND11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#endif

#include "BnBNodeComparison.hpp"


class CombinaBnBSolver {

public:

    CombinaBnBSolver(const std::vector<double>& dt, const std::vector<std::vector<double>>& b_rel,
        const unsigned int& n_c, const unsigned int& n_b, 
        const std::vector<double>& w_b, const unsigned int& init_active_control);

    ~CombinaBnBSolver();

    void run(std::vector<unsigned int> max_swichtes, std::vector<double> min_up_time);

    // get-functions

    double get_eta();

    std::vector<std::vector<unsigned int>> get_b_bin();


private:

    void set_sigma_max(std::vector<unsigned int> n_max_switches);
    void set_dwell_time(std::vector<double> min_up_time);

    void prepare_bnb_data();
    void compute_initial_upper_bound();
    void precompute_sum_of_etas();

    void initialize_bnb_queue();
    void add_initial_nodes_to_bnb_queue();
    void compute_eta_of_current_node(BnBNode * ptr_parent_node);
    void increas_eta_node();
    void increment_sigma_on_init_active_control_change();
    void increment_sigma_and_eta(unsigned int switched_control, unsigned int control_status);
    void set_lower_bound_of_branch();
    void add_node_to_bnb_queue(BnBNode * ptr_parent_node);

    void add_nodes_to_bnb_queue(BnBNode * ptr_parent_node);

    void run_bnb();
    void update_best_solution(BnBNode * ptr_active_node);
    void set_new_best_node(BnBNode * ptr_active_node);
    void display_solution_update();
    void add_child_nodes_to_bnb_queue(BnBNode * ptr_parent_node);
    void increment_sigma_and_eta_on_active_control_change(BnBNode * ptr_active_node);
    void delete_node(BnBNode * ptr_active_node);

    void retrieve_solution();
    void clean_up_nodes();

    std::vector<double> dt;
    std::vector<std::vector<double>> b_rel;
    std::vector<double> w_b;

    std::vector<unsigned int> sigma_max;
    std::vector<double> dwell_time;

    unsigned int n_c;
    unsigned int n_b;

    unsigned int init_active_control;

    double eta_max;

    std::vector<double> sum_eta_b_rel_true;
    std::vector<double> sum_eta_b_rel_false;

    std::priority_queue<BnBNode*, std::vector<BnBNode*>, 
        BnBNodeComparison> bnb_node_queue;
    std::vector<BnBNode*> bnb_node_index;
    BnBNode * ptr_best_node;

    std::vector<std::vector<unsigned int>> b_bin;

    std::vector<double> eta_node;

    std::vector<double> eta_parent;
    std::vector<unsigned int> sigma_node;

    unsigned int active_control;
    unsigned int depth_node;
    double lb_node;
    double lb_parent;

    std::vector<std::vector<std::vector<double>>> sum_eta;

    unsigned int n_iterations;

};
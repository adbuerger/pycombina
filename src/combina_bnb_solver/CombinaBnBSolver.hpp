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

#ifndef __COMBINA_BNB_SOLVER_HPP
#define __COMBINA_BNB_SOLVER_HPP

#include <map>
#include <vector>

#include "combina_fwd.hpp"


class CombinaBnBSolver {

public:

    CombinaBnBSolver(std::vector<double> const & dt,
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

               unsigned int const & b_active_pre);

    ~CombinaBnBSolver();

    MonitorPtr get_monitor() const { return monitor_; }             ///< Returns current monitor.
    void set_monitor(MonitorPtr monitor) { monitor_ = monitor; }    ///< Replaces current monitor.
    NodeQueuePtr get_node_queue() const { return node_queue; }      ///< Returns current node queue.
    void set_node_queue(NodeQueuePtr queue) { node_queue = queue; } ///< Replaces current node queue.

    long get_max_iter() const { return max_iter; }                  ///< Returns current iteration limit.
    void set_max_iter(long n) { max_iter = n; }                     ///< Sets iteration limit.
    double get_max_cpu_time() const { return max_cpu_time; }        ///< Returns current CPU time limit.
    void set_max_cpu_time(double t) { max_cpu_time = t; }           ///< Sets CPU time limit.

    void run(bool use_warm_start);
    void stop();

    double get_eta() const;
    const std::vector<double>& get_dt() const;
    std::vector<std::vector<unsigned int>> get_b_bin() const;
    unsigned int get_status() const;
    unsigned long get_num_sol() const;
    unsigned int get_num_time() const;
    unsigned int get_num_ctrl() const;
    const std::vector<unsigned int>& get_num_max_switches() const;


private:
    
    void prepare_bnb();
    void compute_initial_upper_bound();
    void precompute_sum_of_etas();

    bool control_activation_forbidden(unsigned int const b_active_child,
        unsigned int const b_active_parent,
        std::vector<unsigned int> const & sigma_child,
        std::vector<double> const & min_down_time_parent,
        std::vector<double> const & up_time_parent,
        std::vector<double> const & total_up_time_parent,
        unsigned int const depth_child);

    void compute_child_node_properties(
        unsigned int const b_active_child, unsigned int const b_active_parent,
        std::vector<double> & eta_child, std::vector<unsigned int> & sigma_child,
        std::vector<double> & min_down_time_child, std::vector<double> & up_time_child,
        std::vector<double> & total_up_time_child,
        double const lb_parent, double* lb_child, unsigned int* depth_child);

    NodePtr create_or_fathom_child_node(const NodePtr& parent_node, 
        unsigned int const b_active_child, std::vector<unsigned int> const & sigma_child,
        std::vector<double> const & min_down_time_child,
        std::vector<double> const & up_time_child,
        std::vector<double> const & total_up_time_child, double const depth_child,
        std::vector<double> const & eta_child, double const lb_child);

    void run_bnb();
    void check_it_termination_criterion_reached(int n_iter, clock_t t_start);
    void set_new_best_node(const NodePtr& active_node);
    void display_solution_update(bool solution_update, double runtime);
    void add_nodes_to_queue(const NodePtr& parent_node);

    void retrieve_solution();

/*
    void clean_up_nodes();

*/

    std::vector<double> dt;
    std::vector<std::vector<double>> b_rel;

    unsigned int n_c;
    unsigned int n_t;

    std::vector<unsigned int> n_max_switches;
    std::vector<double> min_up_time;
    std::vector<double> min_down_time;
    std::vector<double> max_up_time;
    std::vector<double> total_max_up_time;

    std::vector<std::vector<unsigned int>> b_valid;
    std::vector<std::vector<unsigned int>> b_adjacencies;

    std::vector<double> min_down_time_pre;
    unsigned int b_active_pre;

    std::vector<std::vector<std::vector<double>>> sum_eta;

    std::shared_ptr<NodeQueue> node_queue;
    NodePtr best_node;

    double ub_bnb;

    std::vector<std::vector<unsigned int>> b_bin;

    long n_iter;
    long n_print;

    unsigned long n_sol;

    long max_iter;
    double max_cpu_time;

    bool terminate;
    bool user_interrupt;

    unsigned int status;
    MonitorPtr monitor_;
    size_t nodeseq;
};

#endif /* end of include guard: __COMBINA_BNB_SOLVER_HPP */

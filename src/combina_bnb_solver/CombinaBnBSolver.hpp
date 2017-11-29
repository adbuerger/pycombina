/*
 *
 * CombinaBnBSolver.hpp
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

#include "BnBNodeComparison.hpp"


class CombinaBnBSolver {

public:

    CombinaBnBSolver(const std::vector<double>& Tg, const std::vector<std::vector<double>>& b_rel,
        const unsigned int& N_c, const unsigned int& N_b);

    ~CombinaBnBSolver();

    void run(std::vector<unsigned int> n_max_swichtes);

    // get-functions

    double get_eta();

    std::vector<std::vector<unsigned int>> get_b_bin();


private:

    void set_sigma_max(std::vector<unsigned int> n_max_switches);

    void prepare_bnb_data();
    void compute_initial_upper_bound();
    void precompute_sum_of_etas();

    void initialize_bnb_queue();
    void add_initial_nodes_to_bnb_queue();
    void compute_eta_of_current_node();
    void compute_lower_bound_of_node();
    void add_node_to_bnb_queue(BnBNode * ptr_parent_node);

    void add_nodes_to_bnb_queue(BnBNode * ptr_parent_node);

    void run_bnb();
    void update_best_solution(BnBNode * ptr_active_node);
    void display_solution_update(BnBNode * ptr_best_node);
    void add_child_nodes_to_bnb_queue(BnBNode * ptr_parent_node);
    void increment_sigma_on_active_control_change(BnBNode * ptr_active_node);
    void delete_node(BnBNode * ptr_active_node);

    void retrieve_solution();

    std::vector<double> Tg;
    std::vector<std::vector<double>> b_rel;

    std::vector<unsigned int> sigma_max;

    unsigned int N_c;
    unsigned int N_b;

    double eta;

    std::vector<double> sum_eta_b_rel_true;
    std::vector<double> sum_eta_b_rel_false;

    std::priority_queue<BnBNode*, std::vector<BnBNode*>, 
        BnBNodeComparison> *ptr_bnb_node_queue;
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
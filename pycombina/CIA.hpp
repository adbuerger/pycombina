/*
 *
 * CIA.hpp
 *
 */

#include <vector>
#include <queue>

#ifndef BNB_NODE_H
#define BNB_NODE_H
#include "BnBNode.hpp"
#endif

#include "BnBNodeComparison.hpp"


class CIA {

public:

    CIA(const std::vector<double>& T, const std::vector<double>& b_rel);

    ~CIA();

    void run_cia(int n_max_swichtes = 2);

    // get-functions

    std::vector<double> get_T();
    std::vector<double> get_b_rel();
    
    int get_sigma_max();

    std::vector<double> get_Tg();
    double get_ub();

    std::vector<unsigned int> get_b_bin();


private:

    void welcome_prompt();
    void validate_input_data();
    void validate_input_dimensions();
    void validate_input_values();
    void validate_input_values_T();
    void validate_input_values_b_rel();

    void set_sigma_max(int n_max_switches);

    void prepare_bnb_data();
    void determine_number_of_control_intervals();
    void compute_time_grid_from_time_points();
    void compute_initial_upper_bound();

    void initialize_bnb_queue();

    void add_nodes_to_bnb_queue(BnBNode * ptr_parent_node);

    void run_bnb();
    void update_best_solution(BnBNode * ptr_active_node);
    void display_solution_update(BnBNode * ptr_best_node);
    void create_new_child_nodes(BnBNode * ptr_parent_node);
    void delete_node(BnBNode * ptr_active_node);

    void retrieve_solution();

    std::vector<double> T;
    std::vector<double> b_rel;

    int sigma_max;

    unsigned int N;
    double ub;
    std::vector<double> Tg;

    std::vector<double> sum_eta_b_rel_true;
    std::vector<double> sum_eta_b_rel_false;

    std::priority_queue<BnBNode*, std::vector<BnBNode*>,
        BnBNodeComparison> *ptr_bnb_node_queue;
    BnBNode * ptr_best_node;

    std::vector<unsigned int> b_bin;

};
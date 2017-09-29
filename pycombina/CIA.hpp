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

    // Run BnB

    void run_cia(const int& sigma_max);

    // get-functions

    std::vector<double> get_T();
    std::vector<double> get_b_rel();
    
    double get_ub();
    std::vector<double> get_Tg();

    std::vector<double> get_b_bin();


private:

    void welcome_prompt();
    void validate_input_data();
    void validate_input_dimensions();
    void validate_input_values();
    void validate_input_values_T();
    void validate_input_values_b_rel();

    void run_cia_preparation_phase();
    void determine_number_of_control_intervals();
    void compute_time_grid_from_time_points();
    void compute_initial_upper_bound();
    void compute_integrated_deltas_of_b_rel_to_binary_values();

    std::vector<double> T;
    std::vector<double> b_rel;

    unsigned int N;
    double ub;
    std::vector<double> Tg;

    std::vector<double> integ_delta_b_rel_true;
    std::vector<double> integ_delta_b_rel_false;

    std::priority_queue<BnBNode*, std::vector<BnBNode*>,
        BnBNodeComparison> *ptr_bnb_node_queue;

    std::vector<double> b_bin;

};
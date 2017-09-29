/*
 *
 * CIA.cpp
 *
 */

#include <iostream>

#ifndef BNB_NODE_H
#define BNB_NODE_H
#include "BnBNode.hpp"
#endif

#include "CIA.hpp"


CIA::CIA(const std::vector<double>& T, const std::vector<double>& b_rel)

    : T(T), 
      b_rel(b_rel),

      N(0),
      ub(0.0),
      Tg(T.size()-1),

      integ_delta_b_rel_true(b_rel.size()),
      integ_delta_b_rel_false(b_rel.size()),

      ptr_bnb_node_queue(new std::priority_queue<BnBNode*, std::vector<BnBNode*>,
        BnBNodeComparison>()),

      b_bin(b_rel.size())

{

    welcome_prompt();
    validate_input_data();

};


CIA::~CIA(){

};


void CIA::welcome_prompt(){

    std::cout << "\n-----------------------------------------------------------\n";
    std::cout << "|                                                         |\n";
    std::cout << "|    pycombina -- Combinatorial Integral Approximation    |\n";
    std::cout << "|                                                         |\n";
    std::cout << "-----------------------------------------------------------\n";

};


void CIA::validate_input_data() {

    validate_input_dimensions();
    validate_input_values();
};


void CIA::validate_input_dimensions() {

    if (T.size() != b_rel.size()+1) {

        throw std::invalid_argument("T must contain one element more than b_rel.");

    }
};


void CIA::validate_input_values() {

    validate_input_values_T();
    validate_input_values_b_rel();

};


void CIA::validate_input_values_T() {

    for(int i = 1; i < T.size(); i++) {

        if((T.at(i) - T.at(i-1)) <= 0.0) {

            throw std::invalid_argument("Values in T must be strictly increasing.");

        }
    }
};


void CIA::validate_input_values_b_rel() {

    for(double b: b_rel) {

        if(b < 0.0 || b > 1.0) {

            throw std::invalid_argument("All elements b of the relaxed binary input must be 0 <= b <= 1.");

        }
    }
};


void CIA::run_cia(const int& sigma_max = -1) {

    run_cia_preparation_phase();

};


void CIA::run_cia_preparation_phase() {

    clock_t t_start;
    clock_t t_end;

    std::cout << "\n- Running preparation phase ...\n";

    t_start = clock();

    determine_number_of_control_intervals();
    compute_time_grid_from_time_points();
    compute_initial_upper_bound();
    compute_integrated_deltas_of_b_rel_to_binary_values();

    t_end = clock();

    std::cout << "  Preparation phase finished after " << 
        double(t_end - t_start) / CLOCKS_PER_SEC << " s\n";

};


void CIA::determine_number_of_control_intervals() {

    N = b_rel.size();
};


void CIA::compute_time_grid_from_time_points() {

    for(int i = 1; i < N+1; i++) {

        Tg.at(i-1) = T.at(i) - T.at(i-1);
    }
};

void CIA::compute_initial_upper_bound() {

    for(int i; i < N; i++) {

        ub += Tg.at(i);

    }
};


void CIA::compute_integrated_deltas_of_b_rel_to_binary_values() {

    integ_delta_b_rel_true.at(N-1) = b_rel.at(N-1) - 1;
    integ_delta_b_rel_false.at(N-1) = b_rel.at(N-1);

    for(int i = N-2; i >= 0; i--){

        integ_delta_b_rel_true.at(i) = integ_delta_b_rel_true.at(i+1) + b_rel.at(i) - 1;
        integ_delta_b_rel_false.at(i) = integ_delta_b_rel_false.at(i+1) + b_rel.at(i);
    }

};


// get-functions

std::vector<double> CIA::get_T() {

    return T;
};


std::vector<double> CIA::get_b_rel() {

    return b_rel;
};


double CIA::get_ub() {

    return ub;
};


std::vector<double> CIA::get_Tg() {

    return Tg;
};


std::vector<double> CIA::get_b_bin() {

    return b_bin;
}


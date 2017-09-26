// cia.hpp

#ifndef VECTOR_H
#define VECTOR_H
#include <vector>
#endif

#ifndef MAP_H
#define MAP_H
#include <map>
#endif

struct bnb_node{

    double priority;
    int d;
    int k;

    double eta;
    int k_prev;
    
    int p;
    int sigma;

};


std::vector<int> cia(const std::vector<double>& b_rel, const int& sigma_max);

void input_validation(const std::vector<double>& b_rel);

void welcome_prompt();

void cia_preparation_phase(const std::vector<double>& b_rel,
    std::vector<double>& delta_b_bin_p_k_true, 
    std::vector<double>& delta_b_bin_p_k_false);

void cia_main_phase(const std::vector<double>& b_rel, const int& sigma_max,
    const std::vector<double>& delta_b_bin_p_k_true, 
    const std::vector<double>& delta_b_bin_p_k_false,
    std::map<int, bnb_node>& bnb_tree);

void cia_postprocessing_phase(std::map<int, bnb_node>& bnb_tree, 
    std::vector<int>& b_bin);

bool bnb_queue_order_comparison(const std::pair<int, bnb_node>& pair_a, 
        const std::pair<int, bnb_node>& pair_b);

struct bnb_node_priority_comparison{
    
    bool operator()(const bnb_node& node_a, const bnb_node& node_b);
    
};

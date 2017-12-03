/*
 * BnBNode.hpp
 *
 */

#ifndef VECTOR_H
#define VECTOR_H
#include <vector>
#endif

#ifndef ALGORITHM_H
#define ALGORITHM_H
#include <algorithm>
#endif

class BnBNode {
    friend class BnBNodeComparison;

public:

    BnBNode(BnBNode * const ptr_parent_node, unsigned int const active_control,
            std::vector<unsigned int> const sigma, unsigned int const depth,
            std::vector<double> const eta_node, double const lb_branch);


    ~BnBNode();

    void child_node_becomes_active();
    void child_node_becomes_inactive();

    unsigned int get_max_sigma() const;

    // get-functions

    BnBNode* get_ptr_parent_node();
    unsigned int get_active_control();
    double get_duration();
    std::vector<unsigned int> get_sigma();
    unsigned int get_depth();
    std::vector<double> get_eta_node();
    double get_lb_branch();

    int get_n_active_children();


private:

    BnBNode * ptr_parent_node;
    unsigned int active_control;
    double duration;
    std::vector<unsigned int> sigma;
    unsigned int depth;
    std::vector<double> eta_node;
    double lb_branch;

    unsigned int n_active_children;

};

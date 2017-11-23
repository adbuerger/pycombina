/*
 *
 * BnBNodeComparison.cpp
 *
 */

#ifndef ALGORITHM_H
#define ALGORITHM_H
#include <algorithm>
#endif

#include "BnBNodeComparison.hpp"


bool BnBNodeComparison::operator() (BnBNode const *node_a, BnBNode const *node_b) const {

    if(node_a->eta_branch != node_b->eta_branch) {

        return(node_a->eta_branch > node_b->eta_branch);
    }

    else if(node_a->depth != node_b->depth) {

        return (node_a->depth < node_b->depth);
    }

    else {

        return (std::max_element(node_a->sigma.begin(), node_a->sigma.end()) > 
            std::max_element(node_b->sigma.begin(), node_b->sigma.end()));
    }
}

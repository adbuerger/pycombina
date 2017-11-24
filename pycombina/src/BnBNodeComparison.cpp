/*
 *
 * BnBNodeComparison.cpp
 *
 */

#include "BnBNodeComparison.hpp"


bool BnBNodeComparison::operator() (BnBNode const *node_a, BnBNode const *node_b) const {

    if(node_a->eta_branch != node_b->eta_branch) {

        return(node_a->eta_branch > node_b->eta_branch);
    }

    else if(node_a->depth != node_b->depth) {

        return (node_a->depth < node_b->depth);
    }

    else {

        return(node_a->get_max_sigma() > node_b->get_max_sigma());
    }
}

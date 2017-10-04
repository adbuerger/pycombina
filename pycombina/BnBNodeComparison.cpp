/*
 *
 * BnBNodeComparison.cpp
 *
 */

// #ifndef BNB_NODE_H
// #define BNB_NODE_H
// #include "BnBNode.hpp"
// #endif

#include "BnBNodeComparison.hpp"


bool BnBNodeComparison::operator() (BnBNode const *node_a, BnBNode const *node_b) const {

    if(node_a->lb != node_b->lb) {

        return(node_a->lb > node_b->lb);
    }

    else if(node_a->depth != node_b->depth) {

        return (node_a->depth < node_b->depth);
    }

    else {

        return (node_a->sigma > node_b->sigma);
    }
}

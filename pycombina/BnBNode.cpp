/*
 * BnBNode.cpp
 *
 */

#include <iostream>

#ifndef BNB_NODE_H
#define BNB_NODE_H
#include "BnBNode.hpp"
#endif

BnBNode::BnBNode(BnBNode * const ptr_parent_node, unsigned int const b,
            unsigned int const sigma, unsigned int const depth,
            double const eta, double const lb)

    : ptr_parent_node(ptr_parent_node),
      b(b),
      sigma(sigma),
      depth(depth),
      eta(eta),
      lb(lb),

      n_active_children(0)

{

    if(ptr_parent_node != NULL) {

        ptr_parent_node->child_node_becomes_active();

    }

}


BnBNode::~BnBNode(){

    if(ptr_parent_node != NULL) {

        ptr_parent_node->child_node_becomes_inactive();
    }

}


void BnBNode::child_node_becomes_active() {

    n_active_children++;    
}


void BnBNode::child_node_becomes_inactive() {

    n_active_children--;

    if(n_active_children == 0) {

        delete this;
    }

    // return; // why did Jung add this return-statement?
}


// get-functions

BnBNode* const BnBNode::get_ptr_parent_node() {

    return ptr_parent_node;
}


unsigned int const BnBNode::get_b() {

    return b;
}


unsigned int const BnBNode::get_sigma() {

    return sigma;
}


unsigned int const BnBNode::get_depth() {

    return depth;
}


double const BnBNode::get_eta() {

    return eta;
}


double const BnBNode::get_lb() {

    return lb;
}


int const BnBNode::get_n_active_children() {

    return n_active_children;
}


/*
 * BnBNode.cpp
 *
 */

#include <iostream>

#ifndef BNB_NODE_H
#define BNB_NODE_H
#include "BnBNode.hpp"
#endif

BnBNode::BnBNode(BnBNode * const ptr_parent_node, unsigned int const active_control,
            std::vector<unsigned int> const sigma, unsigned int const depth,
            std::vector<double> const eta_node, double const eta_branch)

    : ptr_parent_node(ptr_parent_node),
      active_control(active_control),
      sigma(sigma),
      depth(depth),
      eta_node(eta_node),
      eta_branch(eta_branch),

      n_active_children(0)

{

    if(ptr_parent_node) {

        ptr_parent_node->child_node_becomes_active();

    }

}


BnBNode::~BnBNode(){

    if(ptr_parent_node) {

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

BnBNode* BnBNode::get_ptr_parent_node() {

    return ptr_parent_node;
}


unsigned int BnBNode::get_active_control() {

    return active_control;
}


std::vector<unsigned int> BnBNode::get_sigma() {

    return sigma;
}


unsigned int BnBNode::get_depth() {

    return depth;
}


std::vector<double> BnBNode::get_eta_node() {

    return eta_node;
}


double BnBNode::get_eta_branch() {

    return eta_branch;
}


int BnBNode::get_n_active_children() {

    return n_active_children;
}


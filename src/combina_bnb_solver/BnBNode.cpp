/*
 * BnBNode.cpp
 *
 * This file is part of pycombina.
 *
 * Copyright 2017-2018 Adrian Bürger, Clemens Zeile, Sebastian Sager, Moritz Diehl
 *
 * pycombina is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * pycombina is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with pycombina. If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include <iostream>

#ifndef BNB_NODE_H
#define BNB_NODE_H
#include "BnBNode.hpp"
#endif

BnBNode::BnBNode(BnBNode * const ptr_parent_node, unsigned int const active_control,
            std::vector<unsigned int> const sigma, unsigned int const depth,
            std::vector<double> const eta_node, double const lb_branch)

    : ptr_parent_node(ptr_parent_node),
      active_control(active_control),
      sigma(sigma),
      depth(depth),
      eta_node(eta_node),
      lb_branch(lb_branch),

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

        // delete this;
    }

    // return; // why did Jung add this return-statement?
}


unsigned int BnBNode::get_max_sigma() const {

    return * std::max_element(sigma.begin(), sigma.end());
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


double BnBNode::get_lb_branch() {

    return lb_branch;
}


int BnBNode::get_n_active_children() {

    return n_active_children;
}


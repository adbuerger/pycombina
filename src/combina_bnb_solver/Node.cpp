/*
 * Node.cpp
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

#ifndef NODE_H
#define NODE_H
#include "Node.hpp"
#endif

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;

Node::Node(Node* const parent_node,

           unsigned int const b_active,
           unsigned int const n_c,
           
           std::vector<unsigned int> const sigma,

           std::vector<double> const min_down_time,
           std::vector<double> const up_time,
           std::vector<double> const total_up_time,

           unsigned int const depth,
           std::vector<double> const eta,
           double const lb)

    : parent_node(parent_node),

      b_active(b_active),

      sigma(sigma),
      
      min_down_time(min_down_time),
      up_time(up_time),
      total_up_time(total_up_time),

      depth(depth),
      eta(eta),
      lb(lb),

      child_nodes(n_c)

{

    for(unsigned int i = 0; i < n_c; i++) {

        child_nodes[i] = nullptr;
    }

    if(parent_node) {

        parent_node->set_child(this, b_active);
    }
}


Node::~Node(){

    if(parent_node) {

        parent_node->set_child(nullptr, b_active);
    }

}


void Node::set_child(Node* child_node, unsigned int b_active) {

    child_nodes[b_active] = child_node;

    if (no_children_left()) {

        delete this;

        #ifndef NDEBUG
        Node::n_delete_self++;
        #endif
    }

}


bool Node::no_children_left() {

    for (Node* child: child_nodes) {
        
        if (child != nullptr) {

            return false;
        }
    }

    return true;
}


unsigned int Node::get_max_sigma() const {

    return * std::max_element(sigma.begin(), sigma.end());
}


Node* Node::get_parent() {

    return parent_node;
}

std::vector<Node*> Node::get_child_nodes() {

    return child_nodes;
}


unsigned int Node::get_b_active() {

    return b_active;
}


std::vector<unsigned int> Node::get_sigma() {

    return sigma;
}


std::vector<double> Node::get_min_down_time() {

    return min_down_time;
}


std::vector<double> Node::get_up_time() {

    return up_time;
}


std::vector<double> Node::get_total_up_time() {

    return total_up_time;
}


unsigned int Node::get_depth() {

    return depth;
}


std::vector<double> Node::get_eta() {

    return eta;
}


double Node::get_lb() {

    return lb;
}

bool operator<(Node& lhs, Node& rhs) {
    unsigned int lhs_depth = lhs.get_depth(), rhs_depth = rhs.get_depth();
    double lhs_lb = lhs.get_lb(), rhs_lb = rhs.get_lb();
    if(lhs_depth != rhs_depth) {
        return(rhs_depth < lhs_depth);
    }
    else if(lhs_lb != rhs_lb) {
        return(lhs_lb < rhs_lb);
    }
    else {
        return(lhs.get_max_sigma() < rhs.get_max_sigma());
    }
}

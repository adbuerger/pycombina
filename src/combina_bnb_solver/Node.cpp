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

#include <algorithm>

#include "Node.hpp"

Node::Node(const NodePtr& parent_node,
           size_t seq_num,

           unsigned int const b_active,
           
           std::vector<unsigned int> const sigma,

           std::vector<double> const min_down_time,
           std::vector<double> const up_time,
           std::vector<double> const total_up_time,

           unsigned int const depth,
           std::vector<double> const eta,
           double const lb)

    : parent_node(parent_node),
      seqnum(seq_num),

      b_active(b_active),

      sigma(sigma),
      
      min_down_time(min_down_time),
      up_time(up_time),
      total_up_time(total_up_time),

      depth(depth),
      eta(eta),
      lb(lb)
{
#ifndef NDEBUG
    ++Node::n_add;
#endif
}


Node::~Node() {
#ifndef NDEBUG
    ++Node::n_delete;
#endif
}


unsigned int Node::get_max_sigma() const {

    return * std::max_element(sigma.begin(), sigma.end());
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

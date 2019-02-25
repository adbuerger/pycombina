/*
 * Node.hpp
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

#ifndef __COMBINA_NODE_HPP
#define __COMBINA_NODE_HPP

#include <vector>

#include "combina_fwd.hpp"

class Node {
public:

    Node(const NodePtr& parent_node,
         size_t seq_num,

         unsigned int const b_active,
         std::vector<unsigned int> const sigma,

         std::vector<double> const min_down_time,
         std::vector<double> const up_time,
         std::vector<double> const total_up_time,
         
         unsigned int const depth,
         std::vector<double> const eta,
         double const lb);

    NodePtr get_parent() const { return parent_node; }
    size_t get_seq_num() const { return seqnum; }
    
    unsigned int get_b_active();

    unsigned int get_max_sigma() const;
    std::vector<unsigned int> get_sigma();

    std::vector<double> get_min_down_time();
    std::vector<double> get_up_time();
    std::vector<double> get_total_up_time();

    unsigned int get_depth();
    std::vector<double> get_eta();
    double get_lb();

    #ifndef NDEBUG
    static unsigned int n_add;
    static unsigned int n_delete_self;
    static unsigned int n_delete_other;
    #endif


private:
    NodePtr parent_node;
    const size_t seqnum;

    unsigned int b_active;

    std::vector<unsigned int> sigma;
    
    std::vector<double> min_down_time;
    std::vector<double> up_time;
    std::vector<double> total_up_time;

    unsigned int depth;
    std::vector<double> eta;
    double lb;

};

bool operator<(Node& lhs, Node& rhs);

#endif /* end of include guard: __COMBINA_NODE_HPP */

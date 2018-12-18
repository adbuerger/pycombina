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

#ifndef VECTOR_H
#define VECTOR_H
#include <vector>
#endif

#ifndef ALGORITHM_H
#define ALGORITHM_H
#include <algorithm>
#endif

class Node {
    friend class NodeComparison;

public:

    Node(Node* const parent_node,

         unsigned int const b_active,
         unsigned int const n_c,
         std::vector<unsigned int> const sigma,

         std::vector<double> const min_down_time,
         std::vector<double> const up_time,
         std::vector<double> const total_up_time,
         
         unsigned int const depth,
         std::vector<double> const eta,
         double const lb);

    ~Node();


    void set_child(Node* child_node, unsigned int b_active);
    bool no_children_left();

    Node* get_parent();
    std::vector<Node*> get_child_nodes();
    
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

    Node* parent_node;
    std::vector<Node*> child_nodes;

    unsigned int b_active;

    std::vector<unsigned int> sigma;
    
    std::vector<double> min_down_time;
    std::vector<double> up_time;
    std::vector<double> total_up_time;

    unsigned int depth;
    std::vector<double> eta;
    double lb;

};

/*
 *
 * NodeComparison.cpp
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

#include "NodeComparison.hpp"


bool NodeComparison::operator() (Node const *node_a, Node const *node_b) const {


    if(node_a->depth != node_b->depth) {

        return (node_a->depth < node_b->depth);
    }

    else if(node_a->lb != node_b->lb) {

        return(node_a->lb > node_b->lb);
    }
    
    else {

        return(node_a->get_max_sigma() > node_b->get_max_sigma());
    }
}

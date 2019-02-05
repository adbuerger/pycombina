/*
 * NodeQueue.hpp
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

#ifndef __COMBINA_NODE_QUEUE_HPP
#define __COMBINA_NODE_QUEUE_HPP

#include <string>
#include <vector>

#include "combina_fwd.hpp"

class NodeQueue {
protected:
    NodeQueue(CombinaBnBSolver* solver) : solver(solver) {}
    NodeQueue(const NodeQueue& queue) : solver(queue.solver) {}
    virtual ~NodeQueue() {}

public:
    virtual size_t size() const = 0;
    virtual Node* top() const = 0;
    virtual void push(const std::vector<Node*>& nodes) = 0;
    virtual void pop() = 0;

    bool empty() const { return size() == 0; }

    static NodeQueuePtr create(CombinaBnBSolver* solver, std::string type = std::string());
    static void register_type(const std::string& type, const NodeQueueFactory& factory, bool make_default = false);
    static void register_default_types();
    static const std::vector<std::string>& get_types();

protected:
    CombinaBnBSolver* solver;
};

#endif /* end of include guard: __COMBINA_NODE_QUEUE_HPP */

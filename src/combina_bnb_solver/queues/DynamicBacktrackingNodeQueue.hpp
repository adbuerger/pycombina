/*
 * DynamicBacktrackingNodeQueue.hpp
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

#ifndef __COMBINA_DYNAMIC_BACKTRACKING_NODE_QUEUE_HPP
#define __COMBINA_DYNAMIC_BACKTRACKING_NODE_QUEUE_HPP

#include <queue>
#include <deque>

#include "../combina_fwd.hpp"
#include "../Node.hpp"
#include "../NodeQueue.hpp"

class DynamicBacktrackingNodeQueue : public NodeQueue {
public:
    DynamicBacktrackingNodeQueue(CombinaBnBSolver* solver);
    DynamicBacktrackingNodeQueue(const DynamicBacktrackingNodeQueue& queue);
    DynamicBacktrackingNodeQueue(DynamicBacktrackingNodeQueue&& queue);
    virtual ~DynamicBacktrackingNodeQueue();

    double get_global_lb() const { return glob_lb; }
    virtual size_t size() const;
    virtual NodePtr top() const;
    virtual void push(const std::vector<NodePtr>& node);
    virtual void pop();
    virtual void clear();

private:
    double calculate_cutoff();
    void rearrange_nodes();

    double glob_lb;
    double min_beta;
    std::vector<NodePtr> heap;
    std::deque<NodePtr> stack;
};

#endif /* end of include guard: __COMBINA_DYNAMIC_BACKTRACKING_NODE_QUEUE_HPP */

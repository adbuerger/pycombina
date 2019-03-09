/*
 * DepthFirstNodeQueue.hpp
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

#ifndef __COMBINA_DEPTH_FIRST_NODE_QUEUE_HPP
#define __COMBINA_DEPTH_FIRST_NODE_QUEUE_HPP

#include <queue>

#include "../combina_fwd.hpp"
#include "../NodeQueue.hpp"

class DepthFirstNodeQueue : public NodeQueue {
public:
    DepthFirstNodeQueue(CombinaBnBSolver* solver);
    DepthFirstNodeQueue(const DepthFirstNodeQueue& queue);
    DepthFirstNodeQueue(DepthFirstNodeQueue&& queue);
    ~DepthFirstNodeQueue();

    virtual size_t size() const;
    virtual NodePtr top() const;
    virtual void push(const std::vector<NodePtr>& nodes);
    virtual void pop();
    virtual void clear();

private:
    std::deque<NodePtr> stack;
};

#endif /* end of include guard: __COMBINA_DFS_NODE_QUEUE_HPP */

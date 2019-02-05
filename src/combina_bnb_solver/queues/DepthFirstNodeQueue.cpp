/*
 * DepthFirstNodeQueue.cpp
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

#include "DepthFirstNodeQueue.hpp"
#include "../Node.hpp"

DepthFirstNodeQueue::DepthFirstNodeQueue(CombinaBnBSolver* solver)
    : NodeQueue(solver),
      stack()
{}

DepthFirstNodeQueue::DepthFirstNodeQueue(const DepthFirstNodeQueue& queue)
    : NodeQueue(queue),
      stack(queue.stack)
{}

DepthFirstNodeQueue::DepthFirstNodeQueue(DepthFirstNodeQueue&& queue)
    : NodeQueue(std::forward<NodeQueue>(queue)),
      stack(std::move(queue.stack))
{}

DepthFirstNodeQueue::~DepthFirstNodeQueue()
{}

size_t DepthFirstNodeQueue::size() const {
    return stack.size();
}

Node* DepthFirstNodeQueue::top() const {
    return stack.top();
}

void DepthFirstNodeQueue::push(const std::vector<Node*>& nodes) {
    std::vector<Node*> sorted = nodes;
    std::sort(sorted.begin(), sorted.end(), [](Node* const lhs, Node* const rhs) {
        return *rhs < *lhs;
    });
    for(Node* node : sorted) {
        stack.push(node);
    }
}

void DepthFirstNodeQueue::pop() {
    stack.pop();
}

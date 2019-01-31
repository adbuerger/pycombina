/*
 * DynamicBacktrackingNodeQueue.cpp
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

#include "DynamicBacktrackingNodeQueue.hpp"

#include <limits>

DynamicBacktrackingNodeQueue::DynamicBacktrackingNodeQueue(double beta, CombinaBnBSolver* solver)
    : NodeQueue(solver),
      beta(beta),
      glob_lb(std::numeric_limits<double>::infinity()),
      heap(),
      stack()
{}

DynamicBacktrackingNodeQueue::DynamicBacktrackingNodeQueue(const DynamicBacktrackingNodeQueue& queue)
    : NodeQueue(queue),
      beta(queue.beta),
      glob_lb(queue.glob_lb),
      heap(queue.heap),
      stack(queue.stack)
{}

DynamicBacktrackingNodeQueue::DynamicBacktrackingNodeQueue(DynamicBacktrackingNodeQueue&& queue)
    : NodeQueue(std::forward<NodeQueue>(queue)),
      beta(queue.beta),
      glob_lb(queue.glob_lb),
      heap(std::move(queue.heap)),
      stack(std::move(queue.stack))
{}

DynamicBacktrackingNodeQueue::~DynamicBacktrackingNodeQueue()
{}

double DynamicBacktrackingNodeQueue::get_cutoff() const {
    return glob_lb + beta * (solver->get_ub() - glob_lb);
}

size_t DynamicBacktrackingNodeQueue::size() const {
    return heap.size() + stack.size();
}

Node* DynamicBacktrackingNodeQueue::top() const {
    // refill stack if necessary
    if(stack.empty()) {
        return heap.top();
    }
    else {
        return stack.front();
    }
}

void DynamicBacktrackingNodeQueue::push(const std::vector<Node*>& nodes) {
    std::vector<Node*> sorted = nodes;
    std::sort(sorted.begin(), sorted.end(), [](Node* const lhs, Node* const rhs) {
        return *rhs < *lhs;
    });
    for(Node* node : sorted) {
        stack.push_front(node);
        if(node->get_lb() < glob_lb) {
            glob_lb = node->get_lb();
        }
    }
}

void DynamicBacktrackingNodeQueue::pop() {
    // remove topmost node from stack
    Node* node;
    if(stack.empty()) {
        node = heap.top();
	heap.pop();
    }
    else {
        node = stack.front();
        stack.pop_front();
    }

    // recalculate global lower bound if necessary
    if(node->get_lb() == glob_lb) {
        glob_lb = solver->get_ub();
        for(Node* const stack_node : stack) {
            glob_lb = std::min(stack_node->get_lb(), glob_lb);
        }
        if(!heap.empty()) {
            glob_lb = std::min(heap.top()->get_lb(), glob_lb);
        }
    }

    // move nodes above cutoff from stack to heap
    const double cutoff = get_cutoff();
    while(!stack.empty() && stack.front()->get_lb() > cutoff) {
        heap.push(stack.front());
        stack.pop_front();
    }
}

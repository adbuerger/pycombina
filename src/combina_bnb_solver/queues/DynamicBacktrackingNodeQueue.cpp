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

#include <cmath>
#include <limits>

DynamicBacktrackingNodeQueue::DynamicBacktrackingNodeQueue(double beta, double gamma, CombinaBnBSolver* solver)
    : NodeQueue(solver),
      beta(beta),
      gamma(gamma),
      glob_lb(std::numeric_limits<double>::infinity()),
      heap(),
      stack()
{}

DynamicBacktrackingNodeQueue::DynamicBacktrackingNodeQueue(const DynamicBacktrackingNodeQueue& queue)
    : NodeQueue(queue),
      beta(queue.beta),
      gamma(queue.gamma),
      glob_lb(queue.glob_lb),
      heap(queue.heap),
      stack(queue.stack)
{}

DynamicBacktrackingNodeQueue::DynamicBacktrackingNodeQueue(DynamicBacktrackingNodeQueue&& queue)
    : NodeQueue(std::forward<NodeQueue>(queue)),
      beta(queue.beta),
      gamma(queue.gamma),
      glob_lb(queue.glob_lb),
      heap(std::move(queue.heap)),
      stack(std::move(queue.stack))
{}

DynamicBacktrackingNodeQueue::~DynamicBacktrackingNodeQueue()
{}

size_t DynamicBacktrackingNodeQueue::size() const {
    return heap.size() + stack.size();
}

Node* DynamicBacktrackingNodeQueue::top() const {
    // rearrange nodes internally
    const_cast<DynamicBacktrackingNodeQueue*>(this)->rearrange_nodes();

    // return next node
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
        glob_lb = solver->get_eta();
        for(Node* const stack_node : stack) {
            glob_lb = std::min(stack_node->get_lb(), glob_lb);
        }
        if(!heap.empty()) {
            glob_lb = std::min(heap.top()->get_lb(), glob_lb);
        }
    }
}

double DynamicBacktrackingNodeQueue::calculate_cutoff(Node* node) const {
    // determine upper bound, maximum depth, and solution count
    const double glob_ub = solver->get_eta();
    const double max_depth = solver->get_num_t();
    const unsigned long n_sol = solver->get_num_sol();

    // calculate derived parameter beta
    const double node_beta = beta + (1.0 - beta) * std::pow(1.0 - double(node->get_depth()) / max_depth, gamma * n_sol);

    // return convex combination of lower and upper bound
    return glob_lb + node_beta * (glob_ub - glob_lb);
}

void DynamicBacktrackingNodeQueue::rearrange_nodes() {
    const double glob_ub = solver->get_eta();
    Node* node;

    // process top stack elements, stop early if fathomable
    while(!stack.empty() && (node = stack.front())->get_lb() <= glob_ub) {
        // compute depth-specific cutoff point
        const double cutoff = calculate_cutoff(node);

        // proceed according to lower bound
        if(node->get_lb() <= cutoff) {
            break;
        }

        // move ignored node to heap
        heap.push(node);
        stack.pop_front();
    }
}

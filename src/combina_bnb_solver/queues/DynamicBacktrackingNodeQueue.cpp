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

DynamicBacktrackingNodeQueue::DynamicBacktrackingNodeQueue(CombinaBnBSolver* solver)
    : NodeQueue(solver),
      glob_lb(std::numeric_limits<double>::infinity()),
      min_beta(1.0),
      heap(),
      stack()
{}

DynamicBacktrackingNodeQueue::DynamicBacktrackingNodeQueue(const DynamicBacktrackingNodeQueue& queue)
    : NodeQueue(queue),
      glob_lb(queue.glob_lb),
      min_beta(queue.min_beta),
      heap(queue.heap),
      stack(queue.stack)
{}

DynamicBacktrackingNodeQueue::DynamicBacktrackingNodeQueue(DynamicBacktrackingNodeQueue&& queue)
    : NodeQueue(std::forward<NodeQueue>(queue)),
      glob_lb(queue.glob_lb),
      min_beta(queue.min_beta),
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

double DynamicBacktrackingNodeQueue::calculate_cutoff() {
    // determine upper bound, number of solutions, and queue size
    const double glob_ub = solver->get_eta();
    const unsigned long n_sol = solver->get_num_sol();
    const size_t n_node = size();

    // perform depth-first search until first UB is found
    if(n_sol == 0) {
        min_beta = 1.0;
        return glob_ub;
    }

    // compute beta
    double beta = 1.0 - std::min(1.0, double(n_sol) / 10.0);
    beta += std::min(1.0 - beta, double(n_node) / 4e5);
    if(beta < min_beta) {
        min_beta = beta;
    }

    return glob_lb + beta * (glob_ub - glob_lb);
}

void DynamicBacktrackingNodeQueue::rearrange_nodes() {
    const double glob_ub = solver->get_eta();
    const double cutoff = calculate_cutoff();
    Node* node;

    // process top stack elements, stop early if fathomable
    while(!stack.empty() && (node = stack.front())->get_lb() <= glob_ub) {
        // proceed according to lower bound
        if(node->get_lb() <= cutoff) {
            break;
        }

        // move ignored node to heap
        heap.push(node);
        stack.pop_front();
    }
}

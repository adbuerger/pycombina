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

#include <algorithm>

#include "DynamicBacktrackingNodeQueue.hpp"
#include "../CombinaBnBSolver.hpp"

#include <cmath>
#include <limits>


static bool node_comparator(const NodePtr& lhs, const NodePtr& rhs) {
    return *rhs < *lhs;
}

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

NodePtr DynamicBacktrackingNodeQueue::top() const {
    // rearrange nodes internally
    const_cast<DynamicBacktrackingNodeQueue*>(this)->rearrange_nodes();

    // return next node
    if(stack.empty()) {
        return heap.front();
    }
    else {
        return stack.front();
    }
}

void DynamicBacktrackingNodeQueue::push(const std::vector<NodePtr>& nodes) {
    std::vector<NodePtr> sorted = nodes;
    std::sort(sorted.begin(), sorted.end(), [](const NodePtr& lhs, const NodePtr& rhs) {
        return *rhs < *lhs;
    });
    for(const NodePtr& node : sorted) {
        stack.push_front(node);
        if(node->get_lb() < glob_lb) {
            glob_lb = node->get_lb();
        }
    }
}

void DynamicBacktrackingNodeQueue::pop() {
    // remove topmost node from stack
    NodePtr node;
    if(stack.empty()) {
        node = heap.front();
        std::pop_heap(heap.begin(), heap.end(), node_comparator);
        heap.pop_back();
    }
    else {
        node = stack.front();
        stack.pop_front();
    }

    // recalculate global lower bound if necessary
    if(node->get_lb() == glob_lb) {
        glob_lb = solver->get_eta();
        for(const NodePtr& stack_node : stack) {
            glob_lb = std::min(stack_node->get_lb(), glob_lb);
        }
        if(!heap.empty()) {
            glob_lb = std::min(heap.front()->get_lb(), glob_lb);
        }
    }
}

void DynamicBacktrackingNodeQueue::clear() {
    glob_lb = std::numeric_limits<double>::infinity();
    min_beta = 1.0;
    heap.clear();
    stack.clear();
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
    beta += std::min(1.0 - beta, (1.0 - min_beta) * (double(n_node) / 100000.0));
    if(beta < min_beta) {
        min_beta = beta;
    }

    return glob_lb + beta * (glob_ub - glob_lb);
}

void DynamicBacktrackingNodeQueue::rearrange_nodes() {
    const double glob_ub = solver->get_eta();
    const double cutoff = calculate_cutoff();
    NodePtr node;

    // process top stack elements, stop early if fathomable
    while(!stack.empty() && (node = stack.front())->get_lb() <= glob_ub) {
        // proceed according to lower bound
        if(node->get_lb() <= cutoff) {
            break;
        }

        // move ignored node to heap
        heap.push_back(node);
        std::push_heap(heap.begin(), heap.end(), node_comparator);
        stack.pop_front();
    }
}

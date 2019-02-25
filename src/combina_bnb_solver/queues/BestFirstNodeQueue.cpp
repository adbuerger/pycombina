/*
 * BestFirstNodeQueue.cpp
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

#include "BestFirstNodeQueue.hpp"


static bool node_comparator(const NodePtr& lhs, const NodePtr& rhs) {
    return *rhs < *lhs;
}

BestFirstNodeQueue::BestFirstNodeQueue(CombinaBnBSolver* solver)
    : NodeQueue(solver), queue()
{}

BestFirstNodeQueue::BestFirstNodeQueue(const BestFirstNodeQueue& queue)
    : NodeQueue(queue), queue(queue.queue)
{}

BestFirstNodeQueue::BestFirstNodeQueue(BestFirstNodeQueue&& queue)
    : NodeQueue(std::forward<NodeQueue>(queue)), queue(std::move(queue.queue))
{}

BestFirstNodeQueue::~BestFirstNodeQueue()
{}

size_t BestFirstNodeQueue::size() const {
    return queue.size();
}

NodePtr BestFirstNodeQueue::top() const {
    return queue.front();
}

void BestFirstNodeQueue::push(const std::vector<NodePtr>& nodes) {
    for(NodePtr node : nodes) {
        queue.push_back(node);
        std::push_heap(queue.begin(), queue.end(), node_comparator);
    }
}

void BestFirstNodeQueue::pop() {
    std::pop_heap(queue.begin(), queue.end(), node_comparator);
    queue.pop_back();
}

void BestFirstNodeQueue::clear() {
    queue.clear();
}

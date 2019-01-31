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

#include "BestFirstNodeQueue.hpp"

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

Node* BestFirstNodeQueue::top() const {
    return queue.top();
}

void BestFirstNodeQueue::push(const std::vector<Node*>& nodes) {
    for(Node* node : nodes) {
        queue.push(node);
    }
}

void BestFirstNodeQueue::pop() {
    queue.pop();
}

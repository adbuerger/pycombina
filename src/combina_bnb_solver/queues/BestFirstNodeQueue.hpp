/*
 * BestFirstNodeQueue.hpp
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

#ifndef __COMBINA_BEST_FIRST_NODE_QUEUE_HPP
#define __COMBINA_BEST_FIRST_NODE_QUEUE_HPP

#include <queue>
#include <vector>

#include "../Node.hpp"
#include "../NodeQueue.hpp"

class BestFirstNodeQueue : public NodeQueue {
public:
    BestFirstNodeQueue(CombinaBnBSolver* solver);
    BestFirstNodeQueue(const BestFirstNodeQueue& queue);
    BestFirstNodeQueue(BestFirstNodeQueue&& queue);
    virtual ~BestFirstNodeQueue();

    virtual size_t size() const;
    virtual Node* top() const;
    virtual void push(const std::vector<Node*>& node);
    virtual void pop();

protected:
    struct compare_nodes {
        bool operator()(Node* const lhs, Node* const rhs) const {
            return *rhs < *lhs;
        }
    };

private:
    std::priority_queue<Node*, std::vector<Node*>, compare_nodes> queue;
};

#endif /* end of include guard: __COMBINA_BEST_FIRST_NODE_QUEUE_HPP */

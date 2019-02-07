/*
 * BestThenDiveNodeQueue.hpp
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

#ifndef __COMBINA_BEST_THEN_DIVE_NODE_QUEUE_HPP
#define __COMBINA_BEST_THEN_DIVE_NODE_QUEUE_HPP

#include <vector>
#include <utility>

#include "../combina_fwd.hpp"
#include "../NodeQueue.hpp"

class BestThenDiveNodeQueue : public NodeQueue {
public:
    BestThenDiveNodeQueue(CombinaBnBSolver* solver);
    BestThenDiveNodeQueue(const BestThenDiveNodeQueue& queue);
    BestThenDiveNodeQueue(BestThenDiveNodeQueue&& queue);
    virtual ~BestThenDiveNodeQueue();

    virtual size_t size() const;
    virtual Node* top() const;
    virtual void pop();
    virtual void push(const std::vector<Node*>& nodes);

private:
    double adjusted_lower_bound(Node* const node) const;
    bool prefer_dive(Node* const lhs, Node* const rhs) const;
    bool later_root(const std::pair<double, Node*>& lhs, const std::pair<double, Node*>& rhs) const;

    Node* curtop;
    std::vector<Node*> limbo;
    std::vector<std::pair<double, Node*>> store;
};

#endif /* end of include guard: __COMBINA_RESTRICTED_BEST_THEN_DIVE_NODE_QUEUE_HPP */

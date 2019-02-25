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
    virtual NodePtr top() const;
    virtual void pop();
    virtual void push(const std::vector<NodePtr>& nodes);
    virtual void clear();

private:
    double adjusted_lower_bound(const NodePtr& node) const;
    bool prefer_dive(const NodePtr& lhs, const NodePtr& rhs) const;
    bool later_root(const std::pair<double, NodePtr>& lhs, const std::pair<double, NodePtr>& rhs) const;

    NodePtr curtop;
    std::vector<NodePtr> limbo;
    std::vector<std::pair<double, NodePtr>> store;
};

#endif /* end of include guard: __COMBINA_BEST_THEN_DIVE_NODE_QUEUE_HPP */

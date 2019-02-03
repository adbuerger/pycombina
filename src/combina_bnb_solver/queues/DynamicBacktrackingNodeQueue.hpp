/*
 * DynamicBacktrackingNodeQueue.hpp
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

#ifndef __COMBINA_DYNAMIC_BACKTRACKING_NODE_QUEUE_HPP
#define __COMBINA_DYNAMIC_BACKTRACKING_NODE_QUEUE_HPP

#include <queue>
#include <deque>

#include "../NodeQueue.hpp"

class DynamicBacktrackingNodeQueue : public NodeQueue {
public:
    DynamicBacktrackingNodeQueue(double beta, double gamma, CombinaBnBSolver* solver);
    DynamicBacktrackingNodeQueue(const DynamicBacktrackingNodeQueue& queue);
    DynamicBacktrackingNodeQueue(DynamicBacktrackingNodeQueue&& queue);
    virtual ~DynamicBacktrackingNodeQueue();

    void set_beta(double val) { beta = val; }
    void set_gamma(double val) { gamma = val; }
    double get_beta() const { return beta; }
    double get_gamma() const { return gamma; }
    double get_global_lb() const { return glob_lb; }

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
    double calculate_cutoff(Node* node) const;
    void rearrange_nodes();

    double beta;
    double gamma;
    double glob_lb;
    std::priority_queue<Node*, std::vector<Node*>, compare_nodes> heap;
    std::deque<Node*> stack;
};

#endif /* end of include guard: __COMBINA_DYNAMIC_BACKTRACKING_NODE_QUEUE_HPP */

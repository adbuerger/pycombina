/*
 * Monitor.hpp
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

#ifndef __COMBINA_MONITOR_HPP
#define __COMBINA_MONITOR_HPP

#include <forward_list>

#include "combina_fwd.hpp"


/// Node states for monitor notification.
enum NodeState {
    NODE_ACTIVE,
    NODE_SELECTED,
    NODE_FATHOMED,
    NODE_INFEASIBLE,
    NODE_SOLVED,
    NODE_INTEGER,
};


/// Abstract base class for monitors.
class MonitorBase {
protected:
    CombinaBnBSolver* const solver;

public:
    MonitorBase(CombinaBnBSolver *solver) : solver(solver) {}
    MonitorBase(const MonitorBase& monitor) : solver(monitor.solver) {}
    virtual ~MonitorBase() = 0;

    virtual void on_start_search();                         ///< Branch-and-bound has been started.
    virtual void on_create(Node* node);                     ///< Node has been created.
    virtual void on_select(Node* node);                     ///< Node has been selected.
    virtual void on_change(Node* node, NodeState state);    ///< Node state has changed.
    virtual void on_stop_search();                          ///< Branch-and-bound has been stopped.
};


/// Adaptor for multiple monitors.
class MultiMonitor : public MonitorBase {
private:
    std::forward_list<MonitorPtr> monitors;

public:
    MultiMonitor(CombinaBnBSolver* solver)
        : MonitorBase(solver)
    {}

    MultiMonitor(const MultiMonitor& monitor)
        : MonitorBase(monitor),
          monitors(monitor.monitors)
    {}

    MultiMonitor(MultiMonitor&& monitor)
        : MonitorBase(std::forward<MonitorBase>(monitor)),
          monitors(std::move(monitor.monitors))
    {}

    virtual void on_start_search();
    virtual void on_create(Node* node);
    virtual void on_select(Node* node);
    virtual void on_change(Node* node, NodeState state);
    virtual void on_stop_search();
};

#endif /* end of include guard: __COMBINA_MONITOR_HPP */

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

#include "Monitor.hpp"


MonitorBase::~MonitorBase() {}


void MonitorBase::on_start_search() {}


void MonitorBase::on_create(Node* node) {}


void MonitorBase::on_select(Node* node) {}


void MonitorBase::on_change(Node* node, NodeState state) {}


void MonitorBase::on_stop_search() {}


void MultiMonitor::on_start_search() {
    for(MonitorPtr p : monitors) {
        p->on_start_search();
    }
}


void MultiMonitor::on_create(Node* node) {
    for(MonitorPtr p : monitors) {
        p->on_create(node);
    }
}


void MultiMonitor::on_select(Node* node) {
    for(MonitorPtr p : monitors) {
        p->on_select(node);
    }
}


void MultiMonitor::on_change(Node* node, NodeState state) {
    for(MonitorPtr p : monitors) {
        p->on_change(node, state);
    }
}


void MultiMonitor::on_stop_search() {
    for(MonitorPtr p : monitors) {
        p->on_stop_search();
    }
}

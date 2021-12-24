/*
 * NodeQueue.hpp
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

#include "NodeQueue.hpp"
#include "queues/BestFirstNodeQueue.hpp"
#include "queues/BestThenDiveNodeQueue.hpp"
#include "queues/DepthFirstNodeQueue.hpp"
#include "queues/DynamicBacktrackingNodeQueue.hpp"

#include <algorithm>
#include <iterator>
#include <map>
#include <memory>
#include <string>
#include <vector>

// data structures for type registry
static std::map<std::string, NodeQueueFactory> type_registry;
static std::vector<std::string> type_names;
static std::string default_type_name;

/**
 * \brief Create node queue of a given type.
 *
 * This method requires that register_type() be used first to register
 * a factory function with the type registry. By default, the method
 * will create a NodeQueue of the type last marked as default.
 *
 * \param [in] solver pointer to the owning Combina solver instance.
 * \param [in] type denotes the type of NodeQueue desired.
 *
 * \throw std::out_of_range if the given type has not been registered.
 *
 * \returns A shared pointer to a newly created NodeQueue.
 */
NodeQueuePtr NodeQueue::create(CombinaBnBSolver* solver, std::string type) {
    if(type.empty()) {
        type = default_type_name;
    }

    auto factory = type_registry.at(type);
    return factory(solver);
}

/**
 * \brief Registers a new NodeQueue type.
 *
 * The given factory function is entered into the type registry,
 * overwriting any previously registered type of the same name. If
 * make_default is set, the type name is registered as the default
 * type name.
 *
 * \param [in] type name of the new type.
 * \param [in] factory factory function for the new type.
 * \param [in] make_default indicates that the new type should be made
 *      the new default type.
 *
 * \note The first type to be registered is always made the default
 *      type, regardless of whether make_default is set.
 */
void NodeQueue::register_type(const std::string& type, const NodeQueueFactory& factory, bool make_default) {
    type_registry.emplace(type, factory);
    if(make_default || default_type_name.empty()) {
        default_type_name = type;
    }

    type_names.clear();
    std::transform(type_registry.cbegin(), type_registry.cend(), std::back_inserter(type_names), [](const auto& entry) {
        return entry.first;
    });
}

/**
 * \brief Registers built-in default NodeQueue types.
 *
 * To achieve the desired behavior, this method should be called
 * before registering any additional types. It will register the
 * built-in default NodeQueue types for depth-first and best-first
 * search as well as any additional strategies that may be implemented
 * by the core Combina solver. It ensures that DFS is the default
 * strategy.
 */
void NodeQueue::register_default_types() {
    register_type("dfs", [](CombinaBnBSolver* solver) {
            return std::make_shared<DepthFirstNodeQueue>(solver);
        }, true);
    register_type("bfs", [](CombinaBnBSolver* solver) {
            return std::make_shared<BestFirstNodeQueue>(solver);
        });
    register_type("btd", [](CombinaBnBSolver* solver) {
            return std::make_shared<BestThenDiveNodeQueue>(solver);
        });
    register_type("dbt", [](CombinaBnBSolver* solver) {
            return std::make_shared<DynamicBacktrackingNodeQueue>(solver);
        });
}

/**
 * \brief Returns a sorted list of registered type names.
 */
const std::vector<std::string>& NodeQueue::get_types() {
    return type_names;
}

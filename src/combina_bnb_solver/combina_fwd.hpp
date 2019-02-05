/*
 * combina_fwd.hpp
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

#ifndef __COMBINA_FWD_HPP
#define __COMBINA_FWD_HPP

#include <functional>
#include <memory>

class CombinaBnBSolver;
class Node;
class NodeQueue;

typedef std::shared_ptr<Node> NodePtr;
typedef std::shared_ptr<const Node> ConstNodePtr;
typedef std::shared_ptr<NodeQueue> NodeQueuePtr;
typedef std::shared_ptr<const NodeQueue> ConstNodeQueuePtr;
typedef std::function<NodeQueuePtr (CombinaBnBSolver*)> NodeQueueFactory;

#endif /* end of include guard: __COMBINA_FWD_HPP */

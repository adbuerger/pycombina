/*
 * BnBNode.cpp
 *
 */

#ifndef BNB_NODE_H
#define BNB_NODE_H
#include "BnBNode.hpp"
#endif

BnBNode::BnBNode(BnBNode * const ptr_parent_node, unsigned int const p,
            unsigned int const sigma, unsigned int depth, double lb)

    : ptr_parent_node(ptr_parent_node),
      p(p),
      sigma(sigma),
      depth(depth),
      lb(lb),
      priority(priority)

{

};


BnBNode::~BnBNode(){

};

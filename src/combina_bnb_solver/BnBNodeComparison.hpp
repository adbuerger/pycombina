/*
 *
 * BnBNodeComparison.hpp
 *
 */

#ifndef BNB_NODE_H
#define BNB_NODE_H
#include "BnBNode.hpp"
#endif

class BnBNodeComparison {

public:

    BnBNodeComparison() {};

    ~BnBNodeComparison() {};

    bool operator() (BnBNode const *node_a, BnBNode const *node_b) const;
};

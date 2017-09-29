/*
 * BnBNode.hpp
 *
 */

class BnBNode {
    friend class BnBNodeComparison;

public:

    BnBNode(BnBNode * const ptr_parent_node, unsigned int const p,
            unsigned int const sigma, unsigned int depth, double lb, 
            double priority);


    ~BnBNode();

};

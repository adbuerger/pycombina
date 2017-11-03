/*
 * BnBNode.hpp
 *
 */

class BnBNode {
    friend class BnBNodeComparison;

public:

    BnBNode(BnBNode * const ptr_parent_node, unsigned int const b,
            unsigned int const sigma, unsigned int const depth,
            double const eta, double const lb);


    ~BnBNode();

    void child_node_becomes_active();
    void child_node_becomes_inactive();


    // get-functions

    BnBNode* const get_ptr_parent_node();
    unsigned int const get_b();
    double const get_duration();
    unsigned int const get_sigma();
    unsigned int const get_depth();
    double const get_eta();
    double const get_lb();

    int const get_n_active_children();


private:

    BnBNode * ptr_parent_node;
    unsigned int b;
    double duration;
    unsigned int sigma;
    unsigned int depth;
    double eta;
    double lb;

    unsigned int n_active_children;

};

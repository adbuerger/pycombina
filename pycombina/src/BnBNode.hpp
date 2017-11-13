/*
 * BnBNode.hpp
 *
 */

class BnBNode {
    friend class BnBNodeComparison;

public:

    BnBNode(BnBNode * const ptr_parent_node, unsigned int const b,
            unsigned int const sigma, unsigned int const depth,
            double const eta_node, double const eta_branch);


    ~BnBNode();

    void child_node_becomes_active();
    void child_node_becomes_inactive();


    // get-functions

    BnBNode* get_ptr_parent_node();
    unsigned int get_b();
    double get_duration();
    unsigned int get_sigma();
    unsigned int get_depth();
    double get_eta_node();
    double get_eta_branch();

    int get_n_active_children();


private:

    BnBNode * ptr_parent_node;
    unsigned int b;
    double duration;
    unsigned int sigma;
    unsigned int depth;
    double eta_node;
    double eta_branch;

    unsigned int n_active_children;

};

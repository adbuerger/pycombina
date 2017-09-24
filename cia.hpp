// cia.h

struct bnb_input{

    double *b_data;
    int n_b;
    int sigma_max;

};


struct bnb_output{

    int *b_data;
    int eta;
    int k;

};


struct node{

    double priority;
    int d;
    int k;

    double eta;
    int k_prev;
    
    int p;
    int sigma;

};

struct node_comparison{
    
    bool operator()(const node& node_1, const node& node_2);
    
};



void cia(const bnb_input &bnb_data_init, bnb_output *bnb_output_data);

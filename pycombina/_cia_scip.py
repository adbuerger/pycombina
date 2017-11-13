from pyscipopt import Model, quicksum

class CIA_SCIP:

    def get_T(self):

        return self.T


    def get_b_rel(self):

        return self.b_rel


    def get_eta(self):

        return self.etalpr


    def get_Tg(self):

        return self.Tg


    def get_b_bin(self):

        return self.b_bin


    def validate_input_dimensions(self):

        if len(self.T) != (len(self.b_rel) + 1):

            raise ValueError("T must contain one element more than b_rel.")


    def validate_input_values_T(self):

        for i, t in enumerate(self.T[:-1]):

            if (self.T[i+1] - t) <= 0.0:

                raise ValueError("Values in T must be strictly increasing.")


    def validate_input_values_b_rel(self):

        for b in self.b_rel:

            if ((b < 0.0) or (b > 1.0)):

                raise ValueError("All elements b of the relaxed binary input must be 0 <= b <= 1.")


    def validate_input_values(self):

        self.validate_input_values_T()
        self.validate_input_values_b_rel()


    def validate_input_data(self):

        self.validate_input_dimensions()
        self.validate_input_values()


    def __init__(self, T, b_rel):

        self.T = T
        self.b_rel = b_rel

        self.N = 0
        self.Tg = []
        
        self.eta = 0
        self.b_bin = []

        self.validate_input_data()


    def determine_number_of_control_intervals(self):

        self.N = len(self.b_rel)


    def compute_time_grid_from_time_points(self):

        self.Tg = [0] * self.N

        for i in range(1, self.N):

            self.Tg[i-1] = self.T[i] - self.T[i-1]


    def setup_sigma_max(self, sigma_max):

        self.sigma_max = sigma_max


    def prepare_bnb_data(self):

        self.determine_number_of_control_intervals()
        self.compute_time_grid_from_time_points()


    def initialize_scip_model(self):

        self.model  = Model("Combinatorial Integral Approximation MILP")
        

    def setup_model_variables(self):

        self.eta = self.model.addVar(name = "eta")

        self.b_bin_sym = {}
        self.s = {}

        for i in range(self.N-1):

            self.s[i] = self.model.addVar(vtype = "C", name = "s_%s"%i)

            self.b_bin_sym[i] = self.model.addVar( \
                vtype = "I", ub = 1, name = "b_bin_%s"%i)

        self.b_bin_sym[self.N-1] = self.model.addVar( \
            vtype = "I", ub = 1, name = "b_bin_%s"%(self.N-1))


    def setup_objective(self):

        self.model.setObjective(self.eta)


    def setup_maximum_switching_constraints(self):

        # Using only the relevant facets, see:
        # Sager et al.: Combinatorial integral approximation, 2010

        for i in range(self.N-1):

            self.model.addCons(self.s[i] >= self.b_bin_sym[i] - self.b_bin_sym[i+1])
            self.model.addCons(self.s[i] >= -self.b_bin_sym[i] + self.b_bin_sym[i+1])
            self.model.addCons(self.s[i] <= self.b_bin_sym[i] + self.b_bin_sym[i+1])
            self.model.addCons(self.s[i] <= 2 - self.b_bin_sym[i] - self.b_bin_sym[i+1])

        if self.sigma_max % 2 == 0:

            self.model.addCons(self.sigma_max >= self.b_bin_sym[0] - \
                self.b_bin_sym[self.N-1] + quicksum([self.s[i] for i in range(self.N-1)]))
            self.model.addCons(self.sigma_max >= self.b_bin_sym[self.N-1] - \
                self.b_bin_sym[0] + quicksum([self.s[i] for i in range(self.N-1)]))

        else:

            self.model.addCons(self.sigma_max >= 1 - self.b_bin_sym[0] - \
                self.b_bin_sym[self.N-1] + quicksum([self.s[i] for i in range(self.N-1)]))
            self.model.addCons(self.sigma_max >= self.b_bin_sym[0] + \
                self.b_bin_sym[self.N-1] - 1 + quicksum([self.s[i] for i in range(self.N-1)]))


    def setup_approximation_inequalites(self):

        for i in range(self.N):

            self.model.addCons(self.eta >= quicksum( \
                [self.b_rel[j] - self.b_bin_sym[j] for j in range(i)]))
            self.model.addCons(self.eta >= -quicksum( \
                [self.b_rel[j] - self.b_bin_sym[j] for j in range(i)]))


    def setup_milp(self):

        self.initialize_scip_model()
        self.setup_model_variables()
        self.setup_objective()
        self.setup_maximum_switching_constraints()
        self.setup_approximation_inequalites()


    def solve_milp(self):

        self.model.optimize()


    def run_bnb(self):

        self.setup_milp()
        self.solve_milp()


    def retrieve_solution(self):

        self.eta = self.model.getVal(self.eta)
        self.b_bin = [self.model.getVal(self.b_bin_sym[i]) for i in range(self.N)]


    def run_cia(self, sigma_max = 2):

        self.setup_sigma_max(sigma_max)
        self.prepare_bnb_data()
        self.run_bnb()
        self.retrieve_solution()

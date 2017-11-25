class CIAMilp(object):

    def get_T(self):

        return self.T


    def get_b_rel(self):

        return self.b_rel


    def get_eta(self):

        return self.eta


    def get_Tg(self):

        return self.Tg


    def get_b_bin(self):

        return self.b_bin


    def _determine_number_of_controls(self):

        self.N_c = len(self.b_rel)


    def _determine_number_of_control_intervals(self):

        self.N_b = len(self.T) - 1


    def _validate_input_dimensions(self):

        for b_rel_i in self.b_rel:

            if len(b_rel_i) != self.N_b:

                raise ValueError("All elements in b_rel must contain one more entry that T.")


    def _validate_input_values_T(self):

        for i, t in enumerate(self.T[:-1]):

            if (self.T[i+1] - t) <= 0.0:

                raise ValueError("Values in T must be strictly increasing.")


    def _validate_input_values_b_rel(self):

        for b_rel_i in self.b_rel:

            for b in b_rel_i:

                if ((b < 0.0) or (b > 1.0)):

                    raise ValueError("All elements of the relaxed binary input must be 0 <= b <= 1.")


    def _validate_input_values(self):

        self._validate_input_values_T()
        self._validate_input_values_b_rel()


    def _validate_input_data(self):

        self._validate_input_dimensions()
        self._validate_input_values()


    def __init__(self, T, b_rel):

        self.T = T
        self.b_rel = b_rel

        self.Tg = []
        
        self.eta = 0
        self.b_bin = [[]]

        self._determine_number_of_controls()
        self._determine_number_of_control_intervals()
        self._validate_input_data()


    def compute_time_grid_from_time_points(self):

        self.Tg = [0] * self.N_b

        for i in range(1, self.N_b):

            self.Tg[i-1] = self.T[i] - self.T[i-1]


    def setup_sigma_max(self, sigma_max):

        self.sigma_max = sigma_max


    def prepare_bnb_data(self):

        self.determine_number_of_control_intervals()
        self.compute_time_grid_from_time_points()


    def setup_model_variables(self):

        self.eta_sym = self.model.addVar(vtype = "C", name = "eta")

        self.b_bin_sym = {}
        self.s = {}

        for i in range(self.N-1):

            self.s[i] = self.model.addVar(vtype = "C", name = "s_%s"%i)

            self.b_bin_sym[i] = self.model.addVar( \
                vtype = "B", name = "b_bin_%s"%i)

        self.b_bin_sym[self.N-1] = self.model.addVar( \
            vtype = "B", name = "b_bin_%s"%(self.N-1))

        
    def setup_objective(self):

        self.model.setObjective(self.eta_sym)


    def setup_milp(self):

        self.initialize_model()
        self.setup_model_variables()
        self.setup_objective()
        self.setup_maximum_switching_constraints()
        self.setup_approximation_inequalites()


    def run_bnb(self):

        self.setup_milp()
        self.solve_milp()


    def run_cia(self, sigma_max = 2):

        self.setup_sigma_max(sigma_max)
        self.prepare_bnb_data()
        self.run_bnb()
        self.retrieve_solutions()

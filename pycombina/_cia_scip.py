from pyscipopt import Model, quicksum
from _cia_milp import CIAMilp

class CIAScip(CIAMilp):

    def initialize_model(self):

        self.model = Model("CIA model SCIP")


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

            self.model.addCons(self.eta_sym >= quicksum( \
                [self.Tg[j] * (self.b_rel[j] - self.b_bin_sym[j]) for j in range(i)]))
            self.model.addCons(self.eta_sym >= -quicksum( \
                [self.Tg[j] * (self.b_rel[j] - self.b_bin_sym[j]) for j in range(i)]))


    def solve_milp(self):

        # self.model.setRealParam("numerics/lpfeastol", 1e-17)
        self.model.optimize()


    def retrieve_solutions(self):

        self.eta = self.model.getVal(self.eta_sym)
        self.b_bin = [abs(round(self.model.getVal(self.b_bin_sym[i]))) \
            for i in range(self.N)]

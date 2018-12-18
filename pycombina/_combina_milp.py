import numpy as np
import gurobipy as gp
import ipdb
import time

from ._binary_approximation import BinApprox, BinApproxPreprocessed
from ._combina_rounding import CombinaSUR


class CombinaMILP():

    '''
    Solve a binary approximation problem by combinatorial integral approximation
    using mixed-integer linear programming and Gurobi.

    The following options of :class:`pycombina.BinApprox` are supported:
    
    - Maximum number of switches
    - Minimum up-times
    - Minimum down-times
    - Valid control transitions (b_adjacencies)
    - Valid controls per interval (b_valid)
    - Active control at time point t_0-1 (b_bin_pre)

    All other options are ignore without further notice.

    :param BinApprox: Binary approximation problem

    '''


    def _setup_warm_start(self, b_warm_start) -> None:

        if b_warm_start:

            CombinaSUR._run_sur(self)

            for i in range(self._binapprox_p.n_c):

                for j in range(self._binapprox_p.n_t):

                    self._b_bin_sym[(i,j)].start = self._binapprox_p._b_bin[i][j]


    def _apply_preprocessing(self, binapprox: BinApprox) -> None:

        self._binapprox = binapprox
        self._binapprox_p = BinApproxPreprocessed(binapprox)


    def _initialize_milp(self):

        self._model = gp.Model("Combinatorial Integral Approximation MILP")


    def _welcome_prompt_milp(self):

        print("-----------------------------------------------------------");
        print("                                                           ");
        print("                 pycombina Gurobi                          ");
        print("                                                           ");
        print("Setting up model variables, objective and constraints:     ");


    def _setup_milp(self, binapprox: BinApprox) -> None:

        self._apply_preprocessing(binapprox)
        self._initialize_milp()
        self._welcome_prompt_milp()
        start_time = time.time()
        self._setup_model_variables()
        self._setup_b_bin_pre_variables()
        self._setup_objective()
        self._setup_approximation_inequalities()
        self._setup_sos1_constraints()
        self._setup_maximum_switching_constraints()
        self._setup_dwell_time_constraints()
        self._setup_valid_control_transitions_constraints()
        self._setup_valid_controls_for_intervals_constraints()
        print("--- %s seconds ---" % (time.time() - start_time))


    def __init__(self, binapprox: BinApprox) -> None:

        self._setup_milp(binapprox)


    def _run_solver(self, use_warm_start: bool, gurobi_opts: dict) -> None:

        for gurobi_opt in gurobi_opts.keys():

            try:

                self._model.setParam(gurobi_opt, gurobi_opts[gurobi_opt])

            except ValueError:

                raise ValueError("Values of solver options must be of numerical type.")

        # TODO: Include use_warm_start 
        self._setup_warm_start(use_warm_start)

        self._model.optimize()


    def _retrieve_solutions(self):

        self._binapprox_p._eta = self._model.getVarByName(self._eta_sym.VarName).x
        self._binapprox_p._b_bin = []

        for i in range(self._binapprox_p.n_c):

            self._binapprox_p._b_bin.append([abs(round(self._model.getVarByName( \
                self._b_bin_sym[(i,j)].VarName).x)) for j in range(self._binapprox_p.n_t)])


    def _set_solution(self):

        self._binapprox_p.inflate_solution()
        self._binapprox.set_b_bin(self._binapprox_p.b_bin)
        self._binapprox.set_eta(self._binapprox_p.eta)


    def solve(self, use_warm_start: bool = False , gurobi_opts: dict = {}):

        '''
        Solve the combinatorial integral approximation problem.

        :param use_warm_start: If a binary solution is already contained in the
                               given binary approximation problem, use it to
                               warm-start the solver.

        :param gurobi_opts: Options to be passed for gurobi solver (please see 
                            Gurobi manual for options), examples are:

            - **MIPGap**: relative MIP optimality gap; when solution found fulfilling
                        the gap, Gurobi stops. Default: 0.0001
            - **TimeLimit**: Limits the total time expended (in seconds). Default: Infinity

        '''

        print("                                                           ");
        print("Gurobi model set up finished                               ");
        print("-----------------------------------------------------------");

        self._run_solver(use_warm_start = use_warm_start, gurobi_opts = gurobi_opts)
        self._retrieve_solutions()
        self._set_solution()

        print("-----------------------------------------------------------");


############## Gurobi specific variables and constraints functions #########


    def _setup_model_variables(self):

        self._eta_sym = self._model.addVar(vtype = "C", name = "eta")

        if (self._binapprox_p.cia_norm == "column_sum_norm") or (self._binapprox_p.cia_norm == "row_sum_norm"):
            
            self._eta_sym_indiv = {}

            for i in range(self._binapprox_p.n_c):

                for j in range(self._binapprox_p.n_t):

                    self._eta_sym_indiv[(i,j)] = self._model.addVar( \
                        vtype = "C", name = "eta_sym_indiv".format((i,j)))
                 
        self._b_bin_sym = {}
        self._s = {}

        for i in range(self._binapprox_p.n_c):
        
            for j in range(-1,self._binapprox_p.n_t-1):

                self._s[(i,j)] = self._model.addVar(vtype = "C", \
                    name = "s_{0}".format((i,j)))

                self._b_bin_sym[(i,j)] = self._model.addVar( \
                    vtype = "B", name = "b_bin_{0}".format((i,j)))

            self._b_bin_sym[(i, self._binapprox_p.n_t-1)] = self._model.addVar( \
                vtype = "B", name = "b_bin_{0}".format((i,self._binapprox_p.n_t-1)))


    def _setup_b_bin_pre_variables(self):

        for i in range(self._binapprox_p.n_c):

            if self._binapprox_p.b_bin_pre.sum() == 1: 

                self._model.addConstr(self._b_bin_sym[(i,-1)] == int(self._binapprox_p.b_bin_pre[i]))

        
    def _setup_objective(self):

        self._model.setObjective(self._eta_sym)


    def _setup_approximation_inequalities(self):

        if self._binapprox_p.cia_norm == "max_norm":

            for i in range(self._binapprox_p.n_c):

                lhs = gp.LinExpr()
                rhs = 0.0

                for j in range(self._binapprox_p.n_t):

                    lhs.addTerms(self._binapprox_p.dt[j], self._b_bin_sym[(i,j)])
                    rhs += self._binapprox_p.dt[j] * self._binapprox_p.b_rel[i][j]

                    self._model.addLConstr(lhs + self._eta_sym, gp.GRB.GREATER_EQUAL, rhs)
                    self._model.addLConstr(lhs - self._eta_sym, gp.GRB.LESS_EQUAL, rhs)

                    # self._model.addConstr(self._eta_sym >= sum( \
                    #     [self._binapprox_p.dt[k] * (self._binapprox_p.b_rel[i][k] - self._b_bin_sym[(i,k)]) for k in range(j+1)]))
                    # self._model.addConstr(self._eta_sym >= -sum( \
                    #     [self._binapprox_p.dt[k] * (self._binapprox_p.b_rel[i][k] - self._b_bin_sym[(i,k)]) for k in range(j+1)]))

        elif self._binapprox_p.cia_norm == "column_sum_norm":

            for i in range(self._binapprox_p.n_c):

                lhs = gp.LinExpr()
                rhs = 0.0

                for j in range(self._binapprox_p.n_t):

                    lhs.addTerms(self._binapprox_p.dt[j], self._b_bin_sym[(i,j)])
                    rhs += self._binapprox_p.dt[j] * self._binapprox_p.b_rel[i][j]

                    self._model.addLConstr(lhs + self._eta_sym_indiv[(i,j)], gp.GRB.GREATER_EQUAL, rhs)
                    self._model.addLConstr(lhs - self._eta_sym_indiv[(i,j)], gp.GRB.LESS_EQUAL, rhs)

            for j in range(self._binapprox_p.n_t):

                self._model.addConstr(self._eta_sym >= sum( \
                        [self._eta_sym_indiv[(i,j)]  for i in range(self._binapprox_p.n_c)]))

        elif self._binapprox_p.cia_norm == "row_sum_norm":

            for i in range(self._binapprox_p.n_c):

                lhs = gp.LinExpr()
                rhs = 0.0

                for j in range(self._binapprox_p.n_t):

                    lhs.addTerms(self._binapprox_p.dt[j], self._b_bin_sym[(i,j)])
                    rhs += self._binapprox_p.dt[j] * self._binapprox_p.b_rel[i][j]

                    self._model.addLConstr(lhs + self._eta_sym_indiv[(i,j)], gp.GRB.GREATER_EQUAL, rhs)
                    self._model.addLConstr(lhs - self._eta_sym_indiv[(i,j)], gp.GRB.LESS_EQUAL, rhs)

            for i in range(self._binapprox_p.n_c):

                self._model.addConstr(self._eta_sym >= sum( \
                        [self._eta_sym_indiv[(i,j)]  for j in range(self._binapprox_p.n_t)]))

        print("                                                           ");
        print("Done: variables, objective and approximation inequalities  ");


    def _setup_sos1_constraints(self):

        for j in range(self._binapprox_p.n_t):

            self._model.addConstr(sum([self._b_bin_sym[(i,j)] for i in range(self._binapprox_p.n_c)]) == 1)

         
    def _setup_maximum_switching_constraints(self):

        for i in range(self._binapprox_p.n_c):

            for j in range(-1,self._binapprox_p.n_t-1):

                self._model.addConstr(self._s[(i,j)] >= self._b_bin_sym[(i,j)] - self._b_bin_sym[(i,j+1)])
                self._model.addConstr(self._s[(i,j)] >= -self._b_bin_sym[(i,j)] + self._b_bin_sym[(i,j+1)])
                self._model.addConstr(self._s[(i,j)] <= self._b_bin_sym[(i,j)] + self._b_bin_sym[(i,j+1)])
                self._model.addConstr(self._s[(i,j)] <= 2 - self._b_bin_sym[(i,j)] - self._b_bin_sym[(i,j+1)])

        for i, sigma_max_i in enumerate(self._binapprox_p.n_max_switches):

            if sigma_max_i % 2 == 0:

                self._model.addConstr((self._b_bin_sym[(i,-1)] - self._b_bin_sym[(i,self._binapprox_p.n_t-1)] + \
                    sum([self._s[(i,j)] for j in range(-1,self._binapprox_p.n_t-1)])) <= sigma_max_i)
                self._model.addConstr((self._b_bin_sym[(i,self._binapprox_p.n_t-1)] - self._b_bin_sym[(i,-1)] + \
                    sum([self._s[(i,j)] for j in range(-1,self._binapprox_p.n_t-1)])) <= sigma_max_i) 

            else:

                self._model.addConstr((1 - self._b_bin_sym[(i,-1)] - self._b_bin_sym[(i,self._binapprox_p.n_t-1)] + \
                    sum([self._s[(i,j)] for j in range(-1, self._binapprox_p.n_t-1)])) <= sigma_max_i)
                self._model.addConstr((self._b_bin_sym[(i,-1)] + self._b_bin_sym[(i,self._binapprox_p.n_t-1)] - 1 + \
                    sum([self._s[(i,j)] for j in range(-1, self._binapprox_p.n_t-1)])) <= sigma_max_i)  

        print("Done: maximum switching constraints  ");


    def _setup_dwell_time_constraints(self):

        dt_sums = np.zeros((self._binapprox_p.n_t, self._binapprox_p.n_t)) 

        for j in range(self._binapprox_p.n_t):

                dt_sums[j][j] = self._binapprox_p.dt[j]

                for k in range(j+1,self._binapprox_p.n_t):

                    dt_sums[j][k] =  dt_sums[j][k-1] + self._binapprox_p.dt[k] 

        for i in range(self._binapprox_p.n_c):

            for k in range(self._binapprox_p.n_t):

                if dt_sums[0][k] <= self._binapprox_p.min_up_times[i]:  
                    self._model.addLConstr(gp.LinExpr([1.0, -1.0], [self._b_bin_sym[(i,k)], self._b_bin_sym[(i,0)]]), gp.GRB.GREATER_EQUAL, 0.0)

            for j in range(1,self._binapprox_p.n_t):

                for k in range(j,self._binapprox_p.n_t):

                    if dt_sums[j][k] <= self._binapprox_p.min_up_times[i]:  
                        self._model.addLConstr(gp.LinExpr([1.0, -1.0, 1.0], [self._b_bin_sym[(i,k)], self._b_bin_sym[(i,j)], self._b_bin_sym[(i,j-1)]]), gp.GRB.GREATER_EQUAL, 0.0)

                    if dt_sums[j][k] <= self._binapprox_p.min_down_times[i]:
                        self._model.addLConstr(gp.LinExpr([1.0, 1.0, -1.0], [self._b_bin_sym[(i,k)], self._b_bin_sym[(i,j-1)], self._b_bin_sym[(i,j)]]), gp.GRB.LESS_EQUAL, 1.0)

        print("Done: dwell time constraints  ");


    def _setup_valid_control_transitions_constraints(self):

        for i in range(self._binapprox_p.n_c):

            for j in range(1,self._binapprox_p.n_t):

                self._model.addConstr(1 >= self._b_bin_sym[(i,j)] + sum(self._b_bin_sym[(l,j-1)] for l in range(self._binapprox_p.n_c) if self._binapprox_p.b_adjacencies[l][i] == 0)) 

        print("Done: valid control transitions constraints  ");


    def _setup_valid_controls_for_intervals_constraints(self):

        for i in range(self._binapprox_p.n_c):

            for j in range(self._binapprox_p.n_t):

                if self._binapprox_p.b_valid[i][j] == 0:

                    self._model.addConstr(self._b_bin_sym[(i,j)]  == 0)

        print("Done: valid controls for intervals constraints  ");







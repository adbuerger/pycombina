import numpy as np
import gurobipy as gp
import ipdb

from ._binary_approximation import BinApproxPreprocessed

class CombinaMILP:

    '''
    Solve a binary approximation problem by combinatorial integral approximation
    using mixed-integer linear programming and Gurobi.

    The following options of :class:`pycombina.BinApprox` are supported:

    - ...

    All other options are ignore without further notice.

    :param BinApprox: Binary approximation problem

    '''

    @property
    def cia_norm(self):

        '''Applied CIA norm for objective'''

        try:
            return self._cia_norm

        except AttributeError:
            return "max_norm"


    def set_cia_norm(self, cia_norm):

        if not ((cia_norm == "max_norm") or (cia_norm == "1_norm")):
            raise ValueError("cia_norm must be set either to 'max_norm' or '1_norm'")

        self._cia_norm = cia_norm


    def _apply_preprocessing(self, binapprox):

        self._binapprox_p = BinApproxPreprocessed(binapprox)


    def _initialize_model(self):

        self._model = gp.Model("Combinatorial Integral Approximation MILP")
        self.set_cia_norm("max_norm")


    def _setup_model_variables(self):

        self._eta_sym = self._model.addVar(vtype = "C", name = "eta")

        if self._cia_norm == "1_norm":
            
            self._eta_sym_bin = {}

            for i in range(self._binapprox_p.n_c):

                for j in range(self._binapprox_p.n_t):

                    self._eta_sym_bin[(i,j)] = self._model.addVar( \
                        vtype = "C", name = "eta_bin".format((i,j)))
                 

        self._b_bin_sym = {}
        self._s = {}

        for i in range(self._binapprox_p.n_c):
        
            for j in range(self._binapprox_p.n_t-1):

                self._s[(i,j)] = self._model.addVar(vtype = "C", \
                    name = "s_{0}".format((i,j)))

                self._b_bin_sym[(i,j)] = self._model.addVar( \
                    vtype = "B", name = "b_bin_{0}".format((i,j)))

            self._b_bin_sym[(i, self._binapprox_p.n_t-1)] = self._model.addVar( \
                vtype = "B", name = "b_bin_{0}".format((i,self._binapprox_p.n_t-1)))

            if hasattr(self._binapprox_p, "b_bin_pre"): 

                 self._s[(i,-1)] = self._model.addVar(vtype = "C", \
                    name = "s_{0}".format((i,-1)))

        
    def _setup_objective(self):

        self._model.setObjective(self._eta_sym)


    def _setup_approximation_inequalites(self):

        if self._cia_norm == "max_norm":

            for i in range(self._binapprox_p.n_c):

                for j in range(self._binapprox_p.n_t):

                    self._model.addConstr(self._eta_sym >= gp.quicksum( \
                        [self._binapprox_p.dt[k] * (self._binapprox_p.b_rel[i][k] - self._b_bin_sym[(i,k)]) for k in range(j+1)]))
                    self._model.addConstr(self._eta_sym >= -gp.quicksum( \
                        [self._binapprox_p.dt[k] * (self._binapprox_p.b_rel[i][k] - self._b_bin_sym[(i,k)]) for k in range(j+1)]))

        elif self._cia_norm == "1_norm":
            
            for i in range(self._binapprox_p.n_c):

                for j in range(self._binapprox_p.n_t):

                    self._model.addConstr(self._eta_sym_bin[(i,j)] >= gp.quicksum( \
                        [self._binapprox_p.dt[k] * (self._binapprox_p.b_rel[i][k] - self._b_bin_sym[(i,k)]) for k in range(j+1)]))
                    self._model.addConstr(self._eta_sym_bin[(i,j)] >= -gp.quicksum( \
                        [self._binapprox_p.dt[k] * (self._binapprox_p.b_rel[i][k] - self._b_bin_sym[(i,k)]) for k in range(j+1)]))

            for j in range(self._binapprox_p.n_t):

                self._model.addConstr(self._eta_sym >= gp.quicksum( \
                        [self._eta_sym_bin[(i,j)]  for i in range(self._binapprox_p.n_c)]))

        elif self._cia_norm == "row_sum_norm":
            
            for i in range(self._binapprox_p.n_c):

                for j in range(self._binapprox_p.n_t):

                    self._model.addConstr(self._eta_sym_bin[(i,j)] >= gp.quicksum( \
                        [self._binapprox_p.dt[k] * (self._binapprox_p.b_rel[i][k] - self._b_bin_sym[(i,k)]) for k in range(j+1)]))
                    self._model.addConstr(self._eta_sym_bin[(i,j)] >= -gp.quicksum( \
                        [self._binapprox_p.dt[k] * (self._binapprox_p.b_rel[i][k] - self._b_bin_sym[(i,k)]) for k in range(j+1)]))

            for j in range(self._binapprox_p.n_t):

                self._model.addConstr(self._eta_sym >= gp.quicksum( \
                        [self._eta_sym_bin[(i,j)]  for i in range(self._binapprox_p.n_c)]))


    def _setup_sos1_constraints(self):

        for j in range(self._binapprox_p.n_t):

            self._model.addConstr(gp.quicksum([self._b_bin_sym[(i,j)] for i in range(self._binapprox_p.n_c)]) == 1)

         
    def _setup_maximum_switching_constraints(self):

        for i in range(self._binapprox_p.n_c):

            for j in range(self._binapprox_p.n_t-1):

                self._model.addConstr(self._s[(i,j)] >= self._b_bin_sym[(i,j)] - self._b_bin_sym[(i,j+1)])
                self._model.addConstr(self._s[(i,j)] >= -self._b_bin_sym[(i,j)] + self._b_bin_sym[(i,j+1)])
                self._model.addConstr(self._s[(i,j)] <= self._b_bin_sym[(i,j)] + self._b_bin_sym[(i,j+1)])
                self._model.addConstr(self._s[(i,j)] <= 2 - self._b_bin_sym[(i,j)] - self._b_bin_sym[(i,j+1)])

            if hasattr(self._binapprox_p, "b_bin_pre"): 

                self._model.addConstr(self._s[(i,-1)] >= self._binapprox_p.b_bin_pre[i] - self._b_bin_sym[(i,0)])
                self._model.addConstr(self._s[(i,-1)] >= -self._binapprox_p.b_bin_pre[i] + self._b_bin_sym[(i,0)])
                self._model.addConstr(self._s[(i,-1)] <=  self._binapprox_p.b_bin_pre[i] + self._b_bin_sym[(i,0)])
                self._model.addConstr(self._s[(i,-1)] <= 2 - self._binapprox_p.b_bin_pre[i] - self._b_bin_sym[(i,0)])

        for i, sigma_max_i in enumerate(self._binapprox_p.n_max_switches):

            if hasattr(self._binapprox_p, "b_bin_pre"): 

                if sigma_max_i % 2 == 0:

                    self._model.addConstr((self._b_bin_sym[(i,-1)] - self._b_bin_sym[(i,self._binapprox_p.n_t-1)] + \
                        gp.quicksum([self._s[(i,j)] for j in range(-hasattr(self._binapprox_p, "b_bin_pre"),self._binapprox_p.n_t-1)])) <= sigma_max_i)
                    self._model.addConstr((self._b_bin_sym[(i,self._binapprox_p.n_t-1)] - self._b_bin_sym[(i,-1)] + \
                        gp.quicksum([self._s[(i,j)] for j in range(-hasattr(self._binapprox_p, "b_bin_pre"),self._binapprox_p.n_t-1)])) <= sigma_max_i) 

                else:

                    self._model.addConstr((1 - self._b_bin_sym[(i,-1)] - self._b_bin_sym[(i,self._binapprox_p.n_t-1)] + \
                        gp.quicksum([self._s[(i,j)] for j in range(-hasattr(self._binapprox_p, "b_bin_pre"), self._binapprox_p.n_t-1)])) <= sigma_max_i)
                    self._model.addConstr((self._b_bin_sym[(i,-1)] + self._b_bin_sym[(i,self._binapprox_p.n_t-1)] - 1 + \
                        gp.quicksum([self._s[(i,j)] for j in range(-hasattr(self._binapprox_p, "b_bin_pre"), self._binapprox_p.n_t-1)])) <= sigma_max_i)  

            else:
                
                if sigma_max_i % 2 == 0:

                    self._model.addConstr((self._b_bin_sym[(i,0)] - self._b_bin_sym[(i,self._binapprox_p.n_t-1)] + \
                        gp.quicksum([self._s[(i,j)] for j in range(self._binapprox_p.n_t-1)])) <= sigma_max_i)
                    self._model.addConstr((self._b_bin_sym[(i,self._binapprox_p.n_t-1)] - self._b_bin_sym[(i,0)] + \
                        gp.quicksum([self._s[(i,j)] for j in range(self._binapprox_p.n_t-1)])) <= sigma_max_i) 

                else:

                    self._model.addConstr((1 - self._b_bin_sym[(i,0)] - self._b_bin_sym[(i,self._binapprox_p.n_t-1)] + \
                        gp.quicksum([self._s[(i,j)] for j in range(self._binapprox_p.n_t-1)])) <= sigma_max_i)
                    self._model.addConstr((self._b_bin_sym[(i,0)] + self._b_bin_sym[(i,self._binapprox_p.n_t-1)] - 1 + \
                        gp.quicksum([self._s[(i,j)] for j in range(self._binapprox_p.n_t-1)])) <= sigma_max_i)      


    def _setup_dwell_time_constraints(self):
  
        for i in range(self._binapprox_p.n_c):

            for j in range(1,self._binapprox_p.n_t-1):

                for k in range(j,self._binapprox_p.n_t-1):

                    if sum(self._binapprox_p.dt[l] for l in range(j,k+1)) <= self._binapprox_p.min_up_times[i]:  
                        self._model.addConstr(self._b_bin_sym[(i,k)] >= self._b_bin_sym[(i,j)] - self._b_bin_sym[(i,j-1)])

                    if sum(self._binapprox_p.dt[l] for l in range(j,k+1)) <= self._binapprox_p.min_down_times[i]:  
                        self._model.addConstr(1-self._b_bin_sym[(i,k)] >= self._b_bin_sym[(i,j-1)] - self._b_bin_sym[(i,j)])

        if hasattr(self._binapprox_p, "b_bin_pre"): 

            for i in range(self._binapprox_p.n_c):

                for j in range(int(np.floor(self._binapprox_p.remaining_down_times[i]))):

                    self._model.addConstr(self._b_bin_sym[(i,j)] <= 0.0)



    def _setup_milp(self, binapprox_p):

        self._apply_preprocessing(binapprox_p)
        self._initialize_model()
        self._setup_model_variables()
        self._setup_objective()
        self._setup_approximation_inequalites()
        self._setup_sos1_constraints()
        self._setup_maximum_switching_constraints()
        self._setup_dwell_time_constraints()
        
        #self.setup_multiphase_CIA_control_locking_constraints()
        #self.setup_maximum_switching_constraints()
        #self.setup_locking_constraints()

        #self.setup_gear_continuity_constraint()
        #self.setup_pre_unabled_gears_constraints()


    def __init__(self, binapprox_p):

        self._setup_milp(binapprox_p)


    def _setup_warm_start(self, b_warm_start):

        self.eta_sym_bin = b_warm_start


    def _pass_gurobi_options(self):

        # tbd

        pass


    def _solve_milp(self):

        #self.model.setParam("TimeLimit", self.TimeLimit)
        #self.model.setParam("MIPGap", self.MIPGap)

        self._model.optimize()


    def _retrieve_solutions(self):

        self._binapprox_p._eta = self._model.getVarByName(self._eta_sym.VarName).x
        self._binapprox_p._b_bin = []

        for i in range(self._binapprox_p.n_c):

            self._binapprox_p._b_bin.append([abs(round(self._model.getVarByName( \
                self._b_bin_sym[(i,j)].VarName).x)) for j in range(self._binapprox_p.n_t)])


    def solve(self, use_warm_start = False , gurobi_opts = {}):

        # self._setup_warm_start(use_warm_start)
        self._solve_milp()
        self._retrieve_solutions()


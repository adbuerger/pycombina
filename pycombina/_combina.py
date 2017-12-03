import os

class Combina():


    @property
    def T(self):

        return self._T


    @property
    def b_rel(self):

        return self._b_rel


    @property
    def Tg(self):

        return self._Tg


    @property
    def N_b(self):

        return self._N_b


    @property
    def N_c(self):

        return self._N_c


    @property
    def max_switches(self):

        try:
            return self._max_switches

        except AttributeError:
           raise AttributeError("max_switches not yet available, call solve() first.")


    @property
    def eta(self):

        try:
            return self._eta

        except AttributeError:
           raise AttributeError("eta not yet available, call solve() first.")


    @property
    def b_bin(self):

        try:
            return self._b_bin

        except AttributeError:
           raise AttributeError("b_bin not yet available, call solve() first.")


    def _check_if_prompt_init_messages(self):

        try:
        
            if os.environ["PYCOMBINA_PROMPTS_SHOWN"] == "True":
                
                self._prompt_init_messages = False
        
        except KeyError:
            
            os.environ["PYCOMBINA_PROMPTS_SHOWN"] = "True"
            self._prompt_init_messages = True
            


    def _welcome_prompt(self):

        if self._prompt_init_messages:

            print("\n-----------------------------------------------------------")
            print("|                                                         |")
            print("|                      You're using                       |")
            print("|                                                         |")
            print("|    pycombina -- Combinatorial Integral Approximation    |")
            print("|                                                         |")
            print("|       by A. Buerger, C. Zeile, S. Sager, M. Diehl       |")
            print("|                                                         |")
            print("-----------------------------------------------------------\n")


    def _check_available_solvers(self):

        self._available_solvers = {}

        try:
            from _combina_bnb_solver import CombinaBnBSolver
            self._available_solvers["bnb"] = CombinaBnBSolver
        except ImportError:
            if self._prompt_init_messages:
                print("- pycombina C++ extension not built, BnB solver disabled.")

        try:
            import pyscipopt
            from _combina_milp_solver import CombinaScipSolver
            self._available_solvers["scip"] = CombinaScipSolver
        except ImportError:
            if self._prompt_init_messages:
                print("- pyscipopt not found, SCIP solver disabled.")

        try:
            import gurobipy
            from _combina_milp_solver import CombinaGurobiSolver
            self._available_solvers["gurobi"] = CombinaGurobiSolver
        except ImportError:
            if self._prompt_init_messages:
                print("- gurobipy not found, Gurobi solver disabled.")

        if not self._available_solvers:
            raise RuntimeError("No solvers available for pycombina.")


    def _initialize_combina(self):

        self._check_if_prompt_init_messages()
        self._welcome_prompt()
        self._check_available_solvers()


    def _determine_number_of_controls(self):

        self._N_c = len(self._b_rel)


    def _determine_number_of_control_intervals(self):

        self._N_b = len(self._T) - 1


    def _validate_input_dimensions(self):

        for b_rel_i in self._b_rel:

            if len(b_rel_i) != self._N_b:

                raise ValueError("All elements in b_rel must contain one entry less than T.")


    def _validate_input_values_T(self):

        for i, t in enumerate(self._T[:-1]):

            if (self._T[i+1] - t) <= 0.0:

                raise ValueError("Values in T must be strictly increasing.")


    def _validate_input_values_b_rel(self):

        for b_rel_i in self._b_rel:

            for b in b_rel_i:

                if ((b < 0.0) or (b > 1.0)):

                    raise ValueError("All elements of the relaxed binary input must be 0 <= b <= 1.")


    def _validate_input_values(self):

        self._validate_input_values_T()
        self._validate_input_values_b_rel()


    def _validate_input_data(self):

        self._validate_input_dimensions()
        self._validate_input_values()


    def _compute_time_grid_from_time_points(self):

        self._Tg = [0] * self._N_b

        for i in range(self._N_b):

            self._Tg[i] = self._T[i+1] - self._T[i]


    def __init__(self, T, b_rel):

        self._initialize_combina()

        self._T = T
        self._b_rel = b_rel

        self._determine_number_of_controls()
        self._determine_number_of_control_intervals()
        self._validate_input_data()
        self._compute_time_grid_from_time_points()


    def solve(self, solver = "bnb", max_switches = [2], min_up_time = None):

        try:
            max_switches = list(max_switches)
            self._max_switches = [int(s) for s in max_switches]

            if not len(self._max_switches) == len(self._b_rel):
                raise ValueError

        except ValueError:
            raise ValueError("max_switches must be a list of integer values with length equal to the number of binary controls.")


        if not min_up_time:

           min_up_time = [0.0] * self._N_c

        try:
            min_up_time = list(min_up_time)
            self._min_up_time = [float(m) for m in min_up_time]

            if not len(self._min_up_time) == len(self._b_rel):
                raise ValueError

        except ValueError:
            raise ValueError("max_switches must be a list of float values with length equal to the number of binary controls.")


        try:
            self._solver = self._available_solvers[solver]( \
                self._Tg, self._b_rel, self._N_c, self._N_b)

        except KeyError:
            raise ValueError("Unknown solver '" + solver + "', valid options are:\n" + \
                str(self._available_solvers.keys()))

        self._solver.run(max_switches = self._max_switches, min_up_time = self._min_up_time)

        self._eta = self._solver.get_eta()
        self._b_bin = self._solver.get_b_bin()

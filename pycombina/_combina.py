import os
import numpy as np

class Combina():


    @property
    def t(self):

        '''Discrete time points.'''

        return self._t


    @property
    def b_rel(self):

        '''Relaxed binary controls.'''

        return self._b_rel


    @property
    def dt(self):

        '''Duration between sequent time points.'''

        return self._dt


    @property
    def n_b(self):

        '''Number of discrete values per control.'''

        return self._n_b


    @property
    def n_c(self):

        '''Number of mutually exclusive controls.'''

        return self._n_c


    @property
    def max_switches(self):

        '''Maximum possible amount of switches per control.'''

        try:
            return self._max_switches

        except AttributeError:
           raise AttributeError("max_switches not yet available, call solve() first.")


    @property
    def eta(self):

        '''Objective value of the combinatorial integral approximation problem.'''

        try:
            return self._eta

        except AttributeError:
           raise AttributeError("eta not yet available, call solve() first.")


    @property
    def b_bin(self):

        '''Binary controls obtained from the solution of the combinatorial integral approximation problem.'''

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


    def _validate_input_dimension_t(self):

        self._t = np.squeeze(self._t)

        if not self._t.ndim == 1:

                raise ValueError("Input t must be a vector.")


    def _validate_input_dimension_b_rel(self):

        self._b_rel = np.atleast_2d(self._b_rel)

        if not self._b_rel.shape[1] == self._t.size-1:

            self._b_rel = self._b_rel.T

        if not self._b_rel.shape[1] == self._t.size-1:

            raise ValueError("One dimension of b_rel must be |t|-1.")


    def _validate_input_values_t(self):

        if not np.all((self._t[1:] - self._t[:-1]) > 0):

            raise ValueError("Values in t must be strictly increasing.")


    def _validate_input_values_b_rel(self):

        if not (np.all(self._b_rel >= 0) and np.all(self._b_rel <= 1)):

            raise ValueError("All elements of the relaxed binary input must be 0 <= b <= 1.")


    def _determine_number_of_control_intervals(self):

        self._n_b = self._t.size - 1


    def _determine_number_of_controls(self):

        self._n_c = self._b_rel.shape[0]


    def _validate_input_values(self):

        self._validate_input_values_t()
        self._validate_input_values_b_rel()


    def _validate_input_dimensions(self):

        self._validate_input_dimension_t()
        self._validate_input_dimension_b_rel()


    def _validate_input_data(self):

        self._validate_input_dimensions()
        self._validate_input_values()


    def _compute_time_grid_from_time_points(self):

        self._dt = self._t[1:] - self._t[:-1]


    def _numpy_arrays_to_lists(self):

        # For now, the solver interfaces expect lists, so we need to convert
        # the numpy arrays accordingly

        self._t = self._t.tolist()
        self._b_rel = self._b_rel.tolist()
        self._dt = self._dt.tolist()


    def __init__(self, t, b_rel):

        r'''
        :raises: ValueError, RuntimeError

        :param t: One-dimensional array that contains the discrete time points
                  of the combinatorial integral approximation problem. The
                  values in t must be strictly increasing.
        :type t: numpy.ndarray

        :param b_rel: Two-dimensional array that contains the relaxed binary
                      controls to be approximated. One dimension of the array
                      must be of size |t|-1 and all entries of the array 
                      must be 0 <= b_k,i <= 1.
        :type b_rel: numpy.ndarray

        '''

        self._initialize_combina()

        self._t = t
        self._b_rel = b_rel

        self._validate_input_data()
        self._determine_number_of_controls()
        self._determine_number_of_control_intervals()
        self._compute_time_grid_from_time_points()
        self._numpy_arrays_to_lists()


    def solve(self, solver = 'bnb', max_switches = [2], min_up_time = None):

        r'''
        :raises: ValueError, NotImplementedError

        :param solver: Specifies which solver to use to solve the combinatorial
                       integral approximation problem. Possible options are:

                       * 'bnb' - solve using a custom Branch-and-Bound algorithm
                       * 'scip' - solve using a MILP formulation with SCIP
                       * 'gurobi' - solve using a MILP formulation with Gurobi

                       Availability of solvers depends on whether the necessary
                       libraries and Python interfaces are installed on your
                       system. Also, not all solver options are available
                       for all solvers.
        :type solver: str

        :param max_switches: Array of integer values that specifies the maximum
                             number of allowed switching actions per control.
        :type max_switches: list, numpy.ndarray

        :param min_up_time: Specifies the minimum time per control that must
                            pass in between two switching actions. If None,
                            no minimum time is considered.
        :type min_up_time: None, list, numpy.ndarray

        '''

        try:
            if not np.atleast_1d(np.squeeze(max_switches)).ndim == 1:
                raise ValueError

            max_switches = list(max_switches)
            self._max_switches = [int(s) for s in max_switches]

            if not len(self._max_switches) == len(self._b_rel):
                raise ValueError

        except ValueError:
            raise ValueError("The number of integer values in max_switches must be equal to the number of binary controls.")


        if not min_up_time:

           min_up_time = [0.0] * self._n_c

        try:

            if not np.atleast_1d(np.squeeze(min_up_time)).ndim == 1:
                raise ValueError

            min_up_time = list(min_up_time)
            self._min_up_time = [float(m) for m in min_up_time]

            if not len(self._min_up_time) == len(self._b_rel):
                raise ValueError

        except ValueError:
            raise ValueError("The number of values in min_up_time must be equal to the number of binary controls.")


        try:
            self._solver = self._available_solvers[solver]( \
                self._dt, self._b_rel, self._n_c, self._n_b)

        except KeyError:
            raise ValueError("Unknown solver '" + solver + "', valid options are:\n" + \
                str(self._available_solvers.keys()))

        self._solver.run(max_switches = self._max_switches, min_up_time = self._min_up_time)

        self._eta = self._solver.get_eta()
        self._b_bin = self._solver.get_b_bin()

        self._b_bin = np.asarray(self._b_bin)

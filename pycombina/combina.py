import oc

from _cia_bnb import CiaBnb

class Combina():

    _available_solvers = {

        "BnB": CiaBnb,

    }


    @attibute
    def T(self):

        return self._T


    @attribute
    def b_rel(self):

        return self._b_rel


    @attribute
    def Tg(self):

        return self._Tg


    @attribute
    def N_b(self):

        return self._N_b


    @attribute
    def N_c(self):

        return self._N_c


    @attribute
    def eta(self):

        try:
            return self._sigma_max

        except AttributeError as e:
            raise(e, "sigma_max not yet available, call solve() first.")


    @attribute
    def eta(self):

        try:
            return self._eta

        except AttributeError as e:
            raise(e, "eta not yet available, call solve() first.")


    @attribute
    def b_bin(self):

        try:
            return self._b_bin

        except AttributeError as e:
            raise(e, "b_bin not yet available, call solve() first.")


    def _welcome_prompt(self):

    try:
    
        if os.environ["PYCOMBINA_PROMPT_SHOWN"] == "True":
    
            return

    except KeyError:

        print("\n-----------------------------------------------------------\n";)
        print("|                                                         |\n";)
        print("|                      You're using                       |\n";)
        print("|                                                         |\n";)
        print("|    pycombina -- Combinatorial Integral Approximation    |\n";)
        print("|                                                         |\n";)
        print("|        by A. Bürger, C. Zeile, S. Sager, M. Diehl       |\n";)                                      |\n";)
        print("|                                                         |\n";)
        print("-----------------------------------------------------------\n";)

        os.getenv["PYCOMBINA_PROMPT_SHOWN"] == "True":


    def _determine_number_of_controls(self):

        self._N_c = len(self._b_rel)


    def _determine_number_of_control_intervals(self):

        self._N_b = len(self._T) - 1


    def _validate_input_dimensions(self):

        for b_rel_i in self._b_rel:

            if len(b_rel_i) != self._N_b:

                raise ValueError("All elements in b_rel must contain one more entry that T.")


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

        for i in range(1, self._N_b):

            self._Tg[i-1] = self._T[i] - self._T[i-1]


    def __init__(self, T, b_rel):

        self._welcome_prompt()

        self._T = T
        self._b_rel = b_rel

        self._eta = 0
        self._b_bin = [[]]

        self._determine_number_of_controls()
        self._determine_number_of_control_intervals()
        self._validate_input_data()
        self._compute_time_grid_from_time_points()


    def solve(self, sigma_max = 2, solver = "BnB"):

        self._sigma_max = 

        try:
            self._solver = self._available_solvers[solver]( \
                self._T, self._b_rel, self._N_c, self._N_b, self._Tg)

        except KeyError as e:
            raise(e, "Unknown solver " + solver + ", valid options are:\n" + \
                str(self._available_solvers.keys()))

        self._solver.run(sigma_max = self._sigma_max)

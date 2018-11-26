import signal
import numpy as np

from ._binary_approximation import BinApproxPreprocessed
from ._combina_bnb_solver import CombinaBnBSolver


def handle_interrupt(signum, frame):
    
    # very dirty hack, should be improved

    if signum == signal.SIGINT:
    
        a.stop()


class CombinaBnB():

    def _apply_preprocessing(self, binapprox):

        self._binapprox_p = BinApproxPreprocessed(binapprox)


    def _initialize_bnb(self):

        if self._binapprox_p.b_bin_pre.sum() < 1:

            b_bin_pre = self._binapprox_p.n_c + 1

        else:

            b_bin_pre = int(np.where(self._binapprox_p.b_bin_pre == 1))

        self._bnb_solver = CombinaBnBSolver( \
                self._binapprox_p.dt.tolist(), \
                self._binapprox_p.b_rel.tolist(), \

                self._binapprox_p.n_c, \
                self._binapprox_p.n_t, \

                self._binapprox_p.n_max_switches.tolist(), \
                self._binapprox_p.min_up_times.tolist(), \
                self._binapprox_p.min_down_times.tolist(), \
                self._binapprox_p.b_valid.tolist(), \
                self._binapprox_p.b_adjacencies.tolist(), \

                self._binapprox_p.min_down_times_pre.tolist(), \
                b_bin_pre, \

            )


    def _setup_bnb(self, binapprox):

        self._apply_preprocessing(binapprox)
        self._initialize_bnb()


    def __init__(self, binapprox_p):

        self._setup_bnb(binapprox_p)


    def solve(self, use_warm_start = False , bnb_opts = {}):

        bnb_opts_default = {

            "max_iter" :  5e6,
            "max_cpu_time": 3e2,
        }

        for bnb_opt in bnb_opts.keys():

            try:

                bnb_opts_default.update({bnb_opt: float(bnb_opts[bnb_opt])})

            except ValueError:

                raise ValueError("Values of solver options must be of numerical type.")

        try:
            
            self._bnb_solver.run(use_warm_start, bnb_opts_default)

        except KeyboardInterrupt:

            self._bnb_solver.stop()

        self._binapprox_p._b_bin = self._bnb_solver.get_b_bin()

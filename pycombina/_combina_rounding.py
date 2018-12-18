import numpy as np
import ipdb
import time

from ._binary_approximation import BinApprox, BinApproxPreprocessed

class CombinaSUR():

    '''
    Solve a binary approximation problem by combinatorial integral approximation
    using Sum-Up-Rounding, i.e., an approximation of the global solution

    The following options of :class:`pycombina.BinApprox` are supported:
    
    - b_rel
    - t

    All other options, in particular combinatorial constraints, are ignore without further notice.

    :param BinApprox: Binary approximation problem

    '''


    def _apply_preprocessing(self, binapprox: BinApprox) -> None:

        self._binapprox = binapprox
        self._binapprox_p = BinApproxPreprocessed(binapprox)


    def _welcome_prompt_sur(self):

        print("-----------------------------------------------------------");
        print("                                                           ");
        print("                 pycombina Sum-Up-Rounding                 ");
        print("                                                           ");


    def _setup_sur(self, binapprox: BinApprox) -> None:

        self._apply_preprocessing(binapprox)
        self._welcome_prompt_sur()


    def __init__(self, binapprox: BinApprox) -> None:

        self._setup_sur(binapprox)

 
    def solve(self):

        '''
        Solve the combinatorial integral approximation problem.

        (Sum-Up-Rounding generates a fast approximate solution)

        '''

        self._run_sur(self)
        self._set_solution()

        print("                 Sum-Up-Rounding finished                  ");
        print("-----------------------------------------------------------");


    @staticmethod
    def _run_sur(self):

        self._binapprox_p._b_bin = [[0 for i in range(self._binapprox_p.n_t)] for j in range(self._binapprox_p.n_c)] 
        eta_i = [0]*self._binapprox_p.n_c
        eta = 0.0

        for i in range(self._binapprox_p.n_t):

            myidx = 0

            for j in range(self._binapprox_p.n_c):

                eta_i[j] = eta_i[j] + self._binapprox_p.b_rel[j][i]*self._binapprox_p.dt[i] 

                if (eta_i[j]>eta_i[myidx]):

                    myidx = j

            for j in [x for x in range(self._binapprox_p.n_c) if x != myidx]: 

                self._binapprox_p._b_bin[j][i] = 0

            self._binapprox_p._b_bin[myidx][i] = 1
            eta_i[myidx] =  eta_i[myidx] - 1 * self._binapprox_p.dt[i] 
            eta = abs(max(eta_i, key=abs))
             
        self._binapprox_p._eta = eta


    def _set_solution(self):

        self._binapprox_p.inflate_solution()
        self._binapprox.set_b_bin(self._binapprox_p.b_bin)
        self._binapprox.set_eta(self._binapprox_p.eta)











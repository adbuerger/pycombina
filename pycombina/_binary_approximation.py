import os
import numpy as np
import numpy.matlib as npm
from typing import Union

from abc import ABC

class BinApproxBase(ABC):

    @property
    def t(self) -> np.ndarray:

        '''Discrete time points.'''

        return self._t


    @property
    def b_rel(self) -> np.ndarray:

        '''Relaxed binary controls.'''

        return self._b_rel


    @property
    def off_state_included(self) -> bool:

        '''Flag whether the off-state is included in the problem definition.'''

        return self._off_state_included


    @property
    def reduce_problem_size_before_solve(self) -> bool:

        '''Reduce problem size prior to solving by merging certain time intervals.'''

        return self._reduce_problem_size_before_solve


    @property
    def dt(self) -> np.ndarray:

        return self._dt


    @property
    def n_t(self) -> int:

        '''Number of time intervals.'''

        return self._n_t


    @property
    def n_c(self) -> int:

        '''Number of mutually exclusive controls.'''

        return self._n_c


    @property
    def b_valid(self) -> np.ndarray:

        '''Minimum down time per control.'''

        return self._b_valid


    @property
    def eta(self) -> float:

        '''Objective value of the binary approximation problem.'''

        try:
            return self._eta

        except AttributeError:
           raise AttributeError("eta not yet available.")


    @property
    def b_bin(self) -> np.ndarray:

        '''Binary solution of the binary approximation problem.'''

        try:
            return self._b_bin

        except:
           raise AttributeError("b_bin not yet available.")


    @property
    def n_max_switches(self) -> np.ndarray:

        '''Maximum possible amount of switches per control.'''

        try:
            return self._n_max_switches

        except AttributeError:

            return self.n_t * np.ones(self.n_c, dtype = int)


    @property
    def min_up_times(self) -> np.ndarray:

        '''Minimum up time per control.'''

        try:
            return self._min_up_times

        except AttributeError:

            return np.zeros(self.n_c)


    @property
    def min_down_times(self) -> np.ndarray:

        '''Minimum down time per control.'''

        try:
            return self._min_down_times

        except AttributeError:

            return np.zeros(self.n_c)


    @property
    def b_bin_pre(self) -> np.ndarray:

        '''Binary control active at time grid point "-1".'''

        try:
            return self._b_bin_pre

        except AttributeError:

            return np.zeros(self.n_c)


    @property
    def min_down_times_pre(self) -> np.ndarray:

        '''Remaining minimum down time per control from time grid point "-1".'''

        try:
            return self._min_down_times_pre

        except AttributeError:

            return np.zeros(self.n_c)


    def _determine_number_of_control_intervals(self) -> None:

        self._n_t = self._t.size - 1


    def _determine_number_of_controls(self) -> None:

        self._n_c = self._b_rel.shape[0]


    def _compute_time_grid_from_time_points(self) -> None:

        self._dt = self._t[1:] - self._t[:-1]


class BinApprox(BinApproxBase):

    def _check_if_prompt_init_messages(self) -> None:

        try:
        
            if os.environ["PYCOMBINA_PROMPTS_SHOWN"] == "True":
                
                self._prompt_init_messages = False
        
        except KeyError:
            
            os.environ["PYCOMBINA_PROMPTS_SHOWN"] = "True"
            self._prompt_init_messages = True
            

    def _welcome_prompt(self) -> None:

        if self._prompt_init_messages:

            print("\n-----------------------------------------------------------")
            print("|                                                         |")
            print("|                       pycombina                         |")
            print("|                                                         |")
            print("|     A collection of methods for binary approximation    |")
            print("|                                                         |")
            print("|       by A. Buerger, C. Zeile, S. Sager, M. Diehl       |")
            print("|                                                         |")
            print("-----------------------------------------------------------\n")


    def _set_time_points_t(self, t: Union[list, np.ndarray]) -> None:

        t = np.squeeze(t)

        if not t.ndim == 1:

                raise ValueError("Input t must be a vector.")

        if not np.all((t[1:] - t[:-1]) > 0):

            raise ValueError("Values in t must be strictly increasing.")

        self._t = t


    def _set_relaxed_binaries_b_rel(self, b_rel: Union[list, np.ndarray], \
        binary_threshold: float) -> None:

        self._binary_threshold = binary_threshold

        b_rel = np.atleast_2d(b_rel)

        if not b_rel.shape[1] == self._t.size-1:

            b_rel = b_rel.T

        if not b_rel.shape[1] == self._t.size-1:

            raise ValueError("One dimension of b_rel must be |t|-1.")

        if not (np.all(b_rel >= 0) and np.all(b_rel <= 1)):

            raise ValueError("All elements of the relaxed binary input " + \
                "must be 0 <= b <= 1.")

        b_rel[b_rel < self._binary_threshold] = 0
        b_rel[b_rel > 1.0 - self._binary_threshold] = 1

        self._b_rel = b_rel


    def _initialize_valid_controls(self) -> None:

        self._b_valid = np.ones((self.n_c, self.n_t), dtype = int)


    def _set_off_state(self, off_state_included: bool) -> None:

        if off_state_included and \
            not np.all(np.sum(self._b_rel, axis = 0) == 1.0):

            raise ValueError("The sum of relaxed binary controls per time point " + \
                "must be exactly 1, or off_state_included must be set to False.")

        self._off_state_included = off_state_included


    def _set_problem_size_reduction(self, reduce_problem_size_before_solve: bool) -> None:

        self._reduce_problem_size_before_solve = reduce_problem_size_before_solve


    def __init__(self, t: Union[list, np.ndarray], b_rel: Union[list, np.ndarray], \
        binary_threshold: float = 1e-3, off_state_included: bool = True, \
        reduce_problem_size_before_solve: bool = False) -> None:

        self._check_if_prompt_init_messages()
        self._welcome_prompt()

        self._set_time_points_t(t = t)
        self._set_relaxed_binaries_b_rel(b_rel = b_rel, \
            binary_threshold = binary_threshold)

        self._determine_number_of_control_intervals()
        self._determine_number_of_controls()
        self._compute_time_grid_from_time_points()

        self._initialize_valid_controls()

        self._set_off_state(off_state_included = off_state_included)
        self._set_problem_size_reduction(reduce_problem_size_before_solve = \
            reduce_problem_size_before_solve)


    def set_n_max_switches(self, n_max_switches: Union[int, list, np.ndarray]) -> None:

        try:

            n_max_switches = np.asarray(n_max_switches, dtype = int)

            if not np.atleast_1d(np.squeeze(n_max_switches)).ndim == 1:
                raise ValueError

            if not n_max_switches.size == self.n_c:
                raise ValueError

        except ValueError:
            raise ValueError("The number of integer values in max_switches " + \
                "must be equal to the number of binary controls.")

        self._n_max_switches = n_max_switches


    def set_min_up_times(self, min_up_times: Union[float, list, np.ndarray]) -> None:

        min_up_times = np.asarray(min_up_times)

        try:
            if not np.atleast_1d(np.squeeze(min_up_times)).ndim == 1:
                raise ValueError

            if not min_up_times.size == self.n_c:
                raise ValueError

        except ValueError:
            raise ValueError("The number of values in min_up_times " + \
                "must be equal to the number of binary controls.")

        self._min_up_times = min_up_times


    def set_min_down_times(self, min_down_times: Union[float, list, np.ndarray]) -> None:

        min_down_times = np.asarray(min_down_times)

        try:
            if not np.atleast_1d(np.squeeze(min_down_times)).ndim == 1:
                raise ValueError

            if not min_down_times.size == self.n_c:
                raise ValueError

        except ValueError:
            raise ValueError("The number of values in min_down_times " + \
                "must be equal to the number of binary controls.")

        self._min_down_times = min_down_times


    def set_previously_active_control(self, \
        b_bin_pre: Union[list, np.ndarray]) -> None:

        b_bin_pre = np.asarray(b_bin_pre)

        if not np.sum(b_bin_pre) <= 1:

            raise ValueError("At most one control can be active at a time.")

        if not b_bin_pre.size == self.n_c:

            raise ValueError("The number of values in b_bin_pre " + \
                "must be equal to the number of binary controls.")

        if not np.all((b_bin_pre == 0) | (b_bin_pre == 1)):

            raise ValueError("All elements in b_bin_pre " + \
                "must be either 0 or 1.")

        self.b_bin_pre = b_bin_pre


    def set_min_down_times_pre(self, min_down_times_pre: Union[float, list, np.ndarray]) -> None:

        min_down_times_pre = np.asarray(min_down_times_pre)

        try:
            if not np.atleast_1d(np.squeeze(min_down_times_pre)).ndim == 1:
                raise ValueError

            if not min_down_times_pre.size == self.n_c:
                raise ValueError

        except ValueError:
            raise ValueError("The number of values in min_down_times_pre " + \
                "must be equal to the number of binary controls.")

        self._min_down_times_pre = min_down_times_pre


    def set_valid_controls_for_interval(self, dt: tuple, \
        b_bin_valid: Union[list, np.ndarray]) -> None:

        if not len(dt) == 2:
            raise ValueError("dt must have exactly two entries.")

        b_bin_valid = np.asarray(b_bin_valid)

        try:
            if not np.atleast_1d(np.squeeze(b_bin_valid)).ndim == 1:
                raise ValueError

            if not np.asarray(b_bin_valid).size == self.n_c:
                raise ValueError
            
        except ValueError:
            raise ValueError("The number of values in b_bin_valid " + \
                "must be equal to the number of binary controls.")

        if not np.all((b_bin_valid == 0) | (b_bin_valid == 1)):

            raise ValueError("All elements in b_bin_valid " + \
                "must be either 0 or 1.")

        b_bin_valid = np.atleast_2d(b_bin_valid)

        if not b_bin_valid.shape[1] == 1:
            b_bin_valid = b_bin_valid.T

        idx_interval = np.logical_and(self.t[:-1] >= dt[0], self.t[:-1] < dt[1])
        self._b_valid[:, idx_interval] = \
            npm.repmat(b_bin_valid, 1, np.sum(idx_interval))


class BinApproxPreprocessed(BinApproxBase):

    def _set_orignal_binapprox_problem(self, binapprox: BinApprox) -> None:

        self._binapprox = binapprox


    def _copy_problem_information(self):
        
        self._b_rel = self._binapprox.b_rel
        self._b_valid = self._binapprox.b_valid

        self._n_max_switches = self._binapprox.n_max_switches
        self._min_up_times = self._binapprox.min_up_times
        self._min_down_times = self._binapprox.min_down_times
          
        self._b_bin_pre = self._binapprox.b_bin_pre


    def _append_off_state(self) -> None:

        if not self._binapprox.off_state_included:

            self._b_rel = np.vstack([self._b_rel, \
                np.atleast_2d(1 - np.sum(self._binapprox.b_rel, axis = 0))])

            self._b_valid = np.vstack([self._b_valid, \
                np.ones(self._binapprox.n_t, dtype = int)])

            self._n_max_switches = np.append(self._n_max_switches, \
                self._binapprox.n_t)
            self._min_up_times = np.append(self._min_up_times, 0.0)
            self._min_down_times = np.append(self._min_down_times, 0.0)

            self._b_bin_pre = np.append(self._b_bin_pre, 0)


    def _determine_active_controls(self) -> None:

        b_active = []

        for k, b_rel_k in enumerate(self._b_rel):

            if not np.all(b_rel_k == 0):

                b_active.append(k)

        self._b_active = np.asarray(b_active)


    def _determine_active_time_points(self) -> None:


        if self._binapprox.reduce_problem_size_before_solve:

            # --> TBD! reduce_problem_size etc.

            t_active = range(self._binapprox.n_t) 

        else:

            t_active = range(self._binapprox.n_t)

        self._t_active = np.asarray(t_active)


    def _remove_inactive_controls(self) -> None:

        self._t = np.append(self._binapprox.t[self._t_active], self._binapprox.t[-1])

        self._b_rel = self._b_rel[np.ix_(self._b_active, self._t_active)]
        self._b_valid = self._b_valid[np.ix_(self._b_active, self._t_active)]

        self._n_max_switches = self._n_max_switches[self._b_active]
        self._min_up_times = self._min_up_times[self._b_active]
        self._min_down_times = self._min_down_times[self._b_active]
   
        self._b_bin_pre = self._b_bin_pre[self._b_active]


    def __init__(self, binapprox: BinApprox) -> None:

        self._set_orignal_binapprox_problem(binapprox)
        self._copy_problem_information()
        self._append_off_state()
        self._determine_active_controls()
        self._determine_active_time_points()
        self._remove_inactive_controls()

        self._determine_number_of_control_intervals()
        self._determine_number_of_controls()
        self._compute_time_grid_from_time_points()


if __name__ == "__main__":

    import pylab as pl

    b_rel = pl.array([9.164991131439303e-08, 9.164989910069793e-08, 9.164986964110127e-08, 9.164981439200778e-08, 9.164971954974675e-08, 9.164956322584703e-08, 9.164931096870898e-08, 9.164890871558705e-08, 9.16482717331077e-08, 9.164726728376491e-08, 9.164568747185336e-08, 9.164320671195729e-08, 9.163931511370584e-08, 9.163321414037958e-08, 9.162365315758747e-08, 9.160867333705047e-08, 9.158520628111474e-08, 9.154844464973005e-08, 9.149085452908308e-08, 9.140062376048531e-08, 9.125921952032561e-08, 9.103753238327347e-08, 9.06897600760712e-08, 9.01436326543539e-08, 8.928459967910412e-08, 8.792973591727924e-08, 8.578323033799388e-08, 8.235606307513253e-08, 7.680620700237228e-08, 6.75611734322906e-08, 5.110029321633913e-08, 4.403564664444702e-08, 4.106387808317555e-08, 3.983950373134124e-08, 3.934055898011604e-08, 3.9137914036044536e-08, 3.9054919200406776e-08, 3.901881246871395e-08, 3.899786135210769e-08, 3.897363059366587e-08, 3.8924779784938846e-08, 3.880822297418e-08, 3.852080876236079e-08, 3.780600129669751e-08, 3.601141047402357e-08, 3.139256276666938e-08, 2.9834455518510574e-08, 2.9318934446262996e-08, 2.914964834988244e-08, 2.9094176453158642e-08, 2.907592834306512e-08, 2.9069660025366436e-08, 2.906669316762665e-08, 2.906291807927123e-08, 2.9053105209808462e-08, 2.9023659839179072e-08, 2.893375174707503e-08, 2.865832883983718e-08, 2.781057309571279e-08, 2.516081216626174e-08, 1.6349821111021932e-08, 1.4641381658496285e-08, 1.4321695524188809e-08, 1.4262451136479392e-08, 1.4251493200337602e-08, 1.4249467289977935e-08, 1.424909202859219e-08, 1.4249016931279371e-08, 1.4248970149529801e-08, 1.4248781586888953e-08, 1.4247771634743814e-08, 1.4242308735857878e-08, 1.4212753082407813e-08, 1.4052702623315826e-08, 1.3181284088570942e-08, 8.268584499081758e-09, 7.688662077381325e-09, 7.621735475505242e-09, 7.61405669269621e-09, 7.613347382291173e-09, 7.614772557847257e-09, 7.628032105221415e-09, 7.743336673082607e-09, 7.774748608050492e-09, 7.781914757778366e-09, 7.777476689145606e-09, 7.768965238198726e-09, 7.809086255912332e-09, 8.347837492600157e-09, 1.3149458138366266e-08, 5.812677816280237e-08, 7.980857140061672e-08, 9.34899928315103e-08, 1.0296318896151463e-07, 1.0994080615953228e-07, 1.1547277950297847e-07, 1.2038557045733308e-07, 1.2548706350691847e-07, 1.3170304260698727e-07, 1.4020750175014196e-07, 1.526048438509999e-07, 1.7130057227378714e-07, 2.005178071994339e-07, 2.499858770490773e-07, 3.5728576775753295e-07, 0.20636133458659084, 0.206361456820869, 0.20636151047209217, 0.20636154006894097, 0.20636155692321392, 0.2063615660721068, 0.2063615709426096, 0.2063615747616593, 0.206361581065729, 0.20636159414396368, 0.2063616208814176, 0.20636168097818755, 0.2063617772714703, 0.2063618582371984, 0.20636189781122233, 0.20636190501221507, 0.2063619496037749, 0.2063620732923192, 0.20636249842130122, 0.2063773813145899, 0.252054864921568, 0.2520579982392464, 0.25288811587249843, 0.2593977742761429, 0.3340935108565165, 0.3340940442516569, 0.33409419385053196, 0.3340942499059316, 0.3340942652728998, 0.33409424511989244, 0.3135810041373855, 0.3135809645281175, 0.31358095939038705, 0.3135809756716781, 0.3135810190249818, 0.31358111927309246, 0.3135814262624077, 0.999999950926087, 0.999999974046433, 0.9999999783613379, 0.9999999789321505, 0.9999999787698426, 0.9999999779052294, 0.9999999747514201, 0.9999999550265595, 0.06453461127561795, 0.06453456953472514, 0.06453456775738621, 0.0645345926266459, 0.06453465796048136, 0.06453481999226998, 0.06453538382656564, 0.2131890930121317, 0.2131936809163467, 0.21319408556528727, 0.21319422088078965, 0.21319427911618313, 0.21319430204287756, 0.2131943004833132, 0.213194265080231, 2.287219254968173e-08, 1.0681031150093401e-08, 9.359002315937822e-09, 9.461200350554808e-09, 9.80570097938495e-09, 1.0901115627326692e-08, 1.2859087591404522e-08, 1.5439876067722526e-08, 1.881147846187437e-08, 2.325425317922466e-08, 2.905700927723151e-08, 3.620161250971683e-08, 4.3709179595637425e-08, 4.8807602615609486e-08, 4.614727473289024e-08, 2.319637525384318e-08, 2.3113256911779592e-08, 3.062367109037491e-08, 4.5803905719390506e-08, 7.373574744184745e-08, 1.249404286368601e-07, 2.24798134068856e-07, 4.5731586084303404e-07, 1.3208173664524378e-06, 0.0433240937001994, 0.04332605093577369, 0.043326318185106925, 0.04332641234938346, 0.043326451830150416, 0.04332646332568629, 0.04332645064755273, 0.043326464881207304, 0.04332652140919314, 0.9999999444789713, 0.9999999847239209, 0.9999999852314699, 0.9999999823896432, 0.9999999805987997, 0.9999999804592423, 0.9999999816949504, 0.9999999837988184, 0.9999999862895442, 0.999999988820378, 0.9999999911927993, 0.9999999933222256, 0.9999999952099605, 0.9999999968647432, 0.9999999982733226, 0.9999999994748296, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9999999976933017, 0.9999999927247275, 0.9999999813465971, 0.9999999516982475, 0.9999998765776738, 0.9999996930339815, 0.999999381480724, 0.9999952329064322, 0.33837190283783086, 0.33836939449774384, 0.33836820191669553, 0.3383674235415369, 0.3383668483297875, 0.3383663939468469, 0.33836601976451697, 0.3383657027491601, 0.3383654285764394, 0.33836518772741186, 0.33836497355245754, 0.3383647812216936, 0.3383646071134709, 0.33836444845465696, 0.3383643046158953, 0.33836417338226865, 0.338364053014526, 0.3383639421153582, 0.33836383954553606, 0.3383637443641662, 0.338363655785219, 0.33836357314532267, 0.33836349587948944, 0.3383634235025246, 0.3383633555945778, 0.3383632917897552, 0.3383632317670245, 0.3383631752430078, 0.3383631219726682, 0.33836307197017373, 0.33836302498944143, 0.3383629808173723, 0.3383629392632571, 0.33836290015502957, 0.33836286333638244, 0.3383628286684003, 0.3383627960634522, 0.3383627654812393, 0.33836273685899004, 0.33836271012357955, 0.3383626852031968, 0.33836266203107024, 0.33836264055345605, 0.33836262073384066, 0.33836260260332357, 0.33836258610656866, 0.33836257119446206, 0.33836255782361746, 0.338362545955937, 0.3383625355582329, 0.3383625266019055, 0.3383625190626729, 0.3383625129203459, 0.33836250815864527, 0.3383625047650565, 0.338362502730721, 0.33836250205035523])
    t = 240 * pl.arange(0, b_rel.size+1)
    max_switches = [4]

    binapprox = BinApprox(t = t, b_rel = b_rel, binary_threshold = 1e-3, \
        off_state_included = False)
    binapprox.set_n_max_switches(n_max_switches = [2])
    
    # binapprox.set_min_up_times(min_up_times = [15.0])
    # binapprox.set_min_down_times(min_down_times = [10.0])

    bap = BinApproxPreprocessed(binapprox)


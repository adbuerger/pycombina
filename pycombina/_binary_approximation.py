#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of pycombina.
#
# Copyright 2017-2018 Adrian Bürger, Clemens Zeile, Sebastian Sager, Moritz Diehl
#
# pycombina is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pycombina is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pycombina. If not, see <http://www.gnu.org/licenses/>.

import os
import warnings
import numpy as np
from typing import Union

from abc import ABC

class BinApproxBase(ABC):

    @property
    def t(self) -> np.ndarray:

        '''Get discrete time grid points.'''

        return self._t


    @property
    def b_rel(self) -> np.ndarray:

        '''Get relaxed binary controls.'''

        return self._b_rel


    @property
    def reduce_problem_size_before_solve(self) -> bool:

        '''Get flag whether problem size is reduced prior to solving by merging certain time intervals.'''

        return self._reduce_problem_size_before_solve


    @property
    def dt(self) -> np.ndarray:

        '''Get time intervals between time grid points.'''

        return self._dt


    @property
    def n_t(self) -> int:

        '''Get number of time intervals.'''

        return self._n_t


    @property
    def n_c(self) -> int:

        '''Get number of mutually exclusive binaries.'''

        return self._n_c


    @property
    def b_valid(self) -> np.ndarray:

        '''Get valid binaries controls per time interval.'''

        return self._b_valid


    @property
    def b_adjacencies(self) -> np.ndarray:

        '''
        Get the adjacencies for allowed switching transitions of binary controls, 
        where 1 marks valid transitions and 0 marks invalid transitions.
        E. g., the following output

            >>> print(binapprox.b_adjacencies)
            [[1, 0, 0],
             [1, 1, 1],
             [0, 1, 1]])

        indicates that switching from control 0 to 1 is allowed as well
        as switching from control 1 to 2 and back, but neither from control 1 to 0
        nor from control 2 to 0 or back. Zeros on diagonal elements of this matrix indicate
        that a binary control cannot stay active for more that one subsequent time interval.
        '''

        return self._b_adjacencies


    @property
    def dwell_time_tolerance(self) -> float:

        '''
        Get the tolerance value needed to modify dwell time constraint duration parameters 
        in order to prevent over-fulfillment of dwell time constraints, see issue #7.
        '''

        return self._dwell_time_tolerance


    @property
    def eta(self) -> float:

        '''Get the objective value of the binary approximation problem.'''

        try:
            return self._eta

        except AttributeError:
           raise AttributeError("eta not yet available.")


    @property
    def b_bin(self) -> np.ndarray:

        '''Get the binary solution of the binary approximation problem.'''

        try:
            return self._b_bin

        except:
           raise AttributeError("b_bin not yet available.")


    @property
    def n_max_switches(self) -> np.ndarray:

        '''Get the maximum possible amount of switches per control.'''

        try:
            return self._n_max_switches

        except AttributeError:

            return self.n_t * np.ones(self.n_c, dtype = int)


    @property
    def min_up_times(self) -> np.ndarray:

        '''Get the minimum up times per control.'''

        try:
            return self._min_up_times

        except AttributeError:

            return np.zeros(self.n_c)


    @property
    def min_down_times(self) -> np.ndarray:

        '''Get the minimum down times per control.'''

        try:
            return self._min_down_times

        except AttributeError:

            return np.zeros(self.n_c)


    @property
    def max_up_times(self) -> np.ndarray:

        '''
        Get the maximum up times per control, i. e., the time a control
        be can stay activated before it must be deactivated.
        '''

        try:
            return self._max_up_times

        except AttributeError:

            return np.full(self.n_c, np.inf)


    @property
    def total_max_up_times(self) -> np.ndarray:

        '''
        Get the total maximum up times per control, i. e., the total time a
        control can be active over the whole time horizon.
        '''

        try:
            return self._total_max_up_times

        except AttributeError:

            return np.full(self.n_c, np.inf)


    @property
    def b_bin_pre(self) -> np.ndarray:

        '''Get the binary control active at time grid point "t-1".'''

        try:
            return self._b_bin_pre

        except AttributeError:

            return np.zeros(self.n_c)


    @property
    def cia_norm(self):

        '''Applied CIA norm for objective'''

        try:
            return self._cia_norm

        except AttributeError:
            return "max_norm"


    def _determine_number_of_control_intervals(self) -> None:

        self._n_t = self._t.size - 1


    def _determine_number_of_controls(self) -> None:

        self._n_c = self._b_rel.shape[0]


    def _compute_time_grid_from_time_points(self) -> None:

        self._dt = self._t[1:] - self._t[:-1]


    def _compute_dwell_time_tolerance(self) -> None:

        if max(self.dt)-min(self.dt) > 1e10:

            warnings.warn("Grid interval lengths differ extremely. " + \
                "This might result in dwell time constraint violation" )

        self._dwell_time_tolerance = min(self.dt)*1e-5


    def set_b_bin(self, b_bin: Union[list, np.ndarray]) -> None:

        b_bin = np.atleast_2d(b_bin)

        if not b_bin.shape[1] == self._t.size-1:

            b_bin = b_bin.T

        if not b_bin.shape[1] == self._t.size-1:

            raise ValueError("One dimension of b_bin must be |t|-1.")

        if not np.all((b_bin == 0) | (b_bin == 1)):

            raise ValueError("All elements in b_bin " + \
                "must be either 0 or 1.")

        self._b_bin = b_bin


    def set_eta(self, eta: Union[int, float]) -> None:

        try:
            eta = float(eta)
        
            if eta < 0.0:
                raise ValueError

        except (TypeError, ValueError):
            raise ValueError("eta must be a positve scalar value.")

        self._eta = eta


class BinApprox(BinApproxBase):

    r'''
    Specifies a binary approximation problem.

    :param t: One-dimensional array that contains the discrete time points
              of the binary approximation problem. The
              values in t must be strictly increasing.

    :param b_rel: Two-dimensional array that contains the relaxed binary
                  controls to be approximated. One dimension of the array
                  must be of size len(t)-1 and all entries of the array 
                  must be 0 <= b_k,i <= 1. The sum of relaxed binaries per time
                  point must be sum(b[i])=1 to fulfill the SOS1-constraint.

    :param binary_threshold: If a value b_rel,k,i is smaller than binary_threshold
                             it is considered 0, and if it is bigger than
                             1-binary_threshold it is considered 1.

    :param reduce_problem_size_before_solve: Setting this flag has no effect in
                                             the current version of pycombina.

    :raises: ValueError, AttributeError, RuntimeError

    '''


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

        clamped_down = b_rel < self._binary_threshold
        clamped_up = b_rel > 1.0 - self._binary_threshold
        clamped_count = np.count_nonzero(np.logical_or(clamped_down, clamped_up), axis=0)

        b_rel[clamped_down] = 0
        b_rel[clamped_up] = 1

        self._b_rel = b_rel
        self._clamped = clamped_count


    def _initialize_valid_controls(self) -> None:

        self._b_valid = np.ones((self.n_c, self.n_t), dtype = int)


    def _initialize_control_adjacency(self) -> None:

        self._b_adjacencies = np.ones((self.n_c, self.n_c), dtype = int)


    def _check_sos1_constraint_fulfilled(self) -> None:

        sums = np.sum(self._b_rel, axis=0)
        tol = self._clamped * self._binary_threshold + (self._b_rel.shape[0] + 1) * np.finfo(sums.dtype).eps
        
        if np.any(np.logical_or(sums > 1.0 + tol, sums < 1.0 - tol)):
            warnings.warn("The sum of relaxed binary controls per time point " + \
                "must be exactly 1\n.This seems not to be the case for the data " + \
                " you provided.\npycombina might not work as expected.")


    def _set_problem_size_reduction(self, reduce_problem_size_before_solve: bool) -> None:

        self._reduce_problem_size_before_solve = reduce_problem_size_before_solve


    def __init__(self, t: Union[list, np.ndarray], b_rel: Union[list, np.ndarray], \
        binary_threshold: float = 1e-3, reduce_problem_size_before_solve: bool = False) -> None:

        self._set_time_points_t(t = t)
        self._set_relaxed_binaries_b_rel(b_rel = b_rel, \
            binary_threshold = binary_threshold)

        self._determine_number_of_control_intervals()
        self._determine_number_of_controls()
        self._compute_time_grid_from_time_points()
        self._compute_dwell_time_tolerance()

        self._initialize_valid_controls()
        self._initialize_control_adjacency()

        self._check_sos1_constraint_fulfilled()
        self._set_problem_size_reduction(reduce_problem_size_before_solve = \
            reduce_problem_size_before_solve)


    def set_n_max_switches(self, n_max_switches: Union[int, float, list, np.ndarray]) -> None:

        '''
        Set the maximum number of allowed switches per control for solution of
        the binary approximation problem. By default, the maximum number of
        switches per control is not limited.

        Usage::

            >>> from pycombina import BinApprox

            >>> t = [0, ..., 9.0, 9.5, 10.0]
            >>> b_rel = [[0.0      , ..., 0.558401, 0.558401, 0.558401],
            ...          [0.0      , ..., 0.0     , 0.0     , 0.0     ],
            ...          [1.0      , ..., 0.441599, 0.441599, 0.441599]])

            >>> binapprox = BinApprox(t, b_rel)
            >>> binapprox.set_n_max_switches([3, 2, 5])

            >>> print(binapprox.n_max_switches)
            [3, 2, 5]

        :param n_max_switches: Maximum number of switches allowed per control
                               for solution of the binary approximation problem.
                               Non-integer entries are rounded down.
        '''

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

        '''
        Set the minimum up-times per control, i. e., the minimum time that a
        control must stay active once it has been activated. By default,
        the minimum up-times are 0.

        Usage::

            >>> from pycombina import BinApprox

            >>> t = [0, ..., 9.0, 9.5, 10.0]
            >>> b_rel = [[0.0      , ..., 0.558401, 0.558401, 0.558401],
            ...          [0.0      , ..., 0.0     , 0.0     , 0.0     ],
            ...          [1.0      , ..., 0.441599, 0.441599, 0.441599]])

            >>> binapprox = BinApprox(t, b_rel)
            >>> binapprox.set_min_up_times([2.4, 4.3, 1.4])
        
            >>> print(binapprox.min_up_times)
            [2.4, 4.3, 1.4]

        :param min_up_times: Minimum up-times per binary control. 
        '''

        min_up_times = np.asarray(min_up_times)

        try:
            if not np.atleast_1d(np.squeeze(min_up_times)).ndim == 1:
                raise ValueError

            if not min_up_times.size == self.n_c:
                raise ValueError

        except ValueError:
            raise ValueError("The number of values in min_up_times " + \
                "must be equal to the number of binary controls.")

        # Modify the min up time durations by the dwell time tolerance, see issue #7
        self._min_up_times = min_up_times - self.dwell_time_tolerance*np.ones(min_up_times.size)


    def set_min_down_times(self, min_down_times: Union[float, list, np.ndarray]) -> None:

        '''
        Set the minimum down-times per control, i. e., the minimum time that a
        control must stay inactive once it has been deactivated. By default,
        the minimum down-times are 0.

        Usage::

            >>> from pycombina import BinApprox

            >>> t = [0, ..., 9.0, 9.5, 10.0]
            >>> b_rel = [[0.0      , ..., 0.558401, 0.558401, 0.558401],
            ...          [0.0      , ..., 0.0     , 0.0     , 0.0     ],
            ...          [1.0      , ..., 0.441599, 0.441599, 0.441599]])

            >>> binapprox = BinApprox(t, b_rel)
            >>> binapprox.set_min_down_times([1.3, 3.3, 2.1])

            >>> print(binapprox.min_down_times)
            [1.3, 3.3, 2.1]
        
        :param min_down_times: Minimum down-times per binary control. 
        '''

        min_down_times = np.asarray(min_down_times)

        try:
            if not np.atleast_1d(np.squeeze(min_down_times)).ndim == 1:
                raise ValueError

            if not min_down_times.size == self.n_c:
                raise ValueError

        except ValueError:
            raise ValueError("The number of values in min_down_times " + \
                "must be equal to the number of binary controls.")

        # Modify the min down time durations by the dwell time tolerance, see issue #7
        self._min_down_times = min_down_times - self.dwell_time_tolerance*np.ones(min_down_times.size)


    def set_max_up_times(self, max_up_times: Union[float, list, np.ndarray]) -> None:

        '''
        Set the maximum up-times per control, i. e., the maximum time that a
        control can stay active once it has been activated. By default,
        the maximum up-times are the total duration of the time horizon.

        Usage::

            >>> from pycombina import BinApprox

            >>> t = [0, ..., 9.0, 9.5, 10.0]
            >>> b_rel = [[0.0      , ..., 0.558401, 0.558401, 0.558401],
            ...          [0.0      , ..., 0.0     , 0.0     , 0.0     ],
            ...          [1.0      , ..., 0.441599, 0.441599, 0.441599]])

            >>> binapprox = BinApprox(t, b_rel)
            >>> binapprox.set_max_up_times([3.7, 2.4, 6.3])
        
            >>> print(binapprox.max_up_times)
            [3.7, 2.4, 6.3]

        :param max_up_times: Maximum up-times per binary control. 
        '''

        max_up_times = np.asarray(max_up_times)

        try:
            if not np.atleast_1d(np.squeeze(max_up_times)).ndim == 1:
                raise ValueError

            if not max_up_times.size == self.n_c:
                raise ValueError

        except ValueError:
            raise ValueError("The number of values in max_up_times " + \
                "must be equal to the number of binary controls.")

        # Modify the max up time durations by the dwell time tolerance, see issue #7
        self._max_up_times = max_up_times + self.dwell_time_tolerance*np.ones(max_up_times.size)


    def set_total_max_up_times(self, total_max_up_times: Union[float, list, np.ndarray]) -> None:

        '''
        Set the total maximum up-times per control, i. e., the maximum time
        that a control can stay active over the whole control horizon. By default,
        the total maximum up-times are the total duration of the time horizon.

        Usage::

            >>> from pycombina import BinApprox

            >>> t = [0, ..., 9.0, 9.5, 10.0]
            >>> b_rel = [[0.0      , ..., 0.558401, 0.558401, 0.558401],
            ...          [0.0      , ..., 0.0     , 0.0     , 0.0     ],
            ...          [1.0      , ..., 0.441599, 0.441599, 0.441599]])

            >>> binapprox = BinApprox(t, b_rel)
            >>> binapprox.set_total_max_up_times([3.7, 2.4, 6.3])
        
            >>> print(binapprox.total_max_up_times)
            [3.7, 2.4, 6.3]

        :param total_max_up_times: Total maximum up-times per binary control. 
        '''

        total_max_up_times = np.asarray(total_max_up_times)

        try:
            if not np.atleast_1d(np.squeeze(total_max_up_times)).ndim == 1:
                raise ValueError

            if not total_max_up_times.size == self.n_c:
                raise ValueError

        except ValueError:
            raise ValueError("The number of values in total_max_up_times " + \
                "must be equal to the number of binary controls.")

        # Modify the total max up time durations by the dwell time tolerance, see issue #7
        self._total_max_up_times = total_max_up_times + self.dwell_time_tolerance*np.ones(total_max_up_times.size)


    def set_b_bin_pre(self, b_bin_pre: Union[list, np.ndarray]) -> None:

        '''
        Define the binary control combination active at time point t-1, i. e.,
        the control active at the time before the first time point of the time grid.
        This influences the number of switches needed to activate and deactivate
        binary controls at the first time point, which otherwise does not
        influence the switch count.
        
        Usage::

            >>> from pycombina import BinApprox

            >>> t = [0, ..., 9.0, 9.5, 10.0]
            >>> b_rel = [[0.0      , ..., 0.558401, 0.558401, 0.558401],
            ...          [0.0      , ..., 0.0     , 0.0     , 0.0     ],
            ...          [1.0      , ..., 0.441599, 0.441599, 0.441599]])

            >>> binapprox = BinApprox(t, b_rel)
            >>> binapprox.set_b_bin_pre([1, 0, 0])

            >>> print(binapprox.b_bin_pre)
            [1, 0, 0]

        :param b_bin_pre: Binary control combination active at time point t-1. 
        '''

        b_bin_pre = np.asarray(b_bin_pre)

        if not np.sum(b_bin_pre) <= 1:

            raise ValueError("At most one control can be active at a time.")

        if not b_bin_pre.size == self.n_c:

            raise ValueError("The number of values in b_bin_pre " + \
                "must be equal to the number of binary controls.")

        if not np.all((b_bin_pre == 0) | (b_bin_pre == 1)):

            raise ValueError("All elements in b_bin_pre " + \
                "must be either 0 or 1.")

        self._b_bin_pre = b_bin_pre


    def set_valid_controls_for_interval(self, dt: tuple, \
        b_bin_valid: Union[list, np.ndarray]) -> None:

        '''
        This function can be used to allow activation of only a certain subset
        of the binary controls in between to time points on the grid.

        Usage::

            >>> from pycombina import BinApprox

            >>> t = [0, ..., 9.0, 9.5, 10.0]
            >>> b_rel = [[0.0      , ..., 0.558401, 0.558401, 0.558401],
            ...          [0.0      , ..., 0.0     , 0.0     , 0.0     ],
            ...          [1.0      , ..., 0.441599, 0.441599, 0.441599]])

            >>> binapprox = BinApprox(t, b_rel)

            >>> # Allow activation of only control 1 and 2 for all discrete time
            >>> # points bigger than or equal to 0.2 and smaller than 1.8
            >>> binapprox.set_valid_controls_for_interval((0.2, 1.8), [0, 1, 1])

        :param dt: Lower and upper bound of the time interval.
        :param b_bin_valid: Allowed binary controls on the time interval. 
        '''        

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
        self._b_valid[:, idx_interval] = b_bin_valid


    def set_valid_control_transitions(self, b_i: int, \
        b_valid_upcoming: Union[list, np.ndarray]) -> None:

        '''
        Specify the allowed transitions from control b_i to other controls. By
        default, transitions from all binary controls to each control are
        allowed.

        Usage::

            >>> from pycombina import BinApprox

            >>> t = [0, ..., 9.0, 9.5, 10.0]
            >>> b_rel = [[0.0      , ..., 0.558401, 0.558401, 0.558401],
            ...          [0.0      , ..., 0.0     , 0.0     , 0.0     ],
            ...          [1.0      , ..., 0.441599, 0.441599, 0.441599]])

            >>> binapprox = BinApprox(t, b_rel)

            >>> # Allow transition from control 1 only to control 1 and 2
            >>> binapprox.set_valid_control_transitions(1, [0, 1, 1])

            >>> # Allow transition from control 1 only to control 0 and 2, i. e.,
            >>> # control 1 cannot be active on two subsequent time intervals
            >>> binapprox.set_valid_control_transitions(1, [1, 0, 1])

        :param b_i: Controls for which the allowed transitions are specified.
        :param b_valid_upcoming: Valid upcoming controls for control b_i. 
        '''   

        if self.n_c <= 1:
            raise RuntimeError("Setting of valid binary control transitions (i. e. adjacencies) " + \
                "only possible if number of binary controls is bigger than 1.")

        try:
            if not b_i < self.n_c:
                raise ValueError

        except ValueError:
            raise ValueError("Binary control index b_i " + \
                "must be smaller than the number of binary controls.")

        b_valid_upcoming = np.asarray(b_valid_upcoming)

        try:
            if not np.atleast_1d(np.squeeze(b_valid_upcoming)).ndim == 1:
                raise ValueError

            if not np.asarray(b_valid_upcoming).size == self.n_c:
                raise ValueError
            
        except ValueError:
            raise ValueError("The number of values in b_valid_upcoming " + \
                "must be equal to the number of binary controls.")

        if not np.all((b_valid_upcoming == 0) | (b_valid_upcoming == 1)):

            raise ValueError("All elements in b_valid_upcoming " + \
                "must be either 0 or 1.")


        self._b_adjacencies[:, b_i] = b_valid_upcoming


    def set_cia_norm(self, cia_norm: str) -> None:

        '''
        Specify the norm applied to || integral_t_0^t_f (b_rel-b_bin)*dt ||

        Allowed choices:

        - "max_norm": maximum over all time points and controls
        - "column_sum_norm": maximum over all time points of the sum (over all controls) of absolute accumulated values (b_rel-b_bin)*dt
        - "row_sum_norm": maximum over all controls of the sum (over all time points) of absolute accumulated values (b_rel-b_bin)*dt

        Usage::

            >>> from pycombina import BinApprox

            >>> t = [0, ..., 9.0, 9.5, 10.0]
            >>> b_rel = [[0.0      , ..., 0.558401, 0.558401, 0.558401],
            ...          [0.0      , ..., 0.0     , 0.0     , 0.0     ],
            ...          [1.0      , ..., 0.441599, 0.441599, 0.441599]])

            >>> binapprox = BinApprox(t, b_rel)

            >>> # Induce max_norm:
            >>> binapprox.set_cia_norm("max_norm")

        :param cia_norm: norm choice.
        '''   
        if not ((cia_norm == "max_norm") or (cia_norm == "column_sum_norm") or (cia_norm == "row_sum_norm")):
            raise ValueError("cia_norm must be set either to 'max_norm' or 'column_sum_norm' or 'row_sum_norm'")

        self._cia_norm = cia_norm

class BinApproxPreprocessed(BinApproxBase):

    def _set_orignal_binapprox_problem(self, binapprox: BinApprox) -> None:

        self._binapprox = binapprox


    def _copy_problem_information(self):
        
        self._b_rel = self._binapprox.b_rel
        self._b_valid = self._binapprox.b_valid

        self._n_max_switches = self._binapprox.n_max_switches
        self._min_up_times = self._binapprox.min_up_times
        self._min_down_times = self._binapprox.min_down_times
        self._max_up_times = self._binapprox.max_up_times
        self._total_max_up_times = self._binapprox.total_max_up_times
          
        self._b_bin_pre = self._binapprox.b_bin_pre
        self._b_adjacencies = self._binapprox.b_adjacencies
        self._cia_norm = self._binapprox.cia_norm


    def _determine_active_controls(self) -> None:

        b_active = []
        b_inactive = []

        for k, b_rel_k in enumerate(self._b_rel):

            if not np.all(b_rel_k == 0):

                b_active.append(k)
            
            else:

                b_inactive.append(k)                

        self._b_active = np.asarray(b_active)
        self._b_inactive = np.asarray(b_inactive)


    def _determine_active_time_points(self) -> None:

        if self._binapprox.reduce_problem_size_before_solve:

            # --> TBD! reduce_problem_size etc.

            t_active = range(self._binapprox.n_t)
            t_inactive = []

        else:

            t_active = range(self._binapprox.n_t)
            t_inactive = []

        self._t_active = np.asarray(t_active)
        self._t_inactive = np.asarray(t_inactive)


    def _remove_inactive_controls(self) -> None:

        self._t = np.append(self._binapprox.t[self._t_active], self._binapprox.t[-1])

        self._b_rel = self._b_rel[np.ix_(self._b_active, self._t_active)]
        self._b_valid = self._b_valid[np.ix_(self._b_active, self._t_active)]
        self._b_adjacencies = self._b_adjacencies[np.ix_(self._b_active, self._b_active)]

        self._n_max_switches = self._n_max_switches[self._b_active]
        self._min_up_times = self._min_up_times[self._b_active]
        self._min_down_times = self._min_down_times[self._b_active]
        self._max_up_times = self._max_up_times[self._b_active]
        self._total_max_up_times = self._total_max_up_times[self._b_active]
   
        self._b_bin_pre = self._b_bin_pre[self._b_active]


    def __init__(self, binapprox: BinApprox) -> None:

        self._set_orignal_binapprox_problem(binapprox)
        self._copy_problem_information()
        self._determine_active_controls()
        self._determine_active_time_points()
        self._remove_inactive_controls()

        self._determine_number_of_control_intervals()
        self._determine_number_of_controls()
        self._compute_time_grid_from_time_points()


    def _add_inactive_controls(self) -> None:

        b_bin = np.zeros(( \
            self._b_active.size + self._b_inactive.size, \
            self._t_active.size + self._t_inactive.size))

        b_bin[np.ix_(self._b_active, self._t_active)] = self._b_bin

        self._b_bin = b_bin


    def _add_inactive_time_points(self) -> None:

        # --> TBD! reduce_problem_size etc.

        pass


    def inflate_solution(self) -> None:

        self._add_inactive_controls()
        self._add_inactive_time_points()

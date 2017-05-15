import heapq
cimport numpy as np
from time import time
import numpy
import cython

# http://stackoverflow.com/questions/18938065/iterating-over-arrays-in-cython-is-list-faster-than-np-array

@cython.boundscheck(False)
@cython.wraparound(False)
def bnb_jung(np.float64_t[::1] b_opt, int sigma_max):

    cdef int N_disc = b_opt.size
    cdef double t_start_bnb = time()

    q = []
    q_selected = {}

    cdef int k = -1
    cdef int k_prev = -1

    cdef int d_k = 0

    cdef double eta_k = 0
    cdef float priority_k = 0

    cdef int sigma_k = 0

    cdef np.ndarray[np.float64_t, ndim=1] b_opt_pk_true = \
        numpy.empty(N_disc, dtype=numpy.float64)
    cdef np.ndarray[np.float64_t, ndim=1] b_opt_pk_false = \
        numpy.empty(N_disc, dtype=numpy.float64)

    # b_opt_pk_true[N_disc-1] = b_opt[N_disc-1] - 1
    # b_opt_pk_false[N_disc-1] = b_opt[N_disc-1]

    # cdef int i = 0

    # for i in range(N_disc-1, 0, -1):

    #     b_opt_pk_true[i] = b_opt_pk_true[i+1] + b_opt[i] - 1
    #     b_opt_pk_false[i] = b_opt_pk_false[i+1] + b_opt[i]

    # The following is crucial for runtime!
    # -->

    cdef bint p_k

    # <--

    for p_k in range(2):

        k += 1

        eta_k = b_opt[d_k] - p_k
        priority_k = max(0, abs(eta_k))

        sigma_k = 0

        heapq.heappush(q, (priority_k, d_k, k, eta_k, k_prev, p_k, sigma_k))


    while len(q) != 0:

        a = heapq.heappop(q)

        # Store results in dict for fast access

        q_selected[a[2]] = (a[5], a[4])

        if (a[1] == N_disc):

            a_final = a

            duration_bnb = time() - t_start_bnb

            print "Duration BnB: " + str(duration_bnb) +  " s"

            t_start_reconstruction = time()

            b_opt_bin = [a_final[5]]
            k_prev = a_final[4]

            while k_prev != -1:

                a_prev = q_selected[k_prev]
                b_opt_bin.append(a_prev[0])

                k_prev = a_prev[1]

            duration_reconstruction = time() - t_start_reconstruction

            b_opt_bin = numpy.flip(b_opt_bin,0).tolist()
            b_opt_bin += [b_opt_bin[len(b_opt_bin)-1]] * (N_disc - len(b_opt_bin))

            print "Duration reconstruction: " + str(duration_reconstruction) +  " s"

            print k

            return b_opt_bin, a[3]


        for p_k in range(2):

            k += 1
            d_k = a[1] + 1

            eta_k = a[3] + (b_opt[d_k] - p_k)

            sigma_k = a[6] + abs(a[5] - p_k)

            if sigma_k == sigma_max:

                # if p_k == 1:

                #     eta_k += b_opt_pk_true[d_k+1]

                # else:

                #     eta_k += b_opt_pk_false[d_k+1]                    

                for i in range(d_k+1, N_disc):

                    eta_k += b_opt[i] - p_k

                d_k = N_disc

            priority_k = max(a[0], abs(eta_k))

            heapq.heappush(q, (priority_k, d_k, k, eta_k, a[2], p_k, sigma_k))

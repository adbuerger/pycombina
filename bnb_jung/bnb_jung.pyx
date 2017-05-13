import heapq
cimport numpy as np
from time import time

# http://stackoverflow.com/questions/18938065/iterating-over-arrays-in-cython-is-list-faster-than-np-array

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

        q_selected[a[2]] = (a[-2], a[4])

        if (a[1] == N_disc):

            a_final = a

            duration_bnb = time() - t_start_bnb

            print "Duration BnB: " + str(duration_bnb) +  " s"

            t_start_reconstruction = time()

            b_opt_bin = [a_final[-2]]
            k_prev = a_final[4]

            while k_prev != -1:

                a_prev = q_selected[k_prev]
                b_opt_bin.append(a_prev[0])

                k_prev = a_prev[1]

            duration_reconstruction = time() - t_start_reconstruction

            b_opt_bin = b_opt_bin[::-1]
            b_opt_bin += [b_opt_bin[-1]] * (N_disc - len(b_opt_bin))

            print "Duration reconstruction: " + str(duration_reconstruction) +  " s"

            return b_opt_bin


        for p_k in range(2):

            k += 1
            d_k = a[1] + 1

            eta_k = a[3] + (b_opt[d_k] - p_k)

            sigma_k = a[6] + abs(a[5] - p_k)

            if sigma_k == sigma_max:

                for i in range(d_k+1, N_disc):

                    eta_k += b_opt[i] - p_k

                d_k = N_disc

            priority_k = max(a[0], abs(eta_k))

            heapq.heappush(q, (priority_k, d_k, k, eta_k, a[2], p_k, sigma_k))

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

'''Solver log processing facilities for benchmark scripts.'''

import io
import re


# regular expression for UB update lines
ub_update = re.compile('^\s*U\s+')

def ub_seq(log):
    # ensure log has readline()
    if isinstance(log, str):
        log = io.StringIO(log)
    elif not hasattr(log, 'readline'):
        raise TypeError('log must be string or text IO object')

    while True:
        # read next line
        line = log.readline()
        if len(line) == 0:
            break

        # match line
        m = ub_update.match(line)
        if m is not None:
            line = line[m.end():].strip()
            fields = line.split('|')
            yield int(fields[0]), float(fields[1]), float(fields[3])

# execute as standalone program
if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, default=None, help='input log file (defaults to stdin)')
    parser.add_argument('-o', type=str, default=None, dest='output', help='output data file (defaults to stdout)')
    args = parser.parse_args()

    try:
        with sys.stdin if args.file is None else open(args.file, 'r') as log_in:
            with sys.stdout if args.output is None else open(args.output, 'w') as dat_out:
                for it, ub, rt in ub_seq(log_in):
                    print('{:d} {:g} {:f}'.format(it, ub, rt), file=dat_out)
    except IOError as e:
        print(e, file=sys.stderr)

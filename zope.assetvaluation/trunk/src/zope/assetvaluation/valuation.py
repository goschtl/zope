# Copyright (c) 2010 Zope Foundation and Contributors
# See also LICENSE.txt

import subprocess

TOTAL_SLOC = 'Total Physical Source Lines of Code (SLOC)'
TOTAL_COST = 'Total Estimated Cost to Develop'
ZERO = 'SLOC total is zero, no further analysis performed.'


class Assessor(object):

    def __init__(self, src_dir, data_dir):
        self.src_dir = src_dir
        self.data_dir = data_dir

    def __call__(self):
        command_line = ['sloccount',
                        '--datadir',
                        self.data_dir,
                        self.src_dir,
                       ]
        pipe = subprocess.Popen(command_line, shell=False,
                                stdout=subprocess.PIPE).stdout
        sloc = cost = None
        while True:
            line = pipe.readline()
            if not line:
                break
            if line.startswith(ZERO):
                return 0, 0
            if line.startswith(TOTAL_SLOC):
                sloc_str = line.rsplit('=', 1)[1].strip()
                sloc_str = sloc_str.replace(',', '')
                sloc = int(sloc_str)
            if line.startswith(TOTAL_COST):
                cost_str = line.rsplit('=', 1)[1].strip()
                if cost_str.startswith('$'):
                    cost_str = cost_str[1:].strip()
                cost_str = cost_str.replace(',', '')
                cost = int(cost_str)
        return sloc, cost

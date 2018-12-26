#!/usr/bin/env python2

import re
from datetime import datetime

def check_srt_file(filename):
    re_time = re.compile("([0-9:,]{10,12}) --> ([0-9:,]{10,12})")
    with open(filename) as fp:
        lineno = 0
        last_t2 = None
        for line in fp:
            lineno = lineno + 1
            match = re_time.search(line)
            if match:
                t1s = match.group(1)
                t2s = match.group(2)

                t1 = datetime.strptime(t1s, "%H:%M:%S,%f")
                t2 = datetime.strptime(t2s, "%H:%M:%S,%f")
                delta = (t2 - t1).total_seconds()
                if delta < 0:
                    print("%s:%s: Negative span: %d seconds" % (filename, lineno, delta))
                if delta > 10:
                    print("%s:%s: Too long: %d seconds" % (filename, lineno, delta))
                    
                if last_t2 and t1 < last_t2[0]:
                    print("%s:%s: Overlapped time span with line %d" % (filename, lineno, last_t2[1]))
                last_t2 = (t2, lineno)

                    
if __name__=="__main__":
    import sys
    for f in sys.argv[1:]:
        check_srt_file(f)

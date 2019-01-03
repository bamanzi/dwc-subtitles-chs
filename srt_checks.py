#!/usr/bin/env python2

import re
import sys
import logging
from datetime import datetime

def check_srt_file(filename):
    re_time = re.compile("([0-9:,]{10,12}) --> ([0-9:,]{10,12})")
    with open(filename) as fp:
        lineno = 0
        last_t2 = None
        last_line = None
        for line in fp:
            lineno = lineno + 1
            line = line.strip()
            
            if line.isdigit() and last_line!=None and len(last_line)>0:
                print("%s:%s: No blank line before entry index id" % (filename, lineno))
            else:
                match = re_time.search(line)
                if match:
                    t1s = match.group(1)
                    t2s = match.group(2)
                
                    try:
                        t1 = datetime.strptime(t1s, "%H:%M:%S,%f")
                        t2 = datetime.strptime(t2s, "%H:%M:%S,%f")
                    except:
                        logging.error("Error parsing datetime from %s:%d" % (filename, lineno), exc_info=True)
                        sys.exit(1)
                        
                    delta = (t2 - t1).total_seconds()
                    if delta < 0:
                        print("%s:%s: Negative span: %.1f seconds" % (filename, lineno, delta))
                    if delta > 10:
                        print("%s:%s: Too long: %d seconds" % (filename, lineno, delta))
                        
                    if last_t2 and t1 < last_t2[0]:
                        print("%s:%s: Overlapped time span with line %d" % (filename, lineno, last_t2[1]))
                    last_t2 = (t2, lineno)

            last_line = line

                    
if __name__=="__main__":
    for f in sys.argv[1:]:
        check_srt_file(f)

#!/usr/bin/env python3

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
        dialog = []
        
        for line in fp:
            lineno = lineno + 1
            line = line.strip()

            if line.isdigit(): # new entry starting

                if last_line!=None and len(last_line)>0: 
                    print("%s:%s: No blank line before entry index id" % (filename, lineno))
                if len(dialog)>2:
                    if not dialog[0].startswith('-'):
                        print("%s:%s: Too many dialog lines" % (filename, lineno-2))
                dialog = []  # clear
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
                    if delta < 0.0:
                        print("%s:%s: Negative span: %.1f seconds" % (filename, lineno, delta))
                    if delta > 6.0:
                        print("%s:%s: Time span too long: %.1f seconds" % (filename, lineno, delta))
                        
                    if last_t2 and t1 < last_t2[0]:
                        print("%s:%s: Overlapped time span with line %d" % (filename, lineno, last_t2[1]))
                    last_t2 = (t2, lineno)
                elif len(line)>0 and not line[0:2].isdigit(): # dialog line
                    dialog.append(line)
                    
                    if len(last_line)>0 and not last_line[0:2].isdigit():
                        len_last = len(last_line)
                        len_this = len(line)
                        len_total = len_last + len_this

                        if not _is_ascii(line):
                            if len_this>40:
                                print("%s:%s: Line too long: %d chars (non-ascii)" % (filename, lineno, len_this))

                            if not _is_ascii(last_line) and not last_line.startswith('<'):
                                print("%s:%s: Two non-ascii lines" % (filename, lineno))
                                
                        else:    
                            if len_this>75:
                                print("%s:%s: Line too long: %d chars" % (filename, lineno, len_this))
                        
                            if len_total<60 and (len_last<25 or len_this<25) and not line.startswith('-'):
                                print("%s:%s: Line too short: %d chars" % (filename, lineno, len_this))

            last_line = line

            
def _is_ascii(s):
    try:
        s.encode('cp1250')
        return True
    except UnicodeEncodeError:
        return False

if __name__=="__main__":
    for f in sys.argv[1:]:
        check_srt_file(f)

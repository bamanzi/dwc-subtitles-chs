#!/usr/bin/env python3

import re
import sys
import logging
from datetime import datetime

    
entry_id = 0
def print_entry(entry):
    global entry_id
    entry_id += 1

    assert(len(entry['dialog']) > 0)

    filename = entry['filename']
    lineno0 = entry['lineno']
    non_ascii_line_count = 0
    if len(entry['dialog'])==1:
        print("%s:%d:WARN: one line dialog (no translation?)" % (filename, lineno0+2), file=sys.stderr)
    else:
        for line in entry['dialog']:
            if not _is_ascii(line) and not line.startswith('<'):
                non_ascii_line_count += 1            
        if non_ascii_line_count>1:
            print("%s:%s:WARN: Too many non-ascii lines" % (filename, lineno0), file=sys.stderr)
        elif non_ascii_line_count==0:
            print("%s:%s:WARN: Translate missing" % (filename, lineno0), file=sys.stderr)
    
    print("%d" % entry_id)
    print("%s" % entry['timeline'])        
    for line in entry['dialog']:
        if line.startswith('<i') or _is_ascii(line):
            print('<font color="gray">%s</font>' % line)
        else:
            print(line)
    print('')
    
def main(filename):
    re_time = re.compile("([0-9:,]{10,12}) --> ([0-9:,]{10,12})")
    with open(filename) as fp:
        lineno = 0

        entry = None
        
        for line in fp:
            lineno = lineno + 1
            line = line.strip()

            if line.isdigit(): # new entry starting
                # print last entry
                if entry:
                    print_entry(entry)                
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
                    entry = {}
                    entry['starttime'] = t1
                    entry['endtime']   = t2
                    entry['timeline']  = line
                    entry['dialog']    = []
                    entry['filename']  = filename
                    entry['lineno']    = lineno - 1

                elif len(line)>0 and not line[0:2].isdigit(): # dialog line
                    entry['dialog'].append(line)
             
        print(entry)


def _is_ascii(s):
    try:
        s.encode('cp1250')
        return True
    except UnicodeEncodeError:
        return False

if __name__=="__main__":
    for f in sys.argv[1:]:
        main(f)

#!/usr/bin/env python2

from __future__ import print_function

import re
import sys
import logging

from datetime import datetime

def _is_ascii(s):
    try:
        s.encode('cp1250')
        return True
    except UnicodeEncodeError:
        return False


entry_id = 0
def print_entry(entry):
    dialog = entry['dialog']
    lineno0 = entry['lineno']
    filename = entry['filename']
    
    ascii_line_count = 0
    for line in entry['dialog']:
        if _is_ascii(line):
            ascii_line_count += 1
    if ascii_line_count==0:
        print("%s:%s:WARN: No ascii line" % (filename, lineno0), file=sys.stderr)
        return
    
    global entry_id
    entry_id += 1
    
    line_ts = entry['timeline']

    fpout= sys.stdout
    print("%d" % entry_id, file=fpout)
    print("%s" % line_ts,  file=fpout)
    for line in dialog:
        if _is_ascii(line):
            print("%s" % line, file=fpout)
    print("",              file=fpout)
    

def main(files):
  re_time = re.compile("([0-9:,]{10,12}) --> ([0-9:,]{10,12})")
  for filename in files:
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
             
        print_entry(entry)


if __name__=="__main__":
    if len(sys.argv)<2:
        print("Extract english part.")
        print("Usage: %s eng+chs.srt" % (sys.argv[0]))
    else:
        main(sys.argv[1:])

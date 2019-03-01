#!/usr/bin/env python3

import re
import sys
import logging
from datetime import datetime

def check_duration(entry, last_entry):

    t1 = entry['starttime']
    t2 = entry['endtime']
    lineno = entry['lineno']
    filename = entry['filename']
    
    delta = (t2 - t1).total_seconds()
    if delta < 0.0:
        print("%s:%s:ERROR: Negative span: %.2f seconds" % (filename, lineno, delta))
    if delta > 7.0:
        print("%s:%s:HINT: Time span too long:  %.2f seconds" % (filename, lineno, delta))
    if delta < 1.0:
        print("%s:%s:HINT: Time span too short: %.2f seconds" % (filename, lineno, delta))


def check_span_overlay(entry, last_entry):
    if not last_entry:
        return
    
    last_t2 = last_entry['endtime']
    t1 = entry['starttime']
    lineno = entry['lineno']
    filename = entry['filename']
    
    if last_t2 and t1 < last_t2:
        print("%s:%s:ERROR: Overlapped time span with line %d" % (filename, lineno, last_entry['lineno']))


def check_line_length(entry, last_entry):

    lineno0 = entry['lineno']
    filename = entry['filename']

    lineno = lineno0
    for line in entry['dialog']:
        lineno += 1

        len_this = len(line)
        if not _is_ascii(line):
            if len_this>40:
                print("%s:%s:HINT: Line too long: %d chars (non-ascii)" % (filename, lineno, len_this))
        
        else:
            if len_this>60:
                print("%s:%s:HINT: Line too long: %d chars " % (filename, lineno, len_this))

                #len_last = len(last_line)
                #len_this = len(line)
                #len_total = len_last + len_this
                #if len_total<60 and (len_last<40 or len_this<40) and not line.startswith('-'):
                #    print("%s:%s:HINT: Line too short: %d chars" % (filename, lineno, len_this))


def check_non_ascii_lines(entry, last_entry):
    lineno0 = entry['lineno']
    filename = entry['filename']
    if 'chs' not in filename:
        return

    non_ascii_line_count = 0
    lineno = lineno0
    
    for line in entry['dialog']:
        lineno += 1
        if not _is_ascii(line) and not line.startswith('<'):
            non_ascii_line_count += 1
    
    if non_ascii_line_count>1:
        print("%s:%s:WARN: Too many non-ascii lines" % (filename, lineno0))
    elif non_ascii_line_count==0:
        import pdb; pdb.set_trace()
        print("%s:%s:WARN: Translate missing" % (filename, lineno0))

    
def check_separator(entry, last_entry):
    pass
    

def main(filename):
    re_time = re.compile("([0-9:,]{10,12}) --> ([0-9:,]{10,12})")
    with open(filename) as fp:
        lineno = 0

        last_line = None
        entry = None
        last_entry = None
        
        for line in fp:
            lineno = lineno + 1
            line = line.strip()

            if line.isdigit(): # new entry starting

                if last_line!=None and len(last_line)>0:
                    print("%s:%s:ERROR: No blank line before entry index id" % (filename, lineno))

                else:
                    if entry:
                        checkers = [check_duration,
                                    check_span_overlay,
                                    check_line_length,
                                    check_non_ascii_lines,
                                    check_separator,
                                    ]
                        for checker in checkers:
                            checker(entry, last_entry)

                        last_entry = entry
                    entry = {}
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
                    entry['filename']  = filename
                    entry['dialog']    = []
                    entry['lineno']    = lineno
                elif len(line)>0 and not line[0:2].isdigit(): # dialog line
                    entry['dialog'].append(line)
             
            last_line = line


def _is_ascii(s):
    try:
        s.encode('cp1250')
        return True
    except UnicodeEncodeError:
        return False

if __name__=="__main__":
    for f in sys.argv[1:]:
        main(f)

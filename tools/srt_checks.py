#!/usr/bin/env python3

import re
import sys
import logging
from datetime import datetime

def check_duration(entry, last_entry):

    lineno = entry['lineno']
    filename = entry['filename']
    
    delta = entry['duration']
    if delta < 0.0:
        print("%s:%s:ERROR: Negative span: %.2f seconds" % (filename, lineno, delta))
    if delta > 7.0:
        print("%s:%s:HINT: Time span too long:  %.2f seconds" % (filename, lineno, delta))
    if delta < 0.6:
        print("%s:%s:HINT: Time span too short: %.2f seconds" % (filename, lineno, delta))

    if not last_entry: return
    
    delta_prev = last_entry['duration']
    sep = (entry['starttime'] - entry['endtime']).total_seconds()
    if (sep < 0.4) and (  ((delta < 0.8) and (delta_prev < 1.2))
                       or ((delta < 1.2) and (delta_prev < 0.8)) ):
        print("%s:%s:HINT: Condider merge with previous entry (two short enrites)" % (filename, lineno))


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
    last_line = None
    for line in entry['dialog']:
        lineno += 1

        len_this = len(line)
        if not _is_ascii(line):
            if len_this>40:
                print("%s:%s:HINT: Line too long: %d chars (non-ascii)" % (filename, lineno, len_this))
        
        else:
            if len_this>60:
                print("%s:%s:HINT: Line too long: %d chars " % (filename, lineno, len_this))

            if last_line:
                len_last = len(last_line)
                len_total = len_last + len_this
                if len_total<40 and not line.startswith('-'):  # and (len_last<40 or len_this<40)
                    print("%s:%s:HINT: Line too short: merge with last line? %d" % (filename, lineno, len_this))
        last_line = line


def check_non_ascii_lines(entry, last_entry):
    lineno0 = entry['lineno']
    filename = entry['filename']
    if 'chs' not in filename:
        return

    line_count_needs_trans = 0
    line_count_non_ascii = 0
    lineno = lineno0
    
    for line in entry['dialog']:
        lineno += 1
        if not line.startswith('<') and not line.startswith('('):
            if _is_ascii(line):
                line_count_needs_trans += 1
            else:
                line_count_non_ascii += 1
    
    if line_count_non_ascii>1:
        print("%s:%s:WARN: Too many non-ascii lines" % (filename, lineno0))
    elif (line_count_needs_trans >0) and (line_count_non_ascii==0):
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
                    entry['duration']  = (t2 - t1).total_seconds()
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

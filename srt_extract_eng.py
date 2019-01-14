#!/usr/bin/env python2

from __future__ import print_function

import re
import sys
import logging

from datetime import datetime


def locate_english_in_entries(entries, english):
    english1 = ''.join(english)
    english2 = ' '.join(english)
    for i in range(len(entries)):
        entry = entries[i]
        dialog = entry['dialog']  # to translate

        english_to_trans= dialog[0]
        if (english1 in english_to_trans) or (english2 in english_to_trans):
            return i

def merge_srt_files(filenames):
    re_time = re.compile("([0-9:,]{10,12}) --> ([0-9:,]{10,12})")

    #import pdb; pdb.set_trace()
    count = 0
    fpout = sys.stdout
    for filename in filenames:
      with open(filename) as fp:
        lineno = 0
        
        last_line = None
        entrystack = []
        for line in fp:
            lineno = lineno + 1
            line = line.strip()

            if line.isdigit() and last_line!=None and len(last_line)==0:
                # starting line for a new subtitle entry
                
                
                line_ts = entrystack[1]
                dialog = entrystack[2:]
                entrystack = [] #entrystack.clear()
                
                match = re_time.search(line_ts)
                if match:
                    count += 1
                    
                    t1s = match.group(1)
                    t2s = match.group(2)

                    try:
                        t1 = datetime.strptime(t1s, "%H:%M:%S,%f")
                        t2 = datetime.strptime(t2s, "%H:%M:%S,%f")
                    except:
                        logging.error("Error parsing datetime from %s:%d" % (filename, lineno), exc_info=True)
                        sys.exit(1)

                    chinese = dialog[-1]
                    english = dialog
                    if len(dialog)>1:
                        english = dialog[0:-1]
                    
                    print("%d" % (count+1),    file=fpout)
                    print("%s" % line_ts,  file=fpout)
                    for line in english:
                        print("%s" % line, file=fpout)
                    print("",              file=fpout)

            if line:
                entrystack.append(line)
                    
            last_line = line

                    
if __name__=="__main__":
    if len(sys.argv)<2:
        print("Extract english part.")
        print("Usage: %s eng+chs.srt" % (sys.argv[0]))
    else:
        merge_srt_files(sys.argv[1:])

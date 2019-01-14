#!/usr/bin/env python2

from __future__ import print_function

import re
import sys
import logging
import copy

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

def merge_srt_files(en_srt_file, trans_files):    
    re_time = re.compile("([0-9:,]{10,12}) --> ([0-9:,]{10,12})")

    filenames = copy.copy(trans_files)
    filenames.insert(0, en_srt_file)
    
    entries = []
    #import pdb; pdb.set_trace()
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
                    t1s = match.group(1)
                    t2s = match.group(2)

                    try:
                        t1 = datetime.strptime(t1s, "%H:%M:%S,%f")
                        t2 = datetime.strptime(t2s, "%H:%M:%S,%f")
                    except:
                        logging.error("Error parsing datetime from %s:%d" % (filename, lineno), exc_info=True)
                        sys.exit(1)
                    
                    entry = { 'start_time': t1,
                              'time_line' : line_ts,
                              'dialog'    : dialog,
                              'filename'  : filename }
                    if filename==filenames[0]:  #first file
                        entries.append(entry)
                    elif len(dialog)>1:
                        # translated entries

                        # TODO: auto-tell which line is english and which line is chinese
                        chinese = dialog[-1]
                            
                        idx = locate_english_in_entries(entries, dialog[0:-1])
                        if idx:
                            old_entry = entries[idx]
                            old_entry['dialog'].append(chinese)

            if line:
                entrystack.append(line)
            last_line = line

    # output merged subtitles
    #with open(target_file, 'w') as fp:
    fp = sys.stdout
    for i in range(len(entries)):
        entry = entries[i]

        print("%d" % (i+1),              file=fp)
        print("%s" % entry['time_line'], file=fp)
        for line in entry['dialog']:
            print("%s" % line,           file=fp)
        print("",                    file=fp)
        
                
                    
if __name__=="__main__":
    if len(sys.argv)<2:
        print("Extract translations (by english string), merge them to the timestamp of first file.")
        print("Usage: %s en.srt chs1.srt chs2.srt... " % (sys.argv[0]))
    else:
        merge_srt_files(sys.argv[1], sys.argv[2:])

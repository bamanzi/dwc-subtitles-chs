#!/usr/bin/env python2

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

        raw_english = dialog[0]
        if (english1 in raw_english) or (english2 in raw_english):
            return i

def merge_srt_files(filenames):    
    re_time = re.compile("([0-9:,]{10,12}) --> ([0-9:,]{10,12})")

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
                        chinese = dialog[0]
                            
                        idx = locate_english_in_entries(entries, dialog[1:])
                        if idx:
                            old_entry = entries[idx]
                            old_entry['dialog'].append(chinese)

            if line:
                entrystack.append(line)
            last_line = line

    # output merged subtitles
    for i in range(len(entries)):
        entry = entries[i]

        print("%d" % (i+1))
        print("%s" % entry['time_line'])
        for line in entry['dialog']:
            print("%s" % line)
        print("")
                   
                
                    
if __name__=="__main__":
    import sys
    if len(sys.argv)<3:
        print("Usage: merge two srt files.")
    else:
        merge_srt_files(sys.argv[1:])

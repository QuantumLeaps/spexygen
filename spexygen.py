#!/usr/bin/env python

#=============================================================================
# _Spexygen_ - Traceable Specifications Based on doxygen
# Copyright (C) 2023 Quantum Leaps, LLC. All rights reserved.
#
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Contact information:
# <www.state-machine.com>
# <info@state-machine.com>
#=============================================================================

'''
Spexygen is a Doxygen extension for creating traceable technical
specifications, such as:
- traceable requirement specifications
- traceable source code
- traceable tests
- traceable specifications of other kind
'''

import sys
import os
import json

def debug(*args, **kwargs):
    '''debug output (uncomment the print() inside for debugging)
    '''
    #print(*args, **kwargs)
    pass

class Spexygen:
    '''
    Spexygen class that encapsulates tracing and code generation
    '''

    # public class constants
    VERSION = 210

    LEVELS = ('', '  ', '    ', '      ', '        ')

    def __init__(self):
        # private members
        self._item = None          # current Item
        self._fname = ''           # current file name (for generating output)
        self._lnum = 0             # current linie number (for generating output)
        self._file = None          # current file (for generating output)
        self._prefix = ''          # prefix for each generated line
        self._bw_trace = ''        # bw-trace for current item requested
        self._item_trace_dict = {} # Item dictionary collected during tracing
        self._uid_brief_dict = {}  # UID-brief dictionary collected during tracing
        self._uid_traced_list = [] # UID list built during generation

    def on_file_pattern(self, fname):
        '''return True if file-name is acceptable for Spexygen
        '''
        return fname.endswith('.dox') or \
               fname.endswith('.h') or fname.endswith('.c') or \
               fname.endswith('.hpp') or fname.endswith('.cpp') or \
               fname.endswith('.py') or fname.endswith('.lnt')

    def on_gen_trace(self, level):
        '''recursively generate the forward trace for a "uid"
        from self._uid_traced_list[level]
        '''
        uid = self._uid_traced_list[level]
        debug("  self._uid_traced_list:", self._uid_traced_list)
        item_list = self._item_trace_dict.get(uid)
        for item in item_list:
            if item.uid not in self._uid_traced_list:
                self._file.write("%s%s- @tr{%s}: %s\n"
                    %(self._prefix, Spexygen.LEVELS[level], item.uid, item.brief))
                if level < len(Spexygen.LEVELS) - 2:
                    if item.uid in self._item_trace_dict:
                        self._uid_traced_list.append(item.uid)
                        self.on_gen_trace(level+1) # recursive!
                else:
                    self._file.write(f"{self._prefix}{Spexygen.LEVELS[level+1]}"\
                                     "- ...\n")
                    print(f"  {self._fname}:{self._lnum} too many"\
                          f' forward trace levels for "{item.uid}"')

    class Item:
        '''inner class for traceable items (a.k.a. "work artifacts")
        '''
        ITEM_DOC  = 0
        ITEM_CODE = 1
        def __init__(self, kind = ITEM_DOC, uid = None, brief = None):
            self.kind  = kind # kind of item (0 -> doc-item, 1 -> code-item)
            self.uid   = uid
            self.brief = brief
        def __repr__(self):
            if not self:
                return 'None'
            if self.kind == Spexygen.Item.ITEM_DOC:
                return f"ITEM_DOC {self.uid}: {self.brief}"
            if self.kind == Spexygen.Item.ITEM_CODE:
                return f"ITEM_CODE {self.uid}: {self.brief}"
            return f"ITEM_??? {self.uid}: {self.brief}"

    def uid_begin(self, line):
        '''set the current item 'self._item' if found in the given "line"'''
        if self._item:
            print("Looking for new UID while previous is still active",
                  f"{self._item.uid}")
        kind = Spexygen.Item.ITEM_DOC
        if (i := line.find('@uid{')) >= 0:
            l = 5
        elif (i := line.find('@code_uid{')) >= 0:
            kind = Spexygen.Item.ITEM_CODE
            l = 10
        elif (i := line.find('@code_alias{')) >= 0:
            kind = Spexygen.Item.ITEM_CODE
            l = 12
        else:
            return

        j = line.find(',', i + l)
        if j < 0:
            print("Error: missing ',' in UID definition",
                    "line", self._lnum, ":", i)
            return

        k = line.find('}', j + 1)
        if k < 0:
            print("Error: missing '}' in UID definition",
                    "line", self._lnum, ":", i)
            return

        self._item = self.Item(kind,
                               line[i + l:j].strip(), line[j + 1:k].strip())
        debug("  uid:", self._item)
        if self._item.uid not in self._uid_brief_dict:
            self._uid_brief_dict[self._item.uid] = self._item.brief

    def uid_end(self, line):
        '''return True if UID-end was found in the "line"
        '''
        if not self._item:
            print("Looking for UID-end while no UID active")
            return False

        if self._item.kind == Spexygen.Item.ITEM_DOC:
            if line.find('@enduid') >= 0:
                debug("  end:", self._item.uid)
                self._item = None
                self._bw_trace = ''
                return True
        elif self._item.kind == Spexygen.Item.ITEM_CODE:
            if line.find('@endcode_uid') >= 0:
                debug("  end:", self._item.uid)
                self._item = None
                self._bw_trace = ''
                return True
        else:
            print(f"Unknown current item kind={self._item.kind}")

        return False

    def uid_tr(self, line):
        '''return list of backward traces found in a given "line"
        '''
        tr_list = []
        i = 0
        while (i := line.find('@tr{', i)) >= 0:
            j = line.find('}', i + 4)
            if j >= 0:
                tr = line[i + 4:j]
                tr_list.append(tr)
                i = j
            else:
                print("Error: missing '}' for '@tr{' in line",
                      self._lnum, ":", i)
                break
        return tr_list

    def gen_bw_trace(self, line):
        '''find a bw-trace placeholder
        as long as bw-trace found
        return True if bw-trace placeholder or "@tr{}" found
        '''
        l = 0
        if (i := line.find('@uid_bw_trace')) >= 0:
            l = 13
        elif (i := line.find('@code_bw_trace')) >= 0:
            l = 14
        if i >= 0:
            if line.find('{', i+l) == i+l: # parameter present?
                j = line.find('}', i+l+1)
                if j >= 0:
                    self._bw_trace = line[i+l+1:j]
                else:
                    print("Error: missing '}' for '@uid_bw_trace{' in line",
                          self._lnum, ":", i+l+1)
            else:
                self._bw_trace = 'empty'
            self._file.write(line)
            return True

        if self._bw_trace != '':
            if (i := line.find('@tr{')) >= 0:
                j = line.find('}', i + 4)
                tr = ''
                if j >= 0:
                    tr = line[i + 4:j]
                else:
                    print("Error: missing '}' for '@tr{' in line",
                          self._lnum, ":", i)
                    self._file.write(line)
                    return True
                if self._bw_trace == 'brief' and tr in self._uid_brief_dict:
                    self._file.write(line[:j+1])
                    self._file.write(f": {self._uid_brief_dict[tr]}\n")
                    #self._file.write(line[j+2:])
                else:
                    self._file.write(line)
                return True
        return False


    def gen_fw_trace(self, line):
        '''find a fw-trace placeholder and generate fw-trace
        return True if the placeholder found
        '''
        if (i := line.find('@uid_fw_trace')) < 0:
            i = line.find('@code_fw_trace')
        if i < 0:
            return False # placeholder not found

        self._prefix = line[:i]
        self._file.write(line)
        if self._item.uid in self._item_trace_dict:
            self._uid_traced_list = [self._item.uid]
            self.on_gen_trace(0)
        else:
            print(f'  {self._fname}:{self._lnum} no forward trace'\
                  f' for UID: "{self._item.uid}"')

        return True

    def trace(self, fname):
        '''trace a given file and harvest the traces
        into the dictionaries: self._uid_brief_dict and self._item_trace_dict
        '''
        try:
            f = open(fname, encoding="utf-8")
        except OSError:
            print("File not found", fname)
            return
        with f:
            lines = f.readlines()

        print("Tracing:", fname)
        self._item = None
        self._lnum = 0
        for line in lines:
            self._lnum += 1
            if not self._item:
                self.uid_begin(line)
            else:
                if self.uid_end(line):
                    pass
                else:
                    tr_list = self.uid_tr(line)
                    for tr in tr_list:
                        if not self._item_trace_dict.get(tr):
                            self._item_trace_dict[tr] = []
                        if self._item.uid not in self._item_trace_dict[tr]:
                            self._item_trace_dict[tr].append(self._item)
                            debug(tr, '<-', self._item)

    def gen(self, gendir, fname):
        '''generate a given file, replacing the detected placeholdrs
        with information from the dictionaries:
        self._uid_brief_dict and self._item_trace_dict
        '''
        try:
            f = open(fname, encoding="utf-8")
        except OSError:
            print("File not found", fname)
            return
        with f:
            lines = f.readlines()

        self._fname = os.path.basename(fname)
        fname = gendir + '/' + self._fname
        try:
            self._file = open(fname, 'w', encoding="utf-8")
        except OSError:
            print("File cannot be written", fname)
            return
        with self._file:
            print("Generating:", fname)
            self._lnum = 0
            self._item = None
            self._bw_trace = ''
            for line in lines:
                self._lnum += 1
                if not self._item: # no current item
                    self._file.write(line)
                    self.uid_begin(line)
                else:              # have current item
                    if self.uid_end(line):
                        self._file.write(line)
                    elif self.gen_fw_trace(line):
                        pass
                    elif self.gen_bw_trace(line):
                        pass
                    else:
                        self._file.write(line)

    def main(self):
        '''main entry point to Spexygen
        process command-line arguments and run Spexygen
        '''
        print(f"Spexygen: traceable technical documentation system "\
            f"{self.VERSION//100}.{(self.VERSION//10) % 10}."\
            f"{self.VERSION % 10}")
        print("Copyright (c) 2005-2024 Quantum Leaps, www.state-machine.com\n")

        # defaults
        sfname = 'spex.json'
        gendir = 'spex'
        spexyinp = 'Spexyinput'

        # process command-line arguments...
        argv = sys.argv
        argc = len(argv)
        arg  = 1 # skip the 'Spexygen' argument

        if '-h' in argv or '--help' in argv or '?' in argv \
            or '--version' in argv:
            print("Usage: python Spexygen.py [spexyfile]",
                  "\n(deafult spexyfile: 'spexy.json')")
            sys.exit(0)

        if arg < argc:
            # is the next argument a test script?
            sfname = argv[arg]

        # parse the provided spexyfile as json data
        try:
            sfile = open(sfname, encoding="utf-8")
        except OSError:
            print("spexyfile not found:", sfname)
            sys.exit(-1)
        with sfile:
            try:
                spex = json.load(sfile)
            except ValueError as e:
                print("Error in spexyfile:", sfname)
                print(e)
                sys.exit(-1)

        # perform tracing
        key = 'trace'
        if key not in spex:
            key = 'gen' # no 'trace' section means use 'gen' section
        if key not in spex:
            print("Spexygen: nothing to do")
            return
        for path in spex[key]:
            if os.path.isfile(path):
                if self.on_file_pattern(path):
                    self.trace(path)
            elif os.path.isdir(path):
                for fname in os.listdir(path):
                    if self.on_file_pattern(fname):
                        self.trace(path + '/' + fname)
            else:
                print("not exist:", path)
        debug(self._item_trace_dict)
        debug(self._uid_brief_dict)

        key = 'gen-dir'
        if key in spex:
            gendir = spex[key]
        if gendir == '':
            print("No code generation (empty gen directory)")
            return

        key = 'gen-inc'
        if key in spex:
            spexyinp = spex[key]

        key = 'gen'
        geninc = None
        if key not in spex:
            print("Spexygen: nothing to generate")
            return

        if not os.path.exists(gendir):
            os.mkdir(gendir)
        if spexyinp != '':
            try:
                geninc = open(gendir + '/' + spexyinp, 'w',
                              encoding="utf-8")
            except OSError:
                print("spexyinp cannot be written:", spexyinp)
                sys.exit(-1)
        if geninc:
            geninc.write('INPUT +=')

        # generate documentation
        for path in spex[key]:
            if os.path.isfile(path):
                if self.on_file_pattern(path):
                    self.gen(gendir, path)
                    if geninc:
                        geninc.write(' \\\n' + gendir + '/'
                                     + os.path.basename(path))
            elif os.path.isdir(path):
                for fname in os.listdir(path):
                    if self.on_file_pattern(fname):
                        self.gen(gendir, path + '/' + fname)
                        if geninc:
                            geninc.write(' \\\n' + gendir + '/'
                                        + os.path.basename(fname))
            else:
                print("not exist:", path)

        if geninc:
            geninc.close()

#=============================================================================
if __name__ == "__main__":
    spx = Spexygen()
    spx.main()

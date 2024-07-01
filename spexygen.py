#!/usr/bin/env python

#=============================================================================
# Spexygen - Traceable Specifications Based on Doxygen
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
Spexygen - Traceable Specifications Based on Doxygen
A system for creating formal, *traceable* specifications based on Doxygen,
such as:
- functional safety specification
- requirements specification
- architecture specification
- design specification
- source code

Usage:
python spexygen.py [Spexyfile]
'''

import sys
import os
import json

VERSION = 200

UID_dict = {}

def file_pattern(fname):
    '''return Ture if 'fname' has the pattern accepted by Spexygen.'''
    return fname.endswith('.dox') or \
           fname.endswith('.h') or fname.endswith('.c') or \
           fname.endswith('.hpp') or fname.endswith('.cpp') or \
           fname.endswith('.py')

def gen_trace_fw(f, uid_list):
    '''generates (forward) trace from a ginven UID list'''
    for tr in uid_list:
        f.write('- @ref ' + tr + '\n')

def trace(fname):
    '''harvest tracing information from the file 'fname'
    fills the the global UID_dict with the referenced UIDs.'''
    try:
        f = open(fname, encoding="utf-8")
    except OSError:
        print("File not found", fname)
        return
    with f:
        lines = f.readlines()
    print("Tracing:", fname)
    uid = None
    n = 0
    for line in lines:
        n += 1
        if line.startswith('@uid{'):
            j = line.find(',')
            if j < 0:
                j = line.find('}')
            if j < 0:
                print("Error: missing ',' or '}' for '@uid{' in line", n)
                break
            uid = line[5:j]
        elif line.startswith('@enduid') or line.startswith('*/'):
            uid = None
        elif uid:
            i = 0
            while (i := line.find('@tr{', i)) > 0:
                j = line.find('}', i+4)
                if j > 0:
                    tr = line[i+4:j]
                    #print(tr, '<-', uid)
                    i = j
                    # update the gloabal UID dictionary
                    if not UID_dict.get(tr):
                        UID_dict[tr] = []
                    if uid not in UID_dict[tr]:
                        UID_dict[tr].append(uid)
                else:
                    print("Error: missing '}' for '@tr{' in line", n, "at", i)
                    break

def gen(gendir, fname):
    '''generate the file 'fname' mostly by copying lines as-is, but replacing
    the '@uid_fw_trace' or '@fw_trace' placeholders with the generated lists of UIDs.
    '''
    try:
        f = open(fname, encoding="utf-8")
    except OSError:
        print("File not found", fname)
        return
    with f:
        lines = f.readlines()

    fname = gendir + '/' + os.path.basename(fname)
    try:
        f = open(fname, 'w', encoding="utf-8")
    except OSError:
        print("File cannot be written", fname)
        return
    with f:
        print("Generating:", fname)
        n = 0
        uid = None
        for line in lines:
            n += 1
            write_line = True
            if line.startswith('@uid{'):
                j = line.find(',')
                if j < 0:
                    j = line.find('}')
                if j < 0:
                    print("Error: missing ',' or '}' for '@uid{' in line", n)
                    break
                uid = line[5:j]
            elif line.startswith('@enduid') or line.startswith('*/'):
                uid = None
            elif uid:
                if line.startswith('@uid_fw_trace') or line.startswith('@fw_trace'):
                    uid_list = UID_dict.get(uid)
                    if uid_list:
                        f.write(line)
                        gen_trace_fw(f, uid_list)
                    else:
                        print("empty forward trace list for UID", uid)
                    write_line = False

            if write_line:
                f.write(line)

#=============================================================================
# main entry point to QUTest
def main():
    '''main spexygen entry point
    '''

    # defaults
    sfname = 'spexygen.json'
    gendir = 'gen'
    doxyinc = 'doxyinc'

    # process command-line arguments...
    argv = sys.argv
    argc = len(argv)
    arg  = 1 # skip the "spexygen" argument

    if "-h" in argv or "--help" in argv or "?" in argv:
        print("\nUsage: python spexygen.py [spexyfile]")
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
    if key in spex:
        for path in spex[key]:
            if os.path.isfile(path):
                if file_pattern(path):
                    trace(path)
            elif os.path.isdir(path):
                for fname in os.listdir(path):
                    if file_pattern(fname):
                        trace(path + '/' + fname)
            else:
                print("not exist:", path)

    key = 'gen-dir'
    if key in spex:
        gendir = spex[key]
    if gendir == '':
        print("No code generation (empty gen directory)")
        return

    key = 'gen-inc'
    if key in spex:
        doxyinc = spex[key]

    key = 'gen'
    geninc = None
    if key not in spex:
        key = 'trace' # no gen section means use trace section

    if not os.path.exists(gendir):
        os.mkdir(gendir)
    if doxyinc != '':
        try:
            geninc = open(gendir + '/' + doxyinc, 'w',
                          encoding="utf-8")
        except OSError:
            print("Doxyinc cannot be written:", doxyinc)
            sys.exit(-1)
    if geninc:
        geninc.write('INPUT =')

    # generate documentation
    for path in spex[key]:
        if os.path.isfile(path):
            if file_pattern(path):
                gen(gendir, path)
                if geninc:
                    geninc.write(' \\\n' + gendir + '/'
                                 + os.path.basename(path))
        elif os.path.isdir(path):
            for fname in os.listdir(path):
                if file_pattern(fname):
                    gen(gendir, path + '/' + fname)
                    if geninc:
                        geninc.write(' \\\n' + gendir + '/'
                                    + os.path.basename(fname))
        else:
            print("not exist:", path)

    if geninc:
        geninc.close()

#=============================================================================
if __name__ == "__main__":
    print(f"\nSpexygen documentation system "\
        f"{VERSION//100}.{(VERSION//10) % 10}.{VERSION % 10}")
    print("Copyright (c) 2005-2024 Quantum Leaps, www.state-machine.com")
    main()

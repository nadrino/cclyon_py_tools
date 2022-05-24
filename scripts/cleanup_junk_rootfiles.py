#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GenericToolbox.ROOT as tROOT
import GenericToolbox.Colors as tColors
import GenericToolbox.IO as tIO

import sys
import os
from tqdm import tqdm

debug_mode = False

# READING PARAMETERS
for arg_id in range(len(sys.argv)):

    if sys.argv[arg_id] == "--debug" or sys.argv[arg_id] == "-debug":
        debug_mode = True


print(tColors.warning + "Looking for junk root files in ./*.root")
root_files_list = tIO.ls("./*.root")

for root_filepath in tqdm(root_files_list):
    if not tROOT.do_tfile_is_clean(root_filepath):
        print('rm ' + root_filepath)
        if not debug_mode:
            os.system('rm ' + root_filepath)

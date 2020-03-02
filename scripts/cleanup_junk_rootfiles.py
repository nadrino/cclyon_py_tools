#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import cclyon_toolbox_lib as toolbox_lib
import os

debug_mode = False

# READING PARAMETERS
for arg_id in range(len(sys.argv)):

    if sys.argv[arg_id] == "--debug" or sys.argv[arg_id] == "-debug":
        debug_mode = True

print(toolbox_lib.warning + "Looking for failed root files in ./")
root_files_list = toolbox_lib.ls("./*.root")

for root_filepath in root_files_list:
    if not toolbox_lib.do_tfile_is_clean(root_filepath):
        print('rm ' + root_filepath)
        if not debug_mode:
            os.system('rm ' + root_filepath)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import ruamel.yaml
import sys
sys.path.insert(0, "./lib")
import sc_toolbox

loop_parameters_file_lines = list()
loop_parameters_file_lines.append("# this variable is checked at the end of each server loop")
loop_parameters_file_lines.append("# if False, the server will not start again after a stop call.")
loop_parameters_file_lines.append("# False is set while the server is being backed up.")
loop_parameters_file_lines.append("loop_is_enabled: True")

yaml_file_stream = "\n".join(sc_toolbox.get_lines_list_of_file())

yaml_parser = ruamel.yaml.YAML()
yaml_data = yaml_parser.load()


date_str = time.strftime("%Y%m%d", time.gmtime())






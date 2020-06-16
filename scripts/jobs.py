#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import xml.etree.ElementTree as ET
import cclyon_toolbox_lib as toolbox

nb_job_running = 0
nb_job_submited = 0
nb_job_pending = 0

full_script_names = False
monitoring_mode = False
use_color = True

extra_args = list()

for arg_id in range(len(sys.argv)):
    if sys.argv[arg_id] == "-no-color":
        use_color = False
    if sys.argv[arg_id] == "--monitoring-mode":
        monitoring_mode = True
    if sys.argv[arg_id] == "--full-script-names":
        full_script_names = True
    elif arg_id != 0:
        extra_args.append(sys.argv[arg_id])

print("Extra arguments : " + str(extra_args))

os.system("qstat " + " ".join(extra_args) + " -xml > ${HOME}/qstat.xml")
HOME = os.getenv("HOME")

file_path = HOME + "/qstat.xml"
if not os.path.isfile(file_path):
    print(toolbox.error + file_path + " has not been found.")
    exit(1)

xml_tree = None
from xml.etree.ElementTree import ParseError
try:
    xml_tree = ET.parse(file_path)
except ParseError:
    print(toolbox.error + file_path + " could not be parsed.")
    exit(1)
xml_root = xml_tree.getroot()

red_color = ""
reset_color = ""
gold_color = ""
green_color = ""
if use_color:
    red_color = toolbox.red_color
    reset_color = toolbox.reset_color
    gold_color = toolbox.gold_color
    green_color = toolbox.green_color

terminal_width = toolbox.getTerminalSize()[0]
terminal_height = toolbox.getTerminalSize()[1]
nb_lines = 3 + 4
for child in xml_root:
    if child.tag == 'queue_info':
        for selected_job in child.findall('job_list'):
            nb_job_submited += 1
            nb_job_running += 1
    if child.tag == 'job_info':
        for selected_job in child.findall('job_list'):
            nb_job_submited += 1
            nb_job_pending += 1
print(red_color + "-> Number of remaining jobs : " + str(nb_job_submited) + reset_color)
print(red_color + "-> Number of running jobs : " + str(nb_job_running) + reset_color)
print(red_color + "-> Number of pending jobs : " + str(nb_job_pending) + reset_color)
print("To see the full script names add the option : --full-script-names")
header = True
separation_bar = ''
for child in xml_root:
    if child.tag == 'queue_info':
        for selected_job in child.findall('job_list'):
            if header:
                header_string = gold_color + "Job-id" + (
                        len(selected_job.find('JB_job_number').text) - len("Job-id")) * ' ' + "  |  "
                header_string += "Started at time" + (
                        len(selected_job.find('JAT_start_time').text) - len("Started at time")) * ' ' + "  |  "
                header_string += "State" + (len(selected_job.find('state').text) - len("State")) * ' ' + "  |  "
                header_string += "Slots" + (len(selected_job.find('slots').text) - len("Slots")) * ' ' + "  |  "
                header_string += "Script" + reset_color
                separation_bar = gold_color + terminal_width * '-' + reset_color
                print(separation_bar)
                print(header_string)
                print(separation_bar)
                header = False
            # nb_job_submited += 1
            # nb_job_running += 1
            color = green_color
            entry_string = color + selected_job.find('JB_job_number').text + (
                    len("Job-id") - len(selected_job.find('JB_job_number').text)) * ' ' + "  |  "
            entry_string += selected_job.find('JAT_start_time').text + (
                    len("Started at time") - len(selected_job.find('JAT_start_time').text)) * ' ' + "  |  "
            entry_string += selected_job.find('state').text + (
                    len("State") - len(selected_job.find('state').text)) * ' ' + "  |  "
            entry_string += selected_job.find('slots').text + (
                    len("Slots") - len(selected_job.find('slots').text)) * ' ' + "  |  "
            nb_char_remaining = terminal_width - (len(entry_string) - len(color))
            if not full_script_names and nb_char_remaining < len(selected_job.find('JB_name').text):
                entry_string += selected_job.find('JB_name').text[0:nb_char_remaining] + reset_color
            else:
                entry_string += selected_job.find('JB_name').text + reset_color
            if not monitoring_mode or (nb_lines + 1 <= terminal_height):
                print(entry_string)
                nb_lines += 1
header = True
for child in xml_root:
    if child.tag == 'job_info':
        for selected_job in child.findall('job_list'):
            if header:
                header_string = gold_color + "Job-id" + (
                        len(selected_job.find('JB_job_number').text) - len("Job-id")) * ' ' + "  |  "
                header_string += "State" + (len(selected_job.find('state').text) - len("State")) * ' ' + "  |  "
                header_string += "Slots" + (len(selected_job.find('slots').text) - len("Slots")) * ' ' + "  |  "
                header_string += "Script" + reset_color
                separation_bar = gold_color + terminal_width * '-' + reset_color
                print(separation_bar)
                print(header_string)
                print(separation_bar)
                header = False
            # nb_job_submited += 1
            # nb_job_pending += 1
            color = gold_color
            entry_string = color + selected_job.find('JB_job_number').text + (
                    len("Job-id") - len(selected_job.find('JB_job_number').text)) * ' ' + "  |  "
            entry_string += selected_job.find('state').text + (
                    len("State") - len(selected_job.find('state').text)) * ' ' + "  |  "
            entry_string += selected_job.find('slots').text + (
                    len("Slots") - len(selected_job.find('slots').text)) * ' ' + "  |  "
            nb_char_remaining = terminal_width - (len(entry_string) - len(color))
            if not full_script_names and nb_char_remaining < len(selected_job.find('JB_name').text):
                entry_string += selected_job.find('JB_name').text[0:nb_char_remaining] + reset_color
            else:
                entry_string += selected_job.find('JB_name').text + reset_color
            if not monitoring_mode or (nb_lines + 1 <= terminal_height):
                print(entry_string)
                nb_lines += 1

print(separation_bar)
print(red_color + "-> Number of remaining jobs : " + str(nb_job_submited) + reset_color)
print(red_color + "-> Number of running jobs : " + str(nb_job_running) + reset_color)
print(red_color + "-> Number of pending jobs : " + str(nb_job_pending) + reset_color)
print("To see the full script names add the option : --full-script-names")

os.system("rm ${HOME}/qstat.xml")

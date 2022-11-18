#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GenericToolbox.Colors as tColors
import GenericToolbox.IO as tIO

import os
import sys
import xml.etree.ElementTree as ET

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
    print(tColors.error + file_path + " has not been found.")
    exit(1)

xml_tree = None
try:
    xml_tree = ET.parse(file_path)
except ET.ParseError:
    print(tColors.error + file_path + " could not be parsed.")
    exit(1)
xml_root = xml_tree.getroot()

red_color = ""
reset_color = ""
gold_color = ""
green_color = ""
if use_color:
    red_color = tColors.redColor
    reset_color = tColors.resetColor
    gold_color = tColors.goldColor
    green_color = tColors.greenColor

terminal_width = tIO.getTerminalSize()[0]
terminal_height = tIO.getTerminalSize()[1]
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

runningJobTable = dict()
runningJobTable["Job-id"] = list()
runningJobTable["Started at time"] = list()
runningJobTable["State"] = list()
runningJobTable["Slots"] = list()
runningJobTable["Script name"] = list()

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

            if "Job-id" in runningJobTable:
                runningJobTable["Job-id"].append(selected_job.find('JB_job_number').text)
            if "Started at time" in runningJobTable:
                runningJobTable["Started at time"].append(selected_job.find('JAT_start_time').text)
            if "State" in runningJobTable:
                runningJobTable["State"].append(selected_job.find('state').text)
            if "Slots" in runningJobTable:
                runningJobTable["Slots"].append(selected_job.find('slots').text)
            if "Script name" in runningJobTable:
                runningJobTable["Script name"].append(selected_job.find('JB_name').text)

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


def generateTableStr(dict_):
    colWidthList = list()
    colKeyList = list()

    for title, values in dict_:
        colWidthList.append(len(title))
        colKeyList.append(title)
        for value in values:
            colWidthList[-1] = max(colWidthList[-1], len(value))

    colWidthList[-1] = \
        tIO.getTerminalSize()[0] \
        - sum(colWidthList[:-1]) \
        - 3 * (len(colWidthList) - 1) \
        - 1

    def getLine(separator_, contentList_=None):
        if contentList_ is None: contentList_ = list()
        out = ""

        for iCol in range(len(colWidthList)):
            if iCol != 0: out += " " + separator_ + " "
            if contentList_ is None:
                out += "─" * (colWidthList[iCol])
            else:
                out += contentList_[iCol].ljust(colWidthList[iCol], ' ')

        return out

    linesList = list()
    linesList.append(getLine("┬"))
    linesList.append(getLine("│", colKeyList))
    linesList.append(getLine("┼"))

    for key in colKeyList:
        linesList.append(getLine("│", dict_[key]))

    linesList.append(getLine("┴"))

    return linesList


print("\n".join(generateTableStr(runningJobTable)))

print(separation_bar)
print(red_color + "-> Number of remaining jobs : " + str(nb_job_submited) + reset_color)
print(red_color + "-> Number of running jobs : " + str(nb_job_running) + reset_color)
print(red_color + "-> Number of pending jobs : " + str(nb_job_pending) + reset_color)
print("To see the full script names add the option : --full-script-names")

os.system("rm ${HOME}/qstat.xml")

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time

import GenericToolbox.IO as tIO
import GenericToolbox.Colors as tColors
from GenericToolbox.CmdLineReader import CmdLineReader

cl = CmdLineReader()

cl.addOption("noColor", ["--no-color", "-no-color"], description_="Disable color display.", nbExpectedArgs_=0)
cl.addOption("monitoringMode", ["--monitoring-mode"], description_="Enable monitoring mode.", nbExpectedArgs_=0)
cl.addOption("fullScriptNames", ["--full-script-names"], description_="Display script full names.", nbExpectedArgs_=0)
cl.keepTailArgs = True

cl.printConfigSummary()
cl.readCommandLineArgs()

if len(cl.trailArgList) != 0:
    print(tColors.warning + "Extra arguments : " + " ".join(cl.trailArgList))

filePath = os.getenv("HOME") + "/squeue.json"
os.system("squeue --json " + " ".join(cl.trailArgList) + " > " + filePath)

if not os.path.isfile(filePath):
    print(tColors.error + filePath + " has not been found.")
    exit(1)

red_color = ""
reset_color = ""
gold_color = ""
green_color = ""
if not cl.isOptionTriggered("noColor"):
    red_color = tColors.redColor
    reset_color = tColors.resetColor
    gold_color = tColors.goldColor
    green_color = tColors.greenColor

terminal_width = tIO.getTerminalSize()[0]
terminal_height = tIO.getTerminalSize()[1]
nbLines = 3 + 4

data = json.load(open(filePath, 'r'))


nRunning = 0
nPending = 0
for job in data['jobs']:
    if job["job_state"] == "PENDING":
        nPending += 1
    if job["job_state"] == "RUNNING":
        nRunning += 1


print(red_color + "-> Number of remaining jobs : " + str(nRunning+nPending) + reset_color)
print(red_color + "-> Number of running jobs : " + str(nRunning) + reset_color)
print(red_color + "-> Number of pending jobs : " + str(nPending) + reset_color)
print("To see the full script names add the option : --full-script-names")

runningJobTable = dict()
runningJobTable["Job-id"] = list()
runningJobTable["Started at time"] = list()
runningJobTable["State"] = list()
runningJobTable["Slots"] = list()
runningJobTable["Script name"] = list()

header = True
separation_bar = ''
for job in data['jobs']:
    if job["job_state"] != "RUNNING": continue
    if header:
        header_string = gold_color + "Job-id" + (len(str(job["job_id"])) - len("Job-id")) * ' ' + "  |  "
        header_string += "Started at time" + (len(str(time.ctime(job["start_time"]))) - len("Started at time")) * ' ' + "  |  "
        header_string += "State" + (len(str(job["job_state"])) - len("State")) * ' ' + "  |  "
        header_string += "Slots" + (len(str(job["cpus"])) - len("Slots")) * ' ' + "  |  "
        header_string += "Script" + reset_color
        separation_bar = gold_color + terminal_width * '-' + reset_color
        print(separation_bar)
        print(header_string)
        print(separation_bar)
        header = False
    # nb_job_submited += 1
    # nb_job_running += 1

    if "Job-id" in runningJobTable:
        runningJobTable["Job-id"].append( job["job_id"] )
    if "Started at time" in runningJobTable:
        runningJobTable["Started at time"].append( job["start_time"] )
    if "State" in runningJobTable:
        runningJobTable["State"].append( job["job_state"] )
    if "Slots" in runningJobTable:
        runningJobTable["Slots"].append( job["cpus"] )
    if "Script name" in runningJobTable:
        runningJobTable["Script name"].append( job["name"] )

    color = green_color
    entry_string = color + str(job["job_id"]) + (len("Job-id") - len(str(job["job_id"]))) * ' ' + "  |  "
    entry_string += str(time.ctime(job["start_time"])) + (
            len("Started at time") - len(str(time.ctime(job["start_time"])))) * ' ' + "  |  "
    entry_string += str(job["job_state"]) + (
            len("State") - len(str(job["job_state"]))) * ' ' + "  |  "
    entry_string += str(job["cpus"]) + (
            len("Slots") - len(str(job["cpus"]))) * ' ' + "  |  "
    nb_char_remaining = terminal_width - (len(entry_string) - len(color))
    if not cl.isOptionTriggered("fullScriptNames") and nb_char_remaining < len(str(job["name"])):
        entry_string += str(job["name"])[0:nb_char_remaining] + reset_color
    else:
        entry_string += str(job["name"]) + reset_color
    if not cl.isOptionTriggered("monitoringMode") or (nbLines + 1 <= terminal_height):
        print(entry_string)
        nbLines += 1


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

print( runningJobTable )
print("\n".join(generateTableStr(runningJobTable)))


header = True
for job in data['jobs']:
    if job["job_state"] != "PENDING": continue
    if header:
        header_string = gold_color + "Job-id" + (
                len(str(job["job_id"])) - len("Job-id")) * ' ' + "  |  "
        header_string += "State" + (len(str(job["job_state"])) - len("State")) * ' ' + "  |  "
        header_string += "Slots" + (len(str(job["cpus"])) - len("Slots")) * ' ' + "  |  "
        header_string += "Script" + reset_color
        separation_bar = gold_color + terminal_width * '-' + reset_color
        print(separation_bar)
        print(header_string)
        print(separation_bar)
        header = False
    # nb_job_submited += 1
    # nb_job_pending += 1
    color = gold_color
    entry_string = color + str(job["job_id"]) + (
            len("Job-id") - len(str(job["job_id"]))) * ' ' + "  |  "
    entry_string += str(job["job_state"]) + (
            len("State") - len(str(job["job_state"]))) * ' ' + "  |  "
    entry_string += str(job["cpus"]) + (
            len("Slots") - len(str(job["cpus"]))) * ' ' + "  |  "
    nb_char_remaining = terminal_width - (len(entry_string) - len(color))
    if not cl.isOptionTriggered("fullScriptNames") and nb_char_remaining < len(str(job["name"])):
        entry_string += str(job["name"])[0:nb_char_remaining] + reset_color
    else:
        entry_string += str(job["name"]) + reset_color
    if not cl.isOptionTriggered("monitoringMode") or (nbLines + 1 <= terminal_height):
        print(entry_string)
        nbLines += 1

for job in data['jobs']:
    if job["job_state"] != "PENDING" or job["job_state"] != "RUNNING": continue
    if header:
        header_string = red_color + "Job-id" + (
                len(str(job["job_id"])) - len("Job-id")) * ' ' + "  |  "
        header_string += "State" + (len(str(job["job_state"])) - len("State")) * ' ' + "  |  "
        header_string += "Slots" + (len(str(job["cpus"])) - len("Slots")) * ' ' + "  |  "
        header_string += "Script" + reset_color
        separation_bar = red_color + terminal_width * '-' + reset_color
        print(separation_bar)
        print(header_string)
        print(separation_bar)
        header = False
    # nb_job_submited += 1
    # nb_job_pending += 1
    color = red_color
    entry_string = color + str(job["job_id"]) + (
            len("Job-id") - len(str(job["job_id"]))) * ' ' + "  |  "
    entry_string += str(job["job_state"]) + (
            len("State") - len(str(job["job_state"]))) * ' ' + "  |  "
    entry_string += str(job["cpus"]) + (
            len("Slots") - len(str(job["cpus"]))) * ' ' + "  |  "
    nb_char_remaining = terminal_width - (len(entry_string) - len(color))
    if not cl.isOptionTriggered("fullScriptNames") and nb_char_remaining < len(str(job["name"])):
        entry_string += str(job["name"])[0:nb_char_remaining] + reset_color
    else:
        entry_string += str(job["name"]) + reset_color
    if not cl.isOptionTriggered("monitoringMode") or (nbLines + 1 <= terminal_height):
        print(entry_string)
        nbLines += 1

print(separation_bar)
print(red_color + "-> Number of remaining jobs : " + str(nRunning+nPending) + reset_color)
print(red_color + "-> Number of running jobs : " + str(nRunning) + reset_color)
print(red_color + "-> Number of pending jobs : " + str(nPending) + reset_color)
print("To see the full script names add the option : --full-script-names")

os.system("rm "+filePath)

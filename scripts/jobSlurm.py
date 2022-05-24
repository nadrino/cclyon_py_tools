#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json

import GenericToolbox.IO as tIO
import GenericToolbox.Colors as tColors
from GenericToolbox.CmdLineReader import CommandLineReader

cl = CommandLineReader()

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





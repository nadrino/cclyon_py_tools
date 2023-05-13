#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import getpass
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

# if len(cl.trailArgList) != 0:
#     print(tColors.warning, "Extra arguments :", " ".join(cl.trailArgList))


redColor = ""
resetColor = ""
goldColor = ""
greenColor = ""
if not cl.isOptionTriggered("noColor"):
    redColor = tColors.redColor
    resetColor = tColors.resetColor
    goldColor = tColors.goldColor
    greenColor = tColors.greenColor

filePath = os.getenv("HOME") + "/squeue.json"
os.system("squeue -u $(whoami) --json > " + filePath)

if not os.path.isfile(filePath):
    print(tColors.error + filePath + " has not been found.")
    exit(1)


data = json.load(open(filePath, 'r'))

# nRunning = 0
# nPending = 0
# for job in data['jobs']:
#     if job["job_state"] == "PENDING":
#         nPending += 1
#     if job["job_state"] == "RUNNING":
#         nRunning += 1

jobDataMask = list()
jobDataMask.append("Start time")

runningJobTable = dict()
runningJobTable["Job-id"] = list()
runningJobTable["Start time"] = list()
runningJobTable["State"] = list()
runningJobTable["CPUs"] = list()
runningJobTable["Script name"] = list()

header = True
separation_bar = ''
for job in data['jobs']:
    if job['user_name'] != getpass.getuser():
        continue

    runningJobTable["Job-id"].append(job["job_id"])
    runningJobTable["State"].append(job["job_state"])
    if isinstance(job["cpus"], dict):
        runningJobTable["CPUs"].append(job["cpus"]["number"])
    else:
        runningJobTable["CPUs"].append(job["cpus"])
    runningJobTable["Script name"].append(job["name"])
    runningJobTable["Start time"].append("")
    if runningJobTable["State"][-1] == "RUNNING":
        runningJobTable["Start time"][-1] = str(time.ctime(job["start_time"]))

nRunning = 0
nPending = 0

def generateTableStr(dict_):
    colWidthList = list()
    colKeyList = list()
    nEntries = 0

    global nRunning
    global nPending

    for title, values in dict_.items():
        if title in jobDataMask: continue

        colWidthList.append(len(title))
        colKeyList.append(title)
        nEntries = len(values)
        for value in values:
            colWidthList[-1] = max(colWidthList[-1], len(str(value)))

    colWidthList[-1] = \
        tIO.getTerminalSize()[0] \
        - sum(colWidthList[:-1]) \
        - 3 * (len(colWidthList) - 1) \
        - 1

    def getLine(separator_, contentList_=None, color_=None):
        out = str()

        for iCol in range(len(colWidthList)):
            if contentList_ is None:
                if iCol != 0:
                    out += "─" + separator_ + "─"
                out += "─" * (colWidthList[iCol])
            else:
                if iCol != 0:
                    out += " " + separator_ + " "
                if not color_ is None:
                    out += color_
                if cl.isOptionTriggered("fullScriptNames"):
                    out += str(contentList_[iCol]).ljust(colWidthList[iCol], ' ')
                else:
                    out += str(contentList_[iCol]).ljust(colWidthList[iCol], ' ')[0:colWidthList[iCol]]
                out += resetColor

        return out

    linesList = list()
    linesList.append(getLine("┬"))
    linesList.append(getLine("│", colKeyList))
    linesList.append(getLine("┼"))

    for iJob in range(nEntries):
        entryColor = None

        lineContent = list()
        for key, values in dict_.items():
            if key in jobDataMask: continue

            if key == "State":
                if values[iJob] == "RUNNING":
                    nRunning += 1
                    entryColor = greenColor
                elif values[iJob] == "PENDING":
                    nPending += 1
                    entryColor = goldColor
            lineContent.append(values[iJob])

        linesList.append(getLine("│", lineContent, entryColor))

    linesList.append(getLine("┴"))

    return linesList

table = generateTableStr(runningJobTable)
docString = list()
docString.append(redColor + "-> Number of remaining jobs : " + str(nRunning + nPending) + resetColor)
docString.append(redColor + "-> Number of running jobs : " + str(nRunning) + resetColor)
docString.append(redColor + "-> Number of pending jobs : " + str(nPending) + resetColor)
docString.append("To see the full script names add the option : --full-script-names")

print("\n".join(docString))
print("\n".join(table))
print("\n".join(docString))

os.system("rm " + filePath)

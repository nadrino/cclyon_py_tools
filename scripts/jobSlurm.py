#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import json
import time
import subprocess
from datetime import datetime

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


redColor = ""
resetColor = ""
goldColor = ""
greenColor = ""
if not cl.isOptionTriggered("noColor"):
    redColor = tColors.redColor
    resetColor = tColors.resetColor
    goldColor = tColors.goldColor
    greenColor = tColors.greenColor


class JobInfo:
    def __init__(self):
        self.id = None
        self.state = None
        self.script = None
        self.duration = None
        self.nCpu = None
        self.since = None

    def sinceToStr(self):
        # Convert the Unix timestamp to a datetime object
        elapsed = datetime.now() - datetime.fromtimestamp(self.since)
        # Extract days, hours, minutes, and seconds from the time difference
        days = elapsed.days
        hours, remainder = divmod(elapsed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        out = str()
        if self.state == "RUNNING":
            out += "R:"
        else:
            out += "P:"

        out += f"{days}d"
        out += f"{hours:02}:"
        out += f"{minutes:02}:"
        out += f"{seconds:02}"
        return out


data = json.loads(
        subprocess.check_output("squeue -u $(whoami) --json", shell=True, text=True).strip()
    )

jobList = list()
# it still provides a list, but with more info
for job in data['jobs']:
    if job['user_name'] != getpass.getuser():
        continue

    jobList.append(JobInfo())
    jobList[-1].id = str(job['job_id'])
    jobList[-1].state = job['job_state'][0]
    jobList[-1].script = str(job["name"])

    if isinstance(job["cpus"], dict):
        jobList[-1].nCpu = job["cpus"]["number"]
    else:
        jobList[-1].nCpu = job["cpus"]

    if jobList[-1].state == "RUNNING":
        jobList[-1].since = job["start_time"]["number"]
    else:
        jobList[-1].since = job["submit_time"]["number"]

nRunning = 0
nPending = 0


def generateTableStr(jobList_):
    global nRunning
    global nPending

    outStrList = list()
    linesList = list() # list of columns
    colWidthList = list()

    def generateColList(job_):
        colList = list()
        if job_ is None:
            colList.append("ID")
            colList.append("N")
            colList.append("Since")
            colList.append("Script")
        else:
            colList.append(job_.id)
            colList.append(job_.nCpu)
            colList.append(job_.sinceToStr())
            colList.append(job_.script)
        return colList


    def maxWidth(colList_):
        if len(colWidthList) == 0:
            for col in colList_:
                colWidthList.append(0)
        for iCol in range(len(colList_)):
            colWidthList[iCol] = max(colWidthList[iCol], len(str(colList_[iCol])))

    linesList.append(generateColList(None))
    for job in jobList_:
        linesList.append(generateColList(job))

    print(linesList)
    for colList in linesList:
        maxWidth(colList)

    # regularise last line
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

    outStrList.append(getLine("┬"))
    isTitle = True
    for line in linesList:
        colorStr = None
        if line[2][0] == 'R':
            colorStr = greenColor
        if line[2][0] == 'P':
            colorStr = goldColor
        outStrList.append(getLine("│", line, colorStr))
        if isTitle:
            isTitle = False
            outStrList.append(getLine("┼"))
    outStrList.append(getLine("┴"))

    return outStrList

table = generateTableStr(jobList)
docString = list()
docString.append(redColor + "-> Number of remaining jobs : " + str(nRunning + nPending) + resetColor)
docString.append(redColor + "-> Number of running jobs : " + str(nRunning) + resetColor)
docString.append(redColor + "-> Number of pending jobs : " + str(nPending) + resetColor)
docString.append("To see the full script names add the option : --full-script-names")

print("\n".join(docString))
print("\n".join(table))
print("\n".join(docString))

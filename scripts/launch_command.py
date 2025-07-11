#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import glob

from GenericToolbox import IO as tIO
from GenericToolbox import Old as tOld
from GenericToolbox import Colors as tColors
from GenericToolbox import CmdLineReader

import os
import socket
import stat

# adjustable parameters?
maxRamPerCpu = 5  # GB
minRamPerJob = 8  # GB
maxRamPerJob = 63  # GB


def getJobMaxRamStr(nCores_):
  maxRam = min(maxRamPerCpu * nCores_, maxRamPerJob)
  maxRam = max(maxRam, minRamPerJob)
  return str(maxRam)


# Checking required env variables
WORK_DIR = tIO.get_env_variable("WORK_DIR")
JOBS_DIR = tIO.get_env_variable("JOBS_DIR")
RESULTS_DIR = tIO.get_env_variable("RESULTS_DIR")

executionFolder = os.getcwd()
groupName = "t2k"

print(tColors.redColor + "************** Launch command starts **************" + tColors.resetColor)

cl = CmdLineReader.CmdLineReader()
cl.addOption("nCores", ["-mc"], description_="Trigger multi-core queue and specify nb threads/slots", nbExpectedArgs_=1)
cl.addOption("debug", ["-debug"], description_="Trigger debug mode", nbExpectedArgs_=0)
cl.addOption("shortJob", ["-short"], description_="longlunch approx 2h", nbExpectedArgs_=0)
cl.addOption("longJob", ["-long"], description_="Long time jobs (72h instead of 24h)", nbExpectedArgs_=0)
cl.addOption("interactive", ["-interactive"], description_="Launch the generated script in interactive mode",
             nbExpectedArgs_=0)
cl.addOption("group", ["-g"], description_="Specify group", nbExpectedArgs_=1)

cl.keepTailArgs = True

cl.printConfigSummary()
cl.readCommandLineArgs()
cl.printTriggeredArgs()

if len(cl.trailArgList) == 0:
  print(tColors.error, "No command specified to be launched")
  exit(1)

if cl.isOptionTriggered("group"):
  groupName = cl.getOptionValues("group")[0]

# > Parsing parameters
cmdToJob = " ".join(cl.trailArgList)
print(tColors.greenColor + "Running command : " + tColors.resetColor + cmdToJob)
print(tColors.greenColor + "Running from : " + tColors.resetColor + executionFolder)

logFolder = JOBS_DIR + "/logs/" + cl.trailArgList[0].split("/")[-1] + "/"
scriptFolder = JOBS_DIR + "/scripts/" + cl.trailArgList[0].split("/")[-1] + "/"

# > Outfile names
duplicateInt = 0
outFilesBaseName = f"{tIO.getNowTimeString()}_{duplicateInt}"

# check if already exists
while len(glob.glob(f"{scriptFolder}/Script_{outFilesBaseName}*")) != 0:
  duplicateInt += 1
  outFilesBaseName = f"{tIO.getNowTimeString()}_{duplicateInt}"

for cmdArg in cl.trailArgList:
  argElement = cmdArg  # Copy string object
  argElement = argElement.replace("@", "X")  # Replacing special characters
  if argElement[0] != '-' or (argElement[0:2] == "--"):
    if "/" in argElement: argElement = argElement.split("/")[-1]
    if "." in argElement: argElement = argElement.split(".")[0]
    if len(argElement) > 20: argElement = ".." + argElement[-20:-1]
    outFilesBaseName += "_" + argElement

nCores = 1
if cl.isOptionTriggered("nCores"):
  nCores = int(cl.getOptionValues("nCores")[0])

if len(outFilesBaseName) > 200: outFilesBaseName = outFilesBaseName[0:200]
print(tColors.goldColor + "Output files base name : " + tColors.resetColor + outFilesBaseName)


tIO.mkdir(logFolder)
tIO.mkdir(scriptFolder)

envTransferCmd = str()
jobSubCmd = str()
executableScriptPath = scriptFolder + "/Script_" + outFilesBaseName + ".sh"
liveLogPath = f"{logFolder}/log_{outFilesBaseName}.log"
cmdForJob = f"{cmdToJob} &> {liveLogPath}"

if socket.gethostname().endswith('.cern.ch'):

  # executionFolder = executionFolder.replace("/eos/home-a/adblanch", "/afs/cern.ch/user/a/adblanch/eos")
  liveLogPath = f"{logFolder}/log_{outFilesBaseName}.log"
  tIO.mkdir(f"{logFolder}")
  # envTransferCmd = "source $HOME/.profile"
  cmdForJob = f"{cmdToJob} &> {liveLogPath}"

  JobFlavour = "workday"
  if cl.isOptionTriggered("shortJob"):
    JobFlavour = "longlunch"
  elif cl.isOptionTriggered("longJob"):
    JobFlavour = "testmatch"
  # espresso     = 20 minutes
  # microcentury = 1 hour
  # longlunch    = 2 hours
  # workday      = 8 hours
  # tomorrow     = 1 day
  # testmatch    = 3 days
  # nextweek     = 1 week

  condorSubFile = f"""
notify_user    = adrien.blanchet@cern.ch
notification   = Error
executable     = {executableScriptPath}
output         = {logFolder}/log_full_{outFilesBaseName}.out
error          = {logFolder}/log_full_{outFilesBaseName}.err
log            = {logFolder}/log_full_{outFilesBaseName}.log
request_cpus   = {nCores}
+JobFlavour    = {JobFlavour}
request_memory = {getJobMaxRamStr(nCores)}G
request_disk   = 10G
getenv         = True
queue
"""
  open(scriptFolder + "/Script_" + outFilesBaseName + ".sub", 'w').write(condorSubFile)

  jobSubCmd = f"cd $HOME && condor_submit {scriptFolder}/Script_{outFilesBaseName}.sub && cd -"
else:

  # > Preparing job script
  jobSubArgList = list()
  jobSubArgList.append("sbatch")

  if socket.gethostname().endswith('.baobab') or socket.gethostname().endswith('.yggdrasil'):
    jobSubArgList.append("--mail-user=adrien.blanchet@cern.ch")
    # looks like the maximum: https://doc.eresearch.unige.ch/hpc/slurm
    # sinfo
    if cl.isOptionTriggered("longJob"):
      jobSubArgList.append("-p private-dpnc-cpu")
      jobSubArgList.append("--time=48:00:00")
    else:
      jobSubArgList.append("-p shared-cpu")
      jobSubArgList.append("--time=12:00:00")
  else:
    # CCLYON
    jobSubArgList.append("-L sps")
    jobSubArgList.append("--account=" + groupName)
    jobSubArgList.append("--mail-user=adrien.blanchet@cern.ch")
    # https://doc.cc.in2p3.fr/fr/Computing/slurm/submit.html#sbatch-computing
    if cl.isOptionTriggered("longJob"):
      jobSubArgList.append("--time=72:00:00")
    else:
      jobSubArgList.append("--time=24:00:00")

  # jobSubArgList.append("-n " + str(nCores))
  jobSubArgList.append("-c " + str(nCores))

  jobSubArgList.append("--mem=" + getJobMaxRamStr(nCores) + "G")

  jobSubArgList.append("-o " + logFolder + "/log_full_" + outFilesBaseName + ".log")
  jobSubArgList.append("-e " + logFolder + "/log_full_" + outFilesBaseName + ".err")
  jobSubArgList.append(executableScriptPath)
  jobSubCmd = " ".join(jobSubArgList)

cmdBashScript = f"""#! /bin/bash

{envTransferCmd}

ulimit -c 0 # disable core dumps
echo cd {executionFolder}
cd {executionFolder}

echo '*******************************************************************'
echo COMPUTATION BEGINS
echo '*******************************************************************'

echo {cmdToJob}
{cmdForJob}

echo '*******************************************************************'
echo COMPUTATION FINISHED
echo '*******************************************************************'
"""
open(executableScriptPath, 'w').write(cmdBashScript)

open(liveLogPath, "w").write("")

# make the script executable
st = os.stat(executableScriptPath)
os.chmod(executableScriptPath, st.st_mode | stat.S_IEXEC)

print(f"{tColors.greenColor}Launch script writen as: {tColors.resetColor}{scriptFolder}/Script_{outFilesBaseName}.sh")
print(f"{tColors.greenColor}Job command: {tColors.resetColor}{jobSubCmd}")
print(f"{tColors.greenColor}Log path: {tColors.resetColor}{liveLogPath}")

# > Launching Job
if not cl.isOptionTriggered("debug"):
  if cl.isOptionTriggered("interactive"):
    os.system(cmdToJob)
  else:
    print(tColors.blueColor)
    os.system(jobSubCmd)
    print(tColors.resetColor)

# time.sleep(1)
print(tColors.redColor + "************** Launch command ended. **************" + tColors.resetColor)

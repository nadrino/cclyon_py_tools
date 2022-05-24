import GenericToolbox.Colors as tColors
from GenericToolbox.CmdLineReader import CommandLineReader

nCores = 1
cmdStr = ""

cl = CommandLineReader()


cl.addOption("nCores", ["--nb-cores", "-n"], description_="How many cores requested to the grid.", nbExpectedArgs_=1)

cl.keepTailArgs = True

cl.printConfigSummary()
cl.readCommandLineArgs()

if not cl.isOptionTriggered(""):
    print(tColors.error + "No command provided.")
    exit(0)
else:
    cmdStr = " ".join(cl.getOptionValues(""))
    print(tColors.info + "Command to send: " + cmdStr)

if cl.isOptionTriggered("nCores"): nCores = cl.getOptionValues("nCores")[0]

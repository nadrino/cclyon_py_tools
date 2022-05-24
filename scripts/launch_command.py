#!/usr/bin/env python
# -*- coding: utf-8 -*-

from GenericToolbox import IO as tIO
from GenericToolbox import Old as tOld
from GenericToolbox import Colors as tColors

import sys
import os

useSbatch = True

# Checking required env variables
WORK_DIR = tIO.get_env_variable("WORK_DIR")
JOBS_DIR = tIO.get_env_variable("JOBS_DIR")
RESULTS_DIR = tIO.get_env_variable("RESULTS_DIR")

parmeters_dict = dict()

parmeters_dict["command"] = ""
parmeters_dict["multithread-support"] = False
parmeters_dict["cpu_time"] = "47:59:59"
debug = False
mode = "job"
queue = "default"
here = True  # always true -> for now
command_arg_list = list()

queues_info = tOld.get_queues_info()
execution_folder = os.getcwd()
nb_slots = 1

print(tColors.redColor + "************** Launch command starts **************" + tColors.resetColor)

skip_next = True  # skip the first also
reading_command = False
for arg_id in range(len(sys.argv)):

    if skip_next:
        skip_next = False
        continue

    if not reading_command:
        if sys.argv[arg_id] == "-debug":
            debug = True
        elif sys.argv[arg_id] == "-interactive":
            mode = "interactive"
        # elif sys.argv[arg_id] == "-h":
        #     here = True
        #     execution_folder = os.getcwd()
        elif sys.argv[arg_id] == "-mc":
            parmeters_dict["multithread-support"] = True
            queue = "mc_long"
            nb_slots = int(sys.argv[arg_id + 1])
            skip_next = True
        elif sys.argv[arg_id] == "-q":
            queue = sys.argv[arg_id + 1]
            if queue not in queues_info:
                print(tColors.error + "Unknown queue : " + queue)
                for queue_name in queues_info:
                    print(tColors.error + "  - " + queue_name)
                exit(1)
            else:
                print(tColors.info + "Selected queue = " + queue)
                for queue_info in queues_info[queue]:
                    print(tColors.info + "  - " + queue_info + " : " + queues_info[queue][queue_info])
            skip_next = True
        else:
            reading_command = True
            command_arg_list.append(sys.argv[arg_id])
    else:
        command_arg_list.append(sys.argv[arg_id])
        # this last option have to be in both the command and the python script
        if sys.argv[arg_id] == "--multithread-support":
            parmeters_dict["multithread-support"] = True

if len(sys.argv) == 1 or len(command_arg_list) == 0:
    print(tColors.warning + "The following option have to be put before the command")
    print(tColors.warning + "-interactive : Launch script in prompt")
    print(tColors.warning + "-debug : verbose-only mode")
    print(tColors.warning + "-mc : Multicore preset (8cores + mc_long queue)")
    print(tColors.warning + "-h : Execute the command here, from the current directory")
    print(tColors.warning + "-q <name_of_the_queue> : Set specific queue")
    print(tColors.warning + "-c <number_of_cores> : Specify the number of slots")
    print(
        tColors.warning + "Example of usage : launch_command.py -mc -c 2 Erec_Tuning -it 13 -z-sampling-mode 5-Positions -MC-SVN r1777")
    sys.exit()

# > Parsing parameters
script_subfolder = "LaunchCommand"
script_names = command_arg_list[0].split("/")[-1]  # remove /bin/ etc...
parmeters_dict["command"] = " ".join(command_arg_list)
print(tColors.greenColor + "Launching Command : " + tColors.resetColor + parmeters_dict["command"])
print(tColors.greenColor + "Launching from : " + tColors.redColor + execution_folder)

out_filename_item_list = list()
for argument in command_arg_list:
    argument_str = str(argument)  # Copy string object
    argument_str = argument_str.replace("@", "X")  # Replacing special characters
    if argument_str[0] != '-' or (argument_str[0:2] == "--"):
        if "/" in argument_str:
            argument_str = argument_str.split("/")[-1]
        if "." in argument_str:
            argument_str = argument_str.split(".")[0]
        if len(argument_str) > 20:
            argument_str = ".." + argument_str[-20:-1]
        out_filename_item_list.append(argument_str)

out_files_base_name = tIO.getNowTimeString() + "_" + "_".join(out_filename_item_list)
if len(out_files_base_name) > 200: out_files_base_name = out_files_base_name[0:200]
print(tColors.goldColor + "Output files base name : " + tColors.resetColor + out_files_base_name)

this_python_script_path = os.path.dirname(os.path.realpath(__file__))
log_folder = JOBS_DIR + "/logs/" + command_arg_list[0] + "/"
script_reservoir_folder = JOBS_DIR + "/scripts/" + command_arg_list[0] + "/"

tIO.mkdir(log_folder)
tIO.mkdir(script_reservoir_folder)

if not here:
    execution_folder = RESULTS_DIR + "/" + script_names
    tIO.mkdir(execution_folder)

# > Preparing launch script
lauch_script_string = "#!/bin/bash\n"
lauch_script_string += "\n"
lauch_script_string += "echo cd " + execution_folder + "\n"
lauch_script_string += "cd " + execution_folder + "\n"
lauch_script_string += "\n"
lauch_script_string += "echo '*******************************************************************'\n"
lauch_script_string += "echo COMPUTATION BEGINS\n"
lauch_script_string += "echo '*******************************************************************'\n"
lauch_script_string += "echo " + parmeters_dict["command"] + "\n"
lauch_script_string += parmeters_dict["command"] + " &> " + log_folder + "/log_" + out_files_base_name + ".log \n"
lauch_script_string += "echo '*******************************************************************'\n"
lauch_script_string += "echo COMPUTATION FINISHED\n"
lauch_script_string += "echo '*******************************************************************'\n"

launch_file = open(script_reservoir_folder + "/Script_" + out_files_base_name + ".sh", 'w')
launch_file.write(lauch_script_string)  # python will convert \n to os.linesep
launch_file.close()  # you can omit in most cases as the destructor will call it
print(
    tColors.greenColor + "Launch script writen as : " + tColors.resetColor + script_reservoir_folder + "/Script_" + out_files_base_name + ".sh")

job_launch_command = ""
if useSbatch:
    # > Preparing job script
    job_command_arg_list = list()
    job_command_arg_list.append("sbatch")
    job_command_arg_list.append("-L sps")
    job_command_arg_list.append("-n " + str(nb_slots))
    job_command_arg_list.append("-o " + log_folder + "/log_full_" + out_files_base_name + ".log")
    job_command_arg_list.append("-e " + log_folder + "/log_full_" + out_files_base_name + ".err")
    job_command_arg_list.append("--mail-user=ablanche@lpnhe.in2p3.fr")
    job_command_arg_list.append(script_reservoir_folder + "/Script_" + out_files_base_name + ".sh")
    job_launch_command = " ".join(job_command_arg_list)

else:
    resources_declaration = list()
    # resources_declaration.append("xrootd=1")
    # resources_declaration.append("mysql=1")
    resources_declaration.append("sps=1")
    # resources_declaration.append("hpss=1")
    resources_declaration.append("ct=" + queues_info[queue]["max_cpu_time"])
    # resources_declaration.append("vmem=" + queues_info[queue]["max_virtual"])
    # resources_declaration.append("fsize=" + queues_info[queue]["max_file_size"])

    # > Preparing job script
    job_command_arg_list = list()
    job_command_arg_list.append("qsub")
    if queue != "default":
        job_command_arg_list.append("-q " + queue)
    job_command_arg_list.append("-l os=" + tIO.get_current_os())
    job_command_arg_list.append("-o " + log_folder + "/log_full_" + out_files_base_name + ".log")
    job_command_arg_list.append("-e " + log_folder + "/log_full_" + out_files_base_name + ".err")
    job_command_arg_list.append("-P P_t2k")
    if nb_slots != 1:
        job_command_arg_list.append("-pe multicores " + str(nb_slots))
    # job_command_arg_list.append("-l xrootd=1,mysql=1,sps=1,hpss=1,ct=" + parmeters_dict["cpu_time"] + ",vmem=4G,fsize=20G")
    job_command_arg_list.append("-l " + ",".join(resources_declaration))
    job_command_arg_list.append("-j y")
    job_command_arg_list.append(script_reservoir_folder + "/Script_" + out_files_base_name + ".sh")

    job_launch_command = " ".join(job_command_arg_list)

print(tColors.greenColor + "Job command : " + tColors.resetColor + job_launch_command)
print(tColors.greenColor + "Log path : " + tColors.resetColor + log_folder + "/log_" + out_files_base_name + ".log")

# > Launching Job
if not debug:
    if mode == "job":
        print(tColors.blueColor)
        os.system(job_launch_command)
        print(tColors.resetColor)
    elif mode == "interactive":
        os.system(parmeters_dict["command"])

# time.sleep(1)
print(tColors.redColor + "************** Launch command ended. **************" + tColors.resetColor)

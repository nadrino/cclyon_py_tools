#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cclyon_toolbox_lib as toolbox
import sys
import os

parameters_dict = dict()

is_dry_run = True
do_run_prompt = False
this_script_file_name = os.path.basename(__file__)
current_working_directory = os.getcwd()
now_time_string = toolbox.get_now_time_string()

parameters_dict["bash_script"] = ""
parameters_dict["multithread-support"] = False
parameters_dict["cpu_time"] = "47:59:59"

if os.getenv("JOBS_DIR") is None:
    print(toolbox.error + "$JOBS_DIR is not set.")
    sys.exit(1)

if len(sys.argv) == 1:
    print(toolbox.warning + "--multithread-support : Enables multi-thread support.")
    print(toolbox.warning + "--interactive : Launch the script on prompt.")
    print(toolbox.warning + "--dry-run : Make all the process but don't start the run.")
    print(toolbox.warning + "Example of usage : launch_bash_script.py ./test.sh --multithread-support")
    sys.exit(0)

print(toolbox.red_color +
      "************** " + str(parameters_dict["this_script_file_name"]) + " starts **************" +
      toolbox.reset_color)

for arg_id in range(len(sys.argv)):

    if sys.argv[arg_id] == "--dry-run":
        is_dry_run = True
        print(toolbox.warning + "Dry run enabled.")
    elif sys.argv[arg_id] == "--interactive":
        do_run_prompt = True
        print(toolbox.warning + "Script will be running interactively.")
    elif sys.argv[arg_id] == "--multithread-support":
        parameters_dict["multithread-support"] = True
    else:
        if arg_id >= 1:
            if parameters_dict["bash_script"] is not str():
                parameters_dict["bash_script"] += " "
            parameters_dict["bash_script"] += sys.argv[arg_id]


print(toolbox.info + "Selected bash script : " + parameters_dict["bash_script"].split(" ")[0])
if len(parameters_dict["bash_script"].split(" ")) > 1:
    print(toolbox.info + "Command line arguments : " + " ".join(parameters_dict["bash_script"].split(" ")[1:-1]))
print(toolbox.info + "The script will be launched from : " + current_working_directory)

logs_folder_path = os.getenv("JOBS_DIR") + "/logs/" + this_script_file_name + "/" + parameters_dict["bash_script"].split(" ")[0]
scripts_folder_path = os.getenv("JOBS_DIR") + "/scripts/" + this_script_file_name + "/" + parameters_dict["bash_script"].split(" ")[0]
toolbox.mkdir(logs_folder_path)
toolbox.mkdir(scripts_folder_path)

dynamic_log_file_path = logs_folder_path + "/" + now_time_string + ".log"
job_log_file_path = logs_folder_path + "/" + now_time_string + ".job.log"
job_err_file_path = logs_folder_path + "/" + now_time_string + ".job.err"
job_script_file_path = scripts_folder_path + "/" + now_time_string + ".sh"

launch_script_str =  "#! /bin/bash\n"
launch_script_str += "\n"
launch_script_str += "cd " + current_working_directory + "\n"
launch_script_str += "echo '*******************************************************************'\n"
launch_script_str += "echo COMPUTATION STARTED\n"
launch_script_str += "echo '*******************************************************************'\n"
launch_script_str += "echo \"/bin/bash " + parameters_dict["bash_script"] +"\"\n"
launch_script_str += "/bin/bash " + parameters_dict["bash_script"] + " &> " + dynamic_log_file_path + "\n"
launch_script_str += "echo '*******************************************************************'\n"
launch_script_str += "echo COMPUTATION ENDED\n"
launch_script_str += "echo '*******************************************************************'\n"

job_script_file = open(job_script_file_path, 'w')
job_script_file.write(launch_script_str)  # python will convert \n to os.linesep
job_script_file.close()  # you can omit in most cases as the destructor will call it

job_command_arg_list = list()
job_command_arg_list.append("qsub")
job_command_arg_list.append("-l os=" + toolbox.get_current_os())
job_command_arg_list.append("-o " + job_log_file_path)
job_command_arg_list.append("-e " + job_err_file_path)
job_command_arg_list.append("-P P_t2k")
if parameters_dict["multithread-support"]:
    job_command_arg_list.append("-pe multicores 8 -q mc_long")
job_command_arg_list.append("-l xrootd=1,mysql=1,sps=1,hpss=1,ct=" + parameters_dict["cpu_time"] + ",vmem=4G,fsize=20G")
job_command_arg_list.append("-j y")
job_command_arg_list.append(job_script_file_path)

job_launch_command = " ".join(job_command_arg_list)

if not is_dry_run:
    if not do_run_prompt:
        print(toolbox.blue_color)
        os.system(job_launch_command)
        print(toolbox.reset_color)
    else:
        os.system("/bin/bash " + parameters_dict["bash_script"])


print(toolbox.red_color +
      "************** " + str(parameters_dict["this_script_file_name"]) + " ended. **************" +
      toolbox.reset_color)
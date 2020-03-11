#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################


#################################################
# PROMPT COLORS
#################################################
reset = "\033[00m"
reset_color = "\033[00m"
gold_color = "\033[1;33m"
red_color = "\033[1;31m"
green_color = "\033[1;32m"
blue_color = "\033[1;34m"
purple_color = "\033[1;35m"

error = red_color + "<Error>" + reset_color + " "
info = green_color + "<Info>" + reset_color + " "
warning = gold_color + "<Warning>" + reset_color + " "
special = blue_color + "<Special>" + reset_color + " "
alert = purple_color + "<Alert>" + reset_color + " "

_verbosity_level_ = 0

last_displayed_value = -1

last_time = 0
delta_times_buffer = list()

#################################################
# FUNCTIONS
#################################################

# Display related tools
def display_loading(current_val=100, end_val=100, title='Percent:', bar_length=25):
    import sys
    import cclyon_toolbox_lib # import himself

    bar_length = 30

    if end_val == 0:
        end_val = 1

    percent = float(current_val) / end_val
    if cclyon_toolbox_lib.last_displayed_value == -1 or cclyon_toolbox_lib.last_displayed_value < int(round(percent * 100)):

        cclyon_toolbox_lib.last_displayed_value = int(round(percent * 100))

        remaining_time_str = str(int(float(get_mean_time_since_last_call())*(100-cclyon_toolbox_lib.last_displayed_value)/60.))
        text_width = len(title) + 1 + len(" / Remaining time : ") + len(remaining_time_str) + len(" min...")

        term_width = cclyon_toolbox_lib.getTerminalSize()[0]

        bar_do_fit = False
        progress_bar_str = ""
        while bar_length >= 0 and not bar_do_fit:
            hashes = '=' * int(round(percent * bar_length))
            spaces = ' ' * (bar_length - len(hashes))
            progress_bar_str = "[{0}] {1}%".format(hashes + spaces, cclyon_toolbox_lib.last_displayed_value)
            if term_width > text_width + len(progress_bar_str):
                bar_do_fit = True
            else:
                bar_length-=1

        if bar_length < 0:
            progress_bar_str = "{0}%".format(cclyon_toolbox_lib.last_displayed_value)

        print(gold_color + title + " " + progress_bar_str + " / Remaining time : " + remaining_time_str + " min..." + reset_color + "\r", end='')

    if percent == 100 or current_val == end_val-1:
        cclyon_toolbox_lib.last_displayed_value = -1
        print("")

# Booleans related tools
def do_env_variable_is_defined(env_variable_):
    import os
    return (env_variable_ in os.environ)

# Time related tools
def display_time_since_last_call(label_ = ""):

    delta_time = get_time_since_last_call()
    if delta_time != 0:
        if label_ == "":
            label_ = "Time since last call"
        print(alert + label_ + " : " + str(delta_time) + " s")
def get_time_since_last_call():
    import time, cclyon_toolbox_lib

    current_time = time.time()
    if cclyon_toolbox_lib.last_time != 0:
        delta_time = current_time - cclyon_toolbox_lib.last_time
    else:
        delta_time = 0
    cclyon_toolbox_lib.last_time = current_time
    return delta_time
def get_mean_time_since_last_call():
    import time, cclyon_toolbox_lib

    cclyon_toolbox_lib.delta_times_buffer.append(cclyon_toolbox_lib.get_time_since_last_call())
    if len(cclyon_toolbox_lib.delta_times_buffer) > 5:
        del cclyon_toolbox_lib.delta_times_buffer[0]

    return sum(cclyon_toolbox_lib.delta_times_buffer)/len(cclyon_toolbox_lib.delta_times_buffer)

# Shell related tools
def get_current_os():
    import os

    current_os = str()

    os_string = os.popen('lsb_release -si').read()
    os_string = os_string[:-1]

    if os_string == "Scientific":
        current_os = "sl6"
    elif os_string == "CentOS":
        current_os = "cl7"

    return current_os
def ls(input_path_):
    import os

    if input_path_[0] != '/':
        input_path_ = os.getcwd() + '/' + input_path_
    return os.popen('cd ' + os.getcwd() + ' && ls ' + input_path_).read().split('\n')[:-1]
def get_list_of_files_in_folder(input_folder_, extension_='', name_format_=''):
    import os

    files_list = list()
    input_folder_ = input_folder_.replace('\ ', ' ')

    for path, subdirs, files in os.walk(input_folder_):
        for name in files:
            file_path = os.path.join(path, name)
            if (extension_ == '' or file_path.split('.')[-1] == extension_) \
                    and (name_format_ == '' or name_format_ in file_path):
                files_list.append(file_path)

    return files_list
def getTerminalSize():
    import os

    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        ### Use get(key[, default]) instead of a try/catch
        #try:
        #    cr = (env['LINES'], env['COLUMNS'])
        #except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])
def mkdir(directory_path):
    import os

    if os.path.isdir(directory_path):
        pass
    elif os.path.isfile(directory_path):
        raise OSError("%s exists as a regular file." % directory_path)
    else:
        parent, directory = os.path.split(directory_path)
        if parent and not os.path.isdir(parent): mkdir(parent)
        if directory: os.mkdir(directory_path)
def get_env_variable(env_variable_):
    if not do_env_variable_is_defined(env_variable_):
        import sys
        print(error + "Environement variable has not been set : " + str(env_variable_))
        sys.exit(1)
    else:
        import os
        return os.environ.get(env_variable_)


# Generic related tools
def sort_list_human(list_):
    import re

    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        '''
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        '''
        return [atoi(c) for c in re.split(r'(\d+)', text)]

    list_.sort(key=natural_keys)
def get_quadratic_sum(val1_, val2_):
    from math import sqrt
    return sqrt(val1_ * val1_ + val2_ * val2_)

# ROOT related tools
def do_tfile_is_clean(input_tfile_path_, object_name_list_required_presence_=list(), look_for_valid_histograms_ = False):
    from ROOT import gErrorIgnoreLevel, kFatal, gROOT
    from ROOT import TFile, TH1, TH2, TH3
    from ROOT import nullptr

    old_verbosity = gErrorIgnoreLevel
    gROOT.ProcessLine("gErrorIgnoreLevel = " + str(kFatal) + ";")

    input_tfile = TFile.Open(input_tfile_path_, "READ")
    is_junk = False

    try:
        if input_tfile is None:
            is_junk = True
        elif input_tfile.IsZombie() or input_tfile.TestBit(TFile.kRecovered):
            is_junk = True
        else:
            for i_object in range(len(object_name_list_required_presence_)):
                object_handler = input_tfile.Get(object_name_list_required_presence_[i_object])
                if object_handler is None or object_handler == nullptr:
                    is_junk = True
                elif look_for_valid_histograms_:
                    try:
                        if not object_handler.InheritsFrom("TH1") and not object_handler.InheritsFrom("TH2") and not object_handler.InheritsFrom("TH3"):
                            is_junk = True
                        elif object_handler.GetMaximum() < object_handler.GetMinimum():
                            is_junk = True
                    except TypeError:
                        is_junk = True

                try:
                    object_handler.GetTitle()
                except ReferenceError:
                    is_junk = True

                if is_junk:
                    break
            input_tfile.Close()
    except ReferenceError:
        is_junk = True

    gROOT.ProcessLine("gErrorIgnoreLevel = " + str(old_verbosity) + ";")
    return not is_junk
def mkdir_cd_rootfile(root_file_, folder_path_):
    from ROOT import AddressOf

    try:
        AddressOf(root_file_.GetDirectory(folder_path_))
    except ValueError:
        root_file_.mkdir(folder_path_)

    root_file_.cd(folder_path_)
    return root_file_.GetDirectory(folder_path_)


def save_command_line_in_tfile(output_tfile_, command_line_):
    from ROOT import TNamed
    from ROOT import gDirectory

    current_directory = gDirectory
    mkdir_cd_rootfile(output_tfile_, "")
    TNamed("command_line_TNamed", command_line_).Write()
    current_directory.cd()


def get_now_time_string():
    import time
    return time.strftime("%Y%m%d_%H%M%S", time.gmtime())


def get_queues_info():
    queues_info = {'demon': {'host': '@multiseqs', 'access': 'demonqueue', 'max_cpu_time': '29:00:00', 'max_time': 'INFINITY', 'max_virtual': '32G', 'max_mem': '2G', 'max_file_size': '2G'}, 'huge': {'host': '@multiseqs', 'access': 'hugequeue', 'max_cpu_time': '72:00:00', 'max_time': '86:00:00', 'max_virtual': '32G', 'max_mem': '10G', 'max_file_size': '110G'}, 'interactive': {'host': '@interacts', 'access': ' ', 'max_cpu_time': '36:00:00', 'max_time': '36:00:00', 'max_virtual': '16G', 'max_mem': '3G', 'max_file_size': '500G'}, 'long': {'host': '@multiseqs', 'access': ' ', 'max_cpu_time': '48:00:00', 'max_time': '58:00:00', 'max_virtual': '16G', 'max_mem': '4G', 'max_file_size': '70G'}, 'longlasting': {'host': '@multiseqs', 'access': 'longlastingqueue', 'max_cpu_time': '168:00:00', 'max_time': '192:00:00', 'max_virtual': '16G', 'max_mem': '4G', 'max_file_size': '70G'}, 'mc_debug': {'host': '@mcdebug', 'access': 'mcdebugqueue', 'max_cpu_time': '05:00:00', 'max_time': '06:00:00', 'max_virtual': '32G', 'max_mem': '4G', 'max_file_size': '70G'}, 'mc_gpu_interactive': {'host': '@interactsgpu', 'access': ' ', 'max_cpu_time': '36:00:00', 'max_time': '36:00:00', 'max_virtual': 'INFINITY', 'max_mem': '16G', 'max_file_size': '250G'}, 'mc_gpu_long': {'host': '@gpu', 'access': 'gpuqueue', 'max_cpu_time': '48:00:00', 'max_time': '56:00:00', 'max_virtual': 'INFINITY', 'max_mem': '16G', 'max_file_size': '30G'}, 'mc_gpu_longlasting': {'host': '@gpu', 'access': 'longlastinggpuqueue', 'max_cpu_time': '202:00:00', 'max_time': '226:00:00', 'max_virtual': 'INFINITY', 'max_mem': '16G', 'max_file_size': '30G'}, 'mc_gpu_medium': {'host': '@gpu', 'access': 'gpuqueue,arusers', 'max_cpu_time': '05:00:00', 'max_time': '12:00:00', 'max_virtual': 'INFINITY', 'max_mem': '16G', 'max_file_size': '30G'}, 'mc_highmem_huge': {'host': '@highmem', 'access': 'mchighmemoryqueue', 'max_cpu_time': '144:00:00', 'max_time': '150:00:00', 'max_virtual': '2000G', 'max_mem': '500G', 'max_file_size': '1000G'}, 'mc_highmem_long': {'host': '@highmem', 'access': 'mchighmemoryqueue', 'max_cpu_time': '72:00:00', 'max_time': '72:00:00', 'max_virtual': '2000G', 'max_mem': '40G', 'max_file_size': '1000G'}, 'mc_huge': {'host': '@multiseqs', 'access': 'mchugequeue', 'max_cpu_time': '72:00:00', 'max_time': '86:00:00', 'max_virtual': '32G', 'max_mem': '8G', 'max_file_size': '70G'}, 'mc_interactive': {'host': '@interacts', 'access': ' ', 'max_cpu_time': '36:00:00', 'max_time': '36:00:00', 'max_virtual': '16G', 'max_mem': '3G', 'max_file_size': '500G'}, 'mc_long': {'host': '@multiseqs', 'access': 'mcqueue', 'max_cpu_time': '48:00:00', 'max_time': '58:00:00', 'max_virtual': '32G', 'max_mem': '3.6G', 'max_file_size': '70G'}, 'mc_longlasting': {'host': '@multiseqs', 'access': 'mclonglastingqueue', 'max_cpu_time': '202:00:00', 'max_time': '226:00:00', 'max_virtual': '16G', 'max_mem': '3G', 'max_file_size': '70G'}, 'pa_gpu_long': {'host': '@gpu', 'access': 'pagpuqueue', 'max_cpu_time': '48:00:00', 'max_time': '56:00:00', 'max_virtual': 'INFINITY', 'max_mem': '16G', 'max_file_size': '30G'}, 'pa_long': {'host': '@parallels', 'access': 'paqueue', 'max_cpu_time': '48:00:00', 'max_time': '58:00:00', 'max_virtual': '16G', 'max_mem': '3G', 'max_file_size': '30G'}, 'pa_longlasting': {'host': '@parallels', 'access': 'palonglastingqueue', 'max_cpu_time': '168:00:00', 'max_time': '192:00:00', 'max_virtual': '16G', 'max_mem': '3G', 'max_file_size': '30G'}, 'pa_medium': {'host': '@parallels', 'access': 'paqueue', 'max_cpu_time': '05:00:00', 'max_time': '12:00:00', 'max_virtual': '16G', 'max_mem': '3G', 'max_file_size': '30G'}}
    return queues_info
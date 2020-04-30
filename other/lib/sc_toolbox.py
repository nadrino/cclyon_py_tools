#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################


##################################################
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


def get_lines_list_of_file(file_path_):

    lines_list = list()
    with open(file_path_, 'r') as file:
        for line in file.readlines():
            lines_list.append(line)

    return lines_list

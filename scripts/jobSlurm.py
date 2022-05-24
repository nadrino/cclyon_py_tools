#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import GenericToolbox


HOME = os.getenv("HOME")
filePath = HOME + "/squeue.json"
os.system("squeue --json > " + filePath)



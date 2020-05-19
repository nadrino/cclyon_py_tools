#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import numpy
import math
from tqdm import tqdm
from array import array
from ROOT import gRandom
from ROOT import TFile
from ROOT import TNtupleD
from ROOT import TH2D
from ROOT import TF1
from ctypes import *
import cclyon_toolbox_lib as toolbox

parameters = dict()
parameters["nb_events"] = 100000
parameters["PRNG_seed"] = int(time.time())
parameters["nb_track_steps"] = 50
parameters["neutrino_spectra_file"] = "../output/atmospheric_neutrino_spectra.root"
parameters["PREM_file"] = "../output/PREM.root"
parameters["output_file"] = "../output/generated_neutrinos.root"
parameters["earth_radius"] = 6371 # in km
parameters["neutrino_altitude"] = 15 # in km
parameters["SK_area"] = 0.040*0.040 # in km^2 -> 40m x 40m

neutrino_names_list = list()
neutrino_names_list.append("numu")
neutrino_names_list.append("numubar")
neutrino_names_list.append("nue")
neutrino_names_list.append("nuebar")

neutrinos_PDG_codes = dict()
neutrinos_PDG_codes["numu"] = 14
neutrinos_PDG_codes["numubar"] = -14
neutrinos_PDG_codes["nue"] = 12
neutrinos_PDG_codes["nuebar"] = -12

print(toolbox.warning, "Opening file containing atmospheric neutrino spectra :", parameters["neutrino_spectra_file"])
neutrino_spectra_file = TFile.Open(parameters["neutrino_spectra_file"], "READ")
neutrino_spectra_dict = dict()
neutrino_type_threshold = dict()
neutrino_global_normalisation = 0.
for neutrino_name in neutrino_names_list:
    neutrino_spectra_dict[neutrino_name] = TH2D(neutrino_spectra_file.Get(neutrino_name))
    neutrino_type_threshold[neutrino_name] = neutrino_global_normalisation + neutrino_spectra_dict[neutrino_name].GetSum()
    neutrino_global_normalisation += neutrino_spectra_dict[neutrino_name].GetSum()

print(toolbox.warning, "Opening file containing PREM function :", parameters["PREM_file"])
PREM_file = TFile.Open(parameters["PREM_file"], "READ")
PREM_TF1 = TF1(PREM_file.Get("PREM_TF1"))

gRandom.SetSeed(parameters["PRNG_seed"]) # set the generator seed for TH2D.GetRandom2

variables_names_list = list()

# saved variables
variables_names_list.append("PDG_code")          # sampled by the norm of each spectrum
variables_names_list.append("E_nu")              # sampled by the spectrum

variables_names_list.append("R_Earth_emitted")   # determined by neutrino_altitude and earth radius
variables_names_list.append("R_SK_emitted")      # computed

variables_names_list.append("cos_theta_SK")      # sampled by the spectrum
variables_names_list.append("cos_theta_Earth")   # computed

variables_names_list.append("phi")               # sampled

variables_names_list.append("SK_solid_angle_at_emission")    # computed

variables_names_list.append("averaged_matter_density")    # computed

nb_saved_variables = len(variables_names_list)

# unsaved variables (useful vars to compute others but not tracked)
variables_names_list.append("delta_R_SK")
variables_names_list.append("R_SK_step")
variables_names_list.append("R_Earth_step")

# all variables are stored in this event container array. This will prevent python to reallocate doubles at each loop
event_container = array("d", numpy.zeros((len(variables_names_list),), dtype=float))

print(toolbox.info, "Output file will be writen in", parameters["output_file"])
output_file = TFile.Open(parameters["output_file"], "RECREATE")
output_file.cd()
output_ntuple = TNtupleD("neutrino_tracks", "neutrino_tracks", (":".join(variables_names_list[0:nb_saved_variables])))

event_container[variables_names_list.index("R_Earth_emitted")] = parameters["earth_radius"] + parameters["neutrino_altitude"]
energy = c_double()
c_theta = c_double()

print(toolbox.info, "Generating neutrino tracks...")
for i_event in tqdm(range(parameters["nb_events"])):

    # sampling neutrino type, then sample energy / cos_theta
    random_number = gRandom.Rndm()*neutrino_global_normalisation
    for neutrino_name in neutrino_names_list:
        if random_number < neutrino_type_threshold[neutrino_name]:
            event_container[variables_names_list.index("PDG_code")] = neutrinos_PDG_codes[neutrino_name]
            neutrino_spectra_dict[neutrino_name].GetRandom2(
                energy,
                c_theta
            )
            break
    event_container[variables_names_list.index("E_nu")] = energy.value
    event_container[variables_names_list.index("cos_theta_SK")] = c_theta.value
    event_container[variables_names_list.index("phi")] = gRandom.Rndm()*2*math.pi

    # calculations
    event_container[variables_names_list.index("delta_R_SK")] = 4
    event_container[variables_names_list.index("delta_R_SK")] *= \
        ( event_container[variables_names_list.index("R_Earth_emitted")]**2 ) + \
        ( parameters["earth_radius"]**2 ) * ( -1 + (event_container[variables_names_list.index("cos_theta_SK")]**2) )
    event_container[variables_names_list.index("R_SK_emitted")] = - parameters["earth_radius"]*event_container[variables_names_list.index("cos_theta_SK")]
    event_container[variables_names_list.index("R_SK_emitted")] += 0.5*math.sqrt(event_container[variables_names_list.index("delta_R_SK")])

    event_container[variables_names_list.index("cos_theta_Earth")] = parameters["earth_radius"]
    event_container[variables_names_list.index("cos_theta_Earth")] += event_container[variables_names_list.index("R_SK_emitted")]*event_container[variables_names_list.index("cos_theta_SK")]
    event_container[variables_names_list.index("cos_theta_Earth")] /= event_container[variables_names_list.index("R_Earth_emitted")]

    event_container[variables_names_list.index("SK_solid_angle_at_emission")] = parameters["SK_area"]/(event_container[variables_names_list.index("R_SK_emitted")]**2)

    event_container[variables_names_list.index("averaged_matter_density")] = 0.
    for i_step in range(parameters["nb_track_steps"]):
        event_container[variables_names_list.index("R_SK_step")] = event_container[variables_names_list.index("R_SK_emitted")]
        event_container[variables_names_list.index("R_SK_step")] -= i_step*event_container[variables_names_list.index("R_SK_emitted")]/parameters["nb_track_steps"]

        event_container[variables_names_list.index("R_Earth_step")] = event_container[variables_names_list.index("R_SK_step")]**2
        event_container[variables_names_list.index("R_Earth_step")] += parameters["earth_radius"]**2
        event_container[variables_names_list.index("R_Earth_step")] += 2*parameters["earth_radius"]*\
                                                                       event_container[variables_names_list.index("R_SK_step")]*\
                                                                       event_container[variables_names_list.index("cos_theta_SK")]
        event_container[variables_names_list.index("R_Earth_step")] = math.sqrt(event_container[variables_names_list.index("R_Earth_step")])

        event_container[variables_names_list.index("averaged_matter_density")] += PREM_TF1.Eval(event_container[variables_names_list.index("R_Earth_step")])

    event_container[variables_names_list.index("averaged_matter_density")] /= parameters["nb_track_steps"]

    output_ntuple.Fill(event_container[0:nb_saved_variables])


output_file.cd()
output_ntuple.GetTree().Write()
output_file.Close()

print(toolbox.info, "Output file writen in", parameters["output_file"])
print(toolbox.info, "Process ended successfully.")
exit(0)
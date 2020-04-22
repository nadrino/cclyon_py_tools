#!/usr/bin/env python
# -*- coding: utf-8 -*-

from array import array
from ROOT import TH2D
from ROOT import TFile
import cclyon_toolbox_lib as toolbox

spectrum_file_path = "./data/kam-ally-20-01-mtn-solmin.d.gz" # with mountain + average on phi
output_file_path = "../output/atmospheric_neutrino_spectra.root"

cos_z_lower_bin_edges = list()
energy_lower_bin_edges = list()
value_labels = dict()

histogram_names_list = list()
histogram_names_list.append("nu_mu")
histogram_names_list.append("nu_mu_bar")
histogram_names_list.append("nu_e")
histogram_names_list.append("nu_e_bar")
histograms_dict = dict()


print(toolbox.info, "Opening input data file :", spectrum_file_path)
with open(spectrum_file_path, 'r') as spectrum_file:

    lines = spectrum_file.readlines()

    # checking the binning
    print(toolbox.warning, "Looking for the correct binning...")
    e_bin_has_been_filled = False
    for line in lines:
        # header check
        if line.split(' ')[0] == "average":
            # then it's a new bin in coz / phi_Az
            cos_z_bin_bounds = line.split('[')[1].split(']')[0].split(',')[0].split('=')[1].split('--')
            cos_z_bin_bounds = [bound.replace(' ','') for bound in cos_z_bin_bounds]
            cos_z_bin_bounds = list(map(float, cos_z_bin_bounds))
            cos_z_lower_bin_edges.append(cos_z_bin_bounds[1])
        else:
            values_cols = list( filter(None, line.split(' ')) )
            if not e_bin_has_been_filled:
                try:
                    float(values_cols[0]) # test
                    energy_lower_bin_edges.append(float(values_cols[0]))
                except ValueError:
                    # is header
                    if len(energy_lower_bin_edges):
                        # then it's already filled up.
                        e_bin_has_been_filled = True
                    pass

    # add one extra bin edge
    energy_lower_bin_edges.append(energy_lower_bin_edges[-1]*2 - energy_lower_bin_edges[-2])
    cos_z_lower_bin_edges.append(cos_z_lower_bin_edges[-1]*2 - cos_z_lower_bin_edges[-2])

    cos_z_lower_bin_edges = sorted(cos_z_lower_bin_edges)

    # print(energy_lower_bin_edges)
    # print(cos_z_lower_bin_edges)

    cos_z_lower_bin_edges_array = array('d', cos_z_lower_bin_edges)
    energy_lower_bin_edges_array = array('d', energy_lower_bin_edges)

    print(toolbox.info + "Output file will be writen at", output_file_path)
    output_tfile = TFile.Open(output_file_path, "RECREATE")
    for histogram_name in histogram_names_list:
        histograms_dict[histogram_name] = TH2D(histogram_name, histogram_name,
                                        len(energy_lower_bin_edges) - 1, energy_lower_bin_edges_array,
                                        len(cos_z_lower_bin_edges) - 1, cos_z_lower_bin_edges_array)
        histograms_dict[histogram_name].GetXaxis().SetTitle("E_{#nu} (GeV)")
        histograms_dict[histogram_name].GetYaxis().SetTitle("cos(#theta_{z})")
        histograms_dict[histogram_name].GetZaxis().SetTitle("Neutrino Flux (m^{2}.s.sr.GeV)^{-1}")

    # now reading the data
    print(toolbox.warning, "Now filling the histograms...")
    current_cos_z = -2
    current_energy = -1
    for line in lines:

        if line.split(' ')[0] == "average":
            # then it's a new bin in coz / phi_Az
            cos_z_bin_bounds = line.split('[')[1].split(']')[0].split(',')[0].split('=')[1].split('--')
            cos_z_bin_bounds = [bound.replace(' ','') for bound in cos_z_bin_bounds]
            cos_z_bin_bounds = list(map(float, cos_z_bin_bounds))
            current_cos_z = sum(cos_z_bin_bounds)/len(cos_z_bin_bounds)
        else:
            values_cols = list( filter(None, line.split(' ')) )
            try:
                current_energy = float(values_cols[0])  # test
                # if it passes -> we handle values
                current_energy *= (1.0001)  # make sure to be in the wanted bin
                current_flux = dict()
                for i_value in range(len(values_cols) - 1):
                    current_flux[histogram_names_list[i_value]] = values_cols[i_value + 1]
                for histogram_name in histogram_names_list:
                    histograms_dict[histogram_name].Fill(current_energy, current_cos_z, float(current_flux[histogram_name]))
            except ValueError:
                # is header
                pass

    print(toolbox.warning, "Writing histograms in the output file...")
    output_tfile.cd()
    for histogram_name in histogram_names_list:
        histograms_dict[histogram_name].Write()
    output_tfile.Close()

print(toolbox.info, "Process ended successfully.")
exit(0)















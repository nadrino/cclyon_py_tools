#!/usr/bin/env python
# -*- coding: utf-8 -*-

from array import array
from ROOT import TH2D
from ROOT import TFile
from ROOT import TF1
import cclyon_toolbox_lib as toolbox

spectrum_file_path = "./data/kam-ally-20-01-mtn-solmin.d.gz" # with mountain + average on phi
output_file_path = "../output/atmospheric_neutrino_spectra.root"

cos_z_lower_bin_edges = list()
energy_lower_bin_edges = list()
value_labels = dict()

histogram_names_list = list()
histogram_names_list.append("numu")
histogram_names_list.append("numubar")
histogram_names_list.append("nue")
histogram_names_list.append("nuebar")
histograms_dict = dict()
histograms_L_dict = dict()


# event_container[variables_names_list.index("R_Earth_emitted")] = parameters["earth_radius"] + parameters["neutrino_altitude"]
# event_container[variables_names_list.index("delta_R_SK")] = 4
# event_container[variables_names_list.index("delta_R_SK")] *= \
#   ( event_container[variables_names_list.index("R_Earth_emitted")]**2 ) + \
#   ( parameters["earth_radius"]**2 ) * ( -1 + (event_container[variables_names_list.index("cos_theta_SK")]**2) )
# event_container[variables_names_list.index("R_SK_emitted")] = - parameters["earth_radius"]*event_container[variables_names_list.index("cos_theta_SK")]
# event_container[variables_names_list.index("R_SK_emitted")] += 0.5*math.sqrt(event_container[variables_names_list.index("delta_R_SK")])


def compute_propagation_length(cos_theta_SK_):
    from math import sqrt

    R_SK_emitted = 0

    earth_radius = 6371.
    neutrino_altitude = 15.

    R_Earth_emitted = earth_radius + neutrino_altitude

    delta_R_SK = 4
    delta_R_SK *= \
        ( R_Earth_emitted**2 ) + \
        ( earth_radius**2 ) * ( -1 + (cos_theta_SK_**2) )
    R_SK_emitted = - earth_radius*cos_theta_SK_
    R_SK_emitted += 0.5*sqrt(delta_R_SK)

    return R_SK_emitted


prop_length_bin_edges = list()

print(tColors.info, "Opening input data file :", spectrum_file_path)
with open(spectrum_file_path, 'r') as spectrum_file:

    lines = spectrum_file.readlines()

    # checking the binning
    print(tColors.warning, "Looking for the correct binning...")
    e_bin_has_been_filled = False
    for line in lines:
        # header check
        if line.split(' ')[0] == "average":
            # then it's a new bin in coz / phi_Az
            cos_z_bin_bounds = line.split('[')[1].split(']')[0].split(',')[0].split('=')[1].split('--')
            cos_z_bin_bounds = [bound.replace(' ','') for bound in cos_z_bin_bounds]
            cos_z_bin_bounds = list(map(float, cos_z_bin_bounds))
            cos_z_lower_bin_edges.append(cos_z_bin_bounds[1])
            prop_length_bin_edges.append(compute_propagation_length(cos_z_lower_bin_edges[-1]))
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
    prop_length_bin_edges.append(compute_propagation_length(cos_z_lower_bin_edges[-1]))

    cos_z_lower_bin_edges = sorted(cos_z_lower_bin_edges)
    prop_length_bin_edges = sorted(prop_length_bin_edges)

    # print(energy_lower_bin_edges)
    # print(cos_z_lower_bin_edges)

    cos_z_lower_bin_edges_array = array('d', cos_z_lower_bin_edges)
    prop_length_bin_edges_array = array('d', prop_length_bin_edges)
    energy_lower_bin_edges_array = array('d', energy_lower_bin_edges)

    print(prop_length_bin_edges_array)

    print(tColors.info + "Output file will be writen at", output_file_path)
    output_tfile = TFile.Open(output_file_path, "RECREATE")
    for histogram_name in histogram_names_list:
        histograms_dict[histogram_name] = TH2D(histogram_name, histogram_name,
                                        len(energy_lower_bin_edges) - 1, energy_lower_bin_edges_array,
                                        len(cos_z_lower_bin_edges) - 1, cos_z_lower_bin_edges_array)
        histograms_dict[histogram_name].GetXaxis().SetTitle("E_{#nu} (MeV)")
        histograms_dict[histogram_name].GetYaxis().SetTitle("cos(#theta_{z})")
        histograms_dict[histogram_name].GetZaxis().SetTitle("Neutrino Flux (m^{2}.s.sr.GeV)^{-1}")
        histograms_L_dict[histogram_name] = TH2D(histogram_name+"_L", histogram_name+"_L",
                                        len(energy_lower_bin_edges) - 1, energy_lower_bin_edges_array,
                                        len(prop_length_bin_edges) - 1, prop_length_bin_edges_array)
        histograms_L_dict[histogram_name].GetXaxis().SetTitle("E_{#nu} (MeV)")
        histograms_L_dict[histogram_name].GetYaxis().SetTitle("Propagation Length (km)")
        histograms_L_dict[histogram_name].GetZaxis().SetTitle("Neutrino Flux (m^{2}.s.sr.GeV)^{-1}")


    # now reading the data
    print(tColors.warning, "Now filling the histograms...")
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
                    histograms_L_dict[histogram_name].Fill(current_energy, compute_propagation_length(current_cos_z), float(current_flux[histogram_name]))
            except ValueError:
                # is header
                pass

    print(tColors.warning, "Writing histograms in the output file...")
    output_tfile.cd()
    for histogram_name in histogram_names_list:
        histograms_dict[histogram_name].Write()
        histograms_L_dict[histogram_name].Write()

    ErecNumuEdges = \
        [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50,
         0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00,
         1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45, 1.50,
         1.55, 1.60, 1.65, 1.70, 1.75, 1.80, 1.85, 1.90, 1.95, 2.00,
         2.05, 2.10, 2.15, 2.20, 2.25, 2.30, 2.35, 2.40, 2.45, 2.50,
         2.55, 2.60, 2.65, 2.70, 2.75, 2.80, 2.85, 2.90, 2.95, 3.00,
         3.25, 3.50, 3.75, 4.00,
         4.50, 5.00, 5.50, 6.00,
         7.00, 8.00, 9.00, 10.00,
         30.00]

    ErecNueEdges = \
        [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50,
     0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00,
     1.05, 1.10, 1.15, 1.20, 1.25]

    data_point_nue = list()
    data_point_nue.append([0.11269460201892662, 23.713253590477734])
    data_point_nue.append([0.14600235521323074, 104.307987751685])
    data_point_nue.append([0.17818250158651847, 322.28467379785616])
    data_point_nue.append([0.2262930835238926, 592.3846158349875])
    data_point_nue.append([0.2873938753513712, 850.6402262308328])
    data_point_nue.append([0.35779413558106665, 1085.203074959455])
    data_point_nue.append([0.44543970639488384, 1298.446126733763])
    data_point_nue.append([0.5545550144664245, 1454.8363866298982])
    data_point_nue.append([0.7184579984923083, 1521.217922821562])
    data_point_nue.append([0.9124469261213338, 1443.0945146048864])
    data_point_nue.append([1.1359607395809677, 1258.3680232319862])
    data_point_nue.append([1.4426784686095573, 926.775917891791])
    data_point_nue.append([1.7960782739941235, 434.09680384545595])
    data_point_nue.append([2.2810325775735594, 171.20182202471938])
    data_point_nue.append([2.7837913318508565, 83.59475172571297])
    data_point_nue.append([3.397362341721334, 52.84047330487897])
    data_point_nue.append([4.401478815469318, 36.311688007541306])
    data_point_nue.append([5.479668994803122, 24.512438597415894])
    data_point_nue.append([7.387748641664716, 15.098449054151843])
    data_point_nue.append([9.382494944993221, 3.303298028677318])

    output_tfile.Close()

print(tColors.info, "Process ended successfully.")
exit(0)















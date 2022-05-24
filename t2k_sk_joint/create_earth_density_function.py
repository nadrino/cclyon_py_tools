#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GenericToolbox.Colors as tColors

from ROOT import TFile
from ROOT import TF1


# Preliminary reference Earth model
# https://www.sciencedirect.com/science/article/abs/pii/0031920181900467?via%3Dihub

earth_radius = 6371

output_file_path = "../output/PREM.root"
print(tColors.info, "Output file will be writen as :", output_file_path)
output_tfile = TFile.Open(output_file_path, "RECREATE")

print(tColors.info, "Gathering PREM components parameters")
layer_label = list()
layer_outer_bound = list()
layer_polynomial_coefficients = list()

layer_label.append("InnerCore")
layer_outer_bound.append(1221.5)
layer_polynomial_coefficients.append([13.0885, 0, -8.8381])

layer_label.append("OutterCore")
layer_outer_bound.append(3480.0)
layer_polynomial_coefficients.append([12.5815, -1.2638, -3.6426, -5.5281])

layer_label.append("LowerMantle_1")
layer_outer_bound.append(3630.0)
layer_polynomial_coefficients.append([7.9565, -6.4761, 5.5283, -3.0807])

layer_label.append("LowerMantle_2")
layer_outer_bound.append(5600.0)
layer_polynomial_coefficients.append([7.9565, -6.4761, 5.5283, -3.0807])

layer_label.append("LowerMantle_3")
layer_outer_bound.append(5701.0)
layer_polynomial_coefficients.append([7.9565, -6.4761, 5.5283, -3.0807])

layer_label.append("TransitionZone_1")
layer_outer_bound.append(5771.0)
layer_polynomial_coefficients.append([5.3197, -1.4836])

layer_label.append("TransitionZone_2")
layer_outer_bound.append(5971.0)
layer_polynomial_coefficients.append([11.2494, -8.0298])

layer_label.append("TransitionZone_3")
layer_outer_bound.append(6151.0)
layer_polynomial_coefficients.append([7.1089, -3.8045])

layer_label.append("LVZ")
layer_outer_bound.append(6291.0)
layer_polynomial_coefficients.append([2.6910, 0.6924])

layer_label.append("LID")
layer_outer_bound.append(6346.6)
layer_polynomial_coefficients.append([2.6910, 0.6924])

layer_label.append("Crust_1")
layer_outer_bound.append(6356.0)
layer_polynomial_coefficients.append([2.900])

layer_label.append("Crust_2")
layer_outer_bound.append(6368.0)
layer_polynomial_coefficients.append([2.600])

print(tColors.warning, "Building Formulae...")
functions_list = list()
last_bound = 0.
output_tfile.mkdir("Layers")
output_tfile.cd("Layers")
for i_layer in range(len(layer_label)):

    formulae_string = "( "
    for i_exponent in range(len(layer_polynomial_coefficients[i_layer])):
        if i_exponent != 0:
            formulae_string += " + "
        formulae_string += "( " + str(layer_polynomial_coefficients[i_layer][i_exponent])
        formulae_string += str("*(x/" + str(earth_radius) + ")")*i_exponent
        formulae_string += " )"
    formulae_string += " ) * ( x>=" + str(last_bound) + ") * (x<" + str(layer_outer_bound[i_layer]) + ")"
    functions_list.append(
        TF1(str(layer_label[i_layer]), formulae_string, 0., layer_outer_bound[-1]+100.)
    )
    functions_list[-1].Write()
    last_bound = layer_outer_bound[i_layer]

print(tColors.warning, "Writing PREM function.")
output_tfile.cd("")
PREM_function = TF1("PREM_TF1", " + ".join(layer_label), 0., layer_outer_bound[-1]+100.)
PREM_function.Write()
output_tfile.Close()

print(tColors.info, "Process ended successfully.")
exit(0)
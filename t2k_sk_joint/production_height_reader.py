#!/usr/bin/env python
# -*- coding: utf-8 -*-


from array import array
import numpy as np

from ROOT import TCanvas
from ROOT import TFile
from ROOT import TGraph
from ROOT import kFullDotLarge
from ROOT import TSpline3
from ROOT import TF1


debug_canvas = TCanvas("debug_canvas", "debug_canvas", 800, 600)

neutrino_flavors = list()
neutrino_flavors.append("numu")
neutrino_flavors.append("numubar")
neutrino_flavors.append("nue")
neutrino_flavors.append("nuebar")

parameters = dict()
parameters["neutrino_spectra_file"] = "../output/atmospheric_neutrino_spectra.root"

f_spectra = TFile.Open(parameters["neutrino_spectra_file"], "READ")

graphs_container = dict()


for neutrino_flavor in neutrino_flavors:

    with open("./data/production_height/kam-ally-" + neutrino_flavor + ".d.gz", 'r') as data_file:

        lines = data_file.readlines()
        prob_steps = list()
        prob_steps_array = None
        cos_theta_bin = -1
        phi_bin = -1

        for line in lines:

            line_elements = list(filter(None, line.split(' ')))
            line_is_header = True
            try:
                int(line_elements[0])
                int(line_elements[1])
                int(line_elements[2])
                int(line_elements[3])
            except ValueError:
                line_is_header = False

            if line_is_header:
                cos_theta_bin = int(line_elements[2])
                phi_bin = int(line_elements[3])
                prob_steps = list() # reset
                for i_prob in range(len(line_elements)-4):
                    prob_steps.append(float(line_elements[4 + i_prob]))
                prob_steps_array = array("d", prob_steps)

            else:
                energy_bin_center = float(line_elements[0])
                altitude_steps = list()
                for i_prob in range(len(prob_steps)):
                    altitude_steps.append(float(line_elements[1+i_prob]))

                altitude_steps_array = array("d", altitude_steps)
                graph = TGraph(len(altitude_steps_array), altitude_steps_array, prob_steps_array)
                graph.SetMarkerStyle(kFullDotLarge)
                graph.SetMarkerSize(1)
                graph.SetTitle("alt")

                try:
                    graphs_container[str(energy_bin_center) + '_' + str(cos_theta_bin)] is None
                except KeyError:
                    graphs_container[str(energy_bin_center) + '_' + str(cos_theta_bin)] = list()

                graphs_container[str(energy_bin_center) + '_' + str(cos_theta_bin)].append(graph)

                # spline = TSpline3("spline", graph)
                # spline.Draw("L")
                # input("PRESS KEY")


        # averaging graphs
        averaged_graphs = dict()
        for graphs_name in graphs_container:
            x_points = list()
            y_points = list()
            samples_counter_points = list()
            for graph in graphs_container[graphs_name]:
                for i_point in range(graph.GetN()):
                    if not graph.GetX()[i_point] in x_points:
                        x_points.append(graph.GetX()[i_point])
                        y_points.append(0.)
                        samples_counter_points.append(0)
                    y_points[x_points.index(graph.GetX()[i_point])] += graph.GetY()[i_point]
                    samples_counter_points[x_points.index(graph.GetX()[i_point])] += 1
            for i_point in range(len(y_points)):
                y_points[i_point] /= float(samples_counter_points[i_point])
            x_points, y_points = zip(*sorted(zip(x_points, y_points)))
            x_points_array = array("d", x_points)
            y_points_array = array("d", y_points)
            averaged_graphs[graphs_name] = TGraph(len(x_points), x_points_array, y_points_array)
            averaged_graphs[graphs_name].GetXaxis().SetRangeUser(0, max(x_points_array)*1.10)
            # err_function = TF1("err_function","[0]*TMath::Erf((x-[1])/[2])", 0, max(x_points_array))
            # sigmoid_function = TF1("sigmoid_function","([0]/(1+ TMath::Exp(-[1]*(x-[2]))", 0, max(x_points_array))
            sigmoid_function = TF1("sigmoid_function","(1/(1+ TMath::Exp(-[0]*(x-[1]))))", 0, max(x_points_array))
            pol_function = TF1("pol_function","pol6", 0, max(x_points_array))
            averaged_graphs[graphs_name].Fit(pol_function)
            spline = TSpline3("spline", averaged_graphs[graphs_name])
            averaged_graphs[graphs_name].SetMarkerStyle(kFullDotLarge)
            averaged_graphs[graphs_name].SetMarkerSize(1)
            averaged_graphs[graphs_name].SetTitle(graphs_name)
            averaged_graphs[graphs_name].Draw("AP")
            spline.Draw("LSAME")
            debug_canvas.Update()
            input("PRESS")

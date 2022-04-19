import os

import numpy as np
import pandas as pd


def get_total_signal_and_area(array, threshold, percentile=90, verbose=False):
    """
    This function takes an array and a threshold for background intensity.
    a) It removes the background by subtracting it from the array.
    b) It only looks at the values over the threshold (setting the ones below to 0).
    At the moment, it does b).

    Then it counts all positive elements (area) and their mean intensity and the following params.
    :param array: np.array of intensities
    :param threshold: int, intensity of background to be subtracted/below which pixels values are set to 0
    :param percentile: int, default 90 (%), what percentage of top intensity pixels for calculating k_ten to take

    :return:
    area: Number of pixels with values above predetermined threshold. This value was regarded as size of depot in mice
          mean and max intensity of elemens above thr.
    intensity, intensity_depo: The mean value of the signal for slot (when values<thr are 0) and for the depo (all
                                non-zero values). It also returns median values for comparison.
    intensity_max: Maximum signal value in the array.
    total_signal, total_signal_depo: Total signal in the field of view of the corresponding mice/ organ (sum of all
                                     pixels). This value was regarded as total signal of mice
    k_ten: K10[OG1] index of depots. In this parameter, mean value of top 10% most intensive pixels in the FOV is divided
           by the mean of pixels above threshold. This value was used as an indicator of distribution width of the depot.
    NOTE: intensity_mean and total_signal (and the same for depo) are by definition having correlation 1 since mean is
        simply sum divided by a fix number (size of the field)

    NOTE 2: if nothing is above the thr, then x[x>0] = np.array([]) and the mean/median of this (intensity depo, k10)
          will be nan. Therefore, if this should happen, it will make it to be 0. That, however, messes up k10 (division
          by zero), that remains to be nan
    """

    x = array.copy()
    #     # subtract background
    #     x -= threshold
    #     # remove negative values
    #     x[x < 0] = 0

    # no bcg needs to be subtracted, just account for depo definition
    x[x < threshold] = 0
    # get area, number of non zero elements
    area = (x > 0).sum()
    # get mean intensity
    intensity = np.mean(x)
    # check for empty slice
    if x[x > 0].size:
        intensity_depo = np.mean(x[x > 0])
        median_depo = np.median(x[x > 0])
    else:
        intensity_depo = 0
        median_depo = 0
    # get the max intensity
    intensity_max = np.max(x)
    # get total signal
    total_signal = np.sum(x)
    total_signal_depo = np.sum(x[x > 0])  # this must be by def the same as total_signal...
    # mean of top 10 % div by mean over thr
    k_ten = x[x > np.percentile(x, percentile)].mean() / intensity_depo

    if verbose:
        print(area, intensity, intensity_max, intensity_depo, np.median(x), median_depo, total_signal,
              total_signal_depo, k_ten)

    return area, intensity, intensity_max, intensity_depo, np.median(x), median_depo, total_signal, total_signal_depo, k_ten


""" NOTES
for processing there should be 5 slots. To be sure that we have not missed any, go over
all of them and if some is not having a mouse, skip it. 
"""


def analyse_slots(full_array, slot_coordinates, threshold, path='./', save_name="data"):
    """
    This function goes over all slots in a given array, checks if there is a mouse and if yes,
    returns the area and intensity. There should be 5 slots.
    :param full_array: np array with intensities, shape (1024, 1024)
    :param slot_coordinates: a list of 5 tuples specifying slots with mice
    :param threshold: int, what to consider a mouse
    :param path: where to save the output
    :param save_name: what name to give to it
    :return:
    """

    # df = pd.DataFrame()
    mouse_data = []
    # go over all places
    for i, coordinates in enumerate(slot_coordinates):
        mouse_slot = full_array[coordinates[0]:coordinates[1], coordinates[2]:coordinates[3]]
        if mouse_slot.max() > threshold - 500:  # be on the save side
            area, intensity = get_total_signal_and_area(mouse_slot, threshold)
            mouse_data.append([i + 1, area, intensity])
        else:
            print(f"Slot {i + 1} is empty.")

    if mouse_slot:
        # save the collected dates into a csv
        pd.DataFrame(mouse_slot, columns=["Slot", "Area", "Intensity"]).to_csv(os.path.join(path, save_name + '.csv')
                                                                               , index=False)
        print(f"Saved to {os.path.join(path, save_name + '.csv')}")
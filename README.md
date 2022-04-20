
Set of codes to analyse fluorescence microscopy data on drug decomposition and exclusion. Below find the general ideas. This is the main place where all the information about data processing and analysis done in python for the article is to be found and what is to be used.

# Description of approaches and repo structure

Helper functions are saved in `functions` folder. Notebooks with output to see a reference how it should look are saved in `run_notebooks` and notebooks in this repo are cleared of all output ready to be run. Packages with versions used in this analysis are written in `requirements.txt` and each notebook has a watermark saying what was used to run that notebook. Data are not part of this repo except for some csv files with dates and names and path to the data has to be set manually before running the notebooks.

## Experiment setup
Four polymers were injected each to three mice and the fluorescence was measured in certain time intervals. The chemical should decompose or be washed away and the questions are how fast this happens (what is the kinetcs) and what the mechanism is. 

## Initial data analysis
What you find below is the first analysis and data processing done on this project. That includes loading the raw images, localising mice, finding correction matrices and background signal together with mice's autofluorescence signal, setting thresholds and selecting measures of interest. The second analysis, which was used in the article, comes from TIFF files geenrated based on information from the first analysis and is described in a later section [Analysis of tiff files](https://github.com/jankaWIS/code2pharmacokinetics/README.md#analysis-of-tiff-files).

## Loading data
Files are coming out as BIP files. To process them, the idea is to load them into Python and subsequently process (subtract background, do some corrections (correction matrix), subtract mouse's autofluorescence, ...). I have not found an easy way how to load the BIP files into python because, apparently, they have some header and footer but I do not know their sctructure. I have checked [pycroscopy's github](https://github.com/pycroscopy), [docs](https://pycroscopy.github.io/pycroscopy/index.html), and [spectral](http://www.spectralpython.net/) (much more promising than pycroscopy but as seen from this [issue](https://github.com/spectralpython/spectral/issues/121), it was not very suitable for BIP files, needed an [ENVI](https://www.spectralpython.net/fileio.html) header and even though it has some [BIP function](http://www.spectralpython.net/class_func_ref.html?highlight=bip#spectral.io.bipfile.BipFile), it was hard). Since [FiJi](https://fiji.sc/) was able to open those files and export them into whatever and since [ImageJ](https://imagej.net/Welcome) is [scriptable](https://imagej.nih.gov/ij/developer/macro/macros.html#recorder) (and supports plenty of languages, eg. [Jython](https://imagej.net/Jython_Scripting) which is actually not that useful since it does not support any libraries, eg. numpy...), I have decided to use their macro feature to load the image in FiJi and then save as h5 (compression, universal, possible to load into python or any other software). The good thing is that there are some [tutorials](https://nbviewer.jupyter.org/github/imagej/tutorials/blob/master/notebooks/ImageJ-Tutorials-and-Demo.ipynb) on the ImageJ interface, namely one very useful is for initialisation in [Python/Jupyter](https://nbviewer.jupyter.org/github/imagej/tutorials/blob/master/notebooks/1-Using-ImageJ/6-ImageJ-with-Python-Kernel.ipynb) allowing to open imagej from Jupyter and run needed code. After some testing, this approach has been abandonded mostly because of [this issue](https://github.com/imagej/pyimagej/issues/99). If you are interested in this approach, please contact me. 

___
[hdf5 article](https://blade6570.github.io/soumyatripathy/hdf5_blog.html)

Maybe switch to pyUSID? Consult [this](https://pycroscopy.github.io/pyUSID/faq.html)

### BIP to h5 conversion
As of July 2021 (also done in March 2021), the code for converting BIP to h5 is written in FiJi macro language -- a script called **convert_bip_h5.ijm**. In general, when run, it opens a pop-up window where one can navigate to a folder with all the bip images. It will go over all of them and convert them to h5. It will name them as `"im"+i+"_"+name` where `i` is the order of the image in the folder and `name` its name. It will create a subfolder called `bip` in this given folder where all the `.h5` files will be saved.


## Analysis and Data preprocessing
Note: `bcg` denotes *background* and `frg` *foreground* images.

### Outline
1) For all the files in a given folder, get the exact date when they were obtained. They're binary files but it should not be that difficult. The most difficult problem is that the naming of the data is inconsistent and that a sample I have received does not correspond to the actual names of file to be processed.

2) After conversion to h5 which is done using the **convert_bip_h5.ijm** script, each file has to be uploaded and analysed. There are again a few things. The required information is intensity of the depo signal in that given file in the given mouse (slot) and the area of this depo.

3) The noise of the background and probably also the correction matrix will not be necessary. The noise is too low (units/tens in comparison to hundereds of mouse's autofluorescence and thousands in the signal). What is needed is the autofluorescence to be subtracted. This should be done on the control group -- at least to get a basic feel of what to expect. Should/could be done individually but I do not think it would help much and it makes the analysis much more difficult.

4) There are 3 mice maximum and there should be 5 slots in a given image. It's a bit problematic and atm, the best is to localise the slots manually (they should be constant over time). Sometimes the mice are shifted and not in the 3 middle positions. The code should account for it but may fail with some details (the mouse seems to be 200 px wide and there is an offset of 70 from the top which means that the last slot is <200).

5) If there are 3 mice per an image, it will make it a bit harder to get back to the other data. The idea is to have a DF where are all the information from 1) but those are per file, ie per all three mice. It should not be a problem for a single mouse, thou.

---
#### Update July 2021
The analysis problems has been solved by the following steps:
1. Write a search in bcg pictures (why bcg? The gap between signal and noise is much bigger there than in frg, see the **analyse_bcg** files for more info) for slots with mice. Atm it is that based on the name it searches either for one or three slots with the highest intensity. It then picks and prints and shows those.
2. Run the **analyse_bcg-for_Ondra.ipynb** and manually (Ondra) go over the list of printed images and all pictures. Write all names-positions which are not good into a **remove.xlsx** file, the result is written into **good_mice-idx.csv**. In the following analysis just use names which are in the good and not in remove.
3. There is another naming issue -- not all bcg files have their frg counterparts and vice versa. In general, three things:
  a) Some bcg were simply not taken. For those frg one has to go over all of them to see where the mice are.
  b) Some bcg were not deleted.
  c) Some bcg and frg have very similar names because they were taken in a similar time. It's not the same so we need another list, dict of mapping for each of the files to find the corresponding other.
  d) The beginning of the name is consistent -- so if the first started on Tue (utery), it will always be named utery_...

4. **NOTE** that the `imgxxx` where `xxx` is the order in which it was converted, is not the same for frg and bcg so one needs to NOT rely on this info and take the root.
5. The dates extracted from names are nice but one needs the dates from the bip file to be precise. There is a script for getting the dates. There are some issues with it.
6. ATM Fractal analysis is not implemented -- still no progress with @rougier and the other authors of the paper.
7. We only look at intensity and area, see notes below.


### Mice localisation

Rather then to try to localise mice based on their fluorescence (frg images), do it based on the bcg images (white light) and then based on their name. There are a few reasons for doing so:
1) They should be visible there and then one could just simply take that, go over all positions, save the occupied position numbers together with the mice names and then just use this. It should be simple and goes around all the previously mentioned problems.

2) based on initial checks, there are some slots, some mice, where the signal is around 22-25. This is very low, compared to the control group where it's around 16 or 17 and seems like they go to the background. The fluorescense is so low that they could hence easily be missed. Furthermore, setting this threshold manually is dangerous.

3) Although the name-based system has potential flaws (eg. having 2 mice instead of one or 4 instead of 3), it is quite unlikely that this would happen and if so, we would have anyway hard times determining what to do with it.

The issue with automatic way of detecting mice is that it is not working well because the mouse has such a weak signal that the fourth slot has always the highest intensity regardless whether there is a mouse or not (there has been some artifacts in the images which makes a high signal in some specific spots).

### Mice naming

To be consistent, each mouse will get a name in the following manner:

*type_mX_imYYY_slotI*

where X will be either its name (1,2,3) or its order if all are present (first, second, third), imYYY is the unique number to the file generated during conversion, type is the treatment and slot I is the slot where the mouse is. The rest will be obtained through other functions.

### Background definition
See **background_definition-show_example.ipynb** for all necessary details. In short, I use empty slots to define background specific to a slot and I use the control group to get autofluorescence and background signal for all the mice. Based on this, the thresholds of localising mice and calculating statistics are determined.

## Measures of interest

### Intensity and area measures
At the moment, all possible combinations are exported -- that is intensity (max, mean) of the image and of the depo, area of non zero pixels of the image and of the depo. The depo is defined as anything above 200 after background+control signal subtraction. The value is arbitrary coming from the fact that most of the remaining signal has values <100. For details see **get_total_signal_and_area** function in **process_signal.py**.

### K10 (OG1) index
To get this parameter, mean value of top 10 % most intensive pixels in the FOV is divided by the mean of pixels above threshold. This value was used as an indicator of distribution width of the depot.

### Fractal analysis
Eventually not implemented.

---

### Running the analysis
As described above, there are a few things which need to be done. The general outline is:
1. Convert HIP images to h5 using ImageJ and its FiJi tool -> run **convert_bip_h5.ijm** from FiJi, navigate it to the folder with all the images you want to convert. By default, it will save the files into a subfolder called `bip` in the same folder as the original files. NOTE that this might take a while to run.
2. Get to know the background (see [Background definition](#Background-definition) section).
3. Run **analyse_bcg-manual_check.ipynb**.
4. Run **analyse_bcg-manual_check-run_missing_frg.ipynb** to account for images with missing frg counterpart.
5. Visual check all the files (there are instructions in 3. and 4. about how to do that).
6. Run **run_analysis-check_results.ipynb**


## Analysis of tiff files
This section describes analysis of tiff files which were generated manually using the knowledge and information obtained in the previous section. Data coming from this analysis were used and showed in the article. The relevant information and the data analysis are described in **analyse-tiff.ipynb**.



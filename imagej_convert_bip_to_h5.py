import imagej
import os
import warnings
import tkinter as tk

def initialise_imagej(version=None, local_installation=None):

    if version and local_installation:
        local_installation=False
        warnings.warn("Both local installation and version were provided. Taking only version for reproducibility.")
    elif version:
        # TODO check for version format
        ij = imagej.init(version)
    elif local_installation:
        # open up a window for them to choose path to local file
        path_to_ij = tk.filedialog.askdirectory(initialdir=os.path.dirname(__file__))
        ij = imagej.init(path_to_ij)

    else:
        ij = imagej.init()

    print("Using: ", ij.getVersion())
    return ij

# init
ij = imagej.init('sc.fiji:fiji:2.1.0')
# ij = imagej.init('/Applications/Fiji.app')
# ij = imagej.init()

print(ij.getVersion())

macro = """
#@ String name
#@ int age
#@ String city
#@output Object greeting
greeting = "Hello " + name + ". You are " + age + " years old, and live in " + city + "."
"""
args = {
    'name': 'Chuckles',
    'age': 13,
    'city': 'Nowhere'
}

language_extension = 'ijm'
result_script = ij.py.run_script(language_extension, macro, args)
print(result_script.getOutput('greeting'))

def convert_bip_to_h5(file, path, unique_id, save_path=None):

    # if no save_path given, use the same as path
    if not save_path:
        save_path=path

    macro = """
    #@ String file name (bip)
    #@ String path
    #@output save bip as h5

    //path = getInfo("macro.filepath"); // get dir+name of macro
    //print(path);
    //dir = File.getParent(path) + "/"; // get macro's dir
    print(dir)

    // Open
    
    // this should do the same just has the predefined options for the import and does not open the window
    //file_name = "2020-09-09_11-24-20-MWL-Ex(750)-Em(830)_Frgrnd.bip";
    file_dir = dir
    print("Opening "+file_dir+file_name)
    run("Bio-Formats Importer", "open=["+file_dir+file_name+"] autoscale color_mode=Default view=Hyperstack stack_order=XYCZT");

    // Save
    //save_name="test_m.h5"
    //save_dir=dir
    //run("HDF5 (new or replace)...", "save="+save_name);
    // saving adapted from https://git.embl.de/balazs/Droplet_Actions/-/blob/e8985b933a28b7d1cec4d2838c099bfb32c4d509/Open%20inr+downscale+save.ijm
    run("Scriptable save HDF5 (new or replace)...", "save=["+save_dir+save_name+"] compressionlevel=9 dsetnametemplate=tada");
    print("Saved to: "+save_dir+save_name)
    close();
    """

    args = {
        'dir': path,
        'file_name': file,
        'save_name': unique_id+file,
        'save_dir': save_path,
    }

    language_extension = 'ijm'
    result_script = ij.py.run_script(language_extension, macro, args)
    print('Done')

print("Now the real file")
files2process=os.listdir('./')
convert_bip_to_h5(path='./', file=files2process[0],unique_id=1)

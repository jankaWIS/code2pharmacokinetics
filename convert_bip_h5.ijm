// Check where we are
path = getInfo("macro.filepath"); // get dir+name of macro
print(path);
dir = File.getParent(path) + "/"; // get macro's dir
//print("we are here")
print(dir);


// Let them choose a file
resParentFolder = getDirectory("Open Parent Folder of Results");
//runMacro(path);

// go over all files in a folder
list = getFileList(resParentFolder);
	for (i = 1; i < list.length; i++)
	// loop for testing
	//for (i = 1; i < 5; i++)
	{
		//print(list[i]);
		//print(i);
		print("File Nr. " + i + " name " + list[i]);
		// Open
		fil = list[i];
		// check if the file is bip, //https://forum.image.sc/t/select-only-images-of-given-format-in-folder-containing-other-files/25690
		if (endsWith(fil, ".bip")) {
			print("File: "+fil);
			print("Opening "+resParentFolder+fil);
			// convert
			run("Bio-Formats Importer", "open=["+resParentFolder+fil+"] autoscale color_mode=Default view=Hyperstack stack_order=XYCZT");

			// Save
			tmp = list[i];
			//print("tmp:   "+tmp);
			save_name = replace( tmp, ".bip" , ".h5" ) ;
			save_name = "im"+i+"_"+save_name;
			print("save name:  "+ save_name);
			save_dir = resParentFolder+"/bip/";
			// saving adapted from https://git.embl.de/balazs/Droplet_Actions/-/blob/e8985b933a28b7d1cec4d2838c099bfb32c4d509/Open%20inr+downscale+save.ijm

			run("Scriptable save HDF5 (new or replace)...", "save=["+save_dir+save_name+"] compressionlevel=9 dsetnametemplate=tada");
			print("Saved to: "+save_dir+save_name);
			close();
		} else {
			print("This file is not bip: "+fil);
		}
	
	}



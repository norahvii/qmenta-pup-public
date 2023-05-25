# -*- coding: utf-8 -*-
import os
import glob
import subprocess
import zipfile
    
def run(context):
    # Get settings information from settings.json
    analysis_data = context.fetch_analysis_data()
    settings = context.get_settings()

    # Imported from settings.json
    pet_id = settings["pet_id"] # str
    half_life = str(settings["half_life"]) # float
    data_file = {"a": "0", "b": "1", "c": "2", "d": "5"}[settings["data_file"]] # a or b or c or d
    filterxy = str(settings["filterxy"]) # float
    filterz = str(settings["filterz"]) # float
    delay = str(settings["delay"]) # int
    tbl = str(settings["tbl"]) # int
    tolmoco = str(settings["tolmoco"]) # int
    refimg = settings["refimg"] # str
    tolreg = str(settings["tolreg"]) # int
    rmf = settings["rmf"] # str
    mmf = settings["mmf"] # str
    rbf = settings["rbf"] # str
    mbf = settings["mbf"] # str
    modf = str(settings["modf"]) # int
    pvc2cflag = str(settings["pvc2cflag"]) # int
    rsfflag = str(settings["rsfflag"]) # int
    fwhm = str(settings["fwhm"]) # float
    mst_value = str(settings["mst_value"]) # int
    mdt_value = str(settings["mdt_value"]) # int
    model_choice = {"a": "logan", "b": "nonlogan"}[settings["model_choice"]] # a or b
    suvr_flag = str(settings["suvr_flag"]) # int
    k2_rate = str(settings["k2_rate"]) # float
    roi_label = str(settings["roi_label"]) # str
    fs_version = {"a": "fslut=/usr/local/freesurfer/FreeSurferColorLUT_fs53.txt", "b": "fslut=/usr/local/freesurfer/FreeSurferColorLUT_fs711.txt"}[settings["fs_version"]] # a or b
    roisfn = {"a": "/pup/ROIs_fs53", "b": "/pup/ROIs_fs711"}[settings["fs_version"]]

    with open(f'../data/input/params/{pet_id}.params', 'w') as file:
        file.write(f"""################################################################################
# PET source data params						     #
################################################################################

# Location of the original PET data file (absolute path)
petdir=/data/input/PET/

# PET data file name
# this example is if your PET scan file is in NIFTI format and is assuming that
# your scan file is named the session label plus a .nii file extension.
# If your scan is .nii.gz you'll need to unzip it first so it changes to .nii.
# petfn=3011005_T80_v28.nii

# Here is an example of what PET filename (petfn) should look like if your
# scan is in DICOM format:
petfn="*"
# This format tells PUP to use all files that end in .dcm that are in your
# petdir folder.

# petid is used as the target name of the 4dfp file and the root for various file
# names
petid={pet_id}

# tracer half life (in seconds)
half_life={half_life}

# whether the original data is DICOM (0), ECAT (1), or Siemens InterFile format (2), or NIFTI  (5)
format={data_file}

# filtering parameters
filterxy={filterxy}
filterz={filterz}

# delay of scan versus injection (in minutes)
delay={delay}

################################################################################
# PET motion correction params                                               #
################################################################################

#time bin length (in seconds)
tbl={tbl}

# Tolerance for motion correction
tolmoco={tolmoco}

################################################################################
# FREESURFER parameters                                                      #
################################################################################

# FreeSurfer flag
FS=1

# Location of the FreeSurfer generated mgz files.
fsdir=/data/input/FreeSurfer/mri

# The name of the MR data file in FreeSurfer space (T1.mgz is used)
t1=T1.mgz

# The FreeSurfer segmentation output file (wmparc.mgz is used)
wmparc=wmparc.mgz

# Absolute path for the FreeSurferColorLUT.txt file. It has to match the version
# used to do the FreeSurfer processing
{fs_version}

################################################################################
# PET to target registration parameters                                      #
################################################################################

refimg={refimg}
tolreg={tolreg}
rmf={rmf}
mmf={mmf}
rbf={rbf}
mbf={mbf}
modf={modf}

################################################################################
# ROI parameters                                                                     #
################################################################################
roiimg=RSFMask
rsflist=RSFlist.txt
roilist=RSFlist.txt

################################################################################
# PVC flags                                                                  #
################################################################################

pvc2cflag={pvc2cflag}
rsfflag={rsfflag}
# Full-width-half-max (fwhm) of the assumed PET scanner point spread function
# to be used for partial volume correction
fwhm={fwhm}

################################################################################
# Modeling parameters                                                        #
################################################################################

# Model Starting Time in Minutes from time of injection and scan for dynamic scans
mst={mst_value}

# Model Duration in Minutes  for dynamic scans
mdt={mdt_value}

# Model
model={model_choice}

# SUVR flag
suvr={suvr_flag}

# Eflux rate constant for Logan Analysis
k2={k2_rate}

# Reference ROI label string
refroistr={roi_label}

################################################################################
# Reporting parameters                                                       #
################################################################################

# Absolute path for the file with list of regions to be analyzed
# Currently it is specific to FreeSurfer Based processing

roisfn={roisfn}

    """) # Params file finished

    # Define directories for the input and output files inside the container
    input_dir = os.path.join(os.path.expanduser("~"), "INPUT")
    output_dir = os.path.join(os.path.expanduser("~"), "OUTPUT")
    os.makedirs(output_dir, exist_ok=True)
    context.set_progress(value=0, message="Processing")  # Set progress status so it is displayed in the platform

    # Retrieve input files
    fs_handlers = context.get_files("FreeSurfer", file_filter_condition_name="c_fs")
    for fs_handler in fs_handlers:
        fs_handler.download(input_dir)
        context.set_progress(f"{fs_handler.get_file_path()} -> {input_dir}")
        
    pet_handlers = context.get_files("PET", file_filter_condition_name="c_pet")
    for pet_handler in pet_handlers:
        pet_handler.download(input_dir)
        context.set_progress(f"{pet_handler.get_file_path()} -> {input_dir}")

    # Run the rootpetproc.sh script
    cwd = os.getcwd()
    script_path = cwd+"/rootpetproc.sh"

    output, error = subprocess.Popen(["bash", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    context.set_progress(f"SCRIPT RUN OUTPUT: {output}")
    context.set_progress(f"SCRIPT RUN ERR: {error}")

    # Upload the files 
    for target in glob.glob("/root/OUTPUT/*.petproc"):
        context.upload_file(target, os.path.relpath(target, "/root/OUTPUT/"))

    # Define the target directory and folder name
    target_directory = "/root/OUTPUT"
    folder_name = "pet_proc"

    # Check if the folder exists in the target directory
    folder_path = os.path.join(target_directory, folder_name)
    zip_file_path = os.path.join(target_directory, folder_name + ".zip")

    if os.path.isdir(folder_path):
        # Create the zip file
        with zipfile.ZipFile(zip_file_path, "w") as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, folder_path))

        context.set_progress("Folder '{}' zipped successfully as '{}'.".format(folder_name, zip_file_path))
        context.upload_file(zip_file_path, os.path.basename(zip_file_path))
        context.set_progress("pet_proc.zip uploaded successfully.")
    else:
        context.set_progress("Folder '{}' does not exist in the target directory.".format(folder_name))
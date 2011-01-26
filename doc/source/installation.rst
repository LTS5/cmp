========================
Installation Instruction
========================

Step-by-Step Guide for Installation on Ubuntu/Debian
----------------------------------------------------

Install Diffusion Toolkit::

	firefox http://trackvis.org/dtk/

Install Freesurfer 5.0::

  firefox http://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall
  
Install NeuroDebian. Add the NeuroDebian repository to your source list as described here::

	firefox http://neuro.debian.net/

Upgrade your package index and update::

  sudo apt-get update
  
Install FMRIB Software Library. Using the version in the NeuroDebian repository::

	sudo aptitude fsl fslview fslview-doc python-nibabel python-nibabel-doc

Install Debian/Ubuntu dependencies::

	sudo apt-get install libblitz0-dev libboost-all-dev git-core python-dicom libnifti1

Clone the cmp repository::

	git clone git@github.com:LTS5/cmp.git

In another folder, clone the cfflib repository::

  git clone git://github.com/unidesigner/cfflib.git

You should have setup the environment variables for Bash in */home/username/.bashrc* for
Freesurfer, FSL and Diffusion Toolkit already. They should look something like this::

	# FREESURFER configuration
	export FREESURFER_HOME="/usr/share/freesurfer"
	source "${FREESURFER_HOME}/SetUpFreeSurfer.sh"
	
	# FSL configuration
	export FSL_HOME="/usr/share/fsl"
	source "${FSL_HOME}/etc/fslconf/fsl.sh"
	export PATH="${FSL_HOME}/bin:${PATH}"
	
	# DIFFUSION TOOLKIT configuration
	export DTDIR="/usr/share/dtk"
	export DSI_PATH="${DTDIR}/matrices/"
	export PATH="${DTDIR}:${PATH}"
	
You will have to add the cmp and cfflib to your Python path. Also add to the *.bashrc*::

	# CMP Path
	export PYTHONPATH="${PYTHONPATH}:/path/to/your/cmp/cmp:/path/tocfflib/cfflib"
	# an example if you cloned inside your homefolder in subfolder dev
	# export PYTHONPATH="${PYTHONPATH}:/home/myuser/dev/cmp/cmp:/myuser/dev/cfflib/cfflib"

You should now test if you can properly import cmp and cfflib. Start an IPython Shell::

  ipython
  
And try the two following commands::

  import cmp
  import cfflib
  
They should import without an error. Now you are ready to start to create your folder structure.


Project configuration and setup
-------------------------------

Steps to do before executing the pipeline

#. Create the folder structure for your project for DSI data. For DTI data, rename the folder DSI with DTI.::

	├── myproject
	│   ├── control001
	│   │   └── tp1
	│   │       ├── RAWDATA
	│   │       │   ├── DSI
	│   │       │   ├── T1
	│   │       │   └── T2


#. Copy the DICOM / MPRAGE (T1, T2) images in the corresponding folders. The T2 images
are optional but they improve the registration of the data.

#. Run the Connectome Mapping Pipeline GUI from IPython::

    from cmp.gui import CMPGUI
    cmpgui = CMPGUI()
    cmpgui.show()

#. After the first run of the e.g. the first module DICOM Converter, the folder structure should look like this::

	├── myproject
	│   ├── control001
	│   │   └── tp1
	│   │       ├── CMT
	│   │       │   ├── fibers
	│   │       │   ├── fs_output
	│   │       │   ├── raw_diffusion
	│   │       │   └── scalars
	│   │       ├── FREESURFER
	│   │       │   └── mri
	│   │       ├── LOG
	│   │       ├── NIFTI
	│   │       ├── RAWDATA
	│   │       │   ├── DSI
	│   │       │   ├── T1
	│   │       │   └── T2
	│   │       └── STATS

All the files for your subject will be stored in this folder structure.

In the GUI, now you should setup all the parameters for your your single subject and hit *Map connectome!*.

If you have to restart the GUI later and do not want to enter everything again, you can look in the LOG folder,
there are so-called pickle files with ending .pkl and you can load with the *Load* button in the GUI to restore your configuration state.

If you run into any problems, do not hesitate to send an email with the error description to info AT connectomics DOT org.

Starting the pipeline without GUI
---------------------------------
You can start the pipeline also from IPython or in a script. You can find an map_connectome.py example file
in the cloned cmp repository in /data/default_project/map_connectome.py.

You can start to modify this script to loop over subjects and/or load the "pickle" file automatically, add::

  from cmp.gui import CMPGUI
  cmpgui = CMPGUI()
	cmpgui.load_state('/path/to/your/pickle/state/LOG/cmt.pkl')

You can set the attributes of the cmtgui configuration object in the script and directly call the pipeline execution engine::

	cmpgui.active_dicomconverter = True
	cmpgui.project_name = '...'
	cmpgui.project_dir = '.../'
	cmpgui.subject_name = '...'
	cmpgui.subject_timepoint = '...'
	cmpgui.subject_workingdir = '.../'
	cmp.connectome.mapit(cmpgui)


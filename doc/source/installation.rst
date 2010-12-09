========================
Installation Instruction
========================

Step-by-Step Guide for Installation on Ubuntu/Debian
----------------------------------------------------

Install Diffusion Toolkit::

	firefox http://trackvis.org/dtk/

Install NeuroDebian. Add the NeuroDebian repository to your source list as described here::

	firefox http://neuro.debian.net/

Install FMRIB Software Library. Using the version in the NeuroDebian repository::

	sudo aptitude fsl fslview fslview-doc python-nibabel python-nibabel-doc

Debian/Ubuntu dependencies::

	sudo apt-get install libblitz0-dev libboost-all-dev git-core python-dicom

Install Freesurfer 5.0::

	firefox http://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

Installing cmt for developers (clone the repository)::

	git clone git@github.com:LTS5/cmt.git
	
Setting up the environment variables for Bash in */home/username/.bashrc*::


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
	
	# CMT Path
	export PYTHONPATH=/path/to/your/cmt/


Project configuration and setup
-------------------------------

Steps to do before executing the pipeline

#. Create the folder structure for your project.::

	├── test_cmt
	│   ├── control001
	│   │   └── tp1
	│   │       ├── RAWDATA
	│   │       │   ├── DSI
	│   │       │   ├── T1
	│   │       │   └── T2


#. Copy the DICOM / MPRAGE (T1, T2) images in the corresponding folders

#. Run the Connectome Mapping Toolkit GUI from IPython::

  from cmt.gui import CMTGUI
  cmtgui = CMTGUI()
  cmtgui.show()

#. After the first run of the e.g. the first module DICOM Converter, the folder structure should look like this::

	├── test_cmt
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

You can store a "pickle" version of the configuration settings to a file and load it afterwards.
You can also put the three Python command lines in a Python script, e.g. map_connectome.py and call it::

	python map_connectome.py

You can start to modify this script to loop over subjects and/or load the "pickle" file automatically, add::

	cmtgui.load_state('/path/to/your/saved/pickle/state/cmt.pkl')

You can set the attributes of the cmtgui configuration object in the script and directly call the pipeline execution engine::

	cmtgui.active_dicomconverter = True
	cmtgui.project_name = '...'
	cmtgui.project_dir = '.../'
	cmtgui.subject_name = '...'
	cmtgui.subject_timepoint = '...'
	cmtgui.subject_workingdir = '.../'
	cmt.connectome.mapit(cmtgui)

Comment the following line to stop invoking the GUI::

	cmtgui.show()

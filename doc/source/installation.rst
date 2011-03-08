========================
Installation Instruction
========================

Step-by-Step Guide for Installation on Ubuntu/Debian
----------------------------------------------------

Install Diffusion Toolkit::

	firefox http://trackvis.org/dtk/

Install Freesurfer 5.0::

    firefox http://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

Now, add the NeuroDebian repository to your system. The steps are explained here::

	firefox http://neuro.debian.net/

Install FMRIB Software Library. Using the version in the NeuroDebian repository::

	sudo apt-get install fsl fslview fslview-doc

We need the Python package Nibabel and Python-DICOM for neuroimaging file input-output::

	sudo apt-get install python-nibabel python-nibabel-doc python-dicom

If you have not yet done so, install IPython for an advanced interactive Python shell::

	sudo apt-get install ipython

Install now the Connectome Mapper pipeline::

	sudo apt-get install connectomemapper

At this point, make sure that you have setup the environment variables correctly for the
external packages such as Freesurfer and Diffusion Toolkit (The FSL environment variables should
be set automatically when installing FSL as described above). You should have the environment
variables: FREESURFER_HOME and DTDIR and FSL_HOME. You can check this if you enter in the bash
shell (terminal), they should give you the correct path to your packages::

    echo $FREESURFER_HOME
    echo $FSL_HOME
    echo $DTDIR

In case, you have to updated your bash configuration.::

    gedit /home/username/.bashrc

The should contain something similar as (adapted to your installation paths)::

	# FREESURFER configuration
	export FREESURFER_HOME="/usr/share/freesurfer"
	source "${FREESURFER_HOME}/SetUpFreeSurfer.sh"

	# DIFFUSION TOOLKIT configuration
	export DTDIR="/usr/share/dtk"
	export PATH="${DTDIR}:${PATH}"

Now, you are ready to start the Connectome Mapper::

    connectomemapper

Project configuration and setup
-------------------------------

Steps to do before executing the pipeline

#. Create the folder structure for your project for DSI data. For DTI data, rename the folder DSI to DTI.::

	├── myproject
	│   ├── control001
	│   │   └── tp1
	│   │       ├── RAWDATA
	│   │       │   ├── DSI
	│   │       │   ├── T1
	│   │       │   └── T2


#. Copy the Diffusion / MPRAGE (DSI, DTI, T1, T2) images (DICOM series) in the corresponding folders.
The T2 images are optional but they improve the registration of the data.

#. Run the Connectome Mapper and configure it for your project::

    connectomemapper

#. After the first run of the e.g. the first module DICOM Converter, the folder structure should look like this::

	├── myproject
	│   ├── control001
	│   │   └── tp1
	│   │       ├── CMP
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

In the GUI, now you should setup all the parameters for your your single subject and hit the *Map connectome!* button.

If you have to restart the GUI later and do not want to enter everything again, you can open the LOG folder,
there are so-called pickle files with ending .pkl and you can load them with the *Load* button in the GUI to restore your configuration state.

If you run into any problems, do not hesitate to send an email with the error description to info AT connectomics DOT org.

Starting the pipeline without GUI
---------------------------------
You can start the pipeline also from IPython or in a script. You can find an map_connectome.py example file
in the source code repository in /example/default_project/map_connectome.py.

You can start to modify this script to loop over subjects and/or load the "pickle" file automatically, add::

	from cmp.gui import CMPGUI
	cmpgui = CMPGUI()
	cmpgui.load_state('/path/to/your/pickle/state/LOG/cmp.pkl')

You can set the attributes of the cmpgui configuration object in the script and directly call the pipeline execution engine::

	cmpgui.active_dicomconverter = True
	cmpgui.project_name = '...'
	cmpgui.project_dir = '.../'
	cmpgui.subject_name = '...'
	cmpgui.subject_timepoint = '...'
	cmpgui.subject_workingdir = '.../'
	cmp.connectome.mapit(cmpgui)


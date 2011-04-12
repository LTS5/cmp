========================
Installation Instruction
========================

.. warning:: This software is for research purposes only and shall not be used for
             any clinical use. This software has not been reviewed or approved by
             the Food and Drug Administration or equivalent authority, and is for
             non-clinical, IRB-approved Research Use Only. In no event shall data
             or images generated through the use of the Software be used in the
             provision of patient care.

.. note:: Please `REGISTER <http://www.cmtk.org/users/register>`_ when before you start to use Connectome Mapper or the Connectome Mapping Toolkit.

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

We need Traits, Traits GUI, and setuptools to create the user interface::

	sudo apt-get install python-traits python-traitsgui python-setuptools

In addition, we require NetworkX to store the connection graphs::

	sudo apt-get install python-networkx

And for plotting, we install matplotlib::

    sudo apt-get install python-matplotlib

If you have not yet done so, install IPython for an advanced interactive Python shell::

	sudo apt-get install ipython

You need also Google Protocol Buffers::

    sudo apt-get install python-protobuf

Download the Connectome Mapper: :doc:`/download`

Extract the source code and install the Connectome Mapper from the Bash Shell::

    tar xzf LTS5-....tar.gz
    cd LTS5-cmp-..../
    sudo python setup.py install

Test if you can import the Connectome Mapper correctly in IPython. First start IPython in the Bash Shell::

    ipython

Then, try to import the Connectome Mapper::

    import cmp

Importing should not give you an error. If it does, please send an email to the `CMTK-users group <http://groups.google.com/group/cmtk-users>`_
with the traceback shown.

.. note:: The Connectome Mapper is not yet packaged in NeuroDebian. As soon as this happens, you will then be
          able to install with *sudo apt-get install connectomemapper*

At this point, make sure that you have setup the environment variables correctly for the
external packages such as Freesurfer and Diffusion Toolkit (The FSL environment variables should
be set automatically when installing FSL as described above). You should have the environment
variables: FREESURFER_HOME, DTDIR, DSI_DIR and FSLDIR. You can check this if you enter in the bash
shell (terminal), they should give you the correct path to your packages::

    echo $FREESURFER_HOME
    echo $FSLDIR
    echo $DTDIR

In case, you have to updated your bash configuration.::

    gedit /home/username/.bashrc

The should contain something similar as (adapted to your installation paths)::

	# FREESURFER configuration
	export FREESURFER_HOME="/usr/share/freesurfer"
	source "${FREESURFER_HOME}/SetUpFreeSurfer.sh"

	# DIFFUSION TOOLKIT configuration
	export DTDIR="/usr/share/dtk"
	export DSI_PATH="/usr/share/dtk/matrices"
	export PATH="${DTDIR}:${PATH}"

	# FSL configuration
	source /etc/fsl/4.1/fsl.sh

Now, you are ready to start the Connectome Mapper from the Bash Shell::

    connectomemapper


.. note:: The last stage (Connectome File Format Converter) needs cfflib >= 2.0 which will be released soon. Producing
         connectome files eases sharing annotated datasets with collaborators or the public (e.g. using cffdata),
         or for further analysis using the Connectome Viewer (supported with version >= 2.0).

Sample dataset
--------------

To get you started, we provide two Diffusion Spectrum Imaging sample datasets. They already contain the correct
folder structure described below. You can find the two `raw datasets online <http://cmtk.org/datasets/rawdata/>`_::

project01_dsi
    *connectome_0001* with timepoint *tp1* and DSI, T1 and T2 raw data

project02_dsi
    *connectome_0002* with timepoint *tp1* and DSI, T1 raw data

If you produce any connectome dataset that you want to share with the community, we provide a curated
`cffdata repository on GitHub <http://github.com/LTS5/cffdata>`_ .


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

Alternatively, you can also open a pickle file directly from the Bash shell when starting the Connectome Mapper::

    connectomemapper mypickle.pkl

If you run into any problems or have any questions, post to the `CMTK-users group <http://groups.google.com/group/cmtk-users>`_.

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

For a full list of field names, refer to the `source code <http://github.com/LTS5/cmp/blob/master/cmp/configuration.py>`_.

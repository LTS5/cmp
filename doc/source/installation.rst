Installation Instruction
========================

Contents:

.. toctree::
   :maxdepth: 2


Installation of Software
------------------------

* Ubuntu dependencies

* Python dependencies

* Setting the environment

* Enough disk space

Project configuration and setup
-------------------------------

Steps to do before executing the pipeline

#. Create the folder structure of your project. The structure is this:...XXX: show folder structure

#. Copy the DICOM / MPRAGE (T1, T2) images in the correpsonding folders

#. Update the data/project specific settings in the NiPype processing
   script under section 3.

Run the pipeline
----------------

map_connectome.py --conf meta.cml --subjects subjects.graphml --all

 
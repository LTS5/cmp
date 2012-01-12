# Copyright (C) 2009-2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

from .info import __version__

# PREPROCESSING
import stages.preprocessing.organize as preprocessing

# DICOM CONVERTER
import stages.converter.dicomconverter as dicomconverter

# REGISTRATION
import stages.registration.registration as registration

# FREESURFER
import stages.segmentation.freesurfer as freesurfer

# MASK: ROI_HR_th.nii / fsmask_1mm.nii CREATION
import stages.parcellation.maskcreation as maskcreation

# DIFFUSION TOOLKIT
import stages.reconstruction.dtk as dtk

# REGISTRATION: Apply registration ROI/WM --> b0
import stages.registration.apply_registration as apply_registration

# TRACTOGRAPHY
import stages.tractography.tractography as tractography

# FIBER FILTERING
import stages.postprocessing.fiberfilter as fiberfilter

# FIBER CLUSTERING
import stages.postprocessing.fiberclustering as fiberclustering

# CONNECTION MATRIX
import stages.connectionmatrix.creatematrix as connectionmatrix

# RS-FMRI AVERAGED TIME COURSES
import stages.rsfmri.correlation as fmrianalysis

# STATISTICS
import stages.stats.fiber_statistics as fiberstatistics

# CFF CONVERTER
import stages.converter.cffconverter as cffconverter

# Pipeline Status
import pipeline.pipeline_status as pipeline_status

# others
import configuration, connectome

#!/bin/bash

SUBJECTS_DIR="${DATA_path}/${MY_SUBJECT}/${MY_TP}"


cd "${SUBJECTS_DIR}/3__FREESURFER/label"
mkdir -p regenerated_lh_500
mkdir -p regenerated_rh_500
mkdir -p regenerated_rh_35
mkdir -p regenerated_lh_35
mkdir -p regenerated_rh_60
mkdir -p regenerated_lh_60
mkdir -p regenerated_rh_125
mkdir -p regenerated_lh_125
mkdir -p regenerated_rh_250
mkdir -p regenerated_lh_250



#----------------------------------------------------------------------------------------------------
#--------------------------------------------------RH------------------------------------------------
#----------------------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------------------
#----------------------- my aparc creation and labels creation  for 33 ROIs -------------------------
#----------------------------------------------------------------------------------------------------
mris_ca_label \
    "3__FREESURFER" rh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/rh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlas_33_rh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/rh.myaparc_33.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi rh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_rh_35/"


#----------------------------------------------------------------------------------------------------
#----------------------- my aparc creation and labels creation  for 500 ROIs ------------------------
#----------------------------------------------------------------------------------------------------
mris_ca_label \
    "3__FREESURFER" rh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/rh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlasP1_16_rh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/rh.myaparcP1_16.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi rh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_rh_500/" --annotation "myaparcP1_16"

mris_ca_label \
    "3__FREESURFER" rh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/rh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlasP17_28_rh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/rh.myaparcP17_28.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi rh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_rh_500/" --annotation "myaparcP17_28"

mris_ca_label \
    "3__FREESURFER" rh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/rh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlasP29_35_rh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/rh.myaparcP29_35.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi rh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_rh_500/" --annotation "myaparcP29_35"


#----------------------------------------------------------------------------------------------------
#----------------------- my aparc creation and labels creation  for 60 ROIs -------------------------
#----------------------------------------------------------------------------------------------------
mris_ca_label \
    "3__FREESURFER" rh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/rh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlas_60_rh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/rh.myaparc_60.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi rh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_rh_60/" --annotation "myaparc_60"


#----------------------------------------------------------------------------------------------------
#----------------------- my aparc creation and labels creation  for 125 ROIs ------------------------
#----------------------------------------------------------------------------------------------------
mris_ca_label \
    "3__FREESURFER" rh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/rh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlas_125_rh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/rh.myaparc_125.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi rh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_rh_125/" --annotation "myaparc_125"


#----------------------------------------------------------------------------------------------------
#----------------------- my aparc creation and labels creation  for 250 ROIs ------------------------
#----------------------------------------------------------------------------------------------------
mris_ca_label \
    "3__FREESURFER" rh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/rh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlas_250_rh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/rh.myaparc_250.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi rh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_rh_250/" --annotation "myaparc_250"





#----------------------------------------------------------------------------------------------------
#--------------------------------------------------LH------------------------------------------------
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
#----------------------- my aparc creation and labels creation  for 33 ROIs -------------------------
#----------------------------------------------------------------------------------------------------
mris_ca_label \
    "3__FREESURFER" lh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/lh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlas_33_lh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/lh.myaparc_33.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi lh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_lh_35/"


#----------------------------------------------------------------------------------------------------
#----------------------- my aparc creation and labels creation  for 500 ROIs ------------------------
#----------------------------------------------------------------------------------------------------
mris_ca_label \
    "3__FREESURFER" lh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/lh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlasP1_16_lh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/lh.myaparcP1_16.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi lh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_lh_500/" --annotation "myaparcP1_16"

mris_ca_label \
    "3__FREESURFER" lh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/lh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlasP17_28_lh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/lh.myaparcP17_28.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi lh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_lh_500/" --annotation "myaparcP17_28"

mris_ca_label \
    "3__FREESURFER" lh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/lh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlasP29_35_lh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/lh.myaparcP29_35.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi lh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_lh_500/" --annotation "myaparcP29_35"


#----------------------------------------------------------------------------------------------------
#----------------------- my aparc creation and labels creation  for 60 ROIs -------------------------
#----------------------------------------------------------------------------------------------------
mris_ca_label \
    "3__FREESURFER" lh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/lh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlas_60_lh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/lh.myaparc_60.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi lh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_lh_60/" --annotation "myaparc_60"


#----------------------------------------------------------------------------------------------------
#----------------------- my aparc creation and labels creation  for 125 ROIs ------------------------
#----------------------------------------------------------------------------------------------------
mris_ca_label \
    "3__FREESURFER" lh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/lh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlas_125_lh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/lh.myaparc_125.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi lh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_lh_125/"  --annotation "myaparc_125"


#----------------------------------------------------------------------------------------------------
#----------------------- my aparc creation and labels creation  for 250 ROIs ------------------------
#----------------------------------------------------------------------------------------------------
mris_ca_label \
    "3__FREESURFER" lh \
    "${SUBJECTS_DIR}/3__FREESURFER/surf/lh.sphere.reg" \
    "$CMT_HOME/colortable_and_gcs/my_atlas_gcs/myatlas_250_lh.gcs" \
    "${SUBJECTS_DIR}/3__FREESURFER/label/lh.myaparc_250.annot"
mri_annotation2label \
    --subject "3__FREESURFER" --hemi lh --outdir "${SUBJECTS_DIR}/3__FREESURFER/label/regenerated_lh_250/" --annotation "myaparc_250"




#-----------------------------------------------------------------------------------------------------
#------------------------extract cc and unknown to add to tactography mask ---------------------------
#-----------------------------------------------------------------------------------------------------

cd "${SUBJECTS_DIR}/3__FREESURFER/label/"

cp "regenerated_rh_35/rh.unknown.label" "rh.unknown.label"
cp "regenerated_lh_35/lh.unknown.label" "lh.unknown.label"
cp "regenerated_rh_35/rh.corpuscallosum.label" "rh.corpuscallosum.label"
cp "regenerated_lh_35/lh.corpuscallosum.label" "lh.corpuscallosum.label"

mri_label2vol \
    --label "rh.corpuscallosum.label" \
    --label "lh.corpuscallosum.label" \
    --label "rh.unknown.label" \
    --label "lh.unknown.label" \
    --temp "${SUBJECTS_DIR}/3__FREESURFER/mri/orig.mgz" \
    --o  "cc_unknown.nii"


mris_volmask "3__FREESURFER"
mri_convert -i "${SUBJECTS_DIR}/3__FREESURFER/mri/ribbon.mgz" -o "${SUBJECTS_DIR}/3__FREESURFER/mri/ribbon.nii"
mri_convert -i "${SUBJECTS_DIR}/3__FREESURFER/mri/aseg.mgz" -o "${SUBJECTS_DIR}/3__FREESURFER/mri/aseg.nii"

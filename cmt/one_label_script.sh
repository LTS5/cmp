#!/bin/sh
echo "blub"

for i in $(ls|grep $1) ; do
	echo $i
	echo $2
	mri_label2vol --label $i --temp "$2/3__FREESURFER/mri/orig.mgz" --o $i.nii > /dev/null
done


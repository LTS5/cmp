#!/usr/bin/env python
from glob import glob
import os
import subprocess

def check_command(cmd):
    proc = subprocess.Popen(['which',cmd],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    o,e = proc.communicate()
    if not os.path.exists(o.strip()):
        msg = "%s not found" % cmd
        raise Exception(msg)
    return True

def run_hardirecon():
    dtkdir = '/software/dtk/current'
    hardimat = os.path.join(dtkdir,'hardi_mat')
    odfrecon = os.path.join(dtkdir,'odf_recon')
    odftrack = os.path.join(dtkdir,'odf_tracker')
    spfilter = os.path.join(dtkdir,'spline_filter')
    check_command(odfrecon)
    os.environ['DSI_PATH'] = os.path.join(dtkdir, 'matrices')
    
    basedir = '/mindhive/nklab/projects/ellison/zfMRI'
    dtidir = os.path.join(basedir,'dti')
    subjdirs = glob(os.path.join(dtidir,'dtrecon','e*'))
    #subjdirs = glob(os.path.join(dtidir,'dtrecon','ek028*'))
    subjdirs = sorted(subjdirs)
    index = []
    queuename = 'twocore'
    for sd in subjdirs:
        sid = sd.split('/')[-1]
        dtiimg = glob(os.path.join(sd,'dwi-ec.nii'))
        bvecs = glob(os.path.join(sd,'bvecs.dat'))
        regfile = glob(os.path.join(sd,'register.dat'))
        subjdir = os.path.join(dtidir,'tvhrecon', sid)
        nzbvecs = os.path.join(subjdir,'nzbvecs.dat')
        matrices = os.path.join(subjdir,'matrices.dat')
        asegfile = os.path.join(basedir,'surfaces',sid,'mri','aseg.mgz')
        if dtiimg and bvecs and not os.path.exists(subjdir):
            index.append(sid)
            anglethresh = 35
            reconprefix = os.path.join(subjdir,'%s'%sid)
            trackdir    = os.path.join(subjdir,'dtk_%d'%anglethresh)
            mask_file   = ''.join((reconprefix,'_dwi.nii.gz'))
            tmpfsmask   = ''.join((reconprefix,'_tmpmask.nii.gz'))
            fsmask   = ''.join((reconprefix,'_fsmask.nii.gz'))
            mask_file = fsmask
            temp_track  = os.path.join(trackdir,'track_tmp.trk')
            out_track   = os.path.join(trackdir,''.join((sid,'_%d.trk'%anglethresh)))
            stripbveccmd = 'tail -n 30 %s > %s' % (bvecs[0],
                                                nzbvecs)
            bvec2matcmd = '%s %s %s -ref %s -oc' % (hardimat,
                                                 nzbvecs,
                                                 matrices,
                                                 dtiimg[0])
            reconcmd = '%s %s 31 181 %s -b0 5 -mat %s ' \
                '-p 3 -sn 1 -ot nii.gz' % (odfrecon,
                                           dtiimg[0],
                                           reconprefix,
                                           matrices)
            binarizecmd = 'mri_binarize --i %s %s --inv --o %s' % \
                (asegfile,
                 ' '.join(['--match %d' % idx \
                               for idx in [0,3,42,4,5,14,43,44,72]]),
                 tmpfsmask)
            warp2dticmd = 'mri_vol2vol --mov %s --reg %s --interp nearest ' \
                '--o %s --targ %s --inv' % (dtiimg[0],
                                            regfile[0],
                                            fsmask,
                                            tmpfsmask)
            
            trackcmd = '%s %s %s -at %d -m %s -it nii.gz' % \
                (odftrack, reconprefix, temp_track, anglethresh,
                 mask_file)
            filtcmd  = '%s %s 1 %s' % (spfilter,
                                       temp_track,
                                       out_track)
            dtrcmd   = ';'.join((stripbveccmd,
                                 bvec2matcmd,
                                 reconcmd,
                                 binarizecmd,
                                 warp2dticmd,
                                 trackcmd,
                                 filtcmd))
            outcmd = 'ezsub.py -n sg-%s -q %s -c \"%s\"' % (sid,
                                                            queuename,
                                                            dtrcmd)
            print outcmd.replace(basedir+'/','')
            os.makedirs(trackdir)
            os.system(outcmd)
        else:
            print "%s exists. remove to rerun"%subjdir
    print "submitted %d subjects"%len(index)
    print index

if __name__ == "__main__":
    run_hardirecon()
    
"""
tail -n 30 bvecs.dat > nonzerobvecs.dat
/software/dtk/current/hardi_mat nonzerobvecs.dat hardi_mat.dat -ref
dwi-ec.nii -oc
/software/dtk/current/odf_recon dwi-ec.nii 31 181 hardi -b0 5 -mat hardi_mat.dat -p 3 -sn 1 -ot nii
/software/dtk/current/odf_tracker hardi track_tmp.trk -at 35 -m hardi_dwi.nii -it nii
/software/dtk/current/spline_filter track_tmp.trk 1 hardi.trk
"""

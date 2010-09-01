#if [  ]; then
#    echo; LOG "STEP 5: Apply the REGISTRATION TRANSFORM to the output of FreeSurfer (WM+GM)"
#
#    gfa_GM_lb="0.065"        # lower bound for GRAY MATTER tissue
#    gfa_WM_lb="0.2"            # lower bound for WHITE MATTER tissue

#
#    echo; LOG "[ saved in '4__CMT/fs_output/registred/HR__registered-TO-b0' ]"
#fi

import logging
log = logging.getLogger()

log.info("STEP 5: Apply the REGISTRATION TRANSFORM to the output of FreeSurfer (WM+GM)")

gfa_GM_lb = 0.065
gfa_WM_lb = 0.2

#    "${CMT_HOME}/registration"/REGISTRATION_pipeline.sh 4 "${MY_SUBJECT}" "${FROM_TP}" "${MY_TP}" "${gfa_GM_lb}" "${gfa_WM_lb}"

proc = subprocess.Popen(['python', "step4_registration_applyToTractoMasks.py"])
                         
# XXX -> PUT into Python NODE! with input parameters!

log.info("[ saved in '4__CMT/fs_output/registred/HR__registered-TO-b0' ]")
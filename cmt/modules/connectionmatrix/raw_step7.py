import logging as log
import subprocess

#7) Create connection matrices (MATLAB way)
log.info("STEP7: Create connection matrices")

# $MY_MATLAB "DTB__create_connection_matrix( '${DATA_path}/${MY_SUBJECT}/${MY_TP}/4__CMT' ); exit"

# XXX -> create a nipype matlab node
# replace by DTB_matrix or Chrstiophs work

log.info("[ DONE ]")

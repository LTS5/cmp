#!/usr/bin/env python

# Connectome Mapping Pipeline TEMPLATE
# EPFL, CHUV, 2010

import os.path
from cmt.modules import *

#########################################
# Data and project specific configuration
#########################################

from cmt.configuration import PipelineConfiguration
myp = PipelineConfiguration()

# path to CMT_HOME using environment variable, or set directly
myp.cmt_home = os.path.join(os.environ['CMT_HOME'])
myp.dtdir = os.environ['DSI_PATH']

# My Subjects

myp.subject_list = { ('subject1', 'tp1') : {'workingdir' : '/XXX/THE/PATH'},
                 ('subject2', 'tp1') : {'workingdir' : '/XXX/THE/PATH'},
                }



tractograph.run()
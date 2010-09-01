###############################################################################################################################################
###################################################  TRACTOGRAPHY   ########################################################
###############################################################################################################################################


# You'll need to create a wrapper inheriting from CommandLineInterface define 
#the input specification and output specificiation as well as implement at least
# one method (for collecting outputs after the command  line has been executed). See out FSL classes for instance.

# how to wrap, see http://nipy.sourceforge.net/nipype/devel/cmd_interface_devel.html

# for example see,
# http://github.com/mwaskom/nipype/blob/7bd65916f9c48247aba2cfac46dfb65c78396b87/nipype/interfaces/fsl/utils.py

# STEP 6a: run STREAMLINE tractography
# convert WM MASK to 8 bit/pixel
# perform fiber-tracking
# STEP 6b: spline filtering the fibers

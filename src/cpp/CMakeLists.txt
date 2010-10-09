CMAKE_MINIMUM_REQUIRED(VERSION 2.8)

PROJECT(DTB)
#SET( CMAKE_BUILD_TYPE "Debug" )
SET( CMAKE_INSTALL_PREFIX "$ENV{CMT_HOME}/c++/bin" CACHE PATH "" FORCE)
set( CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/" )


#####################################################################################
########################  FIND PACKAGES USED  #######################################
#####################################################################################
FIND_PACKAGE ( BLITZ REQUIRED )
FIND_PACKAGE ( NIFTI REQUIRED )


SET(Boost_USE_STATIC_LIBS ON)
SET(Boost_USE_MULTITHREAD OFF)
FIND_PACKAGE( Boost 1.40.0 REQUIRED COMPONENTS program_options )



#####################################################################################
###############################  SUBPROJECTS  #######################################
#####################################################################################
ADD_SUBDIRECTORY( DTB_gfa )
ADD_SUBDIRECTORY( DTB_streamline )
ADD_SUBDIRECTORY( DTB_scalar )
ADD_SUBDIRECTORY( DTB_matrix )
ADD_SUBDIRECTORY( DTB_viewer )
ADD_SUBDIRECTORY( DTB_asintotic_matrix )



#####################################################################################
###################################  INSTALL  #######################################
#####################################################################################
INSTALL(FILES "${PROJECT_SOURCE_DIR}/common/181_vecs.dat" DESTINATION .)

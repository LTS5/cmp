PROJECT( DTB_scalar )
ADD_EXECUTABLE( DTB_scalar main.cxx )
ADD_DEPENDENCIES( DTB_scalar fibers_stats.cxx )

#####################################################################################
############################  INCLUDE / LINK  #######################################
#####################################################################################
INCLUDE_DIRECTORIES( "${PROJECT_SOURCE_DIR}/DTB_scalar" )
INCLUDE_DIRECTORIES( ${NIFTI_INCLUDE_DIR} )
INCLUDE_DIRECTORIES( ${Boost_INCLUDE_DIRS} )
INCLUDE_DIRECTORIES ("${DTB_SOURCE_DIR}/common")

TARGET_LINK_LIBRARIES ( DTB_scalar
	${BLITZ_LIBRARIES}
	${Boost_PROGRAM_OPTIONS_LIBRARY}
)


#####################################################################################
###################################  INSTALL  #######################################
#####################################################################################
INSTALL(
	TARGETS DTB_scalar
	RUNTIME DESTINATION .
	PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE
)

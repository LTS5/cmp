ADD_EXECUTABLE( DTB_matrix main.cxx )
ADD_DEPENDENCIES( DTB_matrix cmx_matrix.cxx )


#####################################################################################
############################  INCLUDE / LINK  #######################################
#####################################################################################
INCLUDE_DIRECTORIES( "${PROJECT_SOURCE_DIR}/DTB_matrix" )
INCLUDE_DIRECTORIES( ${NIFTI_INCLUDE_DIR} )
INCLUDE_DIRECTORIES( ${Boost_INCLUDE_DIRS} )
INCLUDE_DIRECTORIES ("${DTB_SOURCE_DIR}/common")

TARGET_LINK_LIBRARIES ( DTB_matrix
	${BLITZ_LIBRARIES}
	${Boost_PROGRAM_OPTIONS_LIBRARY}
)


#####################################################################################
###################################  INSTALL  #######################################
#####################################################################################
INSTALL(
	TARGETS DTB_matrix
	RUNTIME DESTINATION .
	PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE
)

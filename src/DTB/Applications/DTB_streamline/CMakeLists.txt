ADD_EXECUTABLE( DTB_streamline main.cxx )


#####################################################################################
############################  INCLUDE / LINK  #######################################
#####################################################################################
INCLUDE_DIRECTORIES( ${NIFTI_INCLUDE_DIR} )
INCLUDE_DIRECTORIES( ${Boost_INCLUDE_DIRS} )

TARGET_LINK_LIBRARIES( DTB_streamline
	${BLITZ_LIBRARIES}
	${NIFTI_LIBRARIES}
	${Boost_PROGRAM_OPTIONS_LIBRARY}
)

#####################################################################################
###################################  INSTALL  #######################################
#####################################################################################
INSTALL(
	TARGETS DTB_streamline
	RUNTIME DESTINATION "."
	PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE
)

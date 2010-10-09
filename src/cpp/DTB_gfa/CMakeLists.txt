ADD_EXECUTABLE( DTB_gfa main.cxx )

#####################################################################################
############################  INCLUDE / LINK  #######################################
#####################################################################################
INCLUDE_DIRECTORIES( "${PROJECT_SOURCE_DIR}/DTB_gfa" )
INCLUDE_DIRECTORIES( ${NIFTI_INCLUDE_DIR} )
INCLUDE_DIRECTORIES( ${Boost_INCLUDE_DIRS} )
INCLUDE_DIRECTORIES ("${DTB_SOURCE_DIR}/common")

TARGET_LINK_LIBRARIES( DTB_gfa
	${BLITZ_LIBRARIES}
	${Boost_PROGRAM_OPTIONS_LIBRARY}
)

FILE(
	COPY ${PROJECT_SOURCE_DIR}/common/181_vecs.dat
	DESTINATION ${CMAKE_CURRENT_BINARY_DIR}
)

#####################################################################################
###################################  INSTALL  #######################################
#####################################################################################
INSTALL(
	TARGETS DTB_gfa
	RUNTIME DESTINATION .
	PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE
)

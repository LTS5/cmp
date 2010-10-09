ADD_EXECUTABLE( DTB_viewer main.cxx )


#####################################################################################
########################  FIND PACKAGES USED  #######################################
#####################################################################################
FIND_PACKAGE ( OpenGL REQUIRED )
FIND_PACKAGE ( GLUT REQUIRED )
FIND_PACKAGE ( GLU REQUIRED )
IF(APPLE)
     SET(CMAKE_CXX_LINK_FLAGS "-framework OpenGL -framework GLUT")
ELSE(APPLE)
     SET(CMAKE_CXX_LINK_FLAGS "-lGL -lGLU -lglut")
ENDIF(APPLE)


#####################################################################################
############################  INCLUDE / LINK  #######################################
#####################################################################################
INCLUDE_DIRECTORIES( "${PROJECT_SOURCE_DIR}/DTB_viewer" )
INCLUDE_DIRECTORIES( ${NIFTI_INCLUDE_DIR} )
INCLUDE_DIRECTORIES ("${DTB_SOURCE_DIR}/common")

TARGET_LINK_LIBRARIES( DTB_viewer
	${BLITZ_LIBRARIES}
)

FILE(
	COPY ${PROJECT_SOURCE_DIR}/common/181_vecs.dat
	DESTINATION ${CMAKE_CURRENT_BINARY_DIR}
)


#####################################################################################
###################################  INSTALL  #######################################
#####################################################################################
INSTALL(
	TARGETS DTB_viewer
	RUNTIME DESTINATION .
	PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE
)

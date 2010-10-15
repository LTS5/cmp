import cmt, cmt.gui, cmt.connectome
cmtgui = cmt.gui.CMTGUI()
#cmtgui.configure_traits()
cmtgui.project_name = '/home/stephan/Dev/PyWorkspace/cmt/data/default_project'
cmtgui.subject_name = 'test'
cmtgui.subject_timepoint = 'tp1'
cmtgui.subject_workingdir = '/home/stephan/Dev/PyWorkspace/cmt/data/default_project/test/tp1'
cmt.connectome.mapit2(cmtgui)

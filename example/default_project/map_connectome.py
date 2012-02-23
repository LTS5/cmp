from cmp.gui import CMPGUI
import cmp.connectome
cmpgui = CMPGUI()

cmpgui.project_name = 'a'
cmpgui.project_dir = 'a'
cmpgui.subject_name = 'a'
cmpgui.subject_timepoint = 'a'
cmpgui.subject_workingdir = 'a'

#cmpgui.show()
cmp.connectome.mapit(cmpgui)

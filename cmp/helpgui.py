# Copyright (C) 2009-2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

try:
	from traits.api import HasTraits, Int, Str, Directory, List,\
	                 Bool, File, Button, Enum
	    
	from traitsui.api import View, Item, HGroup, Handler, \
	                    message, spring, Group, VGroup, TableEditor
except ImportError:	
	from enthought.traits.api import HasTraits, Int, Str, Directory, List,\
	                 Bool, File, Button, Enum
	    
	from enthought.traits.ui.api import View, Item, HGroup, Handler, \
	                    message, spring, Group, VGroup, TableEditor

from cmp import __version__

desc = {
'About' : """
Connectome Mapper
Version """ + __version__ + """

Copyright (C) 2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland

The code is released under the Modified BSD license.

Contact
-------
info@connectomics.org
http://www.connectomics.org/

Contributors
------------
* Jean-Philippe Thiran
* Reto Meuli
* Alessandro Daducci
* Leila Cammoun
* Patric Hagmann
* Alia Lemkaddem
* Elda Fischi
* Christophe Chenes
* Xavier Gigandet
* Stephan Gerhard

External Contributors
---------------------

Children's Hospital Boston:
* Ellen Grant
* Daniel Ginsburg
* Rudolph Pienaar

""",
'Help' : """
For a short description of the processing stages, please refer to the online documentation:
http://connectomics.org/connectomemapper/

If you have any questions or feedback, please use the mailinglist for the Connectome Mapping Toolkit:
http://groups.google.com/group/cmtk-users

"""
}


class HelpDialog ( HasTraits ):
    
    sections = Enum('About', desc.keys())
    stagedescription = Str(desc['About'])
    
    view = View(
        Item( name  = 'sections', show_label = False ), 
        VGroup(
               
               Item( name  = 'stagedescription', style = 'readonly', show_label = False ),
               show_border = True
        ),
        title     = 'Connectome Mapper Help',
        buttons   = [ 'OK' ],
        resizable = True,
        width = 0.4,
        height = 0.6
    )
    
    def _sections_changed(self, value):
        
        self.stagedescription = desc[value]
        

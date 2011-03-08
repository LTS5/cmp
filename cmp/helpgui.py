from enthought.traits.api import HasTraits, Int, Str, Directory, List,\
                 Bool, File, Button, Enum
    
from enthought.traits.ui.api import View, Item, HGroup, Handler, \
                    message, spring, Group, VGroup, TableEditor
                    
desc = {
'About' : """
Connectome Mapper
Version 1.0

Copyright (C) 2010, Ecole Polytechnique Federale de Lausanne (EPFL) and
Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
                
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
'DICOM Converter' : """
My DICOM Descr""",

'Registration' : """
test
""",
'Segmentation' : """
Seg
""",
'Parcellation' : """
Parcel
""",
'Reconstruction' : """
Rec
""",
'Tractography' : """
Tract
""",
'Fiber Filtering' : """
Filter
""",
'Connectome Creation' : """
CC
""",
'CFF Converter' : """
CFF""",
'Configuration' : """
Conf
""",
'Metadata' : """
Metad
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
        
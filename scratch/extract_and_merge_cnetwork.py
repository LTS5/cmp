# This script takes a set of compressed connectome files .cff
# and produces a new connectome file containing only the requested
# connectome object types. The new connectome object names are composed
# of the originial connectome file title and the original connectome
# object name

import cfflib as cf

original_connectomes = ['myconnectome1.cff', 'myconnectome2.cff']

extracted_networks = []

for i, con in enumerate(original_connectomes):
    mycon = cf.load(con)
    nets = mycon.get_connectome_network()
    for ne in nets:
        # here, you might want to skip networks with a given
        # metadata information
        ne.load()
        contitle = mycon.get_connectome_meta().get_title()
        ne.set_name( str(i) + ': ' + contitle + ' - ' + ne.get_name() )
        extracted_networks.append(ne)

# add networks to new connectome
newcon = cf.connectome(title = 'All CNetworks', connectome_network = extracted_networks )
# Setting additional metadata
metadata = newcon.get_connectome_meta()
metadata.set_creator('My Name')
metadata.set_email('My Email')
cf.save_to_cff(newcon, 'merged_cnetworks.cff') 

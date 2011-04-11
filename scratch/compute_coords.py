""" This helper script computes the center-of-gravity for each region
given on the cortex, using the Freesurfer surface meshes and the networks
produced by the Connectome Mapper

Author: Stephan Gerhard
"""

import networkx as nx
import numpy as np
import nibabel.gifti as gi
import json

# load the left hemisphere surface
surfs_lh = '.../FREESURFER/surf/lh.pial.gii'
surfs_rh = '.../FREESURFER/surf/rh.pial.gii'

# load the left hemisphere parcellation
# originally converted by mris_convert --annot ...
hemilabels_lh = '.../FREESURFER/label/lh.aparc.annot.gii'
hemilabels_rh = '.../FREESURFER/label/rh.aparc.annot.gii'

# load the network description file
netwdesc = '.../CNetwork/connectome_freesurferaparc.gpickle'

# loop over all cortical, left hemisphere nodes
g = nx.read_gpickle(netwdesc)

surf_lh = gi.read(surfs_lh)
vert_lh = surf_lh.darrays[0].data
face_lh = surf_lh.darrays[1].data
hemilab_lh = gi.read(hemilabels_lh)
hemilabdi_lh = hemilab_lh.labeltable.get_labels_as_dict()

surf_rh = gi.read(surfs_rh)
vert_rh = surf_rh.darrays[0].data
face_rh = surf_rh.darrays[1].data
hemilab_rh = gi.read(hemilabels_rh)
hemilabdi_rh = hemilab_rh.labeltable.get_labels_as_dict()

# compute dummy node for all subcortical regions
centercoord = np.vstack( (vert_lh.mean(axis=0), vert_rh.mean(axis=0) ) ).mean(axis=0)

newg = nx.Graph()

# check if the network description node label is contained in the label array
for nid, d in g.nodes_iter(data=True):
    if d['dn_region'] == 'subcortical':
        newg.add_node(nid, dn_fsname = d['dn_fsname'], dn_region = d['dn_region'], dn_hemisphere = d['dn_hemisphere'])
        newg.node[nid]['pial_x'] = str(centercoord[0])
        newg.node[nid]['pial_y'] = str(centercoord[1])
        newg.node[nid]['pial_z'] = str(centercoord[2])
    print "Region ...", d['dn_fsname']
    la = d['dn_fsname']
    if d['dn_region'] == 'cortical' and d['dn_hemisphere'] == 'left':
        print "left"
        hemi = hemilabdi_lh
        labels = hemilab_lh.darrays[0].data
        vert = vert_lh
        face = face_lh
    else:
        print "right"
        hemi = hemilabdi_rh
        labels = hemilab_rh.darrays[0].data
        vert = vert_rh
        face = face_rh
    for k,v in hemi.items():
        if v in la:
            # get the labelid
            print "Found label", v, "with key", k
            # use the labelid to compute on the given surface the center of gravity
            # store this information in the new network description
            dar = vert[np.where(k == labels)[0]]
            dar = dar.mean(axis=0)
            newg.add_node(nid, dn_fsname = d['dn_fsname'], dn_region = d['dn_region'], dn_hemisphere = d['dn_hemisphere'])
            newg.node[nid]['pial_x'] = str(dar[0])
            newg.node[nid]['pial_y'] = str(dar[1])
            newg.node[nid]['pial_z'] = str(dar[2])

# add edges
for u,v,d in g.edges_iter(data=True):
    newg.add_edge(u,v,d)
    
# write out as JSON
f = open('nodes.json', 'w')
json.dump(newg.node, f)
f.close()

f = open('edges.json', 'w')
json.dump(newg.edge, f)
f.close()

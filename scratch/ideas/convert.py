import networkx as nx
from glob import glob
import os.path as op

smallest = False

if False:
    smallest = False
    h=nx.read_graphml('/home/sgerhard/dev/cmp/cmp/data/parcellation/lausanne2008/resolution83/resolution83.graphml')
    a_lh=glob('/home/sgerhard/data/project01_dsi/ale01/tp1/FREESURFER/label/regenerated_lh_36/lh.*.label')
    a_rh=glob('/home/sgerhard/data/project01_dsi/ale01/tp1/FREESURFER/label/regenerated_rh_36/rh.*.label')
    outname = '/home/sgerhard/dev/cmp/cmp/data/parcellation/lausanne2008/resolution83/resolution83_NEW.graphml'

if True:
    h=nx.read_graphml('/home/sgerhard/dev/cmp/cmp/data/parcellation/lausanne2008/resolution150/resolution150.graphml')
    a_lh=glob('/home/sgerhard/data/project01_dsi/ale01/tp2/FREESURFER/label/regenerated_lh_60/lh.*.label')
    a_rh=glob('/home/sgerhard/data/project01_dsi/ale01/tp2/FREESURFER/label/regenerated_rh_60/rh.*.label')
    outname = '/home/sgerhard/dev/cmp/cmp/data/parcellation/lausanne2008/resolution150/resolution150_NEW.graphml'

if False:
    h=nx.read_graphml('/home/sgerhard/dev/cmp/cmp/data/parcellation/lausanne2008/resolution258/resolution258.graphml')
    a_lh=glob('/home/sgerhard/data/project01_dsi/ale01/tp2/FREESURFER/label/regenerated_lh_125/lh.*.label')
    a_rh=glob('/home/sgerhard/data/project01_dsi/ale01/tp2/FREESURFER/label/regenerated_rh_125/rh.*.label')
    outname = '/home/sgerhard/dev/cmp/cmp/data/parcellation/lausanne2008/resolution258/resolution258_NEW.graphml'
	
if False:
    h=nx.read_graphml('/home/sgerhard/dev/cmp/cmp/data/parcellation/lausanne2008/resolution500/resolution500.graphml')
    a_lh=glob('/home/sgerhard/data/project01_dsi/ale01/tp2/FREESURFER/label/regenerated_lh_250/lh.*.label')
    a_rh=glob('/home/sgerhard/data/project01_dsi/ale01/tp2/FREESURFER/label/regenerated_rh_250/rh.*.label')
    outname = '/home/sgerhard/dev/cmp/cmp/data/parcellation/lausanne2008/resolution500/resolution500_NEW.graphml'

if False:
    # highest resolution has a problem
    h=nx.read_graphml('/home/sgerhard/dev/cmp/cmp/data/parcellation/lausanne2008/resolution1015/resolution1015.graphml')
    a_lh=glob('/home/sgerhard/data/project01_dsi/ale01/tp2newparc/FREESURFER/label/regenerated_lh_500/lh.*.label')
    a_rh=glob('/home/sgerhard/data/project01_dsi/ale01/tp2newparc/FREESURFER/label/regenerated_rh_500/rh.*.label')
    outname = 'resolution1015_NEW.graphml'

di = [str(i) for i in range(10)]

#len([b for b in a_lh if str(b.split('.')[1][-1]) in di])
#len([b for b in a_rh if str(b.split('.')[1][-1]) in di])

# only store fs names
b_rh=[b.split('.')[1] for b in a_rh if str(b.split('.')[1][-1]) in di]
# when no numbers, e.g. for rh_36

if smallest:
	b_rh = []
	for b in a_rh:
		name = str(b.split('.')[1])
		if 'unknown' in name or 'corpuscallosum' in name:
			continue
		b_rh.append(name)
		
b_rh.sort()
print "Right", b_rh

# subcortical left
b_lh=[b.split('.')[1] for b in a_lh if str(b.split('.')[1][-1]) in di]

# when no numbers, e.g. for lh_36
if smallest:
	b_lh = []
	for b in a_lh:
		name = str(b.split('.')[1])
		if 'unknown' in name or 'corpuscallosum' in name:
			continue
		b_lh.append(name)
	
### subcortical right
b_lh.sort()

print "Left", b_lh

# create network
# dn_hemisphere
# dn_region
# dn_freesurfer_structname

new = nx.Graph()

e=nx.read_graphml('/home/sgerhard/dev/cmp/cmp/data/parcellation/nativefreesurfer/freesurferaparc/resolution83.graphml')
subcort = nx.Graph()
for i,d in e.nodes_iter(data=True):
	if d['dn_region'] == 'subcortical':
		subcort.add_node(i,d)

rhsub=['35','36','37','38','39','40','41']
rhasg=['49','50','51','52','58','53','54']


lhsub=['76','77','78','79','80','81','82','83']
lhasg=['10','11','12','13','26','17','18','16']

# build up bigraph
i = 1
for reg in b_rh:
	print "Add node", i
	new.add_node(str(i), {'dn_hemisphere' : 'right', 'dn_region' : 'cortical', 'dn_fsname' : reg, 'dn_correspondence_id': str(i), 'dn_name' : 'rh.' + reg } )
	i += 1

# subcortical
for idx, j in enumerate(rhsub):
	print "Add node", i
	new.add_node(str(i), {'dn_hemisphere' : 'right', 'dn_region' : 'subcortical', 'dn_fsname' : subcort.node[j]['dn_fsname'],
	 'dn_correspondence_id': str(i), 'dn_fs_aseg_val' : rhasg[idx], 'dn_name' : subcort.node[j]['dn_fsname'] } )
	i += 1

for reg in b_lh:
	print "Add node", i
	new.add_node(str(i), {'dn_hemisphere' : 'left', 'dn_region' : 'cortical', 'dn_fsname' : reg, 'dn_correspondence_id': str(i), 'dn_name' : 'lh.' + reg} )
	i += 1

# subcortical left
for idx, j in enumerate(lhsub):
	print "Add node", i
	new.add_node(str(i), {'dn_hemisphere' : 'left', 'dn_region' : 'subcortical', 'dn_fsname' : subcort.node[j]['dn_fsname'], 
	 'dn_correspondence_id': str(i), 'dn_fs_aseg_val' : lhasg[idx], 'dn_name' : subcort.node[j]['dn_fsname']} )
	i += 1

print "Final network has number of nodes", len(new.nodes())
nx.write_graphml(new, outname)

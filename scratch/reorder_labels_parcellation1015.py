b = nx.Graph() 
for i,elem in enumerate(right):
	id = str(i+1)
	for idn,dictn in a.nodes(data=True):
		if dictn['dn_fsname'] == elem and dictn['dn_hemisphere'] == 'right':
			b.add_node(id,dictn)
			b.node[id]['dn_correspondence_id'] = id
for i,elem in enumerate(left):
	id = str(i+509) # skip the subcortical region: 501 + 7 + 1
	for idn,dictn in a.nodes(data=True):
		if dictn['dn_fsname'] == elem and dictn['dn_hemisphere'] == 'left':
			b.add_node(id,dictn)
			b.node[id]['dn_correspondence_id'] = id
for i,dictn in a.nodes(data=True):
	if dictn['dn_region'] == 'subcortical':
		b.add_node(i,dictn)



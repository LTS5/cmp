#!/usr/bin/python

################################################################################
# file     : DTB__load_endpoints_from_trk.py
# function : Get the endpoints from each fibers
# date     : 2010-08-20
# author   : Christophe Chenes
#
# input    : fibers.trk file
# outputs  : endpoints, length
################################################################################

import numpy
import trackvis
import struct

def DTB__load_endpoints_from_trk(fibersFile):
	fib, hdr = trackvis.serial_open(fibersFile)
	endpoints = numpy.ndarray((hdr['n_count'],2),'object')
	epLen = numpy.zeros((hdr['n_count'],1))
	pc = -1
	for n in range(0, hdr['n_count']):
		pcN = int(round( float(100*n)/hdr['n_count'] ))
		if pcN > pc :#and pcN%10 == 0:	
			pc = pcN
			print '\t\t%4.0f%%' % (pc)
		M = struct.unpack('<i', fib.read(4))[0]
		data = numpy.zeros((3,M))
		for m in range(0, M):
			data[0,m] = struct.unpack('<f', fib.read(4))[0]
			data[1,m] = struct.unpack('<f', fib.read(4))[0]
			data[2,m] = struct.unpack('<f', fib.read(4))[0]
			
			# scalars treatment
			if hdr['n_scalars'] != 0:
				print '\tscalars...'
				for i in range(0,hdr['n_scalars']):
					tmp = fib.read(4)
			
		# keep only first and last
		data = data[:,[0,M-1]]
		
		v = numpy.zeros((3,2))
		v[0,0] = int(round( data[0,0] / hdr['voxel_size'][0] - 0.5 )) + 1
		v[1,0] = int(round( data[1,0] / hdr['voxel_size'][1] - 0.5 )) + 1
		v[2,0] = int(round( data[2,0] / hdr['voxel_size'][2] - 0.5 )) + 1
		v[0,1] = int(round( data[0,1] / hdr['voxel_size'][0] - 0.5 )) + 1
		v[1,1] = int(round( data[1,1] / hdr['voxel_size'][1] - 0.5 )) + 1
		v[2,1] = int(round( data[2,1] / hdr['voxel_size'][2] - 0.5 )) + 1
		
		v[v<1] = 1
		if v[0,0]>hdr['dim'][0]:
			v[0,0] = hdr['dim'][0]
		if v[1,0]>hdr['dim'][1]:
			v[1,0] = hdr['dim'][1]
		if v[2,0]>hdr['dim'][2]:
			v[2,0] = hdr['dim'][2]
		if v[0,1]>hdr['dim'][0]:
			v[0,1] = hdr['dim'][0]
		if v[1,1]>hdr['dim'][1]:
			v[1,1] = hdr['dim'][1]
		if v[2,1]>hdr['dim'][2]:
			v[2,1] = hdr['dim'][2]
			
		first = {'v1':v[0,0]-1, 'v2':v[1,0]-1, 'v3':v[2,0]-1}
		last = {'v1':v[0,1]-1, 'v2':v[1,1]-1, 'v3':v[2,1]-1}
		endpoints[n, 0] = first
		endpoints[n, 1] = last
		epLen[n] = M-1
		
		# properties treatment
		if hdr['n_properties'] != 0:
			print '\tproperies...'
			for i in range(0,hdr['n_properties']):
				tmp = fib.read(4)
		
	return endpoints, epLen
################################################################################

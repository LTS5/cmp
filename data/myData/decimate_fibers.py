import nibabel as ni

a=ni.trackvis.read('streamline.trk')

ni.trackvis.write('stream.trk', a[0][:10000], a[1])
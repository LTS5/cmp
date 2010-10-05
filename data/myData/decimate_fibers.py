import nibabel as ni

a=ni.trackvis.read('streamline.trk')

ni.trackvis.write('stream.trk', a[0][:100], a[1])
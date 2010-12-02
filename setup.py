#!/usr/bin/env python

"""Connectome Mapping Pipeline
"""
from glob import glob
import os
import sys
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

packages=["cmt",
          "cmt.modules",
          "cmt.modules.connectionmatrix",
          "cmt.modules.converter",
          "cmt.modules.preprocessing",
          "cmt.modules.postprocessing",
          "cmt.modules.segmentation",
          "cmt.modules.reconstruction",
          "cmt.modules.parcellation",
          "cmt.modules.registration",
          "cmt.modules.tractography",
          "cmt.modules.stats",
          "cmt.modules.template_module"]

package_data = {'cmt':
                ['data/colortable_and_gcs/*.txt',
                 'data/colortable_and_gcs/my_atlas_gcs/*.gcs',
                 'data/colortable_and_gcs/My_colortable_rnd/*.txt',
                 'data/colortable_and_gcs/My_colortable_rnd/colortable_rnd_500/*.txt',
                 'binary/linux2/bit32/*',
                 'binary/linux2/bit64/*.*'
                 ]}

################################################################################
# For some commands, use setuptools

if len(set(('develop', 'bdist_egg', 'bdist_rpm', 'bdist', 'bdist_dumb', 
            'bdist_wininst', 'install_egg_info', 'egg_info', 'easy_install',
            )).intersection(sys.argv)) > 0:
    from setup_egg import extra_setuptools_args

# extra_setuptools_args can be defined from the line above, but it can
# also be defined here because setup.py has been exec'ed from
# setup_egg.py.
if not 'extra_setuptools_args' in globals():
    extra_setuptools_args = dict()
    

def main(**extra_args):
    from distutils.core import setup
    
    # regenerate protoc
    import subprocess
    protofname = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cmt', 'pipeline', 'pipeline.proto')
    protoout = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cmt', 'pipeline')
    protopath = os.path.dirname(protofname)
    cmd = 'protoc %s --proto_path=%s --python_out=%s' % (protofname, protopath, protoout)
    print "Calling protoc to generate protobuf python file in current version:"
    print cmd
    process = subprocess.call( cmd, shell = True,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.STDOUT )
    print "protoc return code:", process
    
    setup(name='CMP',
          version='1.0',
          description='Connectome Mapping Pipeline',
          author='EPFL LTS5 Diffusion Group',
          author_email='info@connectomics.org',
          url='http://www.connectomics.org/',
          packages = packages,
          package_data = package_data,
          **extra_args
         )

if __name__ == "__main__":
    main(**extra_setuptools_args)
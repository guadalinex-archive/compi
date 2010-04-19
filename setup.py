from distutils.core import setup
from distutils.extension import Extension
import os
import glob

nombre = "compi"
vers = "beta_3r1"

examples_dir = '/usr/share/doc/%s_%s/examples' %(nombre, vers)
try:
    os.makedirs(examples_dir)
except:
    pass

setup(  name             = nombre,
        version          = vers,
        author           = "Fernando Ruiz Humanes",
        author_email     = "fruiz@forja.guadalinex.org",
        url              = "http://forja.guadalinex.org/repositorio/projects/compi/",
        download_url     = "http://forja.guadalinex.org/repositorio/frs/?group_id=31",
        package_dir      = {'compi': 'src'},
        packages         = ['compi'],
        data_files=[('/usr/share/applications/', ['compi.desktop']),
                    (examples_dir, list(glob.glob('examples/*.mos'))),
                    ('/usr/share/pixmaps/', ['images/mosaico.png']),
                    ('/usr/bin/', ['compi'])],
     )



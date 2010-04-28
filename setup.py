from distutils.core import setup
from distutils.extension import Extension
import os
import glob


    
try:
    from src.config import version as compi_version
except:
    compi_version = "0.4.2"

setup(  name             = "compi",
        version          = compi_version,
        author           = "Fernando Ruiz Humanes",
        author_email     = "fruiz@forja.guadalinex.org",
        url              = "http://forja.guadalinex.org/repositorio/projects/compi/",
        download_url     = "http://forja.guadalinex.org/repositorio/frs/?group_id=31",
        package_dir      = {'compi': 'src'},
        packages         = ['compi'],
        data_files=[('/usr/bin/', ['compi']),
                    ('/usr/share/applications/', ['compi.desktop']),
                    ('/usr/share/compi/compi%s/translations/en/LC_MESSAGES' % compi_version.replace('.',''), ['translations/en/LC_MESSAGES/compi.mo']),
                    ('/usr/share/pixmaps/', tuple(glob.glob("images/*.png")))],
     )

os.chmod('/usr/bin/compi', 0755)
os.chmod('/usr/share/applications/compi.desktop', 0644)

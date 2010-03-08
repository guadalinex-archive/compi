from distutils.core import setup
from distutils.extension import Extension
from shutil import copy2
import os
import stat


setup(  name             = "applets",
        version          = "0.1",
        author           = "Fernando Ruiz Humanes",
        author_email     = "fruiz@forja.guadalinex.org",
        url              = "http://forja.guadalinex.org/repositorio/projects/compi/",
        download_url     = "http://forja.guadalinex.org/repositorio/frs/?group_id=31",
        py_modules       = ['scanApplet', 'jumpApplet', 'joyApplet', 'controlApplet',
                            'mouse', 'gconf_prefs'],
        data_files=[('/usr/lib/bonobo/servers', ['bonobo/GNOME_ControlApplet.server',
                                                 'bonobo/GNOME_ScanApplet.server',
                                                 'bonobo/GNOME_JumpApplet.server',
                                                 'bonobo/GNOME_JoymouseApplet.server']),
                    ('/usr/share/pixmaps/', ['arrows.png', 'scan.gif'])],
        ext_modules=[Extension(name = 'xmouse',
                               sources = ['src/xmouse.c'],
                               libraries = ['X11',"Xtst"])]
     )

applets = ("scanApplet.py", "controlApplet.py", "joyApplet.py", "jumpApplet.py")
for a in applets:
    os.chmod("/usr/lib/python2.5/site-packages/"+a, 0755)

try:
    copy2("/etc/X11/xorg.conf","/etc/X11/xorg.conf.bak")
    f = open('/etc/X11/xorg.conf', 'r')
    l = f.readline() 
    if l == "# This file was modified to work with Joymouse\n": pass
    else:
        try:
            t = open('/etc/X11/xorg.conf~', 'w')
            print "Configuring X server..."
            t.write("# This file was modified to work with Joymouse\n")
            t.write(l)
            added = False
            for l in f.readlines():
                if not added and l == "Section \"InputDevice\"\n":
                    t.write("Section \"InputDevice\"\n")
                    t.write("        Identifier  \"Joystick\"\n")
                    t.write("        Driver      \"mouse\"\n")
                    t.write("        Option      \"Protocol\"       \"ExplorerPS/2\"\n")
                    t.write("        Option      \"Device\"         \"/dev/joymouse\"\n")
                    t.write("        Option      \"SendCoreEvents\" \"true\"\n")
                    t.write("        Option      \"ZAxisMapping\"       \"4 5 6 7\"\n")
                    t.write("EndSection\n\n")
                    t.write(l)
                    added = True
                elif l == "Section \"ServerLayout\"\n":
                    t.write(l)
                    t.write("        InputDevice    \"Joystick\"\n")
                else:
                    t.write(l)
            f.read()
            t.close()
            copy2('/etc/X11/xorg.conf~','/etc/X11/xorg.conf')
            print "X server reconfigured succesfully"
        except:
                f.close()
except:
    print "Failed to read X11 configuration. Joymouse was not configured properly"
    
devices = ("/dev/input/js0","/dev/input/uinput")
for dev in devices:
    if os.path.exists(dev):
        os.chmod(dev, 0666)
    else:
        print "Creating device %s" % dev
        os.mknod(dev, stat.S_IFCHR | 0666)
    os.chmod(dev, 0666)
if os.path.exists("/dev/joymouse"):
    os.chmod("/dev/joymouse", 0666)
else:
    print "Creating device /dev/joymouse"
    os.mknod("/dev/joymouse", stat.S_IFIFO | 0666)
    os.chmod("/dev/joymouse", 0666)
    


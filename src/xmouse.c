#include <Python.h>
#include <X11/Xlib.h>
#include <X11/Xresource.h>
#include <X11/Xutil.h>
#include <X11/extensions/XTest.h>

PyObject* xmouse_position(PyObject* self, PyObject* args)
{
    Display* dpy;
    int screennum = 0; 
    char* display;
    Window rootwin, childwin;
    int root_x, root_y;
    int child_x, child_y;
    int button = 1;
    unsigned int mask;
    PyObject* ret = NULL;

    PyArg_ParseTuple(args, "|zi", &display, &button);

    dpy = XOpenDisplay(display);
    if(!dpy)
    {  
        /* TODO is this right?? */
        PyErr_SetString(PyExc_Exception, "cannot open display");
        return NULL;
    }  

    if(XQueryPointer(dpy, RootWindow(dpy,0), &rootwin, &childwin,
                     &root_x, &root_y, &child_x, &child_y, &mask) == 
True)
        ret = Py_BuildValue("(i,i,i)", child_x, child_y, 
(long)childwin);
    else
        ret = Py_BuildValue("(i,i,i)", root_x, root_y, (long)rootwin);
    if (button != 0){
        XTestFakeButtonEvent(dpy, button, True, CurrentTime);
        XFlush(dpy);
        XTestFakeButtonEvent(dpy, button, False, CurrentTime);
        XFlush(dpy);
    }
    XCloseDisplay(dpy);
    return ret;
}

PyMethodDef methods[] =
{
    {"click", xmouse_position, METH_VARARGS},
};

void initxmouse(void)
{
    Py_InitModule("xmouse", methods);
}

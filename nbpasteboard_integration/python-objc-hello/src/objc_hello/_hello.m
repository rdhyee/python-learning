#import <Foundation/Foundation.h>
#include <Python.h>

const char *getHelloMessage() {
    return "Hello, Python, from Objective-C!";
}

static PyObject *py_getHelloMessage(PyObject *self, PyObject *args) {
    return Py_BuildValue("s", getHelloMessage());
}

static PyMethodDef HelloMethods[] = {
    {"getHelloMessage", py_getHelloMessage, METH_VARARGS, "Get the hello message."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef hello_module = {
    PyModuleDef_HEAD_INIT,
    "objc_hello._hello",
    NULL,
    -1,
    HelloMethods
};

PyMODINIT_FUNC PyInit__hello(void) {
    return PyModule_Create(&hello_module);
}

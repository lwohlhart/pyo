# encoding: utf-8
"""
This module defines the base classes for all objects in the library.

"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
"""
Copyright 2009-2016 Olivier Belanger

This file is part of pyo, a python module to help digital signal
processing script creation.

pyo is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

pyo is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with pyo.  If not, see <http://www.gnu.org/licenses/>.

"""
import os
import sys
import random
import inspect
import tempfile
from subprocess import call
from weakref import proxy

if sys.version_info[0] < 3:
    import __builtin__
    builtins = __builtin__
    bytes_t = str
    unicode_t = unicode
    def tobytes(strng, encoding=None):
        "Convert unicode string to bytes."
        return bytes(strng)
else:
    import builtins
    bytes_t = bytes
    unicode_t = str
    def tobytes(strng, encoding="utf-8"):
        "Convert unicode string to bytes."
        return bytes(strng, encoding=encoding)

if hasattr(builtins, 'pyo_use_double'):
    from _pyo64 import *
    import pyo64 as current_pyo
else:
    from _pyo import *
    import pyo as current_pyo

from ._maps import SLMap, SLMapMul
from ._widgets import createCtrlWindow
from ._widgets import createViewTableWindow
from ._widgets import createViewMatrixWindow

######################################################################
### Utilities
######################################################################
current_pyo_path = os.path.dirname(current_pyo.__file__)
SNDS_PATH = os.path.join(current_pyo_path, "pyolib", "snds")
XNOISE_DICT = {'uniform': 0, 'linear_min': 1, 'linear_max': 2, 'triangle': 3,
               'expon_min': 4, 'expon_max': 5, 'biexpon': 6, 'cauchy': 7,
               'weibull': 8, 'gaussian': 9, 'poisson': 10, 'walker': 11,
               'loopseg': 12}
FILE_FORMATS = {'wav': 0, 'wave': 0, 'aif': 1, 'aiff': 1, 'au': 2, '': 3,
                'sd2': 4, 'flac': 5, 'caf': 6, 'ogg': 7}
FUNCTIONS_INIT_LINES = {
    "pa_count_host_apis": "pa_count_host_apis()",
    "pa_list_host_apis": "pa_list_host_apis()",
    "pa_get_default_host_api": "pa_get_default_host_api()",
    "pa_get_default_devices_from_host": "pa_get_default_devices_from_host(host)",
    "pa_count_devices": "pa_count_devices()",
    "pa_list_devices": "pa_list_devices()",
    "pa_get_devices_infos": "pa_get_devices_infos()",
    "pa_get_version": "pa_get_version()",
    "pa_get_version_text": "pa_get_version_text()",
    "pa_get_input_devices": "pa_get_input_devices()",
    "pa_get_output_devices": "pa_get_output_devices()",
    "pa_get_default_input": "pa_get_default_input()",
    "pa_get_default_output": "pa_get_default_output()",
    "pa_get_input_max_channels": "pa_get_input_max_channels(x)",
    "pa_get_output_max_channels": "pa_get_output_max_channels(x)",
    "pm_get_default_output": "pm_get_default_output()",
    "pm_get_default_input": "pm_get_default_input()",
    "pm_get_output_devices": "pm_get_output_devices()",
    "pm_get_input_devices": "pm_get_input_devices()",
    "pm_list_devices": "pm_list_devices()",
    "pm_count_devices": "pm_count_devices()",
    "sndinfo": "sndinfo(path, print=False)",
    "savefile": "savefile(samples, path, sr=44100, channels=1, "
                "fileformat=0, sampletype=0)",
    "savefileFromTable": "savefileFromTable(table, path, fileformat=0, "
                         "sampletype=0)",
    "upsamp": "upsamp(path, outfile, up=4, order=128)",
    "downsamp": "downsamp(path, outfile, down=4, order=128)",
    "midiToHz": "midiToHz(x)",
    "hzToMidi": "hzToMidi(x)",
    "midiToTranspo": "midiToTranspo(x)",
    "sampsToSec": "sampsToSec(x)",
    "secToSamps": "secToSamps(x)",
    "linToCosCurve": "linToCosCurve(data, yrange=[0, 1], totaldur=1, "
                     "points=1024, log=False)",
    "rescale": "rescale(data, xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0, "
               "xlog=False, ylog=False)",
    "distanceToSegment": "distanceToSegment(p, p1, p2, xmin=0.0, xmax=1.0, "
                         "ymin=0.0, ymax=1.0, xlog=False, ylog=False)",
    "reducePoints": "reducePoints(pointlist, tolerance=0.02)",
    "serverCreated": "serverCreated()",
    "serverBooted": "serverBooted()",
    "example": "example(cls, dur=5, toprint=True, double=False)",
    "class_args": "class_args(cls)",
    "getVersion": "getVersion()",
    "convertStringToSysEncoding": "convertStringToSysEncoding(str)",
    "convertArgsToLists": "convertArgsToLists(*args)",
    "wrap": "wrap(arg, i)",
    "floatmap": "floatmap(x, min=0, max=1, exp=1)",
    "getPyoKeywords": "getPyoKeywords()"
}

class PyoError(Exception):
    """Base class for all pyo exceptions."""

class PyoServerStateException(PyoError):
    """Error raised when an operation requires the server to be booted."""

class PyoArgumentTypeError(PyoError):
    """Error raised when if an object got an invalid argument."""

def isAudioObject(obj):
    "Return True if the argument is an audio object."
    return isinstance(obj, PyoObject) or hasattr(obj, "stream")

def isTableObject(obj):
    "Return True if the argument is a table object."
    return isinstance(obj, PyoTableObject) or hasattr(obj, "tablestream")

def isMatrixObject(obj):
    "Return True if the argument is a matrix object."
    return isinstance(obj, PyoMatrixObject) or hasattr(obj, "matrixstream")

def isPVObject(obj):
    "Return True if the argument is a PV object."
    return isinstance(obj, PyoPVObject) or hasattr(obj, "pv_stream")

def pyoArgsAssert(obj, format, *args):
    """
    Raise an Exception if an object got an invalid argument.

    :Args:

        obj: Pyo object on which method is called.
            Usually "self" in the function call.
        format :
            String of length equal to the number of arguments. Each character
            indicating the expected argument type.

            - O: float or PyoObject
            - o: PyoObject
            - T: float or PyoTableObject
            - t: PyoTableObject
            - m: PyoMatrixObject
            - p: PyoPVObject
            - n: any number (int or float)
            - N: any number (no list-expansion)
            - f: float
            - F: float (no list-expansion)
            - i: integer
            - I: integer (no list-expansion)
            - s: string or unicode
            - S: string or unicode (no list-expansion)
            - b: boolean
            - B: boolean (no list-expansion)
            - l: list
            - L: list or None
            - u: tuple
            - x: sequence (list or tuple)
            - c: callable
            - C: callable (no list-expansion)
            - z: anything
        *args: any
            Arguments passed to the object's method.

    """
    if sys.version_info[0] < 3:
        # Python 2
        longType = int
    else:
        # Python 3
        # Not used in Python 3, ignore it
        longType = None

    i = 0
    expected = ""
    for i, arg in enumerate(args):
        f = format[i]
        argtype = type(arg)
        if f == "O":
            atypes = [list, int, longType, float]
            if not isAudioObject(arg) and argtype not in atypes:
                expected = "float or PyoObject"
        elif f == "o":
            if not isAudioObject(arg) and argtype not in [list]:
                expected = "PyoObject"
        elif f == "T":
            if not isTableObject(arg) and argtype not in [float, list]:
                expected = "float or PyoTableObject"
        elif f == "t":
            if not isTableObject(arg) and argtype not in [list]:
                expected = "PyoTableObject"
        elif f == "m":
            if not isMatrixObject(arg) and argtype not in [list]:
                expected = "PyoMatrixObject"
        elif f == "p":
            if not isPVObject(arg) and argtype not in [list]:
                expected = "PyoPVObject"
        elif f == "n":
            if argtype not in [list, int, longType, float]:
                expected = "any number"
        elif f == "N":
            if argtype not in [int, longType, float]:
                expected = "any number - list not allowed"
        elif f == "f":
            if argtype not in [list, float]:
                expected = "float"
        elif f == "F":
            if argtype not in [float]:
                expected = "float - list not allowed"
        elif f == "i":
            if argtype not in [list, int, longType]:
                expected = "integer"
        elif f == "I":
            if argtype not in [int, longType]:
                expected = "integer - list not allowed"
        elif f == "s":
            if argtype not in [list, bytes_t, unicode_t]:
                expected = "string"
        elif f == "S":
            if argtype not in [bytes_t, unicode_t]:
                expected = "string - list not allowed"
        elif f == "b":
            if argtype not in [bool, list, int, longType]:
                expected = "boolean"
        elif f == "B":
            if argtype not in [bool, int, longType]:
                expected = "boolean - list not allowed"
        elif f == "l":
            if argtype not in [list]:
                expected = "list"
        elif f == "L":
            if argtype not in [list, type(None)]:
                expected = "list or None"
        elif f == "u":
            if argtype not in [tuple]:
                expected = "tuple"
        elif f == "x":
            if argtype not in [list, tuple]:
                expected = "list or tuple"
        elif f == "c":
            if not callable(arg) and argtype not in [list, tuple, type(None)]:
                expected = "callable"
        elif f == "C":
            if not callable(arg) and argtype not in [type(None)]:
                expected = "callable - list not allowed"
        elif f == "z":
            pass

        if expected:
            break

    if expected:
        name = obj.__class__.__name__
        err = 'bad argument at position %d to "%s" (%s expected, got %s)'
        raise PyoArgumentTypeError(err % (i, name, expected, argtype))

def convertStringToSysEncoding(strng):
    """
    Convert a string to the current platform file system encoding.

    Returns the new encoded string.

    :Args:

        strng: string
            String to convert.

    """
    if type(strng) not in [bytes_t, unicode_t]:
        strng = strng.decode("utf-8")
    strng = strng.encode(sys.getfilesystemencoding())
    return strng

def convertArgsToLists(*args):
    """
    Convert all arguments to list if not already a list or a PyoObjectBase.
    Return new args and maximum list length.

    """
    converted = []
    for i in args:
        if isinstance(i, PyoObjectBase) or isinstance(i, list):
            converted.append(i)
        else:
            converted.append([i])

    max_length = max(len(i) for i in converted)
    return tuple(converted + [max_length])

def wrap(arg, i):
    """
    Return value at position `i` from `arg` with wrap around `arg` length.

    """
    x = arg[i % len(arg)]
    if isinstance(x, PyoObjectBase):
        return x[0]
    else:
        return x

def example(cls, dur=5, toprint=True, double=False):
    """
    Execute the documentation example of the object given as an argument.

    :Args:

        cls: PyoObject class
            Class reference of the desired object example.
        dur: float, optional
            Duration of the example.
        toprint: boolean, optional
            If True, the example script will be printed to the console.
            Defaults to True.
        double: boolean, optional
            If True, force the example to run in double precision (64-bit)
            Defaults to False.

    >>> example(Sine)

    """
    doc = cls.__doc__.splitlines()
    lines = []
    store = False
    for line in doc:
        if not store:
            if ">>> s = Server" in line:
                store = True
        if store:
            if line.strip() == "":
                store = False
            else:
                lines.append(line)

    if lines == []:
        print("There is no manual example for %s object." % cls.__name__)
        return

    ex_lines = [l.lstrip("    ") for l in lines if ">>>" in l or "..." in l]
    if hasattr(builtins, 'pyo_use_double') or double:
        ex = "import time\nfrom pyo64 import *\n"
    else:
        ex = "import time\nfrom pyo import *\n"
    for line in ex_lines:
        if ">>>" in line:
            line = line.lstrip(">>> ")
        if "..." in line:
            line = "    " +  line.lstrip("... ")
        ex += line + "\n"

    ex += "time.sleep(%f)\ns.stop()\ntime.sleep(0.25)\ns.shutdown()\n" % dur
    f = tempfile.NamedTemporaryFile(delete=False)
    if toprint:
        f.write(tobytes('print("""\n%s\n""")\n' % ex))
    f.write(tobytes(ex))
    f.close()
    executable = sys.executable
    if not executable or executable is None:
        executable = "python"
    call([executable, f.name])

def removeExtraDecimals(x):
    "Return a floating-point value as a string with only two digits."
    if isinstance(x, float):
        return "=%.2f" % x
    elif type(x) in [bytes_t, unicode_t]:
        return '="%s"' % x
    else:
        return "=" + str(x)

def class_args(cls):
    """
    Returns the init line of a class reference.

    This function takes a class reference (not an instance of that class)
    as input and returns the init line of that class with the default values.

    :Args:

        cls: PyoObject class
            Class reference of the desired object's init line.

    >>> print(class_args(Sine))
    >>> 'Sine(freq=1000, phase=0, mul=1, add=0)'

    """
    name = cls.__name__
    try:
        # Try for a class __init__ function
        init = getattr(cls, "__init__")
        arg, varargs, varkw, defaults = inspect.getargspec(init)
        arg = inspect.formatargspec(arg, varargs, varkw, defaults,
                                    formatvalue=removeExtraDecimals)
        arg = arg.replace("self, ", "")
        return name + arg
    except TypeError:
        try:
            # Try for a function
            if name in FUNCTIONS_INIT_LINES:
                return FUNCTIONS_INIT_LINES[name]
        except:
            print("class_args was unable to retrieve the "
                  "init line of the object as an argument.")
        return ""

def getVersion():
    """
    Returns the version number of the current pyo installation.

    This function returns the version number of the current pyo
    installation as a 3-ints tuple (major, minor, rev).

    The returned tuple for version '0.4.1' will look like: (0, 4, 1)

    >>> print(getVersion())
    >>> (0, 5, 1)

    """
    major, minor, rev = PYO_VERSION.split('.')
    return (int(major), int(minor), int(rev))

def pa_get_default_devices_from_host(host):
    """
    Returns the default input and output devices for a given audio host.

    This function can greatly help finding the device indexes (especially
    on Windows) to give to the server in order to use to desired audio host.

    :Args:

        host: string
            Name of the desired audio host. Possible hosts are:

            - For Windows: mme, directsound, asio, wasapi or wdm-ks.
            - For linux: alsa, oss, pulse or jack.
            - For MacOS: core audio, jack or soundflower.

    Return: (default_input_device, default_output_device)

    """
    host_default_in = pa_get_default_input()
    host_default_out = pa_get_default_output()

    # Retrieve host apis infos.
    tempfile = os.path.join(os.path.expanduser("~"), "pa_retrieve_host_apis")
    with open(tempfile, "w") as f:
        with f as sys.stdout:
            pa_list_host_apis()
        sys.stdout = sys.__stdout__

    with open(tempfile, "r") as f:
        lines = f.readlines()

    os.remove(tempfile)

    # Build the list of currently available hosts.
    host_names = []
    for line in lines:
        p1 = line.find("name: ") + 6
        p2 = line.find(",", p1+1)
        host_names.append(line[p1:p2])

    # Search for the desired host.
    found = False
    for line in lines:
        if host.lower() in line.lower():
            splitted = line.replace("\n", "").split(", ")
            attributes = [x.split(": ") for x in splitted]
            found = True
            break

    # If not found, return portaudio default values.
    if not found:
        print("Pyo can't find audio host '%s'. Currently available hosts are:" % host)
        for host in host_names:
            print("    %s" % host.lower())
        return host_default_in, host_default_out

    # If found, search default device indexes.
    for attribute in attributes:
        if attribute[0] == "default in":
            host_default_in = int(attribute[1])
        elif attribute[0] == "default out":
            host_default_out = int(attribute[1])

    return host_default_in, host_default_out

def getWeakMethodRef(x):
    "Return a callable object as a weak method reference."
    if type(x) in [list, tuple]:
        tmp = []
        for y in x:
            if hasattr(y, "__self__"):
                y = WeakMethod(y)
            tmp.append(y)
        x = tmp
    else:
        if hasattr(x, "__self__"):
            x = WeakMethod(x)
    return x

class WeakMethod(object):
    """A callable object. Takes one argument to init: 'object.method'.
    Once created, call this object -- MyWeakMethod() --
    and pass args/kwargs as you normally would.
    """
    def __new__(cls, callobj):
        if callable(callobj):
            return super(WeakMethod, cls).__new__(cls)

    def __init__(self, callobj):
        if hasattr(callobj, "__self__"):
            self.target = proxy(callobj.__self__)
            self.method = proxy(callobj.__func__)
            self.isMethod = True
        else:
            self.method = callobj
            self.isMethod = False

    def __call__(self, *args, **kwargs):
        """Call the method with args and kwargs as needed."""
        if self.isMethod:
            return self.method(self.target, *args, **kwargs)
        else:
            return self.method(*args, **kwargs)

######################################################################
### PyoObjectBase -> abstract class for pyo objects
######################################################################
class PyoObjectBase(object):
    """
    Base class for all pyo objects.

    This object encapsulates some common behaviors for all pyo objects.

    One typically inherits from a more specific subclass of this class
    instead of using it directly.

    .. note::

        **Operations allowed on all PyoObjectBase**

        >>> len(obj)      # Return the number of streams managed by the object.
        >>> obj[x]        # Return stream `x` of the object.
        >>>               # `x` is a number from 0 to len(obj)-1.
        >>> dir(obj)      # Return the list of attributes of the object.
        >>> for x in obj: # Can be used as an iterator (iterates over
        >>>               # object's audio streams).

    """

    # Descriptive word for this kind of object, for use in printing
    # descriptions of the object. Subclasses need to set this.
    _STREAM_TYPE = ''

    def __init__(self):
        self._base_objs = []
        self._trig_objs = None
        self.__index = 0
        if not serverCreated():
            raise PyoServerStateException("You must create and boot a Server "
                                          "before creating any audio object.")
        if not serverBooted():
            raise PyoServerStateException("The Server must be booted before "
                                          "creating any audio object.")

    def dump(self):
        """
        Print infos about the current state of the object.

        Print the number of Stream objects managed by the instance
        and the current status of the object's attributes.

        """
        attrs = dir(self)
        pp = '< Instance of %s class >' % self.__class__.__name__
        pp += '\n-----------------------------'
        pp += '\nNumber of %s streams: %d' % (self._STREAM_TYPE, len(self))
        pp += '\n--- Attributes ---'
        for attr in attrs:
            pp += '\n' + attr + ': ' + str(getattr(self, attr))
        pp += '\n-----------------------------'
        return pp

    def getBaseObjects(self):
        """
        Return a list of Stream objects managed by the instance.

        """
        return self._base_objs

    def getServer(self):
        """
        Return a reference to the current Server object.

        """
        return self._base_objs[0].getServer()

    def getSamplingRate(self):
        """
        Return the current sampling rate (samples per second), as a float.

        """
        return self._base_objs[0].getServer().getSamplingRate()

    def getBufferSize(self):
        """
        Return the current buffer size (samples per buffer), as an integer.

        """
        return self._base_objs[0].getServer().getBufferSize()

    def __iter__(self):
        self.__index = 0
        return self

    def __next__(self):
        if self.__index >= len(self):
            raise StopIteration
        x = self[self.__index]
        self.__index += 1
        return x

    def next(self):
        "Alias for __next__ method."
        # In Python 2.x, __next__() method is called next().
        return self.__next__()

    def __getitem__(self, i):
        if i == 'trig':
            return self._trig_objs
        if type(i) == slice or i < len(self._base_objs):
            return self._base_objs[i]
        else:
            if type(i) in [bytes_t, unicode_t]:
                args = (self.__class__.__name__, i)
                print("Object %s has no stream named '%s'!" % args)
            else:
                args = (self._STREAM_TYPE, self.__class__.__name__)
                print("'i' too large in slicing %s object %s!" % args)

    def __len__(self):
        return len(self._base_objs)

    def __repr__(self):
        return '< Instance of %s class >' % self.__class__.__name__

    def __dir__(self):
        init = getattr(self.__class__, "__init__")
        args, _, _, _ = inspect.getargspec(init)
        args = [a for a in args if hasattr(self.__class__, a) and a != "self"]
        return args

######################################################################
### PyoObject -> base class for pyo sound objects
######################################################################
class PyoObject(PyoObjectBase):
    """
    Base class for all pyo objects that manipulate vectors of samples.

    The user should never instantiate an object of this class.

    :Parent: :py:class:`PyoObjectBase`

    :Args:

        mul: float or PyoObject, optional
            Multiplication factor. Defaults to 1.
        add: float or PyoObject, optional
            Addition factor. Defaults to 0.

    .. note::

        **Arithmetics**

        Multiplication, addition, division and substraction can be applied
        between pyo objects or between pyo objects and numbers. Doing so
        returns a Dummy object with the result of the operation.

        >>> # Creates a Dummy object `b` with `mul` set to 0.5.
        >>> # Leaves `a` unchanged.
        >>> b = a * 0.5

        Inplace multiplication, addition, division and substraction can be
        applied between pyo objects or between pyo objects and numbers.
        These operations will replace the `mul` or `add` factor of the object.

        >>> a *= 0.5 # replaces the `mul` attribute of `a`.

        The next operators can only be used with PyoObject, not with
        XXX_base objects.

        **Exponent** and **modulo**

        >>> a ** 10 # returns a Pow object created as: Pow(a, 10)
        >>> 10 ** a # returns a Pow object created as: Pow(10, a)
        >>> a % 4 # returns a Wrap object created as: Wrap(a, 0, 4)
        >>> a % b # returns a Wrap object created as: Wrap(a, 0, b)

        **Unary negative** (**-**)

        >>> -a # returns a Dummy object with negative values of streams in `a`.

        **Comparison operators**

        >>> # Comparison operators return a Compare object.
        >>> x = a < b # same as: x = Compare(a, comp=b, mode="<")
        >>> x = a <= b # same as: Compare(a, comp=b, mode="<=")
        >>> x = a == b # same as: Compare(a, comp=b, mode="==")
        >>> x = a != b # same as: Compare(a, comp=b, mode="!=")
        >>> x = a > b # same as: Compare(a, comp=b, mode=">")
        >>> x = a >= b # same as: Compare(a, comp=b, mode=">=")

        A special case concerns the comparison of a PyoObject with None.
        All operators return False except `a != None`, which returns True.

    """

    _STREAM_TYPE = 'audio'

    def __init__(self, mul=1.0, add=0.0):
        PyoObjectBase.__init__(self)
        self._target_dict = {}
        self._signal_dict = {}
        self._callback_dict = {}
        self._keep_trace = []
        self._mul = mul
        self._add = add
        self._op_duplicate = 1
        self._map_list = []
        self._zeros = None
        self._base_players = None

    def __add__(self, x):
        x, lmax = convertArgsToLists(x)
        if self.__len__() >= lmax:
            _add_dummy = Dummy([obj + wrap(x, i//self._op_duplicate) \
                                for i, obj in enumerate(self._base_objs)])
        else:
            if isinstance(x, PyoObject):
                _add_dummy = x + self
            else:
                _add_dummy = Dummy([wrap(self._base_objs, i) + obj \
                                    for i, obj in enumerate(x)])
        self._keep_trace.append(_add_dummy)
        return _add_dummy

    def __radd__(self, x):
        x, lmax = convertArgsToLists(x)
        if self.__len__() >= lmax:
            _add_dummy = Dummy([obj + wrap(x, i//self._op_duplicate) \
                                for i, obj in enumerate(self._base_objs)])
        else:
            _add_dummy = Dummy([wrap(self._base_objs, i) + obj \
                                for i, obj in enumerate(x)])
        self._keep_trace.append(_add_dummy)
        return _add_dummy

    def __iadd__(self, x):
        self.setAdd(x)
        return self

    def __sub__(self, x):
        x, lmax = convertArgsToLists(x)
        if self.__len__() >= lmax:
            _add_dummy = Dummy([obj - wrap(x, i//self._op_duplicate) \
                                for i, obj in enumerate(self._base_objs)])
        else:
            if isinstance(x, PyoObject):
                _add_dummy = Dummy([wrap(self._base_objs, i) - wrap(x, i) \
                                    for i in range(lmax)])
            else:
                _add_dummy = Dummy([wrap(self._base_objs, i) - obj \
                                    for i, obj in enumerate(x)])
        self._keep_trace.append(_add_dummy)
        return _add_dummy

    def __rsub__(self, x):
        x, lmax = convertArgsToLists(x)
        if self.__len__() >= lmax:
            tmp = []
            for i, obj in enumerate(self._base_objs):
                sub_upsamp = Sig(wrap(x, i//self._op_duplicate))
                self._keep_trace.append(sub_upsamp)
                tmp.append(sub_upsamp - obj)
            _add_dummy = Dummy(tmp)
        else:
            tmp = []
            for i, obj in enumerate(x):
                sub_upsamp = Sig(obj)
                self._keep_trace.append(sub_upsamp)
                tmp.append(sub_upsamp - wrap(self._base_objs, i))
            _add_dummy = Dummy(tmp)
        self._keep_trace.append(_add_dummy)
        return _add_dummy

    def __isub__(self, x):
        self.setSub(x)
        return self

    def __mul__(self, x):
        x, lmax = convertArgsToLists(x)
        if self.__len__() >= lmax:
            _mul_dummy = Dummy([obj * wrap(x, i//self._op_duplicate) \
                                for i, obj in enumerate(self._base_objs)])
        else:
            if isinstance(x, PyoObject):
                _mul_dummy = x * self
            else:
                _mul_dummy = Dummy([wrap(self._base_objs, i) * obj \
                                    for i, obj in enumerate(x)])
        self._keep_trace.append(_mul_dummy)
        return _mul_dummy

    def __rmul__(self, x):
        x, lmax = convertArgsToLists(x)
        if self.__len__() >= lmax:
            _mul_dummy = Dummy([obj * wrap(x, i//self._op_duplicate) \
                                for i, obj in enumerate(self._base_objs)])
        else:
            _mul_dummy = Dummy([wrap(self._base_objs, i) * obj \
                                for i, obj in enumerate(x)])
        self._keep_trace.append(_mul_dummy)
        return _mul_dummy

    def __imul__(self, x):
        self.setMul(x)
        return self

    def __truediv__(self, x):
        return self.__div__(x)

    def __rtruediv__(self, x):
        return self.__rdiv__(x)

    def __itruediv__(self, x):
        return self.__idiv__(x)

    def __div__(self, x):
        x, lmax = convertArgsToLists(x)
        if self.__len__() >= lmax:
            _mul_dummy = Dummy([obj / wrap(x, i//self._op_duplicate) \
                                for i, obj in enumerate(self._base_objs)])
        else:
            if isinstance(x, PyoObject):
                _mul_dummy = Dummy([wrap(self._base_objs, i) / wrap(x, i) \
                                    for i in range(lmax)])
            else:
                _mul_dummy = Dummy([wrap(self._base_objs, i) / obj \
                                    for i, obj in enumerate(x)])
        self._keep_trace.append(_mul_dummy)
        return _mul_dummy

    def __rdiv__(self, x):
        x, lmax = convertArgsToLists(x)
        if self.__len__() >= lmax:
            tmp = []
            for i, obj in enumerate(self._base_objs):
                div_upsamp = Sig(wrap(x, i//self._op_duplicate))
                self._keep_trace.append(div_upsamp)
                tmp.append(div_upsamp / obj)
            _mul_dummy = Dummy(tmp)
        else:
            tmp = []
            for i, obj in enumerate(x):
                div_upsamp = Sig(obj)
                self._keep_trace.append(div_upsamp)
                tmp.append(div_upsamp / wrap(self._base_objs, i))
            _mul_dummy = Dummy(tmp)
        self._keep_trace.append(_mul_dummy)
        return _mul_dummy

    def __idiv__(self, x):
        self.setDiv(x)
        return self

    def __pow__(self, x):
        return Pow(self, x)

    def __rpow__(self, x):
        return Pow(x, self)

    def __mod__(self, x):
        return Wrap(self, 0, x)

    def __neg__(self):
        if self._zeros is None:
            self._zeros = Sig(0)
        return self._zeros - self

    def __lt__(self, x):
        return self.__do_comp__(comp=x, mode="<")

    def __le__(self, x):
        return self.__do_comp__(comp=x, mode="<=")

    def __eq__(self, x):
        return self.__do_comp__(comp=x, mode="==")

    def __ne__(self, x):
        return self.__do_comp__(comp=x, mode="!=", default=True)

    def __gt__(self, x):
        return self.__do_comp__(comp=x, mode=">")

    def __ge__(self, x):
        return self.__do_comp__(comp=x, mode=">=")

    def __do_comp__(self, comp, mode, default=False):
        if comp is None:
            return default
        else:
            return Compare(self, comp=comp, mode=mode)

    def isPlaying(self, all=False):
        """
        Returns True if the object is playing, otherwise, returns False.

        :Args:

            all: boolean, optional
                If True, the object returns a list with the state of all
                streams managed by the object.

                If False, it return a boolean corresponding to the state
                of the first stream.

        """
        pyoArgsAssert(self, "B", all)
        if all:
            return [obj._getStream().isPlaying() for obj in self._base_objs]
        else:
            return self._base_objs[0]._getStream().isPlaying()

    def isOutputting(self, all=False):
        """
        Returns True if the object is outputting.

        Returns True if the object is sending samples to dac,
        otherwise, returns False.

        :Args:

            all: boolean, optional
                If True, the object returns a list with the state of all
                streams managed by the object.

                If False, it return a boolean corresponding to the state
                of the first stream.

        """
        pyoArgsAssert(self, "B", all)
        if all:
            return [obj._getStream().isOutputting() for obj in self._base_objs]
        else:
            return self._base_objs[0]._getStream().isOutputting()

    def get(self, all=False):
        """
        Return the first sample of the current buffer as a float.

        Can be used to convert audio stream to usable Python data.

        Object that implements string identifier for specific audio
        streams must use the corresponding string to specify the stream
        from which to get the value. See get() method definition in these
        object's man pages.

        :Args:

            all: boolean, optional
                If True, the first value of each object's stream
                will be returned as a list.

                If False, only the value of the first object's stream
                will be returned as a float.

        """
        pyoArgsAssert(self, "B", all)
        if not all:
            return self._base_objs[0]._getStream().getValue()
        else:
            return [obj._getStream().getValue() for obj in self._base_objs]

    def play(self, dur=0, delay=0):
        """
        Start processing without sending samples to output.
        This method is called automatically at the object creation.

        This method returns `self`, allowing it to be applied at the object
        creation.

        :Args:

            dur: float, optional
                Duration, in seconds, of the object's activation. The default
                is 0 and means infinite duration.
            delay: float, optional
                Delay, in seconds, before the object's activation. Defaults to 0.

        """
        pyoArgsAssert(self, "nn", dur, delay)
        dur, delay, lmax = convertArgsToLists(dur, delay)
        if self._trig_objs is not None:
            if isinstance(self._trig_objs, list):
                for i in range(lmax):
                    for obj in self._trig_objs:
                        obj.play(wrap(dur, i), wrap(delay, i))
            else:
                self._trig_objs.play(dur, delay)
        if self._base_players is not None:
            [obj.play(wrap(dur, i), wrap(delay, i)) \
             for i, obj in enumerate(self._base_players)]
        [obj.play(wrap(dur, i), wrap(delay, i)) \
         for i, obj in enumerate(self._base_objs)]
        return self

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        """
        Start processing and send samples to audio output beginning at `chnl`.

        This method returns `self`, allowing it to be applied at the object
        creation.

        :Args:

            chnl: int, optional
                Physical output assigned to the first audio stream of the
                object. Defaults to 0.
            inc: int, optional
                Output channel increment value. Defaults to 1.
            dur: float, optional
                Duration, in seconds, of the object's activation. The default
                is 0 and means infinite duration.
            delay: float, optional
                Delay, in seconds, before the object's activation.
                Defaults to 0.

        If `chnl` >= 0, successive streams increment the output number by
        `inc` and wrap around the global number of channels.

        If `chnl` is negative, streams begin at 0, increment
        the output number by `inc` and wrap around the global number of
        channels. Then, the list of streams is scrambled.

        If `chnl` is a list, successive values in the list will be
        assigned to successive streams.

        """
        pyoArgsAssert(self, "iInn", chnl, inc, dur, delay)
        dur, delay, lmax = convertArgsToLists(dur, delay)
        if self._trig_objs is not None:
            if isinstance(self._trig_objs, list):
                for i in range(lmax):
                    for obj in self._trig_objs:
                        obj.play(wrap(dur, i), wrap(delay, i))
            else:
                self._trig_objs.play(dur, delay)
        if self._base_players is not None:
            [obj.play(wrap(dur, i), wrap(delay, i))
             for i, obj in enumerate(self._base_players)]
        if isinstance(chnl, list):
            [obj.out(wrap(chnl, i), wrap(dur, i), wrap(delay, i)) \
             for i, obj in enumerate(self._base_objs)]
        else:
            if chnl < 0:
                [obj.out(i*inc, wrap(dur, i), wrap(delay, i)) \
                 for i, obj in enumerate(random.sample(self._base_objs,
                                                       len(self._base_objs)))]
            else:
                [obj.out(chnl+i*inc, wrap(dur, i), wrap(delay, i)) \
                 for i, obj in enumerate(self._base_objs)]
        return self

    def stop(self):
        """
        Stop processing.

        This method returns `self`, allowing it to be applied at the object
        creation.

        """
        if self._trig_objs is not None:
            if isinstance(self._trig_objs, list):
                [obj.stop() for obj in self._trig_objs]
            else:
                self._trig_objs.stop()
        if self._base_players is not None:
            [obj.stop() for obj in self._base_players]
        [obj.stop() for obj in self._base_objs]
        return self

    def mix(self, voices=1):
        """
        Mix the object's audio streams into `voices` streams and return
        a Mix object.

        :Args:

            voices: int, optional
                Number of audio streams of the Mix object created by this
                method. Defaults to 1.

                If more than 1, object's streams are alternated and added into
                Mix object's streams.

        """
        return Mix(self, voices)

    def range(self, min, max):
        """
        Adjust `mul` and `add` attributes according to a given range.

        This function assumes a signal between -1 and 1. Arguments may be
        list of floats for multi-streams objects.

        This method returns `self`, allowing it to be applied at the object
        creation:

        >>> lfo = Sine(freq=1).range(500, 1000)

        :Args:

            min: float
                Minimum value of the output signal.
            max: float
                Maximum value of the output signal.

        """
        pyoArgsAssert(self, "nn", min, max)
        min, max, lmax = convertArgsToLists(min, max)
        if lmax > 1:
            mul = [(wrap(max, i) - wrap(min, i)) * 0.5 for i in range(lmax)]
            add = [(wrap(max, i) + wrap(min, i)) * 0.5 for i in range(lmax)]
        else:
            mul = (max[0] - min[0]) * 0.5
            add = (max[0] + min[0]) * 0.5
        self.setMul(mul)
        self.setAdd(add)
        return self

    def setMul(self, x):
        """
        Replace the `mul` attribute.

        :Args:

            x: float or PyoObject
                New `mul` attribute.

        """
        pyoArgsAssert(self, "O", x)
        self._mul = x
        x, _ = convertArgsToLists(x)
        [obj.setMul(wrap(x, i // self._op_duplicate)) \
         for i, obj in enumerate(self._base_objs)]

    def setAdd(self, x):
        """
        Replace the `add` attribute.

        :Args:

            x: float or PyoObject
                New `add` attribute.

        """
        pyoArgsAssert(self, "O", x)
        self._add = x
        x, _ = convertArgsToLists(x)
        [obj.setAdd(wrap(x, i // self._op_duplicate)) \
         for i, obj in enumerate(self._base_objs)]

    def setSub(self, x):
        """
        Replace and inverse the `add` attribute.

        :Args:

            x: float or PyoObject
                New inversed `add` attribute.

        """
        pyoArgsAssert(self, "O", x)
        self._add = x
        x, _ = convertArgsToLists(x)
        [obj.setSub(wrap(x, i // self._op_duplicate)) \
         for i, obj in enumerate(self._base_objs)]

    def setDiv(self, x):
        """
        Replace and inverse the `mul` attribute.

        :Args:

            x: float or PyoObject
                New inversed `mul` attribute.

        """
        pyoArgsAssert(self, "O", x)
        self._mul = x
        x, _ = convertArgsToLists(x)
        [obj.setDiv(wrap(x, i // self._op_duplicate)) \
         for i, obj in enumerate(self._base_objs)]

    def set(self, attr, value, port=0.025, callback=None):
        """
        Replace any attribute with portamento.

        This method is intended to be applied on attributes that are not
        already assigned to PyoObjects. It will work only with floats or
        list of floats.

        :Args:

            attr: string
                Name of the attribute as a string.
            value: float
                New value.
            port: float, optional
                Time, in seconds, to reach the new value.
            callback: callable, optional
                A python function to be called at the end of the ramp. If the
                end of the ramp is not reached (ex.: called again before the
                end of the portamento), the callback will not be called.

        """
        pyoArgsAssert(self, "SnnC", attr, value, port, callback)
        self._target_dict[attr] = value
        self._callback_dict[attr] = callback
        init = getattr(self, attr)
        if attr in self._signal_dict:
            if isinstance(self._signal_dict[attr], VarPort):
                if self._signal_dict[attr].isPlaying():
                    init = self._signal_dict[attr].get(True)
                    self._signal_dict[attr].stop()
        self._signal_dict[attr] = VarPort(value, port, init,
                                          self._reset_from_set, attr)
        setattr(self, attr, self._signal_dict[attr])

    def _reset_from_set(self, attr=None):
        if isinstance(getattr(self, attr), VarPort):
            setattr(self, attr, self._target_dict[attr])
            if self._callback_dict[attr] is not None:
                self._callback_dict[attr]()
                del self._callback_dict[attr]
        self._signal_dict[attr].stop()

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        """
        Opens a sliders window to control the parameters of the object.
        Only parameters that can be set to a PyoObject are allowed
        to be mapped on a slider.

        If a list of values are given to a parameter, a multisliders
        will be used to control each stream independently.

        :Args:

            map_list: list of SLMap objects, optional
                Users defined set of parameters scaling. There is default
                scaling for each object that accept `ctrl` method.
            title: string, optional
                Title of the window. If none is provided, the name of the
                class is used.
            wxnoserver: boolean, optional
                With wxPython graphical toolkit, if True, tells the
                interpreter that there will be no server window.

        If `wxnoserver` is set to True, the interpreter will not wait for
        the server GUI before showing the controller window.

        """
        if map_list is None:
            map_list = self._map_list
        if map_list == []:
            clsname = self.__class__.__name__
            print("There are no controls for %s object." % clsname)
            return
        createCtrlWindow(self, map_list, title, wxnoserver)

    @property
    def mul(self):
        """float or PyoObject. Multiplication factor."""
        return self._mul
    @mul.setter
    def mul(self, x):
        self.setMul(x)

    @property
    def add(self):
        """float or PyoObject. Addition factor."""
        return self._add
    @add.setter
    def add(self, x):
        self.setAdd(x)

######################################################################
### PyoTableObject -> base class for pyo table objects
######################################################################
class PyoTableObject(PyoObjectBase):
    """
    Base class for all pyo table objects.

    A table object is a buffer memory to store precomputed samples.

    The user should never instantiate an object of this class.

    :Parent: :py:class:`PyoObjectBase`

    :Args:

        size: int
            Length of the table in samples. Usually provided by the
            child object.

    """

    _STREAM_TYPE = 'table'

    def __init__(self, size=0):
        PyoObjectBase.__init__(self)
        self._size = size
        self.viewFrame = None
        self.graphFrame = None

    def save(self, path, format=0, sampletype=0, quality=0.4):
        """
        Writes the content of the table in an audio file.

        The sampling rate of the file is the sampling rate of the server
        and the number of channels is the number of table streams of the
        object.

        :Args:

            path: string
                Full path (including extension) of the new file.
            format: int, optional
                Format type of the new file. Supported formats are:
                    0. WAVE - Microsoft WAV format (little endian) {.wav, .wave}
                    1. AIFF - Apple/SGI AIFF format (big endian) {.aif, .aiff}
                    2. AU - Sun/NeXT AU format (big endian) {.au}
                    3. RAW - RAW PCM data {no extension}
                    4. SD2 - Sound Designer 2 {.sd2}
                    5. FLAC - FLAC lossless file format {.flac}
                    6. CAF - Core Audio File format {.caf}
                    7. OGG - Xiph OGG container {.ogg}
            sampletype: int, optional
                Bit depth encoding of the audio file.

                SD2 and FLAC only support 16 or 24 bit int. Supported types are:
                    0. 16 bit int (default)
                    1. 24 bit int
                    2. 32 bit int
                    3. 32 bit float
                    4. 64 bit float
                    5. U-Law encoded
                    6. A-Law encoded
            quality: float, optional
                The encoding quality value, between 0.0 (lowest quality) and
                1.0 (highest quality). This argument has an effect only with
                FLAC and OGG compressed formats. Defaults to 0.4.

        """
        pyoArgsAssert(self, "SIIN", path, format, sampletype, quality)
        ext = path.rsplit('.')
        if len(ext) >= 2:
            ext = ext[-1].lower()
            if ext in FILE_FORMATS:
                format = FILE_FORMATS[ext]
        savefileFromTable(self, path, format, sampletype, quality)

    def write(self, path, oneline=True):
        """
        Writes the content of the table in a text file.

        This function can be used to store the table data as a
        list of floats into a text file.

        :Args:

            path: string
                Full path of the generated file.
            oneline: boolean, optional
                If True, list of samples will inserted on one line.

                If False, list of samples will be truncated to 8 floats
                per line.

        """
        pyoArgsAssert(self, "SB", path, oneline)
        f = open(path, "w")
        if oneline:
            f.write(str([obj.getTable() for obj in self._base_objs]))
        else:
            text = "["
            for obj in self._base_objs:
                text += "["
                for i, val in enumerate(obj.getTable()):
                    if (i % 8) == 0:
                        text += "\n"
                    text += str(val) + ", "
                text += "]"
            text += "]"
            f.write(text)
        f.close()

    def read(self, path):
        """
        Reads the content of a text file and replaces the table data
        with the values stored in the file.

        :Args:

            path: string
                Full path of the file to read.

        The format is a list of lists of floats. For example, A two
        tablestreams object must be given a content like this:

        [ [ 0.0, 1.0, 0.5, ... ], [ 1.0, 0.99, 0.98, 0.97, ... ] ]

        Each object's tablestream will be resized according to the
        length of the lists.

        """
        pyoArgsAssert(self, "S", path)
        f = open(path, "r")
        f_list = eval(f.read())
        f_len = len(f_list)
        f.close()
        [obj.setData(f_list[i%f_len]) for i, obj in enumerate(self._base_objs)]
        self.refreshView()

    def getBuffer(self, chnl=0):
        """
        Return a reference to the underlying object implementing the buffer protocol.

        With the buffer protocol, a table can be referenced and modified,
        without copying the data, with numpy functions. To create an array
        using the same memory as the table:

            t = SndTable(SNDS_PATH+"/transparent.aif")
            arr = numpy.asarray(t.getBuffer())

        Now, every changes applied to the array will be reflected in
        the SndTable.

        For more details about the buffer protocol, see PEP 3118 and
        python documentation.

        """
        if chnl < 0 or chnl >= len(self):
            print("getBuffer(chnl): `chnl` argument out-of-range...")
        else:
            return self._base_objs[chnl].getTableStream()

    def setSize(self, size):
        """
        Change the size of the table.

        This will erase the previously drawn waveform.

        :Args:

            size: int
                New table size in samples.

        """
        pyoArgsAssert(self, "I", size)
        self._size = size
        [obj.setSize(size) for obj in self._base_objs]
        self.refreshView()

    def getSize(self, all=False):
        """
        Return table size in samples.

        :Args:

            all: boolean
                If the table contains more than one stream and `all` is True,
                returns a list of all sizes. Otherwise, returns only the
                first size as an int. Defaults to False.

        """
        pyoArgsAssert(self, "B", all)
        if all:
            return [obj.getSize() for obj in self._base_objs]
        else:
            if isinstance(self._size, list):
                return self._size[0]
            else:
                return self._size

    def put(self, value, pos=0):
        """
        Puts a value at specified sample position in the table.

        If the object has more than 1 tablestream, the default is to
        record the value in each table. User can call obj[x].put()
        to record into a specific table.

        :Args:

            value: float
                Value, as floating-point, to record in the table.
            pos: int, optional
                Position, in samples, where to record value. Defaults to 0.

        """
        pyoArgsAssert(self, "NI", value, pos)
        [obj.put(value, pos) for obj in self._base_objs]
        self.refreshView()

    def get(self, pos):
        """
        Returns the value, as float, stored at a specific position in the table.

        If the object has more than 1 tablestream, the default is to
        return a list with the value of each tablestream. User can call
        obj[x].get() to get the value of a specific table.

        :Args:

            pos: int, optional
                Position, in samples, where to read the value. Defaults to 0.

        """
        pyoArgsAssert(self, "I", pos)
        values = [obj.get(pos) for obj in self._base_objs]
        if len(values) == 1:
            return values[0]
        else:
            return values

    def getTable(self, all=False):
        """
        Returns the content of the table as list of floats.

        :Args:

            all: boolean, optional
                If True, all sub tables are retrieved and returned as a list
                of list of floats.

                If False, a single list containing the content of the first
                subtable (or the only one) is returned.

        """
        pyoArgsAssert(self, "B", all)
        if all:
            return [obj.getTable() for obj in self._base_objs]
        else:
            return self._base_objs[0].getTable()

    def normalize(self):
        """
        Normalize table samples between -1 and 1.

        """
        [obj.normalize() for obj in self._base_objs]
        self.refreshView()
        return self

    def reset(self):
        """
        Resets table samples to 0.0.

        """
        [obj.reset() for obj in self._base_objs]
        self.refreshView()
        return self

    def removeDC(self):
        """
        Filter out DC offset from the table's data.

        """
        [obj.removeDC() for obj in self._base_objs]
        self.refreshView()
        return self

    def reverse(self):
        """
        Reverse the table's data in time.

        """
        [obj.reverse() for obj in self._base_objs]
        self.refreshView()
        return self

    def invert(self):
        """
        Reverse the table's data in amplitude.

        """
        [obj.invert() for obj in self._base_objs]
        self.refreshView()
        return self

    def rectify(self):
        """
        Positive rectification of the table's data.

        """
        [obj.rectify() for obj in self._base_objs]
        self.refreshView()
        return self

    def pow(self, exp=10):
        """
        Apply a power function on each sample in the table.

        :Args:

            exp: float, optional
                Exponent factor. Defaults to 10.

        """
        pyoArgsAssert(self, "N", exp)
        [obj.pow(exp) for obj in self._base_objs]
        self.refreshView()
        return self

    def bipolarGain(self, gpos=1, gneg=1):
        """
        Apply different gain factor for positive and negative samples.

        :Args:

            gpos: float, optional
                Gain factor for positive samples. Defaults to 1.
            gneg: float, optional
                Gain factor for negative samples. Defaults to 1.

        """
        pyoArgsAssert(self, "NN", gpos, gneg)
        [obj.bipolarGain(gpos, gneg) for obj in self._base_objs]
        self.refreshView()
        return self

    def lowpass(self, freq=1000):
        """
        Apply a one-pole lowpass filter on table's samples.

        :Args:

            freq: float, optional
                Filter's cutoff, in Hertz. Defaults to 1000.

        """
        pyoArgsAssert(self, "N", freq)
        [obj.lowpass(freq) for obj in self._base_objs]
        self.refreshView()
        return self

    def fadein(self, dur=0.1):
        """
        Apply a gradual increase in the level of the table's samples.

        :Args:

            dur: float, optional
                Fade in duration, in seconds. Defaults to 0.1.

        """
        pyoArgsAssert(self, "N", dur)
        [obj.fadein(dur) for obj in self._base_objs]
        self.refreshView()
        return self

    def fadeout(self, dur=0.1):
        """
        Apply a gradual decrease in the level of the table's samples.

        :Args:

            dur: float, optional
                Fade out duration, in seconds. Defaults to 0.1.

        """
        pyoArgsAssert(self, "N", dur)
        [obj.fadeout(dur) for obj in self._base_objs]
        self.refreshView()
        return self

    def add(self, x):
        """
        Performs addition on the table values.

        Adds the argument to each table values, position by position
        if the argument is a list or another PyoTableObject.

        :Args:

            x: float, list or PyoTableObject
                value(s) to add.

        """
        pyoArgsAssert(self, "T", x)
        if isinstance(x, list):
            if isinstance(x[0], list):
                [obj.add(wrap(x, i)) for i, obj in enumerate(self._base_objs)]
            else:
                [obj.add(x) for obj in self._base_objs]
        else:
            x, _ = convertArgsToLists(x)
            [obj.add(wrap(x, i)) for i, obj in enumerate(self._base_objs)]
        self.refreshView()
        return self

    def sub(self, x):
        """
        Performs substraction on the table values.

        Substracts the argument to each table values, position by position
        if the argument is a list or another PyoTableObject.

        :Args:

            x: float, list or PyoTableObject
                value(s) to substract.

        """
        pyoArgsAssert(self, "T", x)
        if isinstance(x, list):
            if isinstance(x[0], list):
                [obj.sub(wrap(x, i)) for i, obj in enumerate(self._base_objs)]
            else:
                [obj.sub(x) for obj in self._base_objs]
        else:
            x, _ = convertArgsToLists(x)
            [obj.sub(wrap(x, i)) for i, obj in enumerate(self._base_objs)]
        self.refreshView()
        return self

    def mul(self, x):
        """
        Performs multiplication on the table values.

        Multiply each table values by the argument, position by position
        if the argument is a list or another PyoTableObject.

        :Args:

            x: float, list or PyoTableObject
                value(s) to multiply.

        """
        pyoArgsAssert(self, "T", x)
        if isinstance(x, list):
            if isinstance(x[0], list):
                [obj.mul(wrap(x, i)) for i, obj in enumerate(self._base_objs)]
            else:
                [obj.mul(x) for obj in self._base_objs]
        else:
            x, _ = convertArgsToLists(x)
            [obj.mul(wrap(x, i)) for i, obj in enumerate(self._base_objs)]
        self.refreshView()
        return self

    def copyData(self, table, srcpos=0, destpos=0, length=-1):
        """
        Copy samples from a source table.

        Copy `length` samples from a source table to this table.

        :Args:

            table: PyoTableObject
                The source table.
            srcpos: int, optional
                The start position in the source table. Defaults to 0.
            destpos ; int, optional
                The start position in the destination (self) table. Defaults
                to 0.
            length: int, optional
                The number of samples to copy from source to destination. if
                length is negative, the length of the smallest table is used.
                Defaults to -1.

        """
        pyoArgsAssert(self, "tIII", table, srcpos, destpos, length)
        [obj.copyData(table[i], srcpos,
                      destpos, length) for i, obj in enumerate(self._base_objs)]
        self.refreshView()

    def rotate(self, pos):
        """
        Rotate the table content to the left around the position given as argument.

        Samples between the given position and the end of the table will
        be relocated in front of the samples from the beginning to the
        given position.

        :Args:

            pos: int
                The rotation position in samples. A negative position means
                a rotation to the right.

        """
        pyoArgsAssert(self, "I", pos)
        [obj.rotate(pos) for obj in self._base_objs]
        self.refreshView()

    def copy(self):
        """
        Returns a deep copy of the object.

        """
        args = [getattr(self, att) for att in self.__dir__()]
        if self.__class__.__name__ == "SndTable":
            _size = self.getSize()
            if not isinstance(_size, list):
                _size = [_size]
            _chnls = len(self._base_objs)
            args[0] = None
            args.append(_chnls)
            newtable = getattr(current_pyo, self.__class__.__name__)(*args)
            baseobjs = newtable.getBaseObjects()
            [obj.setSize(_size[i%len(_size)]) for i, obj in enumerate(baseobjs)]
            [obj.copy(self[i]) for i, obj in enumerate(newtable.getBaseObjects())]
        else:
            newtable = getattr(current_pyo, self.__class__.__name__)(*args)
            [obj.copy(self[i]) for i, obj in enumerate(newtable.getBaseObjects())]
        return newtable

    def view(self, title="Table waveform", wxnoserver=False):
        """
        Opens a window showing the contents of the table.

        :Args:

            title: string, optional
                Window title. Defaults to "Table waveform".
            wxnoserver: boolean, optional
                With wxPython graphical toolkit, if True, tells the
                interpreter that there will be no server window.

        If `wxnoserver` is set to True, the interpreter will not wait for
        the server GUI before showing the controller window.

        """
        pyoArgsAssert(self, "SB", title, wxnoserver)
        samples = self._base_objs[0].getViewTable((500, 200))
        createViewTableWindow(samples, title, wxnoserver,
                              self.__class__.__name__, self)

    def _setViewFrame(self, frame):
        self.viewFrame = frame

    def _setGraphFrame(self, frame):
        self.graphFrame = frame

    def _get_current_data(self):
        # Thid method must be override by children.
        return []

    def refreshView(self):
        """
        Updates the graphical display of the table, if applicable.

        """
        if self.viewFrame is not None:
            size = self.viewFrame.wavePanel.GetSize()
            samples = self._base_objs[0].getViewTable((size[0], size[1]))
            self.viewFrame.update(samples)
        if self.graphFrame is not None:
            data = self._get_current_data()
            length = len(data)
            flength = self.graphFrame.getLength()
            if length < flength:
                data = data + [0] * (flength - length)
            elif length > flength:
                data = data[:flength]
            self.graphFrame.update(data)

    @property
    def size(self):
        """int. Table size in samples."""
        return self._size
    @size.setter
    def size(self, x):
        self.setSize(x)

######################################################################
### PyoMatrixObject -> base class for pyo matrix objects
######################################################################
class PyoMatrixObject(PyoObjectBase):
    """
    Base class for all pyo matrix objects.

    A matrix object is a 2 dimensions buffer memory to store
    precomputed samples.

    The user should never instantiate an object of this class.

    :Parent: :py:class:`PyoObjectBase`

    """

    _STREAM_TYPE = 'matrix'

    def __init__(self):
        self._size = (0, 0)
        PyoObjectBase.__init__(self)
        self.viewFrame = None

    def write(self, path):
        """
        Writes the content of the matrix into a text file.

        This function can be used to store the matrix data as a
        list of list of floats into a text file.

        :Args:

            path: string
                Full path of the generated file.

        """
        pyoArgsAssert(self, "S", path)
        f = open(path, "w")
        f.write(str([obj.getData() for obj in self._base_objs]))
        f.close()

    def read(self, path):
        """
        Reads the content of a text file and replaces the matrix data
        with the values in the file.

        Format is a list of lists of floats. For example, A two
        matrixstreams object must be given a content like this:

        [ [ [0.0 ,1.0, 0.5, ... ], [1.0, 0.99, 0.98, 0.97, ... ] ],
        [ [0.0, 1.0, 0.5, ... ], [1.0, 0.99, 0.98, 0.97, ... ] ] ]

        Each object's matrixstream will be resized according to the
        length of the lists, but the number of matrixstreams must be
        the same.

        :Args:

            path: string
                Full path of the file to read.

        """
        pyoArgsAssert(self, "S", path)
        f = open(path, "r")
        f_list = eval(f.read())
        f_len = len(f_list)
        f.close()
        [obj.setData(f_list[i%f_len]) for i, obj in enumerate(self._base_objs)]

    def getSize(self):
        """
        Returns matrix size in samples. Size is a tuple (x, y).

        """
        return self._size

    def normalize(self):
        """
        Normalize matrix samples between -1 and 1.

        """
        [obj.normalize() for obj in self._base_objs]
        return self

    def blur(self):
        """
        Apply a simple gaussian blur on the matrix.

        """
        [obj.blur() for obj in self._base_objs]

    def boost(self, min=-1.0, max=1.0, boost=0.01):
        """
        Boost the constrast of values in the matrix.

        :Args:

            min: float, optional
                Minimum value. Defaults to -1.0.
            max: float, optional
                Maximum value. Defaults to 1.0.
            boost: float, optional
                Amount of boost applied on each value. Defaults to 0.01.

        """
        pyoArgsAssert(self, "NNN", min, max, boost)
        [obj.boost(min, max, boost) for obj in self._base_objs]

    def put(self, value, x=0, y=0):
        """
        Puts a value at specified position in the matrix.

        If the object has more than 1 matrixstream, the default is to
        record the value in each matrix. User can call obj[x].put()
        to record in a specific matrix.

        :Args:

            value: float
                Value, as floating-point, to record in the matrix.
            x: int, optional
                X position where to record value. Defaults to 0.
            y: int, optional
                Y position where to record value. Defaults to 0.

        """
        pyoArgsAssert(self, "NII", value, x, y)
        [obj.put(value, x, y) for obj in self._base_objs]

    def get(self, x, y):
        """
        Returns the value, as float, at specified position in the matrix.

        If the object has more than 1 matrixstream, the default is to
        return a list with the value of each matrixstream. User can call
        obj[x].get() to get the value of a specific matrix.

        :Args:

            x: int, optional
                X position where to get value. Defaults to 0.
            y: int, optional
                Y position where to get value. Defaults to 0.

        """
        pyoArgsAssert(self, "II", x, y)
        values = [obj.get(x, y) for obj in self._base_objs]
        if len(values) == 1:
            return values[0]
        else:
            return values

    def view(self, title="Matrix viewer", wxnoserver=False):
        """
        Opens a window showing the contents of the matrix.

        :Args:

            title: string, optional
                Window title. Defaults to "Matrix viewer".
            wxnoserver: boolean, optional
                With wxPython graphical toolkit, if True, tells the
                interpreter that there will be no server window.

        If `wxnoserver` is set to True, the interpreter will not wait for
        the server GUI before showing the controller window.

        """
        pyoArgsAssert(self, "SB", title, wxnoserver)
        samples = self._base_objs[0].getImageData()
        createViewMatrixWindow(samples, self.getSize(), title, wxnoserver, self)

    def _setViewFrame(self, frame):
        self.viewFrame = frame

    def refreshView(self):
        """
        Updates the graphical display of the matrix, if applicable.

        """
        if self.viewFrame is not None:
            samples = self._base_objs[0].getImageData()
            self.viewFrame.update(samples)

######################################################################
### PyoObject -> base class for pyo phase vocoder objects
######################################################################
class PyoPVObject(PyoObjectBase):
    """
    Base class for objects working with phase vocoder's magnitude and frequency streams.

    The user should never instantiate an object of this class.

    :Parent: :py:class:`PyoObjectBase`

    """

    _STREAM_TYPE = 'pvoc'

    def __init__(self):
        PyoObjectBase.__init__(self)
        self._target_dict = {}
        self._signal_dict = {}
        self._map_list = []
        self._base_players = None

    def isPlaying(self, all=False):
        """
        Returns True if the object is playing, otherwise, returns False.

        :Args:

            all: boolean, optional
                If True, the object returns a list with the state of all
                streams managed by the object.

                If False, it return a boolean corresponding to the state
                of the first stream.

        """
        pyoArgsAssert(self, "B", all)
        if all:
            return [obj._getStream().isPlaying() for obj in self._base_objs]
        else:
            return self._base_objs[0]._getStream().isPlaying()

    def play(self, dur=0, delay=0):
        """
        Start processing without sending samples to output.
        This method is called automatically at the object creation.

        This method returns `self`, allowing it to be applied at the object
        creation.

        :Args:

            dur: float, optional
                Duration, in seconds, of the object's activation.
                The default is 0 and means infinite duration.
            delay: float, optional
                Delay, in seconds, before the object's activation.
                Defaults to 0.

        """
        pyoArgsAssert(self, "nn", dur, delay)
        dur, delay, _ = convertArgsToLists(dur, delay)
        if self._trig_objs is not None:
            self._trig_objs.play(dur, delay)
        if self._base_players is not None:
            [obj.play(wrap(dur, i), wrap(delay, i)) \
             for i, obj in enumerate(self._base_players)]
        [obj.play(wrap(dur, i), wrap(delay, i)) \
         for i, obj in enumerate(self._base_objs)]
        return self

    def stop(self):
        """
        Stop processing.

        This method returns `self`, allowing it to be applied at the object
        creation.

        """
        if self._trig_objs is not None:
            self._trig_objs.stop()
        if self._base_players is not None:
            [obj.stop() for obj in self._base_players]
        [obj.stop() for obj in self._base_objs]
        return self

    def set(self, attr, value, port=0.025):
        """
        Replace any attribute with portamento.

        This method is intended to be applied on attributes that are not
        already assigned to PyoObjects. It will work only with floats or
        list of floats.

        :Args:

            attr: string
                Name of the attribute as a string.
            value: float
                New value.
            port: float, optional
                Time, in seconds, to reach the new value.

        """
        pyoArgsAssert(self, "Snn", attr, value, port)
        self._target_dict[attr] = value
        init = getattr(self, attr)
        if attr in self._signal_dict:
            if isinstance(self._signal_dict[attr], VarPort):
                if self._signal_dict[attr].isPlaying():
                    init = self._signal_dict[attr].get(True)
                    self._signal_dict[attr].stop()
        self._signal_dict[attr] = VarPort(value, port, init,
                                          self._reset_from_set, attr)
        setattr(self, attr, self._signal_dict[attr])

    def _reset_from_set(self, attr=None):
        if isinstance(getattr(self, attr), VarPort):
            setattr(self, attr, self._target_dict[attr])
        self._signal_dict[attr].stop()

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        """
        Opens a sliders window to control the parameters of the object.
        Only parameters that can be set to a PyoObject are allowed
        to be mapped on a slider.

        If a list of values are given to a parameter, a multisliders
        will be used to control each stream independently.

        :Args:

            map_list: list of SLMap objects, optional
                Users defined set of parameters scaling. There is default
                scaling for each object that accept `ctrl` method.
            title: string, optional
                Title of the window. If none is provided, the name of the
                class is used.
            wxnoserver: boolean, optional
                With wxPython graphical toolkit, if True, tells the
                interpreter that there will be no server window.

        If `wxnoserver` is set to True, the interpreter will not wait for
        the server GUI before showing the controller window.

        """
        if map_list is None:
            map_list = self._map_list
        if map_list == []:
            clsname = self.__class__.__name__
            print("There are no controls for %s object." % clsname)
            return
        createCtrlWindow(self, map_list, title, wxnoserver)

######################################################################
### Internal classes -> Used by pyo
######################################################################
class Mix(PyoObject):
    """
    Mix audio streams to arbitrary number of streams.

    Mix the object's audio streams as `input` argument into `voices`
    streams.

    :Parent: :py:class:`PyoObject`

    :Args:

        input: PyoObject or list of PyoObjects
            Input signal(s) to mix the streams.
        voices: int, optional
            Number of streams of the Mix object. If more than 1, input
            object's streams are alternated and added into Mix object's
            streams. Defaults to 1.

    .. note::

        The mix method of PyoObject creates and returns a new Mix object
        with mixed streams of the object that called the method. User
        don't have to instantiate this class directly. These two calls
        are identical:

        >>> b = a.mix()
        >>> b = Mix(a)

    >>> s = Server().boot()
    >>> s.start()
    >>> a = Sine([random.uniform(400,600) for i in range(50)], mul=.02)
    >>> b = Mix(a, voices=2).out()
    >>> print(len(a))
    50
    >>> print(len(b))
    1

    """
    def __init__(self, input, voices=1, mul=1, add=0):
        pyoArgsAssert(self, "oIOO", input, voices, mul, add)
        PyoObject.__init__(self, mul, add)
        self._input = input
        mul, add, lmax = convertArgsToLists(mul, add)
        if isinstance(input, list):
            input_objs = []
            input_objs = [obj for pyoObj in input for obj in pyoObj.getBaseObjects()]
        else:
            input_objs = input.getBaseObjects()
        input_len = len(input_objs)
        if voices < 1:
            voices = 1
            num = 1
        elif voices > input_len and voices > lmax:
            num = voices
        elif lmax > input_len:
            num = lmax
        else:
            num = input_len
        sub_lists = []
        for i in range(voices):
            sub_lists.append([])
        for i in range(num):
            obj = input_objs[i % input_len]
            sub_lists[i % voices].append(obj)
        self._base_objs = [Mix_base(l, wrap(mul, i),
                                    wrap(add, i)) for i, l in enumerate(sub_lists)]
        self.play()

class Dummy(PyoObject):
    """
    Dummy object used to perform arithmetics on PyoObject.

    The user should never instantiate an object of this class.

    :Parent: :py:class:`PyoObject`

    :Args:

        objs_list: list of audio Stream objects
            List of Stream objects return by the PyoObject hidden method
            getBaseObjects().

    .. note::

        Multiplication, addition, division and substraction don't changed
        the PyoObject on which the operation is performed. A dummy object
        is created, which is just a copy of the audio Streams of the object,
        and the operation is applied on the Dummy, leaving the original
        object unchanged. This lets the user performs multiple different
        arithmetic operations on an object without conficts. Here, `b` is
        a Dummy object with `a` as its input with a `mul` attribute of 0.5.
        attribute:

        >>> a = Sine()
        >>> b = a * .5
        >>> print(a)
        <pyolib.input.Sine object at 0x11fd610>
        >>> print(b)
        <pyolib._core.Dummy object at 0x11fd710>

    >>> s = Server().boot()
    >>> s.start()
    >>> m = Metro(time=0.25).play()
    >>> p = TrigChoice(m, choice=[midiToHz(n) for n in [60,62,65,67,69]])
    >>> a = SineLoop(p, feedback=.05, mul=.1).mix(2).out()
    >>> b = SineLoop(p*1.253, feedback=.05, mul=.06).mix(2).out()
    >>> c = SineLoop(p*1.497, feedback=.05, mul=.03).mix(2).out()

    """
    def __init__(self, objs_list):
        PyoObject.__init__(self)
        self._objs_list = objs_list
        tmp_list = []
        for x in objs_list:
            if isinstance(x, Dummy):
                tmp_list.extend(x.getBaseObjects())
            else:
                tmp_list.append(x)
        self._base_objs = tmp_list

class InputFader(PyoObject):
    """
    Audio streams crossfader.

    :Args:

        input: PyoObject
            Input signal.

    .. note::

        The setInput method, available to object with `input` attribute,
        uses an InputFader object internally to perform crossfade between
        the old and the new audio input assigned to the object.

    >>> s = Server().boot()
    >>> s.start()
    >>> a = SineLoop([449,450], feedback=0.05, mul=.2)
    >>> b = SineLoop([650,651], feedback=0.05, mul=.2)
    >>> c = InputFader(a).out()
    >>> # to created a crossfade, assign a new audio input:
    >>> c.setInput(b, fadetime=5)

    """
    def __init__(self, input):
        pyoArgsAssert(self, "o", input)
        PyoObject.__init__(self)
        self._input = input
        input, lmax = convertArgsToLists(input)
        self._base_objs = [InputFader_base(wrap(input, i)) for i in range(lmax)]
        self.play()

    def setInput(self, x, fadetime=0.05):
        """
        Replace the `input` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Defaults to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._input = x
        x, _ = convertArgsToLists(x)
        [obj.setInput(wrap(x, i),
                      fadetime) for i, obj in enumerate(self._base_objs)]

    @property
    def input(self):
        """PyoObject. Input signal."""
        return self._input
    @input.setter
    def input(self, x):
        self.setInput(x)

class Sig(PyoObject):
    """
    Convert numeric value to PyoObject signal.

    :Parent: :py:class:`PyoObject`

    :Args:

        value: float or PyoObject
            Numerical value to convert.

    >>> import random
    >>> s = Server().boot()
    >>> s.start()
    >>> fr = Sig(value=400)
    >>> p = Port(fr, risetime=0.001, falltime=0.001)
    >>> a = SineLoop(freq=p, feedback=0.08, mul=.3).out()
    >>> b = SineLoop(freq=p*1.005, feedback=0.08, mul=.3).out(1)
    >>> def pick_new_freq():
    ...     fr.value = random.randrange(300,601,50)
    >>> pat = Pattern(function=pick_new_freq, time=0.5).play()

    """
    def __init__(self, value, mul=1, add=0):
        pyoArgsAssert(self, "OOO", value, mul, add)
        PyoObject.__init__(self, mul, add)
        self._value = value
        value, mul, add, lmax = convertArgsToLists(value, mul, add)
        self._base_objs = [Sig_base(wrap(value, i), wrap(mul, i),
                                    wrap(add, i)) for i in range(lmax)]
        self.play()

    def setValue(self, x):
        """
        Changes the value of the signal stream.

        :Args:

            x: float or PyoObject
                Numerical value to convert.

        """
        pyoArgsAssert(self, "O", x)
        self._value = x
        x, _ = convertArgsToLists(x)
        [obj.setValue(wrap(x, i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0, 1, "lin", "value", self._value)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def value(self):
        """float or PyoObject. Numerical value to convert."""
        return self._value
    @value.setter
    def value(self, x):
        self.setValue(x)

class VarPort(PyoObject):
    """
    Convert numeric value to PyoObject signal with portamento.

    When `value` attribute is changed, a smoothed ramp is applied from the
    current value to the new value. If a callback is provided as `function`
    argument, it will be called at the end of the line.

    :Parent: :py:class:`PyoObject`

    :Args:

        value: float
            Numerical value to convert.
        time: float, optional
            Ramp time, in seconds, to reach the new value. Defaults to 0.025.
        init: float, optional
            Initial value of the internal memory. Defaults to 0.
        function: Python callable, optional
            If provided, it will be called at the end of the line.
            Defaults to None.
        arg: any Python object, optional
            Optional argument sent to the function called at the end of the line.
            Defaults to None.

    .. note::

        The out() method is bypassed. VarPort's signal can not be sent to
        audio outs.

    >>> s = Server().boot()
    >>> s.start()
    >>> def callback(arg):
    ...     print("end of line")
    ...     print(arg)
    ...
    >>> fr = VarPort(value=500, time=2, init=250, function=callback, arg="YEP!")
    >>> a = SineLoop(freq=[fr,fr*1.01], feedback=0.05, mul=.2).out()

    """
    def __init__(self, value, time=0.025, init=0.0, function=None, arg=None,
                 mul=1, add=0):
        pyoArgsAssert(self, "nnnczOO", value, time, init, function, arg, mul, add)
        PyoObject.__init__(self, mul, add)
        self._value = value
        self._time = time
        self._function = getWeakMethodRef(function)
        value, time, init, function, arg, mul, add, lmax = convertArgsToLists(
            value, time, init, function, arg, mul, add)
        self._base_objs = [VarPort_base(wrap(value, i), wrap(time, i), wrap(init, i),
                                        WeakMethod(wrap(function, i)), wrap(arg, i),
                                        wrap(mul, i), wrap(add, i)) for i in range(lmax)]
        self.play()

    def setValue(self, x):
        """
        Changes the value of the signal stream.

        :Args:

            x: float
                Numerical value to convert.

        """
        pyoArgsAssert(self, "n", x)
        self._value = x
        x, _ = convertArgsToLists(x)
        [obj.setValue(wrap(x, i)) for i, obj in enumerate(self._base_objs)]

    def setTime(self, x):
        """
        Changes the ramp time of the object.

        :Args:

            x: float
                New ramp time.

        """
        pyoArgsAssert(self, "n", x)
        self._time = x
        x, _ = convertArgsToLists(x)
        [obj.setTime(wrap(x, i)) for i, obj in enumerate(self._base_objs)]

    def setFunction(self, x):
        """
        Replace the `function` attribute.

        :Args:

            x: Python function
                new `function` attribute.

        """
        pyoArgsAssert(self, "c", x)
        self._function = getWeakMethodRef(x)
        x, _ = convertArgsToLists(x)
        [obj.setFunction(WeakMethod(wrap(x, i))) \
         for i, obj in enumerate(self._base_objs)]

    @property
    def value(self):
        """float. Numerical value to convert."""
        return self._value
    @value.setter
    def value(self, x):
        self.setValue(x)

    @property
    def time(self):
        """float. Ramp time."""
        return self._time
    @time.setter
    def time(self, x):
        self.setTime(x)

    @property
    def function(self):
        """Python callable. Function to be called."""
        return self._function
    @function.setter
    def function(self, x):
        self.setFunction(x)

class Pow(PyoObject):
    """
    Performs a power function on audio signal.

    :Parent: :py:class:`PyoObject`

    :Args:

        base: float or PyoObject, optional
            Base composant. Defaults to 10.
        exponent: float or PyoObject, optional
            Exponent composant. Defaults to 1.

    >>> s = Server().boot()
    >>> s.start()
    >>> # Exponential amplitude envelope
    >>> a = LFO(freq=1, type=3, mul=0.5, add=0.5)
    >>> b = Pow(Clip(a, 0, 1), 4, mul=.3)
    >>> c = SineLoop(freq=[300,301], feedback=0.05, mul=b).out()

    """
    def __init__(self, base=10, exponent=1, mul=1, add=0):
        pyoArgsAssert(self, "OOOO", base, exponent, mul, add)
        PyoObject.__init__(self, mul, add)
        self._base = base
        self._exponent = exponent
        base, exponent, mul, add, lmax = convertArgsToLists(base, exponent, mul, add)
        self._base_objs = [M_Pow_base(wrap(base, i), wrap(exponent, i),
                                      wrap(mul, i), wrap(add, i)) for i in range(lmax)]
        self.play()

    def setBase(self, x):
        """
        Replace the `base` attribute.

        :Args:

            x: float or PyoObject
                new `base` attribute.

        """
        pyoArgsAssert(self, "O", x)
        self._base = x
        x, _ = convertArgsToLists(x)
        [obj.setBase(wrap(x, i)) for i, obj in enumerate(self._base_objs)]

    def setExponent(self, x):
        """
        Replace the `exponent` attribute.

        :Args:

            x: float or PyoObject
                new `exponent` attribute.

        """
        pyoArgsAssert(self, "O", x)
        self._exponent = x
        x, _ = convertArgsToLists(x)
        [obj.setExponent(wrap(x, i)) for i, obj in enumerate(self._base_objs)]

    @property
    def base(self):
        """float or PyoObject. Base composant."""
        return self._base
    @base.setter
    def base(self, x):
        self.setBase(x)

    @property
    def exponent(self):
        """float or PyoObject. Exponent composant."""
        return self._exponent
    @exponent.setter
    def exponent(self, x):
        self.setExponent(x)

class Wrap(PyoObject):
    """
    Wraps-around the signal that exceeds the `min` and `max` thresholds.

    This object is useful for table indexing, phase shifting or for
    clipping and modeling an audio signal.

    :Parent: :py:class:`PyoObject`

    :Args:

        input: PyoObject
            Input signal to process.
        min: float or PyoObject, optional
            Minimum possible value. Defaults to 0.
        max: float or PyoObject, optional
            Maximum possible value. Defaults to 1.

    .. note::

        If `min` is higher than `max`, then the output will be the average
        of the two.

    >>> s = Server().boot()
    >>> s.start()
    >>> # Time-varying overlaping envelopes
    >>> env = HannTable()
    >>> lff = Sine(.5, mul=3, add=4)
    >>> ph1 = Phasor(lff)
    >>> ph2 = Wrap(ph1+0.5, min=0, max=1)
    >>> amp1 = Pointer(env, ph1, mul=.25)
    >>> amp2 = Pointer(env, ph2, mul=.25)
    >>> a = SineLoop(250, feedback=.1, mul=amp1).out()
    >>> b = SineLoop(300, feedback=.1, mul=amp2).out(1)

    """
    def __init__(self, input, min=0.0, max=1.0, mul=1, add=0):
        pyoArgsAssert(self, "oOOOO", input, min, max, mul, add)
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._min = min
        self._max = max
        self._in_fader = InputFader(input)
        in_fader, min, max, mul, add, lmax = convertArgsToLists(
            self._in_fader, min, max, mul, add)
        self._base_objs = [Wrap_base(wrap(in_fader, i), wrap(min, i), wrap(max, i),
                                     wrap(mul, i), wrap(add, i)) for i in range(lmax)]
        self.play()

    def setInput(self, x, fadetime=0.05):
        """
        Replace the `input` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Defaults to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._input = x
        self._in_fader.setInput(x, fadetime)

    def setMin(self, x):
        """
        Replace the `min` attribute.

        :Args:

            x: float or PyoObject
                New `min` attribute.

        """
        pyoArgsAssert(self, "O", x)
        self._min = x
        x, _ = convertArgsToLists(x)
        [obj.setMin(wrap(x, i)) for i, obj in enumerate(self._base_objs)]

    def setMax(self, x):
        """
        Replace the `max` attribute.

        :Args:

            x: float or PyoObject
                New `max` attribute.

        """
        pyoArgsAssert(self, "O", x)
        self._max = x
        x, _ = convertArgsToLists(x)
        [obj.setMax(wrap(x, i)) for i, obj in enumerate(self._base_objs)]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0., 1., 'lin', 'min', self._min),
                          SLMap(0., 1., 'lin', 'max', self._max),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self):
        """PyoObject. Input signal to process."""
        return self._input
    @input.setter
    def input(self, x):
        self.setInput(x)

    @property
    def min(self):
        """float or PyoObject. Minimum possible value."""
        return self._min
    @min.setter
    def min(self, x):
        self.setMin(x)

    @property
    def max(self):
        """float or PyoObject. Maximum possible value."""
        return self._max
    @max.setter
    def max(self, x):
        self.setMax(x)

class Compare(PyoObject):
    """
    Comparison object.

    Compare evaluates a comparison between a PyoObject and a number or
    between two PyoObjects and outputs 1.0, as audio stream, if the
    comparison is true, otherwise outputs 0.0.

    :Parent: :py:class:`PyoObject`

    :Args:

        input: PyoObject
            Input signal.
        comp: float or PyoObject
            comparison signal.
        mode: string, optional
            Comparison operator as a string. Allowed operator are "<", "<=",
            ">", ">=", "==", "!=". Default to "<".

    >>> s = Server().boot()
    >>> s.start()
    >>> a = SineLoop(freq=[199,200], feedback=.1, mul=.2)
    >>> b = SineLoop(freq=[149,150], feedback=.1, mul=.2)
    >>> ph = Phasor(freq=1)
    >>> ch = Compare(input=ph, comp=0.5, mode="<=")
    >>> out = Selector(inputs=[a,b], voice=Port(ch)).out()

    """
    def __init__(self, input, comp, mode="<", mul=1, add=0):
        pyoArgsAssert(self, "oOsOO", input, comp, mode, mul, add)
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._comp = comp
        self._mode = mode
        self._in_fader = InputFader(input)
        self.comp_dict = {"<": 0, "<=": 1, ">": 2, ">=": 3, "==": 4, "!=": 5}
        in_fader, comp, mode, mul, add, lmax = convertArgsToLists(
            self._in_fader, comp, mode, mul, add)
        self._base_objs = [Compare_base(wrap(in_fader, i),
                                        wrap(comp, i),
                                        self.comp_dict[wrap(mode, i)],
                                        wrap(mul, i),
                                        wrap(add, i)) for i in range(lmax)]
        self.play()

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        return self.play(dur, delay)

    def setInput(self, x, fadetime=0.05):
        """
        Replace the `input` attribute.

        :Args:

            x: PyoObject
                New signal to process.
            fadetime: float, optional
                Crossfade time between old and new input. Default to 0.05.

        """
        pyoArgsAssert(self, "oN", x, fadetime)
        self._input = x
        self._in_fader.setInput(x, fadetime)

    def setComp(self, x):
        """
        Replace the `comp` attribute.

        :Args:

            x: float or PyoObject
                New comparison signal.

        """
        pyoArgsAssert(self, "O", x)
        self._comp = x
        x, _ = convertArgsToLists(x)
        [obj.setComp(wrap(x, i)) for i, obj in enumerate(self._base_objs)]

    def setMode(self, x):
        """
        Replace the `mode` attribute.

        Allowed operator are "<", "<=", ">", ">=", "==", "!=".

        :Args:

            x: string
                New `mode` attribute.

        """
        pyoArgsAssert(self, "s", x)
        self._mode = x
        x, _ = convertArgsToLists(x)
        [obj.setMode(self.comp_dict[wrap(x, i)]) \
         for i, obj in enumerate(self._base_objs)]

    @property
    def input(self):
        """PyoObject. Input signal."""
        return self._input
    @input.setter
    def input(self, x):
        self.setInput(x)

    @property
    def comp(self):
        """PyoObject. Comparison signal."""
        return self._comp
    @comp.setter
    def comp(self, x):
        self.setComp(x)

    @property
    def mode(self):
        """string. Comparison operator."""
        return self._mode
    @mode.setter
    def mode(self, x):
        self.setMode(x)

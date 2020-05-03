"""
Authors: Adam Li and Patrick Myers.

Version: 1.0
"""
import sys


class NoTraceBackWithLineNumber(Exception):
    def __init__(self, msg):
        self.args = ("{0.__name__}: {1}".format(type(self), msg),)
        sys.exit(self)


class EZTrackRuntimeError(NoTraceBackWithLineNumber):
    pass


class EZTrackTypeError(NoTraceBackWithLineNumber):
    pass


class EZTrackValueError(NoTraceBackWithLineNumber):
    pass


class EZTrackLookupError(NoTraceBackWithLineNumber):
    pass


class EZTrackNotImplementedError(NoTraceBackWithLineNumber):
    pass


class EZTrackImportError(NoTraceBackWithLineNumber):
    pass


class EZTrackAttributeError(NoTraceBackWithLineNumber):
    pass


class EZTrackOSError(NoTraceBackWithLineNumber):
    pass

import linecache
import sys
import re

import trafaret as T

primitive_ip_regexp = r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'
store_directory = r'^/.*/$'

TRAFARET_CONF = T.Dict({
    T.Key('host'): T.Regexp(primitive_ip_regexp),
    T.Key('token'): T.String(),
    T.Key('store_directory'): T.Regexp(store_directory),
    T.Key('port'): T.Int(),
    # T.Key('mongo'): T.Any
})


def exception_message():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

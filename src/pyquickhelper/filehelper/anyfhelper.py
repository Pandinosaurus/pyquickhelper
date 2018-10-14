"""
@file
@brief      Various helpers about files
"""

import os
import stat
import sys
import warnings
from .synchelper import explore_folder_iterfile
from .internet_helper import read_url
from .file_info import is_file_string, is_url_string


if sys.version_info[0] == 2:
    from codecs import open
    from StringIO import StringIO
    BytesIO = StringIO
else:
    from io import BytesIO, StringIO


def change_file_status(folder, status=stat.S_IWRITE, strict=False,
                       include_folder=True):
    """
    Changes the status of all files inside a folder.

    @param      folder          folder or file
    @param      status          new status
    @param      strict          False, use ``|=``, True, use ``=``
    @param      include_folder  change the status of the folders as well
    @return                     list of modified files

    By default, status is ``stat.S_IWRITE``.
    If *folder* is a file, the function changes the status of this file,
    otherwise, it will change the status of every file the folder contains.
    """
    if os.path.isfile(folder):
        if include_folder:
            dirname = os.path.dirname(folder)
            todo = [dirname, folder]
        else:
            todo = [folder]
        res = []

        for f in todo:
            mode = os.stat(f).st_mode
            if strict:
                nmode = status
                if nmode != mode:
                    os.chmod(f, nmode)
                    res.append(f)
            else:
                nmode = mode | stat.S_IWRITE
                if nmode != mode:
                    os.chmod(f, nmode)
                    res.append(f)
        return res
    else:
        res = []
        dirname = set()
        if strict:
            for f in explore_folder_iterfile(folder):
                if include_folder:
                    d = os.path.dirname(f)
                    if d not in dirname:
                        dirname.add(d)
                        mode = os.stat(d).st_mode
                        nmode = status
                        if nmode != mode:
                            os.chmod(d, nmode)
                            res.append(d)
                try:
                    mode = os.stat(f).st_mode
                except FileNotFoundError:
                    # It appends for some weird path.
                    warnings.warn(
                        "[change_file_status] unable to find '{0}'".format(f), UserWarning)
                    continue
                nmode = status
                if nmode != mode:
                    os.chmod(f, nmode)
                    res.append(f)

            # It ends up with the folder.
            if include_folder:
                d = folder
                if d not in dirname:
                    mode = os.stat(d).st_mode
                    nmode = status
                    if nmode != mode:
                        os.chmod(d, nmode)
                        res.append(d)
        else:
            for f in explore_folder_iterfile(folder):
                if include_folder:
                    d = os.path.dirname(f)
                    if d not in dirname:
                        dirname.add(d)
                        mode = os.stat(d).st_mode
                        nmode = mode | stat.S_IWRITE
                        if nmode != mode:
                            os.chmod(d, nmode)
                            res.append(d)
                try:
                    mode = os.stat(f).st_mode
                except FileNotFoundError:
                    # it appends for some weird path
                    warnings.warn(
                        "[change_file_status] unable to find '{0}'".format(f), UserWarning)
                    continue
                nmode = mode | stat.S_IWRITE
                if nmode != mode:
                    os.chmod(f, nmode)
                    res.append(f)

            # It ends up with the folder.
            if include_folder:
                d = folder
                if d not in dirname:
                    mode = os.stat(d).st_mode
                    nmode = mode | stat.S_IWRITE
                    if nmode != mode:
                        os.chmod(d, nmode)
                        res.append(d)
        return res


def read_content_ufs(file_url_stream, encoding="utf8", asbytes=False, add_source=False):
    """
    Reads the content of a source, whether it is a url, a file, a stream
    or a string (in that case, it returns the string itself),
    it assumes the content type is text.

    @param      file_url_stream     file or url or stream or string
    @param      encoding            encoding
    @param      asbytes             return bytes instead of chars
    @param      add_source          also return the way the content was obtained
    @return                         content of the source (str) or *(content, type)*

    Type can be:

    * *rb*: binary file
    * *r*: text file
    * *u*: url
    * *ub*: binary content from url
    * *s*: string
    * *b*: binary string
    * *S*: StringIO
    * *SB*: BytesIO
    * *SBb*: BytesIO, return bytes

    The function can return bytes.
    """
    if isinstance(file_url_stream, str  # unicode#
                  ):
        if is_file_string(file_url_stream) and os.path.exists(file_url_stream):
            if asbytes:
                with open(file_url_stream, "rb") as f:
                    content = f.read()
                    return (content, "rb") if add_source else content
            else:
                with open(file_url_stream, "r", encoding=encoding) as f:
                    content = f.read()
                    return (content, "r") if add_source else content
        elif len(file_url_stream) < 5000 and file_url_stream.startswith("http"):
            content = read_url(file_url_stream, encoding=encoding)
            return (content, "u") if add_source else content
        elif is_url_string(file_url_stream):
            if asbytes:
                content = read_url(file_url_stream)
                return (content, "ub") if add_source else content
            else:
                if encoding is None:
                    raise ValueError(
                        "cannot return bytes if encoding is None for url: " + file_url_stream)
                content = read_url(file_url_stream, encoding=encoding)
                return (content, "u") if add_source else content
        elif sys.version_info[0] == 2:
            # the string should the content itself
            return (file_url_stream, "s") if add_source else file_url_stream
        else:
            # the string should the content itself
            if isinstance(file_url_stream, str  # unicode#
                          ):
                if asbytes:
                    raise TypeError(
                        "file_url_stream is str when expected bytes")
                else:
                    return (file_url_stream, "s") if add_source else file_url_stream
            else:
                if asbytes:
                    return (file_url_stream, "b") if add_source else file_url_stream
                else:
                    raise TypeError(
                        "file_url_stream is bytes when expected str")
    elif isinstance(file_url_stream, bytes):
        if asbytes:
            return (file_url_stream, "b") if add_source else file_url_stream
        else:
            content = file_url_stream.encode(encoding=encoding)
            return (content, "b") if add_source else content
    elif isinstance(file_url_stream, StringIO):
        v = file_url_stream.getvalue()
        if asbytes and v:
            content = v.encode(encoding=encoding)
            return (content, "Sb") if add_source else content
        else:
            return (v, "S") if add_source else v
    elif isinstance(file_url_stream, BytesIO):
        v = file_url_stream.getvalue()
        if asbytes or not v:
            return (v, "SBb") if add_source else v
        else:
            content = v.decode(encoding=encoding)
            return (content, "SB") if add_source else content
    else:
        if sys.version_info[0] == 2 and isinstance(file_url_stream, BytesIO):
            v = file_url_stream.getvalue()
            if asbytes or not v:
                return (v, "SBb") if add_source else v
            else:
                content = v.decode(encoding=encoding)
                return (content, "SB") if add_source else content
        raise TypeError(
            "unexpected type for file_url_stream: {0}".format(type(file_url_stream)))

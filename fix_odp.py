#!/usr/bin/env python
# Python 2 and 3 from same source.
from __future__ import print_function

try:
    # TODO: always use io.StringIO - it exists in 2.6 as well, but gives a
    # ``TypeError: can't write str to text stream``.
    import cStringIO as StringIO
except ImportError:
    import io as StringIO
import os
import shutil
import sys
import xml.etree.ElementTree as etree  # cElementTree has no _namespace_map?
import zipfile

def link_exists(href, directory):
    if href.startswith('../'):
        return os.path.exists(os.path.join(directory, href[3:]))
    elif href.startswith('/'):
        return os.path.exists(os.path.join(directory, href))
    else:
        # Link within the zip file.  TODO: validate.
        print('  embedded %r' % path)
        return True

def fix_path(href, directory):
    """Return new path."""
    
    if link_exists(href, directory):
        print('  existing %r' % href)
    else:
        print('  BROKEN %r' % href)
    candidate = '../' + os.path.basename(href)
    if link_exists(candidate, directory):
        if candidate == href:
            print('    unchanged.')
        else:
            print('    -> existing %r.' % candidate)
        return candidate
    else:
        print('    no candidate found in %r, LEFT AS IS.' % directory)
        return href

def fix_tree(root, directory):
    """Mutates an ElementTree in place."""
    # root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}plugin')
    for elem in root.getiterator():
        if elem.tag.endswith('}plugin'):
            for attr in elem.attrib:
                if attr.endswith('}href'):
                    href = elem.attrib[attr]
                    elem.set(attr, fix_path(href, directory))

def fix_content(content, directory):
    """bytes -> bytes"""
    # Namespace-preserving parsing stolen from
    # http://effbot.org/zone/element-namespaces.htm
    root = None
    events = ("start", "start-ns")
    for event, elem in etree.iterparse(StringIO.StringIO(content), events):
        if event == "start":
            if root is None:
                root = elem
        if event == "start-ns":
            prefix, uri = elem
            etree._namespace_map[uri] = prefix
    tree = etree.ElementTree(root)

    fix_tree(root, directory)
    
    sio = StringIO.StringIO()
    # TODO: use nice namespace aliases
    tree.write(sio, encoding='utf8')
    return sio.getvalue()

def fix_odf(fname):
    output_fname = '%s_fixed%s' % os.path.splitext(fname)
    print('reading', fname)
    input_zip = zipfile.ZipFile(fname, 'r')
    output_zip = zipfile.ZipFile(output_fname, 'w')
    for zinfo in input_zip.filelist:
        s = input_zip.read(zinfo.filename)
        if zinfo.filename == 'content.xml':
            s = fix_content(s, os.path.dirname(fname))
        output_zip.writestr(zinfo, s)
    output_zip.close()
    print('WROTE', output_fname)

if len(sys.argv) == 1:  # devel shortcut
    fix_odf('./test/tmp.odp')
else:
    for fname in sys.argv[1:]:
        fix_odf(fname)

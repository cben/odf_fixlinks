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
import xml.etree.cElementTree as etree
import zipfile

def link_exists(href):
    if href.startswith('../'):
        return os.path.exists(href[3:])
    elif href.startswith('/'):
        return os.path.exists(href)
    else:
        # Link within the zip file.  TODO: validate.
        print('  embedded %r' % path)
        return True

def fix_path(href):
    """Return new path."""
    
    if link_exists(href):
        print('  existing %r' % href)
    else:
        print('  BROKEN %r' % href)
    candidate = '../' + os.path.basename(href)
    if link_exists(candidate):
        if candidate == href:
            print('    unchanged.')
        else:
            print('    -> existing %r.' % candidate)
        return candidate
    else:
        print('    no candidate found in current dir, LEFT AS IS.')
        return href

def fix_tree(root):
    """Mutates an ElementTree in place."""
    # root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}plugin')
    for elem in root.getiterator():
        if elem.tag.endswith('}plugin'):
            for attr in elem.attrib:
                if attr.endswith('}href'):
                    href = elem.attrib[attr]
    ##                print etree.tostring(elem)
                    elem.set(attr, fix_path(href))
    ##                print etree.tostring(elem)

def fix_content(content):
    """bytes -> bytes"""
    tree = etree.ElementTree()
    tree.parse(input_zip.open('content.xml'))
    root = tree.getroot()
    #content = f.read('content.xml')
    #root = etree.fromstring(content)

    fix_tree(root)
    sio = StringIO.StringIO()
    # TODO: use nice namespace aliases
    tree.write(sio, encoding='utf8')
    return sio.getvalue()

if len(sys.argv) == 2:
    FILE = sys.argv[1]
    print()
    print(FILE)
else:
    FILE = './test/tmp.odp'

os.chdir(os.path.dirname(FILE))  # TODO: don't rely on cwd!
input_zip = zipfile.ZipFile(os.path.basename(FILE), 'r')
output_zip = zipfile.ZipFile('fixed_' + os.path.basename(FILE), 'w')
for zinfo in input_zip.filelist:
    s = input_zip.read(zinfo.filename)
    if zinfo.filename == 'content.xml':
        s = fix_content(s)
    output_zip.writestr(zinfo, s)
output_zip.close()
print('WROTE', 'fixed_' + os.path.basename(FILE))

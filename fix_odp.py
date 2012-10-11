#!/usr/bin/env python
import os
import sys
import xml.etree.cElementTree as etree
import zipfile

if len(sys.argv) == 2:
    FILE = sys.argv[1]
    print
    print FILE
else:
    FILE = './test/tmp.odp'
os.chdir(os.path.dirname(FILE))  # TODO: don't rely on cwd!
f = zipfile.ZipFile(os.path.basename(FILE))
tree = etree.ElementTree()
tree.parse(f.open('content.xml'))
root = tree.getroot()
#content = f.read('content.xml')
#root = etree.fromstring(content)

def fix_path(path):
    """Return new path."""
    if path.startswith('../'):
        fs_path = path[3:]
    elif path.startswith('/'):
        fs_path = path
    else:
        # Link within the zip file.  TODO: validate.
        print '  %r embedded' % path
        return path

    if os.path.exists(fs_path):
        fs_exists = '  %r exists' % path
    else:
        fs_exists = '  %r BROKEN' % path
    candidate = os.path.basename(fs_path)
    if os.path.exists(candidate):
        print fs_exists, '-> %r exists' % candidate
        return candidate
    else:
        print fs_exists, 'no candidate found in current dir, LEFT AS IS.'
        return path

# root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}plugin')
for elem in root.getiterator():
    if elem.tag.endswith('}plugin'):
        for attr in elem.attrib:
            if attr.endswith('}href'):
                href = elem.attrib[attr]
##                print etree.tostring(elem)
                elem.set(attr, fix_path(href))
##                print etree.tostring(elem)


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

def link_exists(href):
    if href.startswith('../'):
        return os.path.exists(href[3:])
    elif href.startswith('/'):
        return os.path.exists(href)
    else:
        # Link within the zip file.  TODO: validate.
        print '  embedded %r' % path
        return True

def fix_path(href):
    """Return new path."""
    
    if link_exists(href):
        print '  existing %r' % href
    else:
        print '  BROKEN %r' % href
    candidate = '../' + os.path.basename(href)
    if link_exists(candidate):
        if candidate == href:
            print '    unchanged.'
        else:
            print '    -> existing %r.' % candidate
        return candidate
    else:
        print '    no candidate found in current dir, LEFT AS IS.'
        return href

# root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}plugin')
for elem in root.getiterator():
    if elem.tag.endswith('}plugin'):
        for attr in elem.attrib:
            if attr.endswith('}href'):
                href = elem.attrib[attr]
##                print etree.tostring(elem)
                elem.set(attr, fix_path(href))
##                print etree.tostring(elem)


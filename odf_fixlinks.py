#!/usr/bin/env python3

import io
import os
import shutil
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile

class LinkResolver(object):
    """Holds context relevant to resolving links."""
    def __init__(self, zfile, directory):
        self.zfile = zfile
        self.directory = directory

    def link_exists(self, href):
        href = urllib.parse.unquote(href)
        if href.startswith('../'):
            return os.path.exists(os.path.join(self.directory, href[3:]))
        elif href.startswith('/'):
            return os.path.exists(os.path.join(self.directory, href))
        else:
            # Link within the zip file.  TODO: validate.
            print('  embedded %r' % path)
            return True

    def fix_path(self, href):
        """Return new path."""
        
        if self.link_exists(href):
            print('  existing %r' % href)
        else:
            print('  BROKEN %r' % href)
        candidate = '../' + os.path.basename(href)
        if self.link_exists(candidate):
            if candidate == href:
                print('    unchanged.')
            else:
                print('    -> existing %r.' % candidate)
            return candidate
        else:
            print('    no candidate %r found, LEFT AS IS.' % candidate)
            return href

    def fix_tree(self, root):
        """Mutates an ElementTree in place."""
        # root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}plugin')
        for elem in root.iter():
            # I don't want to assume the namespace will never change.
            if elem.tag.endswith('}plugin'):
                for attr in elem.attrib:
                    if attr.endswith('}href'):
                        href = elem.attrib[attr]
                        elem.set(attr, self.fix_path(href))

    def fix_content(self, content: bytes) -> bytes:
        root = ET.fromstring(content)
        self.fix_tree(root)
        return ET.tostring(root, encoding='UTF-8')

def fix_odf(fname):
    print('reading', fname)
    input_zfile = zipfile.ZipFile(fname, 'r')
    resolver = LinkResolver(input_zfile, os.path.dirname(fname))

    output_fname = '%s_fixlinks%s' % os.path.splitext(fname)
    output_zfile = zipfile.ZipFile(output_fname, 'w')
    for zinfo in input_zfile.filelist:
        s = input_zfile.read(zinfo.filename)
        if zinfo.filename == 'content.xml':
            s = resolver.fix_content(s)
        output_zfile.writestr(zinfo, s)
    output_zfile.close()
    print('WROTE', output_fname)

if __name__ == '__main__':
    files = sys.argv[1:]
    if not files:  # devel shortcut
        files = ['./test/tmp.odp']
    for fname in files:
        if os.path.splitext(fname)[0].endswith('_fixlinks'):
            print('SKIPPING', fname, 'to avoid ..._fixlinks_fixlinks...')
        else:
            fix_odf(fname)

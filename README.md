# Change linked media in OpenDocument files to relative links

This script helps with managing *linked* (not embedded) media in LibreOffice/OpenOffice files.
(This is important with big video files, as embedding them would inflate the document to impractical size.)

LibreOffice tends to record *absolute paths* when you insert linked media, which breaks as soon as you move the document and media around your filesystem / to different computers :-(
This script modifies links to files that it finds in the **same directory as the ODF document** to be relative links.
It doesn't matter if the original link works, so you can run this after moving the directory with document(s) and media around. 

 - It'd be easy to support other conventions, e.g. having media in a subdirectory relative to document.
   Let me know if you want any such support...

# Safety

Links whose target does not exist in current directory are left alone for safety.
It prints a report of all links and what it did to stdout.
It never modifies the original file but creates a new one e.g. `foo.odp` -> `foo_fixlinks.odp`.

## What works

Specifically tested with ODP presentations created by Impress but should work on any kind of OpenDocument format files.

Doens't work with PowerPoint 2010(?) — while it has buitin support for ODP import and export, its export seems to interpret the href field differently and I couldn't get its import to show linked videos at all - even from an ODP file exported by same PowerPoint!

## License

MIT license.

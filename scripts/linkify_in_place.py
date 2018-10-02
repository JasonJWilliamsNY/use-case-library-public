#!/usr/bin/env python
import os, re, sys
import subprocess

"""
Linkify all links in a document using Pandoc
"""

def usage():
    print("linkify_in_place:")
    print("This script will search a pile of Markdown files for")
    print("hyperlinks and turn them into markdownified hyperlinks")
    print("in-place. WARNING: This is a destructive task.")
    print("")
    print("Usage:")
    print("    ./linkify_in_place [FLAGS] <path-to-markdown-files>")
    print("")
    print("        -n | --dry-run       Print the names of files that would be")
    print("                             changed if the linkify_in_place script")
    print("                             were run.")
    print("")
    print("Example:")
    print("    ./linkify_in_place ../library")
    print("")
    exit(1)

def main():

    if(len(sys.argv)<2):
        usage()

    # Extract dry run arguments, if present
    args = sys.argv[1:]
    dry_run = False
    for dry_run_flag in ['-n','--dry-run']:
        if(dry_run_flag in args):
            dry_run = True
            args.remove(dry_run_flag)

    # Set the location of the source files and check it exists
    SRC_DOCS = args[0]
    if not os.path.isdir(SRC_DOCS):
        err = "ERROR: No source directory %s was found."%(SRC_DOCS)
    
    # Walk the directory and look for Markdown files
    markdown_files = []
    for fdir,fdirnames,fnames in os.walk(SRC_DOCS):
        for f in fnames:

            # Check a set of conditions to see if we
            # really want to linkify this document.
            bool1 = f[-3:]=='.md'       # only add markdown
            bool2 = f[-7:]!='_new.md'   # ignore _new.md (?)
            bool3 = '.github' not in fdir  # ignore github templates

            if( bool1 and bool2 and bool3):
                markdown_files.append( os.path.join( fdir, f ) )
    

    # Linkify each markdown document found
    for md in markdown_files:
    
        print("-"*40,file=sys.stderr)
        print("Linkifying (in-place) document: %s"%(md),file=sys.stderr)
    
        if dry_run is False:

            # print md to screen
            cat_cmd = ['cat', md]
            cat_proc = subprocess.Popen(cat_cmd,
                    stdout=subprocess.PIPE)
    
            # pandoc: md to json
            pandoc_from_cmd = ['pandoc','-f','gfm','-t','json','-s']
            pandoc_from_proc = subprocess.Popen(pandoc_from_cmd, 
                    stdin=cat_proc.stdout,
                    stdout=subprocess.PIPE)
    
            '''
            # ---------------------------------
            # If we were applying a filter,
            # we would use these two steps:

            # above, you would set:
            FILTER = 'filters/parse_links.py'

            # filter: json to json
            pandoc_filter_cmd = [FILTER]
            pandoc_filter_proc = subprocess.Popen(pandoc_filter_cmd, 
                    stdin=pandoc_from_proc.stdout,
                    stdout=subprocess.PIPE)
            
            # pandoc: json to markdown
            pandoc_to_cmd = ['pandoc','-f','json','-t','gfm']
            pandoc_to_proc = subprocess.Popen(pandoc_to_cmd, 
                    stdin=pandoc_filter_proc.stdout,
                    stdout=subprocess.PIPE)
            '''

            # -------------------------------------
            # If we are not applying a filter,
            # we skip straight to converting 
            # the document back to Markdown.

            # pandoc: json to markdown
            pandoc_to_cmd = ['pandoc','-f','json','-t','gfm']
            pandoc_to_proc = subprocess.Popen(pandoc_to_cmd, 
                    stdin=pandoc_from_proc.stdout,
                    stdout=subprocess.PIPE)

            # we now have the text of the pandoc output
            pandoc_output = pandoc_to_proc.stdout.read().decode('utf-8')

            # apply any filtering at this point
            # 
            # github checkboxes (not handled well by pandoc...)
            # \[x\] or \[X\] into [x]
            pandoc_output = re.sub(r'\\\[X\\\]','[x]',pandoc_output)
            pandoc_output = re.sub(r'\\\[x\\\]','[x]',pandoc_output)
            pandoc_output = re.sub(r'\\\[ \\\]','[ ]',pandoc_output)
            pandoc_output = re.sub(r'\\\[\\\]', '[ ]',pandoc_output)
            final_document = pandoc_output

            # -------------------------------------
            # target file is same as source/input file
            target = md

            # write to target file
            with open(target,'w') as f:
                f.write(final_document)

            print("Finished linkifying document: %s"%(target),file=sys.stderr)

        else:

            # target file is same as source/input file
            target = md

            print("Dry run would have linkified document: %s"%(target),file=sys.stderr)
        

if __name__=="__main__":
    main()

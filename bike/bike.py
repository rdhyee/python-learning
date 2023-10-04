#!/Users/raymondyee/.pyenv/versions/myenv/bin/python

# grab the selected row and convert to markdown

# from rdhyee_utils.bike.bikeformat import bike_etree_to_panflute
from pathlib import Path as P
import panflute as pf
import pypandoc
import sh
import json

import select
import sys


import click
from lxml import etree as ET

from rdhyee_utils.bike import Bike

from rdhyee_utils.bike.bikeformat import (
    namespaces,
    bike_etree_to_panflute,
    bike_etree_list_to_panflute,
)

from rdhyee_utils.clipboard.macos import GeneralPasteboard, ptypes
from appscript import app, k, its


SOURCE_MARKDOWN_FORMAT = (
    "markdown+lists_without_preceding_blankline+wikilinks_title_after_pipe+mark"
)
DEST_MARKDOWN_FORMAT = "markdown+lists_without_preceding_blankline+wikilinks_title_after_pipe+mark-native_divs-native_spans-header_attributes-link_attributes"
ONLY_DOC_CHILDREN = True


# https://stackoverflow.com/a/3763257/7782
def check_stdin(stdin=sys.stdin):
    """Check whether there is data on stdin. Works on unix systems
    https://stackoverflow.com/questions/3762881/how-do-i-check-if-stdin-has-some-data
    """
    rlist, _, _ = select.select([stdin], [], [], 0.1)
    if rlist:
        return True
    else:
        return False



# https://www.perplexity.ai/search/Write-me-a-MFQekCRfQSyjfylvmBlUng?s=c
def merge_consecutive_codeblocks(elem, doc):
    """Merge consecutive code blocks"""
    if (
        isinstance(elem, pf.CodeBlock)
        and doc.prev_elem
        and isinstance(doc.prev_elem, pf.CodeBlock)
    ):
        doc.prev_elem.text += "\n" + elem.text
        return []
    doc.prev_elem = elem


def etree_to_panflute(etree, only_doc_children=ONLY_DOC_CHILDREN):
    if only_doc_children:
        etree2 = etree.findall("ns:body/ns:ul/*", namespaces=namespaces)
        pfd = bike_etree_list_to_panflute(etree2)
        # TO DO: fancier wrapping of items -- for example, there might be ListItems that are not wrapped in a List type of some sort
        pfd = pf.Doc(*pfd)
    else:
        pfd = bike_etree_to_panflute(etree)

    pf.run_filter(merge_consecutive_codeblocks, doc=pfd)
    return pfd


def bike_selected_to_md(heading_level):
    bike = Bike()

    d = bike.windows[0].document
    etree = d.lxml_etree(from_=d.selection_rows)

    pfd = etree_to_panflute(etree, only_doc_children=ONLY_DOC_CHILDREN)
    pandoc_json = pfd.to_json()

    output_md = pypandoc.convert_text(
        json.dumps(pandoc_json),
        to=DEST_MARKDOWN_FORMAT,
        format="json",
        extra_args=["--wrap=none"],
        filters=[],
        # filters=["./change_marker.lua", "./remove_spans.lua"],
    )

    sh.pbcopy(_in=output_md)

    # write to scratchpad in Obsidian

    with open(P.home() / "obsidian/MainRY/ScratchPad.md", "bw") as f:
        f.write(output_md.encode("utf-8"))

    # convert output_md to HTML and write to /tmp/scratchpad.html
    output_html = pypandoc.convert_text(output_md, to="html", format="markdown")
    with open(P("/tmp/ScratchPad.html"), "bw") as f:
        f.write(output_html.encode("utf-8"))

    # convert to docx and write to /tmp/scratchpad.docx

    if True:
        output_docx = pypandoc.convert_text(
            output_md,
            to="docx",
            format="markdown",
            outputfile=P("/tmp/ScratchPad.docx"),
            extra_args=["--toc"],
        )
    else:
        sh.pandoc(
            "--toc", _in=output_md, _out="/tmp/ScratchPad.docx", to="docx", f="markdown"
        )

    # convert to PDF and write to /tmp/scratchpad.pdf
    if False:
        output_pdf = pypandoc.convert_text(
            output_md,
            to="pdf",
            format="markdown",
            outputfile=("/tmp/ScratchPad.pdf"),
            extra_args=["--toc"],
        )


@click.group()
def main():
    pass


@main.command()
@click.option(
    "--heading_level",
    envvar="KMVAR_Heading_Level",
    default=1,
    help="Heading level to use for the top level of the document.",
)
def sel2pb(heading_level):
    bike_selected_to_md(heading_level)


@main.command()
@click.argument('args', nargs=-1)
@click.option('-t', '--to', default=DEST_MARKDOWN_FORMAT, help='Output format')
@click.pass_context
def pandoc(ctx, args, to):
    kwargs = {
        'stdin': click.get_text_stream('stdin'),
        'stdout': click.get_text_stream('stdout')
    }
    # print("hello from bike pandoc")
    # print("args:", args)
    # print("kwargs:", kwargs)
    # print("to:", to)

    # inputs: start with: stdin, input_path, 

    data = None

    if len(args) > 0:
        input_path = args[0]
        data = open(input_path, 'rb').read()
    elif check_stdin(kwargs['stdin']):
        data = sys.stdin.read()
    
    # if no data yet, check for clipboard
    if data is None or len(data) == 0:
        pb = GeneralPasteboard()
        data = pb.get_string()
    
    # convert to the json format first
    if data is None or len(data) == 0:
        return
    
    etree = ET.fromstring(data, ET.XMLParser(remove_blank_text=True))
    pfd = etree_to_panflute(etree, only_doc_children=False)

    # then convert to to format
    output = pypandoc.convert_text(json.dumps(pfd.to_json()), to=to, format="json")
    
    # if there is a second argument, assume it's a file
    if len(args) > 1:
        output_path = args[1]
        open(output_path, "w", encoding="utf-8").write(output)
    else:
        # otherwise, write to stdout
        stdout = kwargs['stdout']
        stdout.write(output)


if __name__ == "__main__":
    main()

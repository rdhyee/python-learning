#!/Users/raymondyee/.pyenv/versions/myenv/bin/python

# grab the selected row and convert to markdown

# from rdhyee_utils.bike.bikeformat import bike_etree_to_panflute
from pathlib import Path as P
import panflute as pf
import pypandoc
import sh
import json

import click


from rdhyee_utils.bike import Bike

from rdhyee_utils.bike.bikeformat import (
    namespaces,
    bike_etree_to_panflute,
    bike_etree_list_to_panflute,
)

from rdhyee_utils.clipboard.macos import GeneralPasteboard, ptypes
from appscript import app, k, its

#
DEST_MARKDOWN_FORMAT = "markdown+compact_definition_lists+lists_without_preceding_blankline+wikilinks_title_after_pipe+mark-native_divs-native_spans-header_attributes-link_attributes"
ONLY_DOC_CHILDREN = True


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


def bike_selected_to_md(heading_level):
    bike = Bike()

    d = bike.windows[0].document
    etree = d.lxml_etree(from_=d.selection_rows)

    # what if I export just the rows under the root ul?
    if ONLY_DOC_CHILDREN:
        etree2 = etree.findall("ns:body/ns:ul/*", namespaces=namespaces)
        pfd = bike_etree_list_to_panflute(etree2, heading_level=heading_level)
        # TO DO: fancier wrapping of items -- for example, there might be ListItems that are not wrapped in a List type of some sort
        pfd = pf.Doc(*pfd)
    else:
        pfd = bike_etree_to_panflute(etree)

    pf.run_filter(merge_consecutive_codeblocks, doc=pfd)
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


if __name__ == "__main__":
    main()

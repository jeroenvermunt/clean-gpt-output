#!/usr/bin/env python
import os
import re
import subprocess

import chardet


def remove_p_tags(htmlstring):
    """removes all p tags within ol and ul tags without parsing to html or tree"""

    # Match <ol>...</ol> and <ul>...</ul> blocks, including newlines
    list_blocks = re.findall(r"<li[^>]*>.*?</li>", htmlstring, re.DOTALL)

    # Extract all <p> tags from inside those blocks
    p_tags_inside_lists = []
    for block in list_blocks:
        p_tags_inside_lists += re.findall(r"<p[^>]*>.*?</p>", block, re.DOTALL)

        for p_tag in p_tags_inside_lists:
            cleaned_p_tag = re.sub(r"<p[^>]*>", "", p_tag)
            cleaned_p_tag = re.sub(r"<\/p>", "", cleaned_p_tag)

            htmlstring = htmlstring.replace(p_tag, cleaned_p_tag)

    return htmlstring


dtype = "text/html"

# call 'xclip -selection clipboard -t text/html | tidy -qi --wrap 0'
clip_command = ["xclip", "-selection", "clipboard", "-o", "-t", dtype]
tidy_command = ["tidy", "-qi", "--wrap", "120", "--show-body-only", "yes"]

try:
    # Get the clipboard contents
    htmlclip = subprocess.check_output(clip_command)

    # # print("Formatting HTML in clipboard")
    htmlclip = subprocess.check_output(tidy_command, input=htmlclip)
    # print("succes")

    # print(htmlclip)

except subprocess.CalledProcessError as e:
    print("Error running command:", e)
    exit(1)

encoding = chardet.detect(htmlclip)["encoding"]
htmlclip = remove_p_tags(htmlclip.decode(encoding))

# Shove the clipboard to a temporary file
tmpfn = "/tmp/htmlclip_%i" % os.getpid()

with open(tmpfn, "wb") as editfile:
    editfile.write(htmlclip.encode(encoding))

# call 'cat tmpfn | xclip -selection clipboard -t text/html'
subprocess.call(
    ["xclip", "-selection", "clipboard", "-t", dtype, tmpfn],
    stdin=open(tmpfn, "r"),
)

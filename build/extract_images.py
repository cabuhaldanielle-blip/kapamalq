#!/usr/bin/env python3
"""Extracts figure images from the manual PDF in visual (top-to-bottom) order.

Usage: python3 build/extract_images.py <manual.pdf> <out_dir>
Writes images named p-<page>-<index>.<ext>, where <index> counts placements
on the page ordered by vertical position, so caption N on a page corresponds
to image N.
"""
import os
import sys

import fitz

pdf_path, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)

doc = fitz.open(pdf_path)
n = 0
for pno in range(len(doc)):
    page = doc[pno]
    infos = [i for i in page.get_image_info(xrefs=True) if i.get("xref")]
    infos.sort(key=lambda i: (round(i["bbox"][1]), i["bbox"][0]))
    for info in infos:
        img = doc.extract_image(info["xref"])
        name = f"p-{pno + 1:03d}-{n:03d}.{img['ext']}"
        with open(os.path.join(out_dir, name), "wb") as fh:
            fh.write(img["image"])
        n += 1
print(f"{n} images written to {out_dir}")

"""Tag rhymes in ADSO with RhymeTagger"""

from lxml import etree
from string import ascii_uppercase
import os
from time import strftime

from rhymetagger import RhymeTagger


NSMAP = {"tei": "http://www.tei-c.org/ns/1.0"}

adso_path = "../source/cssdo/source"
adso_with_rhymes = "../source/cssdo/source_with_rhymes"
if not os.path.exists(adso_with_rhymes):
  os.mkdir(adso_with_rhymes)

rt = RhymeTagger()
rt.load_model("es")

for dname in sorted(os.listdir(adso_path)):
  print(f"- Start {dname} [{strftime('%R')}]")
  for fname in sorted(os.listdir(os.path.join(adso_path, dname))):
    print(f"  - {fname}")
    ffname = os.path.join(adso_path, dname) + os.sep + fname
    tree = etree.parse(ffname)
    lines = []
    # some lines have witnesses, take the first one
    for ele in tree.xpath("//tei:l", namespaces=NSMAP):
      first_witness = ele.xpath(".//tei:lem/text()", namespaces=NSMAP)
      if len(first_witness) > 0:
        lines.append(first_witness[0].strip())
      else:
        lines.append(ele.xpath("./text()")[0].strip())
    # lines = [x.strip() for x in tree.xpath("//tei:l/text()", namespaces=NSMAP)]
    rhymes = rt.tag(lines, output_format=3)
    rhymes_letters = [ascii_uppercase[typ - 1]
                      if typ is not None else "-" for typ in rhymes]
    assert len(lines) == len(rhymes)
    for idx, rhyme in enumerate(rhymes_letters):
      tree.xpath("//tei:l", namespaces=NSMAP)[idx].attrib["rhyme"] = rhyme
    odir = os.path.join(adso_with_rhymes, dname)
    if not os.path.exists(odir):
      os.mkdir(odir)
    with open(os.path.join(odir, fname), mode="wb") as outfn:
      otree = etree.tostring(tree, xml_declaration=True, pretty_print=True, encoding="UTF-8")
      outfn.write(otree)

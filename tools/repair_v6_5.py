from lxml import etree
from pathlib import Path
import sys

src = Path(sys.argv[1])
out = Path(sys.argv[2])
parser = etree.XMLParser(huge_tree=True, remove_blank_text=True)
tree = etree.parse(str(src), parser)
root = tree.getroot()
ns = {'b': 'https://developers.google.com/blockly/xml'}

def first_block(container):
    return next((c for c in container if c.tag.endswith('block')), None)

def next_block(block):
    nxt = block.find('{%s}next' % ns['b'])
    return None if nxt is None else first_block(nxt)

ap = root.xpath('.//b:statement[@name="AFTERPURCHASE_STACK"]', namespaces=ns)
assert len(ap) == 1
ap = ap[0]
risk = root.xpath('.//b:block[@id="MasikaRiskGate"]', namespaces=ns)
stop = root.xpath('.//b:block[@id="MasikaStopGate"]', namespaces=ns)
assert len(risk) == 1 and len(stop) == 1
risk, stop = risk[0], stop[0]
stop_else = stop.xpath('./b:statement[@name="ELSE"]', namespaces=ns)[0]
first = first_block(stop_else)
assert first is not None

# V6.4: RiskGate -> StopGate -> three outcome/state blocks -> trade_again.
chain = []
cur = first
for _ in range(3):
    assert cur is not None
    chain.append(cur)
    cur = next_block(cur)
assert cur is not None and cur.get('type') == 'trade_again'
trade_again = cur

# Remove outcome/state chain from StopGate ELSE.
stop_else.remove(first)
# Detach trade_again from the third state block.
third = chain[-1]
third_next = third.find('{%s}next' % ns['b'])
assert third_next is not None and first_block(third_next) is trade_again
third.remove(third_next)
# StopGate ELSE now contains only trade_again.
stop_else.append(trade_again)

# Move RiskGate after the three state blocks.
assert first_block(ap) is risk
ap.remove(risk)
third_next = etree.SubElement(third, '{%s}next' % ns['b'])
third_next.append(risk)
# chain[0] already links to chain[1], which links to chain[2].
ap.append(chain[0])

xml = etree.tostring(root, encoding='UTF-8', xml_declaration=True, pretty_print=False)
xml = xml.replace(b'V6.4', b'V6.5')
out.write_bytes(xml)

# Structural validation.
check = etree.parse(str(out), parser)
cr = check.getroot()
blocks = cr.xpath('.//b:block', namespaces=ns)
ids = [b.get('id') for b in blocks if b.get('id')]
assert len(ids) == len(set(ids))
ap2 = cr.xpath('.//b:statement[@name="AFTERPURCHASE_STACK"]', namespaces=ns)[0]
cur = first_block(ap2)
expected = [chain[0].get('id'), chain[1].get('id'), chain[2].get('id'), 'MasikaRiskGate']
actual = []
for _ in range(4):
    assert cur is not None
    actual.append(cur.get('id'))
    cur = next_block(cur)
assert actual == expected
stop2 = cr.xpath('.//b:block[@id="MasikaStopGate"]', namespaces=ns)[0]
se = stop2.xpath('./b:statement[@name="ELSE"]', namespaces=ns)[0]
assert first_block(se).get('type') == 'trade_again'
assert b'V6.5' in xml and b'V6.4' not in xml
print(f'Wrote {out} ({out.stat().st_size} bytes), blocks={len(blocks)}')

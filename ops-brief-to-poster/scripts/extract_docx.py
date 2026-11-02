#!/usr/bin/env python3
"""Read a DOCX brief into ordered JSON blocks and original image files (stdlib only)."""
import argparse
import json
import posixpath
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}


def extract(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError('Output directory already exists; choose a new version directory.')
    warnings, media, blocks = [], {}, []
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        if len(infos) > 2000 or sum(i.file_size for i in infos) > 128 * 1024 * 1024:
            raise ValueError('DOCX exceeds extraction limits; inspect it separately.')
        root = ET.fromstring(archive.read('word/document.xml'))
        relpath = 'word/_rels/document.xml.rels'
        relations = ET.fromstring(archive.read(relpath)) if relpath in archive.namelist() else []
        pending = []
        for rel in relations:
            if not rel.attrib.get('Type', '').endswith('/image'):
                continue
            rid, target = rel.attrib['Id'], rel.attrib.get('Target', '')
            if rel.attrib.get('TargetMode') == 'External':
                warnings.append('External image not fetched: ' + rid)
                continue
            member = posixpath.normpath(posixpath.join('word', target))
            if not member.startswith('word/media/') or member not in archive.namelist():
                warnings.append('Unsupported or missing image target: ' + rid)
                continue
            suffix = Path(member).suffix.lower()
            if suffix not in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tif', '.tiff', '.emf', '.wmf', '.svg'}:
                suffix = '.bin'
            filename = f'image-{len(pending) + 1:02d}{suffix}'
            media[rid] = {'file': 'assets/' + filename, 'original_member': member}
            pending.append((filename, archive.read(member)))

        def paragraph(node):
            pieces, images = [], []
            for item in node.iter():
                if item.tag == '{' + NS['w'] + '}t':
                    pieces.append(item.text or '')
                elif item.tag == '{' + NS['w'] + '}tab':
                    pieces.append('\t')
                elif item.tag in {'{' + NS['w'] + '}br', '{' + NS['w'] + '}cr'}:
                    pieces.append('\n')
                for key in ('embed', 'link'):
                    rid = item.attrib.get('{' + NS['r'] + '}' + key)
                    if rid and rid not in images:
                        images.append(rid)
                # Older VML pictures use r:id rather than DrawingML r:embed.
                if item.tag.endswith('}imagedata'):
                    rid = item.attrib.get('{' + NS['r'] + '}id')
                    if rid and rid not in images:
                        images.append(rid)
            result = {'text': ''.join(pieces), 'image_ids': images}
            for rid in images:
                if rid not in media:
                    warnings.append('Referenced image unavailable: ' + rid)
            return result

        body = root.find('w:body', NS)
        if body is None:
            raise ValueError('DOCX has no document body.')
        for child in body:
            if child.tag == '{' + NS['w'] + '}p':
                blocks.append({'index': len(blocks) + 1, 'type': 'paragraph', **paragraph(child)})
            elif child.tag == '{' + NS['w'] + '}tbl':
                rows = []
                for row in child.findall('w:tr', NS):
                    rows.append([[paragraph(p) for p in cell.findall('.//w:p', NS)]
                                 for cell in row.findall('w:tc', NS)])
                blocks.append({'index': len(blocks) + 1, 'type': 'table', 'rows': rows})
        if root.findall('.//w:ins', NS) or root.findall('.//w:del', NS):
            warnings.append('Tracked changes detected: extraction includes insertions and excludes deletions; verify intended wording.')
        if any(n.startswith('word/header') or n.startswith('word/footer') for n in archive.namelist()):
            warnings.append('Headers/footers exist and are not included; inspect if they contain campaign content.')
        if 'word/comments.xml' in archive.namelist():
            warnings.append('Comments exist and are not included; inspect if they contain design requirements.')
        output.mkdir(parents=True)
        if pending:
            (output / 'assets').mkdir()
        for filename, data in pending:
            (output / 'assets' / filename).write_bytes(data)
        result = {'source': str(source), 'blocks': blocks, 'images': media,
                  'warnings': sorted(set(warnings))}
        (output / 'source.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        result = extract(args.source, args.out)
    except (ValueError, KeyError, OSError, zipfile.BadZipFile, ET.ParseError) as exc:
        parser.exit(1, str(exc) + '\n')
    print(json.dumps({'output': str(Path(args.out).resolve()), 'blocks': len(result['blocks']),
                      'images': len(result['images']), 'warnings': result['warnings']}, ensure_ascii=False))

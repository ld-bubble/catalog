"""Validate the archived reference set without external dependencies."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'datasets' / 'first-50'


def read_json(path):
    return json.loads(path.read_text())


def local_file(value):
    path = (ROOT / value).resolve()
    assert not Path(value).is_absolute(), value
    assert path.is_relative_to(ROOT) and path.is_file(), value
    return path


def dimensions(path):
    data = path.read_bytes()
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', data[16:24])
    assert data[:2] == b'\xff\xd8', path
    offset = 2
    while offset < len(data):
        assert data[offset] == 0xff, path
        while data[offset] == 0xff:
            offset += 1
        marker = data[offset]
        offset += 1
        if marker in [0x01, 0xd8] or 0xd0 <= marker <= 0xd7:
            continue
        length = int.from_bytes(data[offset:offset + 2], 'big')
        if marker in [0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf]:
            height, width = struct.unpack('>HH', data[offset + 3:offset + 7])
            return width, height
        offset += length
    raise AssertionError(f'No JPEG dimensions: {path}')


def check(value, schema, path):
    if 'anyOf' in schema:
        for option in schema['anyOf']:
            try:
                check(value, option, path)
                return
            except AssertionError:
                pass
        raise AssertionError(path)
    if 'const' in schema:
        assert value == schema['const'], path
    if 'enum' in schema:
        assert value in schema['enum'], path
    types = schema.get('type')
    if isinstance(types, str):
        types = [types]
    if types:
        matches = {'null': value is None, 'string': isinstance(value, str),
                   'integer': type(value) is int, 'number': type(value) in [int, float],
                   'boolean': type(value) is bool, 'object': isinstance(value, dict),
                   'array': isinstance(value, list)}
        assert any(matches[t] for t in types), path
    if isinstance(value, dict):
        assert set(schema.get('required', [])) <= set(value), path
        properties = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            assert set(value) <= set(properties), path
        for key, item in value.items():
            check(item, properties.get(key, {}), f'{path}/{key}')
    if isinstance(value, list):
        assert schema.get('minItems', 0) <= len(value) <= schema.get('maxItems', len(value)), path
        for i, item in enumerate(value):
            check(item, schema.get('items', {}), f'{path}/{i}')
    if type(value) in [int, float]:
        assert schema.get('minimum', value) <= value <= schema.get('maximum', value), path


def main():
    schema = read_json(ROOT / 'reference.schema.json')
    records = read_json(ROOT / 'reference-records.json')
    assert len(records) == len({r['id'] for r in records}) == 50
    for record in records:
        check(record, schema, record['id'])
        images = {im['id']: im for im in record['images']}
        assert len(images) == len(record['images'])
        sections = {s['id'] for s in record['sections']}
        for image in images.values():
            path = local_file(image['path'])
            assert hashlib.sha256(path.read_bytes()).hexdigest() == image['sha256'], path
            assert dimensions(path) == (image['width'], image['height']), path
            if image['role'] == 'crop':
                parent = images[image['parent_id']]
                x0, y0, x1, y1 = image['bbox_px']
                assert 0 <= x0 < x1 <= parent['width'] and 0 <= y0 < y1 <= parent['height']
                assert (image['width'], image['height']) == (x1 - x0, y1 - y0)
        for block in record['copy_blocks'] + record['transcription_candidates']:
            assert block['section_id'] in sections
            assert set(block['evidence_ids']) <= set(images)
            if 'bbox_px' in block:
                x0, y0, x1, y1 = block['bbox_px']
                assert 0 <= x0 < x1 <= images['full']['width']
                assert 0 <= y0 < y1 <= images['full']['height']
        for item in record['claims'] + record['sections']:
            assert set(item['evidence_ids']) <= set(images)
        for key in ['gallery_meta_path', 'gallery_text_path']:
            local_file(record['provenance'][key])
        assert read_json(ROOT / 'records' / f"{record['id']}.json") == record
        packet = read_json(ROOT / 'packets' / f"{record['id']}.json")
        assert packet['copy_examples'] == record['copy_blocks']
        for value in packet['expand'].values():
            local_file(value)
        raw = read_json(ROOT / 'ocr' / f"{record['id']}.json")
        local_file(raw[0]['path'])
    index = read_json(ROOT / 'search-index.json')
    assert len(index) == 50 and {r['id'] for r in index} == {r['id'] for r in records}
    for row in index:
        for key in ['hero_image', 'full_image', 'packet']:
            local_file(row[key])
    html = (ROOT / 'review.html').read_text()
    match = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
    gallery = json.loads(match.group(1))
    assert len(gallery) == 50 and {r['id'] for r in gallery} == {r['id'] for r in records}
    for row in gallery:
        assert row['copy'] == next(r['copy_blocks'] for r in records if r['id'] == row['id'])
    print(f"Passed: {len(records)} pages, {sum(len(r['images']) for r in records)} images, "
          f"{sum(len(r['copy_blocks']) for r in records)} checked copy examples.")


if __name__ == '__main__':
    main()

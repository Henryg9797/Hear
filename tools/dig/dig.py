#!/usr/bin/env python3
"""dig — Hear's listening tool for sample hunting.

Scans a folder of audio files you own, separates each track into stems (drums, bass, vocals, guitar, piano, other),
finds the stretches where one instrument plays alone, measures the key and tempo of each stretch, and writes a
results file that Hear's "Sample Search" page reads.

    python dig.py scan ~/Music/Crates --out dig-results.json

Run `python dig.py --help` for the options. First run downloads the separation model (about 300 MB).
"""
import argparse, json, os, sys, time, math, hashlib, re, urllib.request, urllib.parse
from pathlib import Path

import numpy as np

AUDIO_EXT = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.aiff', '.aif', '.wma', '.opus'}
STEM_LABEL = {'drums': 'Drums', 'bass': 'Bass', 'vocals': 'Vocals', 'guitar': 'Guitar', 'piano': 'Piano / keys', 'other': 'Other (horns, strings, synths)'}
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
# Krumhansl–Schmuckler key profiles
MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


# ---------------------------------------------------------------- Internet Archive
IA_COLLECTIONS = {'78s': 'georgeblood', 'netlabels': 'netlabels', 'live': 'etree', 'community': 'opensource_audio', 'any': ''}
UA = {'User-Agent': 'hear-dig/1.0 (personal sample research tool)'}


def ia_json(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(2 + 3 * i)


def ia_query(args):
    parts = ['mediatype:audio']
    col = IA_COLLECTIONS.get(args.collection, args.collection)
    if col: parts.append(f'collection:{col}')
    if args.frm or args.to:
        parts.append(f'date:[{args.frm or 1800}-01-01 TO {args.to or 2100}-12-31]')
    if args.genre: parts.append('subject:(' + ' OR '.join(f'"{g.strip()}"' for g in args.genre.split(',') if g.strip()) + ')')
    if args.q: parts.append(f'({args.q})')
    return ' AND '.join(parts)


def ia_pick_file(files):
    """One audio file per item: a restored transfer if there is one, lossless over lossy, and the first take."""
    cands = []
    for f in files:
        name = f.get('name', ''); fmt = (f.get('format') or '').lower(); ext = Path(name).suffix.lower()
        if ext not in AUDIO_EXT: continue
        score = 0
        if 'restored' in name.lower(): score -= 10
        if ext == '.flac': score -= 5
        elif ext in ('.wav', '.aiff'): score -= 3
        if re.search(r'[_-]0?1[_.-]', name): score -= 1
        cands.append((score, name, f))
    if not cands: return None
    cands.sort(key=lambda c: (c[0], c[1]))
    return cands[0][2]


def fetch(args):
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    q = ia_query(args)
    print('Internet Archive query:', q)
    got, page, seen = 0, 1, set()
    sort = {'popular': 'downloads desc', 'newest': 'addeddate desc', 'oldest': 'date asc', 'random': 'random'}.get(args.sort, 'downloads desc')
    while got < args.limit:
        url = 'https://archive.org/advancedsearch.php?' + urllib.parse.urlencode({'q': q, 'fl[]': 'identifier', 'rows': min(100, args.limit * 2), 'page': page, 'output': 'json', 'sort[]': sort}, doseq=True)
        docs = (ia_json(url).get('response') or {}).get('docs') or []
        if not docs: break
        for d in docs:
            if got >= args.limit: break
            ident = d['identifier']
            if ident in seen: continue
            seen.add(ident)
            folder = out / ident
            if folder.exists() and any(p.suffix.lower() in AUDIO_EXT for p in folder.iterdir()):
                print(f'  have   {ident}'); got += 1; continue
            try:
                meta = ia_json(f'https://archive.org/metadata/{ident}')
            except Exception as e:
                print(f'  skip   {ident} (metadata: {e})'); continue
            f = ia_pick_file(meta.get('files') or [])
            if not f: print(f'  skip   {ident} (no audio file)'); continue
            if args.max_mb and float(f.get('size') or 0) > args.max_mb * 1e6: print(f'  skip   {ident} (file over {args.max_mb} MB)'); continue
            m = meta.get('metadata') or {}
            one = lambda v: (v[0] if isinstance(v, list) else v) or ''
            date = str(one(m.get('date')) or one(m.get('year')) or '')
            side = {'identifier': ident, 'title': str(one(m.get('title'))), 'artist': str(one(m.get('creator'))), 'year': date[:4] if date[:4].isdigit() else '', 'date': date,
                    'subject': m.get('subject') if isinstance(m.get('subject'), list) else [m.get('subject')] if m.get('subject') else [], 'collection': m.get('collection'),
                    'url': f'https://archive.org/details/{ident}', 'file': f['name'], 'license': str(one(m.get('licenseurl')) or one(m.get('rights')) or '')}
            folder.mkdir(exist_ok=True)
            dl = f"https://archive.org/download/{ident}/{urllib.parse.quote(f['name'])}"
            dest = folder / Path(f['name']).name
            print(f'  get    {ident}  {side["title"][:50]} — {side["artist"][:30]} ({side["year"]})  {Path(f["name"]).suffix}', flush=True)
            try:
                with urllib.request.urlopen(urllib.request.Request(dl, headers=UA), timeout=120) as r, open(dest, 'wb') as w:
                    while True:
                        chunk = r.read(1 << 20)
                        if not chunk: break
                        w.write(chunk)
            except Exception as e:
                print(f'         failed ({e})'); dest.unlink(missing_ok=True); continue
            (folder / 'dig-meta.json').write_text(json.dumps(side, indent=1))
            got += 1
            time.sleep(args.pause)
        page += 1
    print(f'\n{got} items in {out}. Next: python dig.py scan "{out}" --out dig-results.json')


# ---------------------------------------------------------------- tags
def read_tags(path):
    out = {'artist': '', 'title': '', 'album': '', 'year': ''}
    side = Path(path).parent / 'dig-meta.json'
    if side.exists():
        try:
            m = json.loads(side.read_text())
            return {'artist': m.get('artist', ''), 'title': m.get('title', ''), 'album': '', 'year': m.get('year', ''), 'url': m.get('url', ''), 'source': 'Internet Archive'}
        except Exception:
            pass
    try:
        import mutagen
        f = mutagen.File(path, easy=True)
        if f:
            def g(*keys):
                for k in keys:
                    v = f.get(k)
                    if v: return str(v[0]).strip()
                return ''
            out['artist'] = g('albumartist', 'artist') or g('artist')
            out['title'] = g('title')
            out['album'] = g('album')
            d = g('date', 'originaldate', 'year')
            out['year'] = d[:4] if d[:4].isdigit() else ''
    except Exception:
        pass
    if not out['title']:
        stem = Path(path).stem
        if ' - ' in stem and not out['artist']:
            a, t = stem.split(' - ', 1); out['artist'], out['title'] = a.strip(), t.strip()
        else:
            out['title'] = stem
    return out


# ---------------------------------------------------------------- separation
def separate(path, model, device, stems_from=None):
    """Returns (sample_rate, {stem: mono float32 array}). With stems_from, reads <stems_from>/<file stem>/<stem>.wav instead."""
    import soundfile as sf
    if stems_from:
        d = Path(stems_from) / Path(path).stem
        stems, sr = {}, None
        for p in sorted(d.glob('*.wav')):
            y, sr = sf.read(str(p), dtype='float32', always_2d=True)
            stems[p.stem] = y.mean(axis=1)
        if not stems: raise RuntimeError(f'no stems in {d}')
        return sr, stems
    import torch
    from demucs.api import Separator
    sep = Separator(model=model, device=device, progress=False)
    _origin, separated = sep.separate_audio_file(str(path))
    return sep.samplerate, {k: v.mean(dim=0).cpu().numpy().astype('float32') for k, v in separated.items()}


# ---------------------------------------------------------------- analysis
def frame_rms(y, sr, win, hop):
    n = max(1, 1 + (len(y) - win) // hop)
    idx = np.arange(n)[:, None] * hop + np.arange(win)[None, :]
    idx = np.minimum(idx, len(y) - 1)
    return np.sqrt(np.mean(y[idx] ** 2, axis=1) + 1e-12)


def find_isolated(sr, stems, win_s=0.5, hop_s=0.25, purity=0.9, mostly=0.75, min_s=2.0, gap_s=0.5, floor_db=-45.0):
    """Segments where one stem carries nearly all the energy: [{stem, start, end, purity, tier}]."""
    win, hop = int(sr * win_s), int(sr * hop_s)
    names = list(stems)
    E = np.stack([frame_rms(stems[n], sr, win, hop) ** 2 for n in names])  # power per stem per frame
    total = E.sum(axis=0)
    db = 10 * np.log10(np.sqrt(total) + 1e-12)
    dom = E.argmax(axis=0)
    share = E.max(axis=0) / (total + 1e-12)
    audible = db > floor_db
    segs = []
    max_gap = int(round(gap_s / hop_s))
    for si, name in enumerate(names):
        on = audible & (dom == si) & (share >= mostly)
        i, n = 0, len(on)
        while i < n:
            if not on[i]: i += 1; continue
            j = i; last = i
            while j < n and (on[j] or j - last <= max_gap):
                if on[j]: last = j
                j += 1
            s, e = i, last + 1
            dur = (e - s) * hop_s + (win_s - hop_s)
            if dur >= min_s:
                sh = share[s:e][on[s:e]]
                p = float(np.median(sh))
                segs.append({'stem': name, 'start': round(s * hop_s, 2), 'end': round(s * hop_s + dur, 2), 'purity': round(p, 3), 'tier': 'clean' if p >= purity else 'mostly'})
            i = e
    segs.sort(key=lambda x: x['start'])
    audible_s = float(audible.sum() * hop_s)
    return segs, audible_s


def key_of(y, sr):
    import librosa
    if len(y) < sr: return None, 0.0
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=2048)
    v = chroma.mean(axis=1)
    if v.sum() <= 0: return None, 0.0
    best, scores = None, []
    for i in range(12):
        for mode, prof in (('major', MAJOR), ('minor', MINOR)):
            r = np.corrcoef(np.roll(prof, i), v)[0, 1]
            scores.append((r, f'{NOTE_NAMES[i]} {mode}'))
    scores.sort(reverse=True)
    conf = float(max(0.0, min(1.0, (scores[0][0] - scores[1][0]) * 4 + (scores[0][0] - 0.5))))
    return scores[0][1], round(conf, 2)


def tempo_of(y, sr):
    import librosa
    if len(y) < sr * 2: return None, 0.0
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    if onset.max() <= 0: return None, 0.0
    t = librosa.feature.tempo(onset_envelope=onset, sr=sr, aggregate=None)
    vals = np.asarray(t).ravel()
    if not len(vals): return None, 0.0
    bpm = float(np.median(vals))
    while bpm > 180: bpm /= 2
    while bpm < 60: bpm *= 2
    # confidence: how peaky the pulse is relative to its neighbourhood
    ac = librosa.autocorrelate(onset)
    conf = float(min(1.0, (ac[1:200].max() / (ac[0] + 1e-9)) * 1.5)) if len(ac) > 200 else 0.3
    return round(bpm, 1), round(conf, 2)


def analyze(path, args):
    import librosa
    tags = read_tags(path)
    t0 = time.time()
    sr, stems = separate(path, args.model, args.device, args.stems_from)
    n = max(len(v) for v in stems.values())
    mix = np.zeros(n, dtype='float32')
    for v in stems.values(): mix[:len(v)] += v
    duration = n / sr
    segs, audible_s = find_isolated(sr, stems, purity=args.purity, mostly=args.mostly, min_s=args.min_seconds, floor_db=args.floor)
    out = []
    for s in segs:
        y = stems[s['stem']][int(s['start'] * sr):int(s['end'] * sr)]
        whole = (s['end'] - s['start']) >= 0.95 * audible_s
        key, kconf = (None, 0.0) if s['stem'] == 'drums' else key_of(y, sr)
        bpm, tconf = tempo_of(y if s['stem'] == 'drums' else mix[int(s['start'] * sr):int(s['end'] * sr)], sr)
        out.append({'instrument': STEM_LABEL.get(s['stem'], s['stem']), 'stem': s['stem'], 'start': s['start'], 'end': s['end'], 'seconds': round(s['end'] - s['start'], 1),
                    'whole': bool(whole), 'purity': s['purity'], 'tier': s['tier'], 'key': key, 'keyConf': kconf, 'tempo': bpm, 'tempoConf': tconf})
    return {'id': hashlib.sha1(str(Path(path).resolve()).encode()).hexdigest()[:12], 'file': str(path), 'artist': tags['artist'], 'title': tags['title'], 'album': tags['album'], 'year': tags['year'],
            'url': tags.get('url', ''), 'source': tags.get('source', 'file'), 'duration': round(duration, 1), 'segments': out, 'took': round(time.time() - t0, 1)}


# ---------------------------------------------------------------- cli
def iter_files(root):
    root = Path(root)
    if root.is_file(): yield root; return
    for p in sorted(root.rglob('*')):
        if p.suffix.lower() in AUDIO_EXT and not p.name.startswith('.'): yield p


def fmt_t(s):
    return f'{int(s // 60)}:{int(s % 60):02d}'


def main():
    ap = argparse.ArgumentParser(description='Find isolated instrument passages (sample material) in audio files you own.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    fe = sub.add_parser('fetch', help='download free audio from the Internet Archive into a folder')
    fe.add_argument('--out', default='crate', help='folder to download into (default crate)')
    fe.add_argument('--collection', default='78s', help='78s (Great 78 Project, 1898–1950s), netlabels, live, community, any, or an archive.org collection id (default 78s)')
    fe.add_argument('--from', dest='frm', type=int, default=None, help='earliest year')
    fe.add_argument('--to', type=int, default=None, help='latest year')
    fe.add_argument('--genre', default='', help='subject words, comma-separated, e.g. "jazz,blues"')
    fe.add_argument('--q', default='', help='extra free-text query (archive.org search syntax)')
    fe.add_argument('--limit', type=int, default=50, help='how many items (default 50)')
    fe.add_argument('--sort', default='popular', help='popular, newest, oldest or random (default popular)')
    fe.add_argument('--max-mb', type=float, default=120, help='skip files bigger than this (default 120)')
    fe.add_argument('--pause', type=float, default=1.0, help='seconds between downloads (default 1)')
    sc = sub.add_parser('scan', help='scan a folder (or one file)')
    sc.add_argument('path')
    sc.add_argument('--out', default='dig-results.json', help='results file for Hear (default dig-results.json)')
    sc.add_argument('--model', default='htdemucs_6s', help='Demucs model: htdemucs_6s (drums/bass/vocals/guitar/piano/other) or htdemucs (4 stems, faster)')
    sc.add_argument('--device', default=None, help='cpu, cuda or mps (Apple GPU); default picks the best available')
    sc.add_argument('--min-seconds', type=float, default=2.0, help='shortest passage to report (default 2)')
    sc.add_argument('--purity', type=float, default=0.9, help='share of the energy one stem must carry to count as clean (default 0.9)')
    sc.add_argument('--mostly', type=float, default=0.75, help='share for "mostly isolated" (default 0.75)')
    sc.add_argument('--floor', type=float, default=-45.0, help='silence floor in dBFS (default -45)')
    sc.add_argument('--stems-from', default=None, help=argparse.SUPPRESS)  # testing: read pre-separated stems
    sc.add_argument('--redo', action='store_true', help='re-analyze files already in the results file')
    args = ap.parse_args()
    if args.cmd == 'fetch':
        fetch(args); return

    if args.device is None and not args.stems_from:
        try:
            import torch
            args.device = 'cuda' if torch.cuda.is_available() else ('mps' if getattr(torch.backends, 'mps', None) and torch.backends.mps.is_available() else 'cpu')
        except ImportError:
            print('demucs/torch not installed: pip install -r requirements.txt', file=sys.stderr); sys.exit(1)

    out_path = Path(args.out)
    results = {'tool': 'dig', 'version': 1, 'generated': '', 'tracks': []}
    if out_path.exists():
        try: results = json.loads(out_path.read_text())
        except Exception: pass
    done = {t['file']: t for t in results.get('tracks', [])}
    files = list(iter_files(args.path))
    todo = [f for f in files if args.redo or str(f) not in done]
    print(f'{len(files)} audio files, {len(todo)} to analyze' + (f' (device {args.device})' if args.device else ''))
    for i, f in enumerate(todo, 1):
        print(f'[{i}/{len(todo)}] {f.name} … ', end='', flush=True)
        try:
            r = analyze(f, args)
        except Exception as e:
            print(f'skipped ({e})'); continue
        done[str(f)] = r
        segs = r['segments']
        print(f'{len(segs)} passage{"s" if len(segs) != 1 else ""} in {r["took"]}s')
        for s in segs:
            where = 'whole track' if s['whole'] else f'{fmt_t(s["start"])}–{fmt_t(s["end"])}'
            print(f'    {s["instrument"]:<30} {where:<13} {s["seconds"]:>5}s  {s["tier"]:<6} ' + (f'{s["key"]:<9}' if s['key'] else '—        ') + (f'{s["tempo"]} bpm' if s['tempo'] else ''))
        results['tracks'] = list(done.values()); results['generated'] = time.strftime('%Y-%m-%dT%H:%M:%S')
        out_path.write_text(json.dumps(results, indent=1))
    results['tracks'] = list(done.values()); results['generated'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    out_path.write_text(json.dumps(results, indent=1))
    n = sum(len(t['segments']) for t in results['tracks'])
    print(f'\n{len(results["tracks"])} tracks, {n} isolated passages → {out_path}\nOpen Hear → Sample Search → Load results and pick this file.')


if __name__ == '__main__':
    main()

# dig — Hear's listening tool

Finds sample material by *listening*: it separates each track into stems (drums, bass, vocals, guitar, piano, other),
marks every stretch where one instrument plays alone, measures the key and tempo of that stretch, and writes a results
file that Hear's **Sample Search** page reads (Home → Samples).

It works on audio files — and the point is audio you have *never heard*. `dig fetch` pulls free, legal records from the
Internet Archive by year and genre: the Great 78 Project (hundreds of thousands of digitized 78s, 1898–1950s), netlabel
releases, Creative Commons albums, the Live Music Archive. Nothing is taken from YouTube, Spotify or Qobuz; they don't
allow it, and the tool doesn't try.

## Install (once)

You need Python 3.10 or newer and about 3 GB of disk for the libraries and the separation model.

**Mac**

```bash
# Python: https://www.python.org/downloads/  (or `brew install python`)
cd ~/Downloads && git clone https://github.com/Henryg9797/Hear.git && cd Hear/tools/dig
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
brew install ffmpeg        # lets it read MP3/M4A; skip if you only have FLAC/WAV
```

**Windows** (PowerShell)

```powershell
# Python: https://www.python.org/downloads/  — tick "Add python.exe to PATH" in the installer
cd $HOME\Downloads; git clone https://github.com/Henryg9797/Hear.git; cd Hear\tools\dig
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
winget install Gyan.FFmpeg
```

The first scan downloads the separation model (~300 MB). On an Apple-silicon Mac the GPU is used automatically; on a
PC with an NVIDIA card install the CUDA build of PyTorch from pytorch.org for a 5–10× speed-up. On a plain CPU expect
roughly one minute per three-minute track.

## Use

1. **Fetch a crate** from the Internet Archive:

   ```bash
   python dig.py fetch --from 1946 --to 1955 --genre "jazz,blues" --limit 100 --out crate-jazz
   ```

   `--collection` picks the pool: `78s` (default, Great 78 Project), `netlabels`, `live`, `community`, `any`, or any
   archive.org collection id. `--sort random` wanders instead of taking the most-downloaded. `--q` adds raw
   archive.org search terms (`--q 'creator:(Lionel Hampton)'`). Each item lands in its own folder with a
   `dig-meta.json` carrying the title, artist, year and link.

2. **Scan it** (safe to interrupt; re-running skips what's done):

   ```bash
   python dig.py scan crate-jazz --out dig-results.json
   ```

   Options: `--min-seconds 4` to ignore short fills, `--purity 0.85` to be more lenient about what counts as "alone",
   `--model htdemucs` for the faster 4-stem model (no guitar/piano split). The terminal lists every passage as it goes:

   ```
   [12/100] Jumpin' At The Woodside … 2 passages in 41.3s
       Drums                          0:00–0:06     6.0s  clean  —        168.0 bpm
       Piano / keys                   1:52–2:04    12.2s  mostly  Bb major 170.1 bpm
   ```

3. **Load it in Hear**: Home → Samples → *Load results file* → pick `dig-results.json`. Filter by year, instrument,
   length, clean/mostly, sort by length, year or tempo, or type a key like `F minor`. Tapping a passage opens the
   record on archive.org at that timestamp. *Sampled?* asks Claude how heavily a record has been used (reliable for
   famous records; obscure ones come back "no known samples", which is the point).

   You can also scan your own files (`python dig.py scan ~/Music/Rips`); tags supply artist, title and year.

## How it decides

Every half-second the tool measures the energy of each stem. A window is "isolated" when one stem carries at least
90% of the energy (`clean`) or 75% (`mostly`) and the track is above the silence floor. Runs of at least two seconds
(short gaps allowed) become passages; a passage covering 95% of the audible track is reported as *Whole track*.
Key is estimated from the isolated stem's chroma against Krumhansl–Schmuckler profiles (never for drums); tempo from
onset strength, folded into 60–180 bpm. Both carry a confidence; Hear shows `?` when it's low. Stem separation is
imperfect — bleed from a cymbal or a vocal can keep a passage at "mostly" — and 78s add surface noise that lands in
"other", so for very noisy transfers try `--purity 0.8`.

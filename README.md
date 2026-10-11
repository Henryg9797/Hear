# Hear

Your records, all in one place. A record-collection front end for Spotify and Qobuz: search any artist, album or label, flip through a discography like a crate of covers, and tap to hear it in the app you already pay for.

Everything runs in the browser. There is no server and no account: the catalog is MusicBrainz, the covers come from the Cover Art Archive, and the "Hear on" buttons are plain links that open Spotify or Qobuz on your phone.

## Run it

**On your computer (quickest way to try it)**

1. Unzip the folder.
2. Double-click **Start Hear.command** (Mac; if macOS refuses the first time, right-click it › Open) or **Start Hear.bat** (Windows). A window opens showing two addresses and the app opens in your browser. (Or run `python3 serve.py` yourself.)
3. Leave that window open while you use the app.

**On your phone, from that same computer**: with the phone on the same Wi-Fi, open the second address the launcher printed (it looks like `http://192.168.1.23:8080`). Then Safari's share button › *Add to Home Screen* (iPhone) or Chrome's menu › *Add to Home screen* (Android) gives you an icon. It works whenever the computer is on and the launcher is running.

**As a real, permanent app**: put the folder on any free static host. Netlify (drag the folder onto app.netlify.com/drop), Cloudflare Pages, GitHub Pages and Vercel all work; they serve it over HTTPS, which lets the phone install it as a proper app with an icon and offline shell. If the folder lives in a GitHub repo, those hosts republish automatically on every change.

## Discogs as the catalog (recommended)

With a Discogs personal access token connected in Settings, Discogs becomes the catalog: artwork for nearly everything from a fast CDN, genres and styles on every record, artist photos and bios, "most collected" ordering on label and genre pages, Discogs' own community rating and have/want counts on album pages, YouTube links, and your Discogs collection as a third shelf. Exact Spotify/Qobuz links are still looked up from MusicBrainz in the background, and ratings, reviews and press still come from Wikipedia and Google Books.

Without a token (or with *Catalog: MusicBrainz* in Settings) everything runs on MusicBrainz and the Cover Art Archive as before.

Album, artist and label addresses from the two catalogs are different (`#/album/dm123` is a Discogs master, `#/album/<uuid>` a MusicBrainz release group); both keep working, so a shelf built on one survives switching to the other.

## Settings (all optional)

Open the Settings tab inside the app.

- **Main service**: which "Hear on…" button is the big one (Spotify or Qobuz).
- **Qobuz store region**: used for Qobuz search links, e.g. `us-en`.
- **Discogs personal access token**: paste it and tap *Connect*; the app checks the token, remembers your username, and switches the catalog to Discogs. Create one at discogs.com/settings/developers (free).
- **Claude API key**: powers the "Describe it" search ("hazy late-night dub-tinged post-punk…") and the AI mood tags on album pages. Get one at console.anthropic.com; usage is pay-as-you-go and tiny for this. Keys are stored only in your browser.

Without a Claude key, "Describe it" offers an **Ask Claude** button that opens claude.ai with your description typed in; paste the list it gives you back into the app and the albums appear as cards. (A rough MusicBrainz tag search is also there, but tags can't follow a real description.) With a key, searches run inside the app and you can refine the results in follow-ups ("less jazzy", "more 70s").

What the key costs: a "Describe it" search is about a cent with Sonnet, mood tags a fraction of a cent, and a "Dig deeper" web search about ten cents per album (cached). Current prices: https://platform.claude.com/docs/en/about-claude/pricing

## Home

The Home tab shows three cover flows that change every time you open or shuffle the app:

- **Genre spotlight**: twelve essential records in one genre (there are about 170 in the rotation), picked by Claude when a key is set, otherwise from MusicBrainz tags.
- **On the label**: a dozen albums from one label out of ~140 (Blue Note, Warp, Stax, Kranky, Soul Jazz…), with a link to the whole catalog.
- **Discography**: one artist's albums in order, from a list of ~230, or half the time an artist from your own shelf.

Plus a search box with type-ahead suggestions (artists, albums and labels appear as you type; things you've already visited come first) and your recently viewed albums. The shuffle button in the corner draws a new set.

## Artist and genre pages

An artist page opens with their photo and a short bio (from Wikipedia, with Discogs as a photo fallback when a token is set), their genres as tappable chips, and their releases as horizontal rows: Albums, EPs, Singles, Compilations, Live, Other, newest first, each cover with its star rating underneath.

A genre page (tap any genre chip) shows Claude's essential artists for that genre, essential albums, and every artist MusicBrainz has tagged with it.

## Star ratings everywhere

Every album, wherever it appears (cover flows, shelf, label pages, search results, picks), shows its aggregate star rating underneath: the mean of the critic scores in the album's Wikipedia ratings box, normalized to five stars (8/10 → 4★, A− → 4.5★). Badges load only when they scroll into view and are cached for a month, so browsing stays light on Wikipedia. Albums without a Wikipedia ratings box show no badge.

**Tap any star rating** to open the review sheet: the aggregate, each critic's score with a link to the review, Metacritic, and "What critics said", the reception paragraph from the album's Wikipedia article (credited and linked).

## Moods, crates and "more like this" (Claude key)

- **Moods tab**: pick up to three moods ("Dark · Lush · Late night"); Claude finds ten records that feel like that, across genres and decades. Results are cached per combination, can be refined ("more 70s"), swapped for a fresh set, or saved as a crate.
- **Crates**: any Describe-it or Moods result can be saved with a name. Crates live in the Shelf tab next to your albums and keep their play links and reasons.
- **More like this**: every album page has a "Find similar albums" button: three records close in sound and era, three kindred spirits from another scene. Cached per album.

## Ratings, reviews and press on every album

Each album page looks up what was written about the record:

- **Ratings**: the "Professional ratings" box from the album's Wikipedia entry (AllMusic, Pitchfork, Rolling Stone, NME, Christgau and so on), each with a link to the review when Wikipedia cites one. Every score is normalized to 5 stars (8/10 → 4★, 85% → 4.25★, A− → 4.5★) and averaged into one aggregate score. Metacritic is shown alongside but not double-counted.
- **Reviews**: every review Wikipedia cites, plus review links MusicBrainz knows about, sorted by year.
- **Interviews & articles**: the other sources Wikipedia cites, classified as interview or article, and magazine pages from Google Books (SPIN, Billboard, CMJ, Vibe and others are digitized there). Items from the release year (−1 to +2) are grouped as "At the time".
- **Dig deeper with Claude**: with a Claude API key, searches the web for more reviews, interviews and features and lists what it finds. Results are cached per album.
- Links to full-text search of digitized magazines on the Internet Archive and to Google Books.

Wikipedia content is used under CC BY-SA and always linked. Albums without a Wikipedia entry still get the Google Books, Internet Archive and Claude routes.

## How the links work

- When MusicBrainz has a direct album link (Spotify, Qobuz, Bandcamp, Apple Music, Deezer, Tidal, Discogs, AllMusic), the button goes straight to that album. Chips with a solid border are direct links.
- When it doesn't, the button opens a search for "artist + title" inside that service. Chips with a soft fill are search links.
- Qobuz web-player links are rewritten to `open.qobuz.com` so they open the Qobuz app on a phone.

## Data sources and limits

- **MusicBrainz** (musicbrainz.org): catalog, discographies, labels, tags and cross-links. Free, no key, limited to one request per second per user; the app queues and caches requests, so a page can take a few seconds the first time.
- **Cover Art Archive** (coverartarchive.org): covers. Coverage is good for well-known albums and patchy for obscure ones; missing covers show a colored placeholder (or Discogs art when a token is set).
- **Discogs** (optional): genres, styles, cover fallback.
- **Claude** (optional): recommendations and mood tags. AI-written text is labeled as such.
- AllMusic reviews are not reproduced; the app links to AllMusic's page for the album.

## Updating the app

`sw.js` caches the app shell on phones. When `index.html` changes, bump `VERSION` in `sw.js` so installed phones pick up the new build on their next open.

## Files

- `index.html` – the whole app (markup, styles, script)
- `manifest.webmanifest` – home-screen install metadata
- `sw.js` – service worker (offline app shell)
- `icons/` – app icons

## Where it lives

The app is published automatically from this repository to https://henryg9797.github.io/Hear/ on every push to `main`.

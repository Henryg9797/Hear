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
- **Claude API key**: powers Ask Claude ("hazy late-night dub-tinged post-punk with a female vocal…"), Moods, "more like this", estimated star ratings and web checks for real scores. Create it at console.anthropic.com (*Get API key*). Keys can carry an expiry date, and a deleted or expired key fails with a 401 "invalid x-api-key": the fix is always to create a new key and paste it into Settings. The Console account also needs a small prepaid balance. Keys are stored only in your browser, and each address (the GitHub Pages site, localhost…) keeps its own settings.
- **Rate unrated albums automatically**: off by default. When on, artist, label, genre and shelf pages ask Claude for estimated ratings of every album that has no critic score, in the background. Off, the same thing is a "Rate the rest" button on those pages.

Without a Claude key, "Describe it" in the Search tab offers an **Ask Claude ↗** button that opens claude.ai with your description typed in; paste the list it gives you back into the app and the albums appear as cards. (A rough MusicBrainz tag search is also there, but tags can't follow a real description.)

What the key costs with Sonnet: an Ask Claude search about a cent, a page of estimated ratings about a cent, mood tags a fraction of a cent, and a web check ("Dig deeper", "Check the web for real scores") about ten cents per album (cached). Current prices: https://platform.claude.com/docs/en/about-claude/pricing

## Home

The Home tab shows three cover flows that change every time you open or shuffle the app:

- **Genre spotlight**: twelve essential records in one genre (there are about 170 in the rotation), picked by Claude when a key is set, otherwise from MusicBrainz tags.
- **On the label**: a dozen albums from one label out of ~140 (Blue Note, Warp, Stax, Kranky, Soul Jazz…), with a link to the whole catalog.
- **Discography**: one artist's albums in order, from a list of ~230, or half the time an artist from your own shelf.

Plus a search box with type-ahead suggestions (artists, albums and labels appear as you type; things you've already visited come first) and your recently viewed albums. The shuffle button in the corner draws a new set.

Under the search box, three ways to browse (tap one to open it, tap again to close):

- **Genres**: a table of sixteen major genres (Rock, Pop, Electronic, Hip Hop, Jazz, Funk / Soul, Blues, Folk, Country, Reggae, Latin, World, Classical, Metal, Punk, Experimental) with their styles underneath, AllMusic-style. Every name is a link to a genre page.
- **Moods**: the same table for moods (Feel, Energy, Texture, Voice, Mind, Time & place). Tap one and the Moods tab finds records that feel like it; a link below lets you mix up to three.
- **Ask Claude**: a search bar for exactly what you want to hear, plus your recent asks and a few examples. See below.

## Ask Claude

Type what you want to hear the way you would say it to a friend behind the counter ("spiritual jazz from the 70s that feels like a sunrise", "like the last two Talk Talk records but made this decade") and the result is its own page: a vertical cover flow of ten records, each with a big cover, the artist, the album, the release year and label, its star rating, and two or three sentences from Claude on why it fits what you asked for and where it only half-fits. Covers tilt and shrink as they leave the middle of the screen and the page snaps from record to record.

Each card has Hear on Spotify / Qobuz buttons and a Details link once the album is matched to the catalog. Below the list: a refine box ("less jazzy", "more 70s", "no strings"), "Ten different records" for a fresh set, and "Save as crate". Results are cached per question, so coming back is free; the last thirty questions are kept.

The Search tab's "Describe it" sends you to the same page when a key is set. Genre pages and the home spotlight have an "Ask Claude for deeper cuts" link that fills the question in for you.

## Artist and genre pages

An artist page opens with their photo and a short bio (from Wikipedia, with Discogs as a photo fallback when a token is set), their genres as tappable chips, and their releases as horizontal rows, AllMusic-style: **Albums** (studio and live), **Singles & EPs**, **Compilations**, oldest first, each cover with its star rating underneath.

**What counts as a studio album** comes from MusicBrainz, whose release groups are typed: an "Album" with no secondary type is a studio album, and Live, Compilation, Remix and Soundtrack are marked as such. Discogs can't make that distinction (a live album, a remix album, a box set and a reissue with extras are all just "Album" there), so with Discogs as the catalog the app looks the artist up in MusicBrainz (by the Discogs link MusicBrainz keeps for most artists, otherwise by name), takes the typed album list from there, and matches each title to Discogs' most-collected masters for the cover and the album page. Radiohead's Albums row is therefore exactly Pablo Honey → A Moon Shaped Pool, nine covers in order. Rows: **Albums**, **Live**, **Singles & EPs** (Discogs, most collected), **Compilations**, **Other albums** (editions, box sets, remixes), **Other**. If MusicBrainz doesn't know the artist, the Albums row falls back to Discogs' album-format masters.

Why not just the newest releases: Discogs lists thousands of entries for a big artist, most of them bootlegs, regional pressings and "appears on" compilations, so "the newest 300" used to miss the classics entirely. Collection counts put the real records first, and masters come with full-size covers rather than the 150-pixel thumbnails of the plain release list.

A genre page (tap any genre chip) shows Claude's essential artists for that genre, essential albums, and every artist MusicBrainz has tagged with it.

## Star ratings everywhere

Every album, wherever it appears (cover flows, shelf, label pages, search results, picks), shows its aggregate star rating underneath: the mean of the critic scores in the album's Wikipedia ratings box, normalized to five stars (8/10 → 4★, A− → 4.5★). Badges load only when they scroll into view and are cached for a month, so browsing stays light on Wikipedia.

**Tap any star rating** to open the review sheet: the aggregate, each critic's score with a link to the review, Metacritic, and "What critics said", the reception paragraph from the album's Wikipedia article (credited and linked).

**Albums with no critic scores** (most of the catalog, outside the famous records) get an estimate from Claude when a key is set, shown in muted stars with an "est." chip so it is never mistaken for a real aggregate. Claude cannot hear the music; the estimate is its reading of the record's reception (AllMusic, Pitchfork, RYM, Metacritic, the press it knows of) on AllMusic's 1–5 scale, with a confidence level, and it says "not enough known" rather than guessing when it doesn't recognize a record. Album pages estimate their own album automatically; artist, label, genre and shelf pages have a "Rate the rest" button (or do it in the background with the auto-rate setting), twenty albums per request. The review sheet and the album page show the one-line reason behind an estimate and a **Check the web for real scores** button, which searches for published reviews and replaces the estimate with their actual scores when it finds any. If Wikipedia later turns out to have a ratings box for an estimated album, the real scores take over.

## Moods, crates and "more like this" (Claude key)

- **Moods tab**: pick up to three moods ("Dark · Lush · Late night"); Claude finds ten records that feel like that, across genres and decades. Results are cached per combination, can be refined ("more 70s"), swapped for a fresh set, or saved as a crate.
- **Crates**: any Ask Claude or Moods result can be saved with a name. Crates live in the Shelf tab next to your albums and keep their play links and reasons.
- **More like this**: every album page has a "Find similar albums" button: three records close in sound and era, three kindred spirits from another scene. Cached per album.

## The album page

The album page is deliberately a streaming view: cover, title, artist, year · type · label, the star rating, a few style chips, the Hear on Spotify / Qobuz buttons with secondary links (Bandcamp, Apple Music, Deezer, Tidal, Discogs, YouTube), Add to shelf, and the tracklist. Everything else sits in four collapsed rows you tap to open, and the app remembers which rows you keep open:

- **Ratings & reviews** (the header shows the score, e.g. "4.2 ★ · 5 reviews", or "3.5 ★ est.")
- **Interviews & articles** (the header shows how many were found)
- **About**: the Wikipedia summary or Discogs notes, all styles and tags, AI mood tags, and release details (labels, formats, country, date, Discogs collection stats)
- **More like this**: Claude's six related records

## Ratings, reviews and press on every album

Behind those rows, each album page looks up what was written about the record:

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
- **Claude** (optional): recommendations, estimated ratings and web checks. AI-written text and estimated scores are labeled as such. Lists come back as structured tool replies (never JSON written as prose), so a stray character can't break a search.
- AllMusic reviews are not reproduced; the app links to AllMusic's page for the album.

## Updating the app

`sw.js` caches the app shell so the home-screen icon works offline, but the page itself is fetched network-first: an online phone always runs the current build on its next open, and a new build's service worker reloads the page once when it takes over. When `index.html` changes, bump `VERSION` in `sw.js` and `BUILD` in `index.html` together; Settings shows the build number so you can check what a device is running.

If Claude features misbehave, Settings → **Test key** sends one tiny request and reports exactly what came back (works and how fast, or the error in plain words). Claude requests time out after two minutes and retry once on connection trouble or when the API is overloaded.

## Files

- `index.html` – the whole app (markup, styles, script)
- `manifest.webmanifest` – home-screen install metadata
- `sw.js` – service worker (offline app shell)
- `icons/` – app icons

## Where it lives

The app is published automatically from this repository to https://henryg9797.github.io/Hear/ on every push to `main`.

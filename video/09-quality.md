# 09 · What "top-notch" means

Free tools don't cap quality. Most videos that look cheap fail on story, sound and consistency, not on the software. This lesson is the quality bar, split into what Claude can check automatically and what needs you.

## The order that matters

1. **Story.** A question in the first 15 seconds that the viewer needs answered, and a reason to keep watching at every act break.
2. **Sound.** Clear narration, controlled music, YouTube loudness (lesson 05).
3. **Pacing.** The picture changes every few seconds; nothing lingers past its point.
4. **Consistency.** One type system, one colour grade, one grain, one narrator, one frame rate.
5. **Spectacle.** Hero shots, 3D, generated clips. Last, because it only lands if 1 to 4 are already right.

## Story and script

| Rule | Check |
|---|---|
| Hook inside 15 seconds: a surprising fact, a contradiction, or stakes | Read only the first three lines aloud. Would you stay? |
| Every act ends on an open question | Each act's last line should make the next one necessary |
| Concrete beats abstract: numbers, names, dates, objects | Circle every vague word ("huge", "many", "very") and replace it with a fact |
| Tag every claim with its source | Documented, inferred or speculative, as on a good documentary channel |
| Show reconstructions as reconstructions | On-screen labels such as the demo's "MASSING STUDY · ILLUSTRATIVE" |

Claude drafts well and tightens well. It also states wrong facts confidently. Make it attach a source to every number, and check the ones the story depends on yourself.

## Picture

| Rule | Why |
|---|---|
| Picture change every 3 to 6 seconds (a cut, a move, a reveal) | Static frames are where viewers leave |
| Every shot has a subject, and the frame says where to look | Light, contrast and composition lead the eye |
| Text stays on screen long enough to read twice | About 1 second per 3 words |
| One grade across sources (3D, archive, stock, graphics) | Matching grain, contrast and colour temperature hide the seams |
| 24 fps everywhere, 1920x1080 or 3840x2160 delivery | Mixed frame rates judder |
| Safe margins: keep text 5% inside the edges | Phones and YouTube's own UI crop the edges |

## Automated checks (the demo's `qa.py`)

| Check | Passes when | Catches |
|---|---|---|
| Integrated loudness | -14 LUFS (plus or minus 1) | A mix that YouTube will turn down, or that sounds weak |
| True peak | -1 dBTP or lower | Distortion after YouTube re-encodes |
| Voice over music | Music at least 15 dB under narration | Words lost on phone speakers |
| Black frames | No black stretch over 0.6 s | A missing render, or a camera inside geometry |
| Frozen picture | No frame held over 1.5 s (grain removed before comparing) | A shot that silently became a still |
| Format | 1920x1080, 24 fps, H.264 + AAC | Upload problems, judder |
| Bitrate | 6 to 25 Mbps for 1080p24 | A file far bigger than YouTube needs (the demo's first export was 51 Mbps) |
| Sync | Audio and video lengths within 0.1 s | Drift at the end of the video |

Run it after every render. It exits with an error when any check fails, so it can block a publish step or a Claude Code hook (lesson 10).

## Frame review by Claude

`qa.py` also writes a **contact sheet**: one frame per second, tiled. Ask Claude to review it against a written brief, for example:

> Review contact_sheet.png for the channel brief in CLAUDE.md. For each problem give the timestamp, what is wrong, and the fix. Check: subject clear, text legible and inside safe margins, consistent grade across shots, no frame that looks broken or empty.

This is how the demo's problems were found: a black shot, a flat first frame, a camera inside a building, labels running together. Claude sees stills, not motion. **Watch the final cut yourself once**, at full screen and on a phone, before it goes live.

## Thumbnails and titles

The thumbnail and title decide whether anyone sees the video at all. They are worth more of your time than any single shot.

- One subject, one idea, three words or fewer of text, readable at phone size.
- Make it from your best frame: render a dedicated hero still at 3840x2160 with the same scene script.
- Write 5 to 10 title options, then pick against the script: the title's promise must be paid off in the first minute.
- Test at the size YouTube actually shows: 320x180. Claude can build a page that shows your options at that size next to each other.

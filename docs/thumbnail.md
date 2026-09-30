# PALS's Notes Thumbnail Guideline

Sep 29, 2026 · @Pedro · revised Sep 30, 2026 (Shorts grid crop)

## The rule

Every long-form thumbnail and every Shorts cover on PALS's Notes uses one template: an ink field, a cream headline with one orange word, one subject, and the orange notch from the logo. The template covers both languages and every topic, from astronomy to linguistics.

The template is sized for browse view, where a thumbnail is judged. The sidebar shows a long-form thumbnail at about 168 × 94 px, roughly 13% of the 1280 × 720 canvas. At that scale, canvas text shorter than about 60 px cannot be read. So annotation text, captions and labels carry no information, and the headline must carry it all.

Recognition comes from repetition. When layout, palette and mark stay fixed, a returning viewer identifies the channel before reading a word. Topic, subject and headline are the only parts that change between videos.

## Palette and type

The palette is taken from the channel logo and holds exactly three colors. No other color appears in type or graphic elements. The subject image keeps its own colors.

| Role | Name | Hex | Used for |
| --- | --- | --- | --- |
| Field | Ink | #16181D | Background, solid bands behind headlines |
| Primary text | Cream | #F2EBDD | Headline words |
| Accent | Signal orange | #E8581C | One headline word, brand notch |

The headline uses one typeface: Archivo Condensed Black, in uppercase, with tracking at 0. When Archivo is unavailable, use Barlow Condensed Black. Weights, italics and second typefaces are not used.

No gradients, glows, outlines or drop shadows are applied to text. Contrast comes from cream or orange on ink, which is sufficient at browse size.

## Long-form layout (1280 × 720)

The canvas splits into a text column on the left and a subject column on the right. Coordinates are in canvas pixels from the top-left corner.

| Zone | Area (x, y, width × height) | Content |
| --- | --- | --- |
| Outer margin | 64 px on every edge | Empty ink |
| Headline column | 64, 64, 640 × 592 | Headline, vertically centered |
| Subject column | 704, 0, 576 × 720 | One cut-out subject, may break the right and top edges |
| Duration badge | 1060, 630, 220 × 90 | Empty: YouTube's duration badge covers it |
| Brand notch | 0, 656, 64 × 64 | Orange right triangle, right angle at bottom-left |

The subject may overlap the headline column by up to 64 px. It never covers a headline letter. The headline never enters the subject column.

## Shorts cover layout (1080 × 1920)

The cover is built into the video. The first 0.5–1 s of every Short is the designed cover card, and that frame is selected as the cover. This works whatever cover options the upload flow offers. Shorts loop, so the card costs almost nothing at replay.

The layout keeps content out of the zones that two surfaces hide.

- **The channel's Shorts grid crops the cover to 2:3.** The tile shows the centre 1080 × 1620 of the cover (y 150–1770) and rounds its corners. The top and bottom 150 px are never seen there. This was measured on the channel's Shorts tab on 2026-09-30, where tiles are 286 × 429 px. A headline that started at y 160 lost its first line in that grid.
- **The Shorts player covers the bottom quarter and the right edge.** The title, channel name and caption sit over the bottom quarter. The action buttons sit down the right edge.

Everything that carries information sits inside the grid-safe area: x 80–1000, y 220–1700. That is the 2:3 crop with a 70 px inner margin, clear of the rounded corners.

| Zone | Area (x, y, width × height) | Content |
| --- | --- | --- |
| Grid crop | 0, 150, 1080 × 1620 | What the Shorts tab shows. Nothing essential outside it |
| Headline band | 80, 220, 920 × 460 | Headline on solid ink. The first line's cap top is at y ≥ 220 |
| Subject band | 80, 680, 840 × 720 | One subject, same asset as the parent long video |
| Brand notch | 80, 1336, 64 × 64 | Orange right triangle, right angle at bottom-left. Never in a corner of the canvas, where the grid's rounding clips it |
| Player overlay | 0, 1440, 1080 × 480 | Ink only, no content |
| Action rail | 940, 800, 140 × 640 | No content |
| Top strip | 0, 0, 1080 × 220 | Ink only: cropped in the grid |

Scene-based Shorts, such as tabletop dioramas or archival footage, may fill the subject band and the player overlay. The headline band stays solid ink in every case, and the scene carries no information in the top strip or below y 1770.

## Headlines

The headline states the question or claim the video resolves, in the fewest words that still say it.

- **Length.** Long-form: four words maximum. Shorts: three words maximum, where a number such as 30s counts as one word.
- **Size.** Long-form cap height is at least 90 px. Shorts cap height is at least 120 px. Break the headline into two or three lines rather than shrink it. On Shorts, three lines must fit the 460 px headline band: two line spacings plus one cap height stay at or under 460 px (the kit's 176 px size at 0.92 line height gives 2 × 162 + 121 = 445 px).
- **Orange word.** Exactly one word is orange: the noun or number the video answers.
- **Word width.** No word is ever split across lines. A word wider than the column may shrink only down to the minimum cap height; if it still does not fit, use a shorter word. Measured in Archivo Condensed Black: EXOPLANET? fits the long-form column at 91 px cap height, EXOPLANETA? needs 83 px and does not, so the Portuguese thumbnail says PLANETA?.
- **Language.** The headline is in the video's language. A Portuguese video gets a Portuguese headline. No headline mixes languages.
- **Relation to the title.** The headline complements the video title and never repeats it word for word.
- **Excluded.** Subtitles, series names, dates, captions, labels, arrows and emoji.

Current catalog, rewritten to the rule (orange word in bold):

| Video | Long-form headline | Shorts headline |
| --- | --- | --- |
| Beta Pictoris b | RADIO FROM AN **EXOPLANET**? | RADIO FROM A **PLANET**? |
| Protein cage | A **CAGE** BUILDS ITSELF | **CAGE** BUILDS ITSELF |
| Flexibility Trap | **FREEDOM** HURTS REASONING | **FREEDOM** HURTS REASONING |
| O Sol | DENTRO DO **SOL** | LUZ DE **170 MIL** ANOS |
| Bubbles | WHY BUBBLES **PLOP** | WHY BUBBLES **PLINK** |
| Segunda Guerra | O MUNDO EM **RUPTURA** | A **GUERRA** EM 30s |
| Jet engine | INSIDE A **JET ENGINE** | **JET ENGINE**, 30s |
| Harness | **MODELS** AREN'T ENOUGH | — |
| Nancy Grace Roman | **ROMAN** MAPS THE SKY | — |
| 2026 Tech Pivot | WHERE 2026 **MONEY** GOES | — |
| The A-Words | THE **A-** PREFIX | — |
| Iran war tabletop | — | **IRAN** WAR, TABLETOP |

JET ENGINE counts as one orange word because the compound names a single object.

## Subjects

Each thumbnail shows one subject: the object the video explains, cut out from its background and placed on ink. Examples are a planet, a protein cage, a turbine cutaway, the Sun, or a single bubble.

- **One object.** A composite of several objects is not allowed. Two objects appear only when the video is a comparison between them.
- **Scale.** The subject fills at least 60% of the height of its zone.
- **Abstract topics.** When the topic has no physical object, as in AI reasoning, investment or etymology, the subject is a single emblem. That can be a letterform, a symbol or one diagram element, drawn in cream and orange.
- **Scenes.** Full scenes (a map, a battlefield, a diorama) are used only when the scene itself is the subject. The headline zone then stays solid ink.

A Short cut from a long video is its visible twin. It uses the same subject asset and the same orange word, where the word limit allows. The Short's related-video link points to the parent video.

## Pre-publish checklist

A thumbnail ships only when every box is ticked.

- [ ] Shrunk to 168 × 94 px (long-form) or 90 × 160 px (Shorts), the headline reads without zooming
- [ ] Shorts only: cropped to the centre 1080 × 1620 (y 150–1770) and shown at 286 × 429 px, the whole headline and the notch are visible, and no letter touches the crop edge
- [ ] Only ink, cream and signal orange appear outside the subject
- [ ] Headline is within the word limit, in the video's language, and has exactly one orange word
- [ ] One subject, filling at least 60% of its zone height
- [ ] Duration badge zone (long-form) or player overlay and action rail (Shorts) hold no content
- [ ] Orange notch is in place
- [ ] Shorts only: the cover card is the first frame, and the related-video link points to the parent video

## Measurement and revision

The guideline stays in force until the numbers say otherwise. Every result is logged, including the losses.

- **Long-form.** Test the template against the current style with Test & Compare in YouTube Studio on the next four uploads. The measure is watch-time share.
- **Shorts.** Compare "viewed vs. swiped away" on the next six Shorts against the median of the eight existing Shorts.
- **Log.** For each test, record the date, video, variant, measure, value, and impressions.

Revise under two conditions. If the template loses on at least three of the four long-form tests, switch the field to cream (#F2EBDD) with ink text, and keep everything else. If the Shorts fall below the existing median, test per-topic field colors on the next six Shorts.

The back catalog migrates only after the template wins. Migration runs in order of current monthly impressions, highest first.

**Exception: the Shorts grid crop.** Every existing Short whose headline starts above y 220 loses its first line in the channel's Shorts tab. As of 2026-09-30, that is all eight covers in the grid. Moving their headlines into the grid-safe area is a defect fix, not a template change, so it does not wait for the test. Keep each cover's style and change only the headline position.

# Retrofit: what the owner can add in YouTube Studio without a new video file

Written by the growth role on 2026-10-02, updated the same day (cl-growth, task growth-answers-001) after the owner published more films. Covers the ten long films and four Shorts the board lists as published on 2026-10-02: v016, v018 (a Short), v019, v022, v024, v025, v026, v027, v028, v029, S07, S10, S16, S18. Nothing here changes an approved file and nothing in any `publish/` folder was edited: the texts below are proposals for the owner to paste. **The short, ordered list of what to do in Studio, with the exact texts, is `OWNER-STUDIO-CHECKLIST.md`.**

**Owner's answers (2026-10-02) that this file now assumes:** advanced features are on; no other pages exist (so no profile links beyond the channel, and no `[OWNER: other pages]` line); automatic dubbing is off and stays off; videos are "not made for kids"; the watermark is on; the owner edits in Studio. The plain channel address is used everywhere, not `?sub_confirmation=1` (the owner did not know it; it is undocumented). **No text here promises a publishing frequency**: the owner's target (30 a day) is not yet real and the coordinator has not confirmed a cadence.

## How this was made, and its limits

- Each film's captions (`publish/captions.en.vtt`) and `publish/description.md` were read in full (v028, v019, v024, v025, v029, S10, S18 in the first pass; v016, v018, v022, v026, v027, S07, S16 in the second).
- The last 24 seconds of each long film were sampled with ffmpeg on the CPU (four frames a second at low resolution to find when the credits card starts, and the last full-resolution frame to measure where its text sits). Shorts: the last 12 seconds. For the second pass (v016, v022, v026, v027) the frames came from the approved cut in each film's `out/`, one frame every two seconds and the last frame at 960 px wide, so those rectangles are good to about 10 px at 1920 wide: **read them again in Studio's own preview before saving.**
- Positions are pixels on the 1920×1080 frame, x from the left edge, y from the top. Studio's end-screen editor works by dragging on a grid, so treat each rectangle as the place to drag to. **I could not verify the smallest size Studio accepts for an element** (`PLATFORM-RULES.md`, section 1); where the free space is small I say so.
- I cannot watch motion or hear sound. "Speech ends at" is the end time of the last caption cue.
- Platform facts are in `PLATFORM-RULES.md`. The one that governs this whole file: clickable description links, pinned comments, chapters and a Short's related video all need **advanced features** on the channel. Check that first (Studio, Settings, Channel, Feature eligibility).
- Evidence labels: **[Platform]**, **[Film]** (read in the film's captions or frames), **[Judgement]**.

## The whole table first

| Film | Length | Credits card (free of speech) | End screen that fits | Next film to promote | Why that one |
|---|---|---|---|---|---|
| v016 A film from a text file | 4:46 | none; closing picture 4:33.5–4:46.0 (12.5 s) | Yes, over the dark sides of the picture | "Best for viewer" | No film follows from "how these films are made" more than another |
| v019 Never seen a wing | 4:18 | 4:12.5–4:18.0 (5.5 s) | Yes, short | v026 | Flow control: a program finds it; one steady car does it |
| v022 The Moon is leaving | 3:55 | about 3:46–3:55 (9 s) | Yes, bottom strip | "Best for viewer"; v020 when published | The pair: tides took Venus's moon; tides are moving ours |
| v024 Your phone needs Einstein | 3:56 | 3:51.0–3:56.0 (5.0 s) | Barely: card is at the 5 s minimum and full of text | "Best for viewer"; v021 when published | The film names the 1919 eclipse in Brazil at 3:26 |
| v025 The blob and the railway | 3:53 | 3:38.5–3:53.0 (14.5 s) | Yes in time, narrow in space | v026 | No planner, one local rule; a jam with no cause is the same idea on a road |
| v026 The traffic jam with no cause | 4:09 | about 3:58.5–4:09.0 (10.5 s) | Yes, bottom strip and right column | v025 | A pattern nobody planned; "where is the planner?" |
| v027 Randomness draws the curve | 3:37 | about 3:31.5–3:37.0 (5.5 s) | Barely: just over the 5 s minimum | v028 | One is unpredictable, many are certain; the same move applied to a decision |
| v028 The test said yes | 4:06 | 3:59.0–4:06.0 (7.0 s) | Yes, roomy | v029 | Both are about data that answers a different question from the one asked |
| v029 No bullet holes | 4:47 | 4:33.5–4:47.0 (13.5 s) | Yes | v028 | The pair of v028 |
| v018 Moon rings (Short) | 1:04 | none | Not on a Short (not verified); related video | v022 | Both are the Moon, both use real NASA material |
| S07 445-day year (Short) | 0:58 | none | Same | related video: v022 | A year of 445 days by decree; v022's year of about 400 days by physics |
| S10 0.1 + 0.2 (Short) | 0:35 | none | Same | related video: v016 | Exact arithmetic vs the engine's "same frame on any machine" claim, with its tolerance |
| S16 Four colours (Short) | about 0:30 | none | Same | none | No long film of ours is about proof or maps |
| S18 Twenty-three people (Short) | 0:42 | none | Same | related video: v028 | Intuition answering the wrong question |

Three things apply to all the long films:

1. **Set the end screen's start at the time given, not earlier.** Each film's last spoken line and closing picture finish first (the role's rule, and the reviewer's: nothing covers a picture the viewer is reading).
2. **Two elements, not four.** One film to watch (primary), the Subscribe element (secondary). YouTube allows four; one primary ask per piece is the channel's rule. [Judgement]
3. **The end screen on these films is silent.** The films do not say "the next film is on screen". The role's rule is that an on-screen ask is spoken. YouTube's elements are the platform's furniture, not our picture, so I count them like the player's own buttons; but this is the weak point of a retrofit, and the reason new films get a spoken line.

---

## v028 · The test said yes. It was probably wrong.

**[Film]** 246.0 s. Last line "And that is the test working exactly as designed." ends at 3:57.5. The closing picture (the POSITIVE slip and the RARE/COMMON slider) holds to 3:58.5. Credits card 3:59.0 to 4:06.0, fading in its last half second. Card text sits at x 551–1369, y 389–681: five centred lines. Everything else is plain ink, with the brand notch at the bottom left corner.

**End screen: 3:59.0–4:06.0 (7 s).** This is the roomiest ending of the five.

| Element | Rectangle (x, y) | Size | Start |
|---|---|---|---|
| Video: v029 "Armour the places with no bullet holes" | 640–1280, 700–1060 | 640×360 | 3:59 |
| Subscribe | 1500–1700, 435–635 | 200×200 | 3:59 |

v029 is published (board, 2026-10-02): set the Video element to v029 directly.

**Why v029.** v028 says the doctors "answered a different question" (2:05) and that the real question is "how common is this, among people like me?" (3:45). v029 says "data is what survived to be counted" (4:05) and asks "what am I not seeing, and what removed it?" (4:12). Same habit of mind, different trap. [Judgement] It is the closest pair in the catalogue.

**Cards**

| Time | Target | Why here |
|---|---|---|
| 3:27 | v029 (video card), teaser "Another filter: the missing bullet holes" | "Each one searches for something rare, and each one drowns in false alarms the same way" closes a list of other fields; the viewer is already being told this pattern is general |

No other card. S18 is a Short on a different idea; a card to it at 2:05 would interrupt the film's central explanation.

**First lines of the description.** Keep the current first paragraph: it is the film's own question and its answer, and it is what shows before "more":

> A screening test finds eight out of every ten cases. Yours comes back positive. How likely is it that you are ill? In 1982, around 95 of about 100 doctors asked a version of this question said about 75%. The answer was under 8%.

Add directly under the third paragraph (the "not medical advice" line), before CHAPTERS:

> Next: Armour the places with no bullet holes: [OWNER: paste v029's YouTube link]

**Link block** (replaces the last two lines of the pasted text; the same block on every long film, see `growth-kit-proposal.md`):

> MORE FROM PALS'S NOTES
> Subscribe: https://www.youtube.com/@PALSsNotes
> All films on numbers that mislead: [OWNER: playlist link, once the playlist "Numbers that fool us" exists]

The owner has no other pages (answer to question 3), so there is no line for them. The plain channel address is used rather than `?sub_confirmation=1`, which no YouTube Help page documents; the owner did not know it either (question smaller-points).

**Pinned comment**

> The numbers in the film are the ones the doctors were given in 1982, not today's figures for any real test. If you want to try it yourself: take any test you know, and ask the film's question, how common is the thing among people like the one being tested? The sources are in the description.

[Judgement] It adds something a commenter can act on, repeats the film's own caution, and asks for nothing.

**Playlists:** "Numbers that fool us" (with v029, v027, S18); "All films".

**Other Studio settings to check:** audience "not made for kids"; hashtags, three at the end of the description: `#statistics #probability #bayes` (Bayes is the subject; the film never says the word, so the owner may prefer `#medicaltests`).

---

## v019 · This controller had never seen a wing

**[Film]** 258.0 s. Last line "Close to a wall, at least, the evidence points to fluid." ends at 4:08.2. The flow picture with that sentence on a panel holds to about 4:12.3. Credits card 4:12.5 to 4:18.0; its lines fade in over the first two seconds. Card text x 473–1445, y 359–710.

**End screen: 4:12.5–4:18.0 (5.5 s).** It is allowed (minimum 5 s) and short. **[Judgement]** A viewer has about three seconds after the elements appear.

| Element | Rectangle | Size | Start |
|---|---|---|---|
| Video: v026 "The traffic jam with no cause" | 676–1245, 736–1056 | 569×320 | 4:12.5 |
| Subscribe | 1560–1760, 435–635 | 200×200 | 4:12.5 |

**A longer option, with a cost.** Starting at 4:08.5, after the last word, gives 9.5 s. For its first four seconds the elements would sit over the flow simulation while the closing sentence is still on its panel (top right, about x 1010–1870, y 90–350) and the label "Our run of HydroGym's pinball · rotation set by hand" is at the bottom left. The wake runs across the middle (y about 380–700). The lower right corner (x 1300–1862, y 724–1040) is empty flow in those frames and stays clear of the credits text afterwards; a Video element fits there at 562×316. The Subscribe element has no place that is clear in both pictures, so it would still start at 4:12.5. I do not recommend this without the art director's look: it puts a clickable box on the film's last image.

**Why v026 (v026 is published; the first pass had v025 until then).** v019's question is whether a program "learned this one flow, or something about fluids in general" (0:16). v025's is "where, in a blob, is the planner?" (0:28) and its answer is one rule about flow in a tube. Both are a published paper followed step by step, and both are about a simple rule doing what looks like design. The link is thematic, not factual. v026 shows one steady car damping a traffic wave, which is flow control by a single actuator, the nearest thing in the catalogue to this film's subject; v025 stays the second choice.

**Cards:** none. The narration never mentions something another film of ours explains. A card with no spoken reason is the thing the role says not to do.

**First lines of the description:** keep the current first paragraph. Add before CHAPTERS:

> Next: The traffic jam with no cause: [OWNER: v026's YouTube link]

**Link block:** as in v028, with the playlist line reading "Films that read one paper closely: [OWNER: playlist link 'One paper, read closely']".

**Pinned comment**

> Two things the film says quickly and the paper says at length: the 11% is total drag on one wing section at one angle, and the 38% is skin friction in the controlled patch only. The preprint is open to read: arXiv 2512.17534 (link in the description). The flow you see moving is our own run of the paper's simulation, with the rotation set by hand; no program learned anything in it.

**Playlists:** "One paper, read closely" (with v025, v026; later v020); "All films".

**Hashtags:** `#fluiddynamics #reinforcementlearning #engineering`

---

## v024 · Your phone needs Einstein to find you

**[Film]** 236.0 s. Last line "And the clock needs Einstein." ends at 3:45.8. The street map with the clock and the title holds to about 3:49, fades by 3:51. Credits card 3:51.0 to 3:56.0. The card is dense: seven lines, text x 193–1730, y 209–829.

**Honest reading: this ending leaves almost no room.** The card lasts exactly the five-second minimum, and its text covers the frame from side to side. The only empty area is the strip below y 829.

**End screen: 3:51.0–3:56.0 (5 s), if Studio accepts elements this small.**

| Element | Rectangle | Size | Start |
|---|---|---|---|
| Video: "Best for viewer" now; v021 when published | 782–1138, 850–1050 | 356×200 | 3:51 |
| Subscribe | 1500–1680, 860–1040 | 180×180 | 3:51 |

If Studio will not shrink the Video element to that height, do not let it cover the credits: the credits are the licence notices for NASA, NIST and U.S. Navy images and must stay readable. Use the Subscribe element alone and rely on the card and the description for the next film.

I looked at starting earlier, over the map (3:46–3:51). The map's upper corners are free there, but an element placed in them lands on the credits text at 3:51. No rectangle is clear in both pictures.

**Why "best for viewer" now.** The natural next film is v021 (the 1919 eclipse at Sobral): the narration says the theory "was first tested by photographing stars during an eclipse, in Brazil, in 1919" (3:26), and the publishing editor already removed a "Related:" line from the description "until it is true". None of the published films follows from GPS and relativity; picking one would be decoration. **[Platform]** The Video element has a "best for viewer" setting that lets YouTube choose. **The day v021 is published, set it to v021.** This is the strongest pair the channel will have: each film names the other's subject aloud.

**Cards**

| Time | Target | When |
|---|---|---|
| 3:27 | v021 "Einstein was proved right in Brazil", teaser "The 1919 eclipse, in Sobral" | Add on the day v021 is public. **[Platform]** a video card needs a public video |

**First lines of the description:** keep the current first paragraph. When v021 is public, add before CHAPTERS (this is the line the publishing editor removed, restored at the moment it becomes true):

> Next: Einstein was proved right in Brazil, the 1919 eclipse: [OWNER: v021's YouTube link]

**Link block:** as in v028, with the playlist line "All films on space and time: [OWNER: playlist link 'Space and time']".

**Pinned comment**

> "Eleven kilometres a day" is the size of the clock error turned into a distance. It is not what your blue dot would do: your phone compares satellites with each other, so an error they all share largely cancels, as the film says at 2:00. The correction still matters because the system is steered from clocks on the ground. Numbers and sources are in the description.

**[Judgement]** This is the claim most likely to be challenged in comments (it is the most repeated GPS myth); answering it first, in the film's own terms, is worth more than any ask.

**Playlists:** "Space and time" (later with v021, v020, v022, v023); "All films".

**Hashtags:** `#gps #relativity #einstein`

**Note on length:** the description is about 4,600 of 5,000 characters. The link block adds about 250. If it does not fit, the description's own note says the NUMBERS block is the one to cut.

---

## v025 · A brainless blob redrew Tokyo's railway

**[Film]** 233.0 s. Last line "This map is our simulation of that rule." ends at 3:36.3. The map holds to about 3:37.8. Credits card 3:38.5 to 3:53.0: fourteen and a half seconds, static. Text x 399–1521, y 213–841, nine lines under the heading CREDITS.

**End screen: 3:39.0–3:53.0 (14 s).** Plenty of time, little space: the text block is 1,122 px wide and 628 px tall, leaving a 240 px strip below and a 400 px column each side.

| Element | Rectangle | Size | Start |
|---|---|---|---|
| Video: v026 "The traffic jam with no cause" | 782–1138, 856–1056 | 356×200 | 3:39 |
| Subscribe | 1610–1830, 420–640 | 220×220 | 3:41 (two seconds later, so the eye goes to the film first) |

If the Video element cannot be that small, the alternative is the right-hand column, x 1541–1880, y 440–631 (339×191), with Subscribe moved to the left column at x 90–310, y 420–640. Both are small. **[Judgement]** this card has the time for a good end screen and not the layout; it is the best argument for the template in `growth-kit-proposal.md`.

**Why v026 (published; v019 is the second choice).** v025 ends on "So where is the planner? Nowhere. Every tube only knows how much is flowing through it" (3:14). v026 ends on "The jam with no cause had a cause after all. All of us, a little too close, a little too late": a pattern nobody planned, from one local rule per driver. That is the same idea on a road. v019 stays the second choice: a program finding a flow-control rule by trial and error, also a paper read closely.

**Cards:** none. The retina and ant-trail beat (2:35–2:50) refers to nothing we have made.

**First lines of the description:** keep. Add before "WHAT IS WHAT IN THIS FILM":

> Next: The traffic jam with no cause: [OWNER: v026's YouTube link]

**Link block:** as in v028, playlist line "One paper, read closely".

**Pinned comment**

> To be exact about the yellow map: it is our own simulation of the rule published in the paper, run on the land around Tokyo. It is not the dish from the 2010 experiment, and no run of the real mould reproduced the railway. On cost and journey length the mould matched it; on surviving a cut, the railway did better. The paper is Tero et al., Science, 2010 (link in the description).

**[Judgement]** The recommended title says "redrew"; the publishing editor already flagged that it says more than the experiment showed. A pinned comment that states the limit plainly protects the title.

**Playlists:** "One paper, read closely"; "All films".

**Hashtags:** `#slimemould #networks #biology`

---

## v029 · Armour the places with no bullet holes (published 2026-10-02)

**[Film]** 287.0 s. Last line "Armour the places with no bullet holes." ends at 4:30.5. The dotted aircraft with armour plates holds to about 4:33.2. Credits card 4:33.5 to 4:47.0; its seven lines fade in over about two seconds and drift a few pixels. Text x 326–1592, y 233–746.

**End screen: 4:34.0–4:47.0 (13 s).** The board says the owner published it on 2026-10-02, so this is now a Studio edit like the others.

| Element | Rectangle | Size | Start |
|---|---|---|---|
| Video: v028 "The test said yes" | 711–1209, 770–1050 | 498×280 | 4:36 (when all credit lines are up) |
| Subscribe | 1640–1840, 390–590 | 200×200 | 4:38 |

**Why v028.** See v028: the two films are a pair, and v028 is already public.

**Cards**

| Time | Target | Why here |
|---|---|---|
| 3:55 | v028, teaser "Another way a count misleads: the test that said yes" | "In each case, the sample was filtered before anyone looked at it" ends the list of other examples; same position as the card in v028 |

**First lines of the description:** keep the current three paragraphs. Add before "WHAT IS REAL, WHAT IS A LEGEND, WHAT IS OUR DRAWING":

> Next: The test said yes. It was probably wrong: [OWNER: v028's YouTube link]

**Link block:** as in v028, playlist line "Numbers that fool us".

**Pinned comment**

> The famous exchange between Wald and the officers is a legend: no source records it, and the film says "the story goes". What is documented is eight technical memoranda from 1943 with a method and no picture. The dotted aeroplane you may know was drawn in this century, and its dots are invented. So are ours. Sources in the description.

**Playlists:** "Numbers that fool us"; "All films".

**Hashtags:** `#survivorshipbias #statistics #history`

---

## S10 · Why 0.1 + 0.2 is not 0.3 (Short, published 2026-10-02)

**[Film]** 35.5 s, vertical. Last line "Close. Not equal." ends at 34.9 s; the final picture is the two numbers with the "not equal" sign and a cursor.

- **End screen and cards:** none. I found no YouTube page that says they exist for Shorts or that they do not; if Studio offers an end-screen editor on this Short (it is over 25 s), tell the coordinator, because that changes the plan for every Short.
- **Related video: v016 "A film from a text file" (published 2026-10-02).** **[Judgement]** The Short is about a computer keeping the nearest number that fits and so being a hair off; v016 says "the same frame, on any machine" is exact for the evaluated frame description and that rendered pixels are compared within a stated tolerance (its description; on screen at 0:41 and 3:59). Both are about what a machine does exactly and what it does only to a tolerance. A real link, not a close one. Related video on a Short is the place where analytics say the viewers with the most minutes arrive (`ANALYTICS-2026-10-02.md`, "related video" has twice the minutes of the Shorts feed).
- **Description:** the first sentence is already the hook and is right. The links in a Short's description are not clickable; the handle `@PALSsNotes` is a mention and is clickable. Keep the handle line as it is.
- **Hashtags:** five are listed and three show. Suggested three: `#programming #floatingpoint #math`.
- **Pinned comment** (on a Short a link would not be clickable, so none is given):

> Try it: type 0.1 + 0.2 in a Python prompt or a browser console. Then try 0.5 + 0.25. That one is exact, because a half and a quarter are sums of powers of two. A tenth is not.

  **[Judgement]** It gives the viewer a second experiment that tests the film's explanation. I checked the claim: 0.5 and 0.25 are exactly representable in binary64 and their sum is 0.75 exactly.
- **Playlists:** "Shorts: one idea each"; "Numbers that fool us" is a fair second home; "How these films are made" is not, the Short is not about the engine.

---

## S18 · Twenty-three people, one shared birthday (Short, published 2026-10-02)

**[Film]** 42.0 s, vertical. The Short ends on a question handed to the viewer: "How many pairs are in the room you are in?" (38.1–41.2 s), with "? PAIRS" on screen.

- **End screen and cards:** none (as S10).
- **Related video: v028 now; v027 when published.** The Short's turn is "you picture your own birthday against the other twenty-two... But nobody asked about yours" (0:06–0:15): intuition answers a different question. v028 says of the doctors, "They answered a different question" (2:05). That is a real link, in both films' words. The backlog paired S18 with v027 (the Galton board); v027 is public too (2026-10-02), so the owner chooses between a film on the same trap (v028) and a film on chance in bulk (v027). **[Judgement]** I would keep v028 for S18 and give v027 to the next mathematics Short, unless analytics say otherwise.
- **The closing question is a comment prompt the film already makes.** Nothing needs adding to the film. The description already gives the formula. Pinned comment:

> The count is n × (n − 1) ÷ 2. Four people at a table: 6 pairs. A class of 30: 435. Tell us your room.

  **[Platform]** asking for a comment is allowed ("You're allowed to encourage viewers to subscribe, hit the like button, share, or leave a comment"). Nothing is offered in return. I checked the two figures: 4×3÷2 = 6, 30×29÷2 = 435.
- **Hashtags:** the description lists `#maths #probability #birthdayproblem #statistics #shorts`. Suggested three: `#maths #probability #birthdayproblem`. `#shorts` is not something the hashtag page asks for.
- **Playlists:** "Shorts: one idea each"; "Numbers that fool us".

---

## v016 · A film from a text file (published 2026-10-02)

**[Film]** 286.0 s. Last line "A film you can diff." ends 4:33.4 (captions). **There is no credits card:** the closing picture (the "ONE FRAME" plate, the sun's colour changing in a one-line diff, the line "RENDERED BY ITSELF, FROM THE DOCUMENT ON THE WALL" in a bar) holds from 4:33.5 to the end at 4:46.0 (12.5 s). Last frame, 1920×1080 measured on a 960-px frame: the plate sits at x 560–1480, y 200–870; the caption bar at x 160–1760, y 905–975; the particle cloud and cube at x 1640–1890, y 230–590; the rest is dark empty stage.

**End screen: 4:35.0–4:46.0 (11 s).** The film's last line and the "change one line" beat finish first; elements start after the plate has settled.

| Element | Rectangle | Size | Start |
|---|---|---|---|
| Video: "Best for viewer" | 40–520, 300–570 | 480×270 | 4:35 |
| Subscribe | 1600–1800, 620–820 | 200×200 | 4:37 |

**Weak point, stated:** both elements sit on the dark edge of the film's closing image, not on a card, and the camera drifts a little in those seconds, so the plate's edges may reach 520 px on the left in some frames. If the Video element touches the plate in Studio's preview, drop it and keep Subscribe only. **[Judgement]**

**Why "Best for viewer".** The film is about how the channel's films are made; no other film follows from that more than the rest. Picking one would be decoration. When a film that uses the same engine on a real result is the right next step (a film from the next batch), change it.

**Cards:** none. The narration names the engine and the format, nothing another film of ours explains.

**First lines of the description:** keep the two opening paragraphs as they are. Above the last line `PALS's Notes: @PALSsNotes`, add:

> MORE FROM PALS'S NOTES
> Subscribe: https://www.youtube.com/@PALSsNotes
> All films: [OWNER: playlist link 'All films']

**Pinned comment**

> To be exact about "the same frame, on any machine": it holds for the evaluated frame description, which is bit-identical. The pixels that come out are compared against reference images within a stated tolerance, as the film says on screen at 0:41 and 3:59. The engine and its format are linked in the description.

**[Judgement]** The film's boldest claim, with its own limit, in the film's own words, first.

**Playlists:** "All films"; "How these films are made" holds only v016 and does not appear on the page until it has two public films (`CHANNEL-PAGE.md`, section 5).

**Hashtags:** the description lists `#renderengine #rust #opens`; I do not know what `#opens` stands for, so the publishing editor should confirm it.

---

## v022 · The Moon is leaving (published 2026-10-02)

**[Film]** 235.0 s. Last line "The Moon is leaving." ends 3:42.5; the eclipse picture holds to about 3:45; the title-and-credits card is fully in at about 3:47 and stays to the end at 3:55. On the last frame the text sits at x 250–1670, y 190–800 (title above, four credit lines below, all centred). The strip below y 830 is empty; the sides are 250 px wide.

**End screen: 3:47.0–3:55.0 (8 s).**

| Element | Rectangle | Size | Start |
|---|---|---|---|
| Video: "Best for viewer" now; v020 when published | 760–1160, 836–1061 | 400×225 | 3:47 |
| Subscribe | 1560–1740, 850–1030 | 180×180 | 3:47 |

Same caveat as v024: **I could not verify the smallest size Studio accepts for a Video element.** If it will not go down to 225 px tall, use Subscribe only. The credits are the licence notices for NASA, Wikimedia and Poly Haven material and must stay readable.

**Why not v018 as the Video element.** v018 is a Short about the same Moon; whether an end-screen Video element can point to a Short is **[Platform: not verified]**. If Studio offers it, v018 is a fair choice; otherwise "Best for viewer". The planned partner is v020 "Venus ate its moon" (tides took Venus's moon; tides are moving ours). **The day v020 is published, set the element to v020.** The film's closing thought ("We happen to be here while it holds") invites that pairing; v020's own card says "It may have. The study is a simulation, not a discovery," and the pinned comment below keeps v022's "may" intact.

**Cards:** none. The narration names no other film of ours.

**First lines of the description:** keep the first paragraph. Add before CHAPTERS:

> Next: [OWNER: title and link of v020, the day it is published. Until then, delete this line.]

**Link block** (as in v028): subscribe line; playlist line "All films on space and time: [OWNER: playlist link 'Space and time']". The description's last paragraph has `[OWNER: …]` brackets still open (the film's own file says so); fill or delete them first.

**Pinned comment**

> Two numbers worth keeping apart. 3.8 centimetres a year is measured, by timing laser light to the mirrors left on the Moon. "Something like 600 million years" until the last total eclipse is an extrapolation at today's rate, and estimates vary. Sources are in the description.

**[Judgement]** It is straight from the film's own "measured and extrapolated" block; no new claim.

**Playlists:** "Space and time" (with v024, v018, S07); "All films".

**Hashtags:** three: `#moon #eclipse #space` (the owner chooses; I did not read the end of the film's description, where the hashtags would be).

---

## v026 · The traffic jam with no cause (published 2026-10-02)

**[Film]** 249.0 s. Last line "All of us, a little too close, a little too late." ends 3:56.6. The real motorway clip with its three labels ("ALL OF US", "A LITTLE TOO CLOSE", "A LITTLE TOO LATE") holds to about 3:58; the credits card is in at about 3:59 and stays to 4:09.0, six centred lines x 316–1602, y 361–714, orange notch at the bottom-left corner. Everything outside the text is plain ink: this is the roomiest of the new endings.

**End screen: 3:59.0–4:09.0 (10 s).**

| Element | Rectangle | Size | Start |
|---|---|---|---|
| Video: v025 "A brainless blob redrew Tokyo's railway" | 684–1235, 730–1040 | 551×310 | 3:59 |
| Subscribe | 1640–1840, 400–600 | 200×200 | 4:01 |

**Why v025.** v026 ends on a pattern nobody intended, made by every driver following one local habit. v025 asks "where is the planner?" and answers "nowhere: every tube only knows how much is flowing through it". Both are one local rule making a pattern nobody planned. [Judgement] The film already ends on its own ask ("You can do the same... do not close the gap", 3:31); that is worth more than anything of ours, and the end screen sits after it.

**Cards:** none.

**First lines of the description:** keep both opening paragraphs. Add before CHAPTERS:

> Next: A brainless blob redrew Tokyo's railway: [OWNER: v025's YouTube link]

**Link block:** as in v028, playlist line "Films that read one paper closely: [OWNER: playlist link 'One paper, read closely']".

**Pinned comment**

> Every ring, row and road with cars on it in this film is our own simulation, labelled on screen, not footage of either experiment. The two real ones: 22 cars on a 230 m ring in Japan in 2008, and 21 to 22 vehicles on a 260 m ring in the United States in 2018, where one car's speed was controlled automatically. "Up to 40% less fuel" is the authors' figure from the preprint. Sources are in the description.

**[Judgement]** The description says exactly this about what is simulated; the comment puts it where viewers read first.

**Playlists:** "One paper, read closely" (with v019 and v025); "All films". **Hashtags:** the description lists `#TrafficJam #Physics #Simulation`.

---

## v027 · Randomness draws the same curve every time (published 2026-10-02)

**[Film]** 217.0 s. Last line "You only have to know whether the world is adding, or multiplying." ends 3:25.0. The Galton board with its curve stays on the right (x 1150–1830, y 10–1070); the credits sit on the **left** of it, six lines, x 170–980, y 310–780, with the heading CREDITS. The card is fully in from about 3:31.5 to the end at 3:37.0 (5.5 s). That is barely over the 5-second minimum.

**End screen: 3:31.5–3:37.0 (5.5 s), if Studio accepts a start that late.** The free areas are the left strip below the credits and the area above them.

| Element | Rectangle | Size | Start |
|---|---|---|---|
| Video: v028 "The test said yes. It was probably wrong." | 420–900, 790–1060 | 480×270 | 3:31.5 |
| Subscribe | 300–500, 70–270 | 200×200 | 3:31.5 |

**Honest reading:** this is the shortest usable ending of the batch; a viewer has about four seconds after the elements appear. **Why v028.** v027's claim is "One ball is unpredictable. Three thousand are a certainty"; v028 is the same move applied to a decision: stop asking about one patient and count a thousand people. Published.

**Cards:** none.

**First lines of the description:** keep. Add before the chapter list:

> Next: The test said yes. It was probably wrong: [OWNER: v028's YouTube link]

**Link block:** as in v028, playlist line "Numbers that fool us".

**Pinned comment**

> The numbers on screen, so you can check them: twelve rows of pegs give 4,096 possible routes and 924 of them lead to the middle bin. The count predicts 677 balls of 3,000 there; the first run landed 696 and the second 659. The second board, where bounces multiply, is a numerical simulation, labelled as one. Sources are in the description.

**Playlists:** "Numbers that fool us"; "All films". **Hashtags:** the description lists `#BellCurve #Probability #Statistics`.

---

## v018 · The Moon rings like a bell (Short, 64 s, published 2026-10-02)

- **End screen and cards:** none to set; no credits card, the film ends on its title line.
- **Related video: v022 "The Moon is leaving".** Both are the Moon; both use real NASA material; v022 does not mention the ringing, so the link is by subject and the Short makes no promise about it.
- **Pinned comment (no link):**

> The record on screen is the real one: Apollo 12's lunar module was crashed on purpose on 20 November 1969 and the seismometer left on the Moon recorded the ground shaking for about 55 minutes. "Ringing" is a comparison: this is vibration in rock, not sound. The explanation by scattering in dry, broken rock is the later reading of that result.

  This replaces the earlier proposal, whose last sentence about water went a step beyond what the film says. Every claim above is in the film's own description.
- **Hashtags:** three: `#moon #apollo12 #nasa`. **Playlists:** "Space and time"; "Shorts: one idea each".

---

## S07 · The year that lasted 445 days (Short, 58 s, published 2026-10-02)

- **Related video: v022 "The Moon is leaving".** v022 says fossil corals from 400 million years ago show about 400 day-lines in a year; S07 is a year of 445 days by decree. A year once really had about 400 days; the Roman one had 445 because of a decree. The Short makes no promise; the link is an offer. **[Judgement]** a thematic link, loose.
- **Closing line:** keep, add nothing.
- **Pinned comment:** 

> Where the 445 comes from: Censorinus, in the third century, gives 355 days plus the regular extra month of 23 plus 67 days added by Caesar. Macrobius gives 443 days for that same year; the film uses Censorinus's figure because its breakdown adds up.

- **Hashtags:** three: `#history #calendar #leapday`. **Playlists:** "Shorts: one idea each"; "Space and time" is not a natural home (calendars are history): leave it out.

---

## S16 · Four colours are always enough (Short, published 2026-10-02)

- **Related video: none.** The Short's own notes say no long film of ours is related. The nearest are v027 (a mathematical fact made visible by counting) and v016 (a computer checking every case before anything is drawn); neither is about proof, so I leave the field empty. **[Judgement]** A related video the Short gives no reason for is noise. If the owner wants one anyway, v027.
- **Pinned comment:**

> The map on screen is an example, not the proof: the proof goes much further. Neighbours here share a border; touching at a single point does not count. The large map was generated for this film and coloured with four colours by a search that checks every border. Source: Robertson, Sanders, Seymour and Thomas, "The Four Color Theorem" (Georgia Tech summary page).

- **Hashtags:** three: `#math #fourcolortheorem #graphtheory`. **Playlists:** "Shorts: one idea each".

---

## What the owner does, in order

The ordered list with the exact texts is in `OWNER-STUDIO-CHECKLIST.md`. The order, in short:

1. Playlists (they feed the link blocks and the Home page). 2. One end screen per long film. 3. The one card (v028). 4. Description edits: "Next:" and link block. 5. One pinned comment per film. 6. Related video on each Short. 7. Targets marked "when published" are changed the day v020, v021 or v023 goes out.

Steps 2 to 6 take no new file, no encode and no review of a cut. Texts that go into a description should pass through the publishing editor, who owns `publish/description.md` and its checklist.

## What to look at afterwards

**[Platform]** Studio reports "End screen element click rate" per video and "Top end screen element types" for the channel. With the first two weeks of numbers: clicks per end-screen impression for each of the five films (v024's small elements against v028's large ones is a natural comparison), card clicks on v028 and v029, and subscribers gained per film against views. These are small films on a new channel: the counts will be low, and a difference between two films will not mean much until there are a few hundred end-screen impressions on each.

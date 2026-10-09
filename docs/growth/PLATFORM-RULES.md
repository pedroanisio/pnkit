# What YouTube allows today

Written by the growth role on 2026-10-02. Every YouTube Help page below was opened on 2026-10-02 (English version, `?hl=en`), downloaded and read as text. Quotes are copied from that text. Rules change: read the page again before relying on a line older than a few months.

Three kinds of statement are kept apart:

- **[Platform]** what a YouTube Help or policy page says, with the page.
- **[Practice]** what creators commonly do. Experience, not evidence.
- **[Judgement]** my reading of what it means for this channel.

## 0. The finding that matters most: "advanced features"

**[Platform]** Several things this plan depends on are not available to a new channel by default. The page "Learn about feature access for YouTube Creators" (https://support.google.com/youtube/answer/9890437?hl=en) lists under **Advanced** features:

- "Add clickable links to your long-form video description and posts"
- "Add a Related Video to your YouTube Short"
- "Pin comments on videos and posts"
- "Add chapters"
- "Multi-language features"
- "A/B testing"

How to get them: "If you're an active YouTube creator who's already established sufficient channel history, you'll likely automatically qualify for advanced features" and "If you want to unlock advanced features right away, you can verify your identity using a valid ID or video." Where to look: YouTube Studio, Settings, Channel, Feature eligibility; "You'll see 'Enabled' next to the features you have access to."

**[Judgement]** The channel is new. If advanced features are not enabled, the links in the four published descriptions are plain text, the chapter lists may not become chapters, no comment can be pinned and no Short can carry a related video. I cannot see the channel's Studio, so I do not know its state: this is the first question for the owner. End screens and cards are not on that list.

## 1. End screens

Page: "Add end screens to videos", https://support.google.com/youtube/answer/6388789?hl=en

**[Platform]**

- Where in the video: "End screens can be added to the last 5–20 seconds of a video."
- Minimum video length: "Your video has to be at least 25 seconds long to have an end screen."
- How many elements: "You can add up to four elements to your end screen for videos with standard 16:9 aspect ratio. Other aspect ratios may have a lower limit."
- Element types: Video ("Feature your most recent upload, best for viewer, or a specific video"), Playlist ("Display a public YouTube playlist"), Subscribe, Channel ("Promote another channel with a custom message"), Link ("If you're in the YouTube Partner Program, you can link to an external website").
- A video or playlist element can be "any video or playlist (public or unlisted) from your or any other channel".
- Timing per element: "End screen elements will show at the same time by default. You can customize individual elements to show at different times."
- Placement: drag in the player; a grid with "Snap to grid" and "Snap to element".
- What is switched off during it: "Other interactive elements, like card teasers and video watermarks, are suppressed during the end screen."
- Where viewers do not see it: "On mobile web (exception: iPad mobile web). In the YouTube Music or YouTube Kids apps. In Flash videos. In 360 videos." Also: "Viewers have the ability to hide end screens while watching your videos."
- Made for kids: "End screens aren't available for videos set as made for kids."
- No guarantee: "Your end screen may not always show, or may show differently than designed."
- YouTube's own advice on the page: "Feature elements that are relevant to the video", "Encourage viewers to click using calls to action for different end screen elements", "Make sure you leave enough space and time at the end of the video for an end screen. Make sure you consider the video's last 20 seconds when editing it", "Consider timing different end screen elements to show at different times."
- Measurement: YouTube Analytics, Engagement tab, "End screen element click rate"; channel level "Top end screen element types" and "Top videos by end screen".

**Not verified**

- **End screens on Shorts.** The page does not mention Shorts. Third-party guides say end screens and cards do not exist on Shorts; I found no YouTube page that says so. Treat "no end screen on a Short" as creator knowledge, and check it in Studio on S10 (35 s, over the 25 s minimum).
- **Element sizes.** The page gives no minimum or maximum size in pixels, and no rule that a Video element is required. The positions in `RETROFIT-published.md` are targets; Studio's editor decides what it accepts. A commonly repeated claim that "at least one element must be a video or playlist" is [Practice]; I did not find it on the page.

**[Judgement]** A five-second end screen is allowed but gives a viewer about three seconds to act after noticing it. Our credits cards run 5 to 14.5 seconds. The lower end is the reason to build a proper end-screen section in new films.

## 2. Cards

Page: "Add info cards to videos", https://support.google.com/youtube/answer/6140493?hl=en

**[Platform]**

- "Info cards can feature a video, playlist, channel, or link." Link cards need the YouTube Partner Program.
- "You can add up to 5 cards to one video."
- A video card links "to a public YouTube video"; a playlist card "to a public YouTube playlist". (So a card cannot point to an unpublished or unlisted film. An end-screen element can point to an unlisted one.)
- Timing: "Change the start time for the card below the video." "When a viewer is watching your video, they'll see a teaser for the time that you designate." Optional message and teaser text.
- "Cards aren't available on videos set as made for kids."
- "Your cards won't show if your video has been claimed by Content ID and the content owner has set up a campaign."
- Under "Who can see cards?" the computer version of the page says "This feature is available to viewers on computers", and elsewhere "On mobile, viewers can see the card icon whenever the player controls are showing." The two sentences do not agree; I could not settle which describes today's apps.
- Policy tie: the Fake engagement policy lists as not allowed "A video that tries to force or trick viewers into watching another video through deceptive means (for example: a misleadingly labeled info card)."

**Not verified:** cards on Shorts (same as end screens: not stated).

## 3. Links: where they are clickable

Page: "Sharing links with your audiences", https://support.google.com/youtube/answer/13748639?hl=en (a table; I read which column each tick is in from the page's HTML).

**[Platform]**

| Link type | Clickable |
|---|---|
| Channel profile links | yes |
| URLs in long-form video comments and descriptions | yes, with a footnote: "To add clickable external links, you must enable your channel's access to advanced features." |
| URLs in Shorts comments and Shorts descriptions | **no** |
| "Related Videos in Shorts link" | yes |
| Mentions and hashtags in Shorts comments and descriptions | yes |
| Posts | no (same footnote) |
| End screens | yes |

- "To reduce spam and scam attempts, URLs placed in YouTube Shorts comments and Shorts descriptions are non-clickable." The page gives no date; the role file's "since August 2023" is not confirmed by this page.
- Profile links: "Use channel profile links to showcase up to 14 links on your channel page." And from "Manage your YouTube channel's profile" (https://support.google.com/youtube/answer/2657964?hl=en): "Your first link will be prominently displayed in the profile section near the subscribe button, and your remaining links will show when your audience clicks to see more links."
- External links must follow the External links policy (https://support.google.com/youtube/answer/9054257?hl=en).

**[Judgement]** The footnote speaks of "external" links. Whether a link to another YouTube video in a description is clickable without advanced features is not stated; test with one description. The publishing editor's open point (does `@PALSsNotes` become a link in a Short's description) is answered by the table: mentions in Shorts descriptions are clickable.

**Not verified:** "the first two or three lines show before 'more'". It is what the watch page does today by observation ([Practice]); I found no Help page that states a number of lines or characters.

## 4. The related video on a Short

Page: "Add a related video to your YouTube Shorts", https://support.google.com/youtube/answer/14075157?hl=en

**[Platform]**

- "You can add a related video after you upload your Short to help direct viewers to your other YouTube content. A related video allows you to showcase your Videos, Shorts, and Live in the Shorts player."
- Steps: Studio, Content, click the Short, "Select a Related Video from your channel", Save.
- "Adding a related video is only available with advanced feature access."
- "The video you select has to be public or unlisted and must follow our Community Guidelines."
- "Viewers will see a clickable link below your channel handle."

**[Judgement]** One related video per Short (the page speaks of "a related video" in the singular throughout; no limit is stated). It can be set and changed after upload, so a Short published before its long film gets the link later, with no new file.

## 5. Pinned comment

Pages: "Review & reply to comments", https://support.google.com/youtube/answer/9482367?hl=en; feature access page above.

**[Platform]**

- "Pin: Tap a comment then tap More, Pin to highlight a comment at the top of your video's watch page."
- "If you pinned a comment to the top of the watch page, but don't want it there anymore, you can unpin it." "You can also pin a different comment, which will unpin the previous one." So: one pinned comment per video.
- Pinning is an advanced feature ("Pin comments on videos and posts").
- A link in a comment on a long video is clickable (section 3); in a comment on a Short it is not.
- Comments are off on anything set as made for kids (section 10).

A search result quoted a sentence I did not find on the pages I opened ("On mobile, viewers must expand the comment section to view the pinned comment"). Not verified.

## 6. Playlists and series playlists

Pages: "Create & manage playlists", https://support.google.com/youtube/answer/57792?hl=en; "Series playlists", https://support.google.com/youtube/answer/6084043?hl=en

**[Platform]**

- A playlist can hold videos and Shorts; a playlist view can be filtered to "Shorts" or "Videos".
- "There's a limit to how many public playlists a channel can create each day... You can increase your daily limit by gaining access to advanced features." The number is not given.
- Series playlist: "A series playlist allows you to mark your playlist as an official set of videos that should be viewed together. Adding videos to a series playlist allows other videos in the playlist to be featured and recommended when someone is viewing a video in the series. YouTube may use this info to modify how the videos are presented or discovered."
- "You must have a verified account to use series playlists." "A video cannot appear in more than one series playlist." "Only videos uploaded by you and that you have the rights to can be added to a series playlist."
- Turned on in playlist settings on a computer: "Set as official series for this playlist".
- A playlist can be an end-screen element and a card target (public playlists).

**[Judgement]** Because a film can sit in only one series playlist, the subject playlists in `CHANNEL-PAGE.md` are ordinary playlists, and the series flag is kept for a set that truly must be watched in order. We have none yet.

## 7. Subscribe button, the bell, and the watermark

Pages: "Subscribe to YouTube channels", https://support.google.com/youtube/answer/4489286?hl=en; "Manage your channel branding", https://support.google.com/youtube/answer/10456525?hl=en

**[Platform]**

- "You can find a Subscribe button under any YouTube video or on a channel's page."
- Notifications: "When you subscribe to a channel, we'll automatically send you notifications about the highlights from that channel. You can opt to get a notification every time the channel publishes content by changing your notification settings." "To get all notifications from a subscribed channel, tap the Notification bell."
- Watermark: "You can add a video watermark to your video to promote your channel's branding." Display time, one setting for the channel: "End of video: The video watermark will show for the last 15 seconds of the video", "Custom start time", or "Entire video".
- Watermark image: "Minimum 150x150 pixels", "Square image less than 1 MB in size".
- "The channel watermark is available in landscape view on computers and mobile devices (not clickable on mobile). Channel watermarks do not show on custom YouTube chromeless players or Adobe Flash."
- Not on made-for-kids videos. Suppressed during the end screen (section 1).
- The only clickable subscribe controls inside the player are the end-screen Subscribe element and the watermark. Nothing else can be placed mid-video except cards.

**[Judgement]** The watermark is set once for the whole channel and applies to every long film, including the four already published, with no new file. It sits in the lower right corner of the player, where our films sometimes have labels. With "entire video" it would sit over our pictures; with "end of video" it shows for the last 15 seconds and disappears when the end screen starts. Given the channel's rule that nothing on screen is unexplained, I would choose "end of video", and check three films' lower right corners first.

## 8. Chapters

Page: "Video Chapters", https://support.google.com/youtube/answer/9884579?hl=en

**[Platform]**

- "Make sure that the first timestamp you list starts with 00:00." "Your video should have at least three timestamps listed in ascending order." "The minimum length for video chapters is 10 seconds."
- "Note: If you don't yet have access to chapters, apply for access to Advanced features."
- "If the channel has any active strikes, or if the content may be inappropriate to some viewers, the video chapters feature won't be available."

**[Judgement]** Our descriptions write the first chapter as `0:00`, not `00:00`. `0:00` is the form in general use and works on other channels ([Practice]); the page's own wording is "00:00". If chapters do not appear on a published film, check advanced features first, then try `00:00`.

## 9. Hashtags

Page: "Find playlists & videos using hashtags", https://support.google.com/youtube/answer/6390658?hl=en

**[Platform]**

- "You can add hashtags to a title and description when you upload a video or record a Short."
- "Out of all the hashtags you add to the video's description, up to three hashtags that are considered most engaging will appear by your video title."
- "If a video or playlist has more than 60 hashtags, we'll ignore each hashtag on that content."
- "Don't add hashtags that are not directly related to the video or playlist. Misleading or unrelated hashtags may result in the removal of your video or playlist."
- "While adding hashtags is allowed, adding ordinary descriptive tags or repetitive sentences in the description is (still) prohibited."

**[Judgement]** Three hashtags per film, each a subject the film really covers. The S18 description ends with `#shorts`; the page says nothing about that tag being needed, and YouTube classifies Shorts by format. I would replace it with a subject tag. The five long-film descriptions carry no hashtags today.

## 10. "Made for kids"

Pages: "Set your channel or video's audience", https://support.google.com/youtube/answer/9527654?hl=en; "Determining if your content is 'made for kids'", https://support.google.com/youtube/answer/9528076?hl=en

**[Platform]** On a video set as made for kids the following "won't be available" (the list on the page includes): "Cards or end screens", "Video watermarks", "Comments", "Notification bell", "Save to playlist and Save to watch later", personalised advertising, playback in the Miniplayer, autoplay on home. From the subscribe page: "You won't get notifications if a channel's audience is set as made for kids."

- "General audience content is content that could appeal to everyone, but isn't intended specifically for children, or content that is intended for a teen or older audience. General audience content should be set as 'not made for kids.'"
- The creator is responsible for the setting; YouTube's systems may also set it.

**[Judgement]** Our films are general-audience science explainers and belong under "not made for kids". Everything in this plan (end screens, cards, pinned comments, the bell, playlists) disappears from a video set the other way, so the setting is worth checking once on each published film. Animated explainers are sometimes mislabelled; the owner chooses the setting, not me.

## 11. Policy lines on asking

Pages: "Fake engagement policy", https://support.google.com/youtube/answer/3399767?hl=en; "Spam Policy", https://support.google.com/youtube/answer/2801973?hl=en

**[Platform]**

- Asking is allowed. Fake engagement policy: "Note: You're allowed to encourage viewers to subscribe, hit the like button, share, or leave a comment". Spam policy: "It's okay to ask viewers to like, comment, or subscribe."
- Not allowed: "content that solely exists to incentivize viewers for engagement (views, likes, comments, etc)"; "coercion, or offering rewards in exchange for likes, views, or subscribers"; "Offering to subscribe to another creator's channel only if they subscribe to your channel ('sub4sub')".
- Misleading metadata, now under "Malicious clickbait": "Using maliciously misleading titles, thumbnails, descriptions, or imagery to trick users into clicking on a video that does not deliver what was promised."
- "Off-platform diversion: Content created solely to drive users off of YouTube to external sites".
- "Comment spam: Using high-volume, repetitive, or deceptive comments... Example: Posting identical or similar 'check out my channel' messages across hundreds of videos."
- One line that touches how this channel is made: "Automated or synthetic mass-production: Using automated tools or AI to churn out high volumes of similar content with minimal changes... Example: Channels that use the exact same background music and repetitive AI generated imagery across many videos, with each video reading out an AI-generated script."

**[Judgement]**

- Nothing in this plan offers anything in exchange for a subscription, a like or a comment. No giveaway, no "subscribe to unlock".
- The pinned comment is written per film. The same link block on every film is normal practice; the same comment text on every film is the thing the comment-spam line describes, so each pinned comment says something about its own film.
- The mass-production line is not about us as I read it: each film has its own research, score and pictures, and the descriptions say the voice is synthetic. It is still a reason to keep the standing rule that each film has its own sound design, and not to publish the eighteen-Short pack in one day. This is my reading, not a ruling from YouTube.

## 12. The channel page

Pages: "Customize your YouTube channel layout", https://support.google.com/youtube/answer/3219384?hl=en; branding and profile pages above.

**[Platform]**

- Channel trailer: "Your channel trailer offers a preview of your channel so viewers can learn more and subscribe. By default, ads won't show on your channel trailer". "Once a viewer watches your channel trailer, it won't be shown to them again." Shown to people who have not subscribed.
- Featured video for returning subscribers ("Spotlight"): "You can highlight your video or any video on YouTube for returning subscribers".
- Sections: "up to 12 custom sections. Your layout will default to display 4 pre-populated sections: Short videos, Uploads, Created playlists, and Subscriptions you've made public."
- Banner: "Minimum dimension for upload: 2048 x 1152 px with an aspect ratio of 16:9." "At the minimum dimension, the safe area for text and logos: 1235 x 338 px." "Recommended dimension (especially for TV): 2560 x 1440 px." "File size: 6 MB or smaller."
- Profile picture: "Image that renders at 98 X 98 px"; not over 15 MB.
- Channel name and description can be translated: Customization, Profile, "ADD LANGUAGE".
- Handle and name can each be changed "twice within a 14-day period".

## 13. Two languages on one video

Pages: "Add Multi-language features to your videos", https://support.google.com/youtube/answer/13338784?hl=en; "Translate your own video titles & descriptions", https://support.google.com/youtube/answer/6289575?hl=en; "Use automatic dubbing", https://support.google.com/youtube/answer/15569972?hl=en

**[Platform]**

- "The Multi-language audio feature allows you to upload audio tracks in different languages to a single video or Short. For long-form videos, you can also upload thumbnails in different languages. This is a powerful way to expand your global reach without creating and managing multiple separate channels."
- "The audio tracks will automatically default to the viewer's preferred language, which is determined by their watch history."
- "Once your videos are translated, your videos can be found when viewers search using a translated video title and description."
- "Multi-language audio is currently available to creators with access to Advanced features."
- The dub file "must be in a supported audio-only file format and roughly the same length as your video."
- Automatic dubbing: "When you upload a new video, dubs will be automatically generated." "This feature is enabled by default for eligible creators." "You cannot edit automatic dubs."

**[Judgement]** Automatic dubbing may already be putting a machine Portuguese track on our films without anyone having checked it. For a channel whose rule is that every spoken number has one source, the owner should look at whether it is on (the page places the switch in Studio's "Advanced settings"; I did not see the screen) and decide. The trade-offs between one channel and two are in `CHANNEL-PAGE.md`.

## 14. Published research on asking

- **[Research]** J. E. Anderson, C. A. Nguyen and S. Anderson, "Like, comment, and subscribe: investigating the effectiveness of digital engagement prompts", Journal of Research in Interactive Marketing 20(1), 49–67 (2026), https://doi.org/10.1108/JRIM-12-2024-0573. Read in the abstract only, on 2026-10-02. 8,500 English-language YouTube videos; spoken prompts found in transcripts; engagement from YouTube's API. As the abstract reports it: spoken "like" prompts go with more likes, most when placed mid-video; spoken "comment" and "subscribe" prompts show no significant effect on comments or subscriptions. Limits stated by the authors: verbal prompts only, English-language Western channels, no measure of content quality. It is an observational study, so it shows association, not cause.
- **[Platform]** YouTube's own advice (section 1) is to "encourage viewers to click using calls to action" for end-screen elements and to use relevant elements. No figure is given.
- **[Judgement]** The one study I found is consistent with the role file's position: a bare spoken "subscribe" is weak, and the next film is the stronger ask. It does not test a subscribe request that states what the viewer gets, and it does not test end screens. The figures that circulate on marketing blogs (click rates, "ask at 80%") have no stated source and are not used anywhere in this plan. Our own analytics will be the first real evidence; `QUESTIONS-for-the-owner.md` asks for them.

## 15. Long videos of 45 to 60 minutes (added 2026-10-02, for the Ultra Explainers)

Read on 2026-10-02; details and sources in `ULTRA-EXPLAINERS.md`. **[Platform]** Maximum upload 256 GB or 12 hours, whichever is less; over 15 minutes needs a verified account (Help 71673). Chapters: at least three timestamps in ascending order, the first at 00:00, each chapter at least 10 seconds (Help 9884579). Mid-roll ads on monetized videos of 8 minutes or more, placed by the creator or automatically, best at natural pauses (Help 6175006, read through a search summary). Premiere: countdown and live chat, schedule at least 24 hours ahead (Help 9080341, search summary). End screen: last 5 to 20 seconds, same rule at any length. **Not verified:** the maximum number of cards per video and whether a card can point to a Short.

## What I could not verify, in one list

1. Whether the channel has advanced features (owner: Studio, Settings, Channel, Feature eligibility).
2. That end screens and cards are unavailable on Shorts (no YouTube page says so; test on S10).
3. Minimum and maximum sizes of end-screen elements in pixels.
4. How many description lines show before "more".
5. Whether cards are visible in the mobile apps today (the page contradicts itself).
6. Whether a link to another YouTube video in a description needs advanced features (the footnote says "external").
7. The date links in Shorts became non-clickable.
8. Whether automatic dubbing is on for this channel.
9. The Anderson et al. paper beyond its abstract.

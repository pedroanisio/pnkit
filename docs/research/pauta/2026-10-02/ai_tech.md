# Pauta: AI and Computing + Technology and Investment
Scout run 2026-10-02. Window looked at: 2026-08-03 to 2026-10-02 (past), 2026-10-03 to 2026-12-31 (ahead).
Read levels: "read in full" = whole text read; "read in part" = downloaded text and read the relevant sections (stated); "abstract only"; "lead only" = a search snippet or a news page, not the primary source.
Nothing here comes from memory. Numbers are as the sources print them. Some key papers date from before 3 Aug (marked "outside window, newly relevant").

---

## 1. Breaking a bitcoin lock: the qubit number is not the number
**It seems** "a quantum computer needs X million qubits to break encryption" is one fixed number. **But really** the cost is a trade of qubits against days against error rate, and the same lock was re-estimated from ~20 million qubits (2019) to under 500,000 (superconducting, minutes) or about 19,000 (trapped ions, 26 days) depending on the machine. One paper proved its circuit works with a zero-knowledge proof without publishing the circuit.
- Facts:
  - Babbush, Zalcman, Gidney et al. (Google Quantum AI), arXiv 2603.28846, 30 Mar 2026: 256-bit elliptic-curve discrete log with fewer than 1200 logical qubits and under 90 million Toffoli gates (or <1450 / <70 million); "in minutes using fewer than half a million physical qubits" on superconducting hardware at 1e-3 error; results validated by a zero-knowledge proof "in the interest of responsible disclosure". https://arxiv.org/abs/2603.28846 | read: abstract only (outside window, newly relevant).
  - Häner, Naehrig et al., arXiv 2609.05625, 4 Sep 2026: same curve (secp256k1) on a trapped-ion design, about 25.7 days, 19,397 physical qubits, success probability 63%. https://arxiv.org/abs/2609.05625 | read: abstract only.
  - Webster et al. (Iceberg Quantum), Pinnacle Architecture, arXiv 2602.11457, Feb 2026: RSA-2048 with fewer than 100,000 physical qubits at 1e-3 error, 1 us cycle, 10 us reaction time. abstract only.
  - Mundada et al., arXiv 2604.06319, Apr 2026: RSA-2048 with 381k qubits in 9.2 days on grid coupling. abstract only.
  - The "20 million (2019)" figure comes only from the news page https://thequantuminsider.com/2026/03/31/q-day-just-got-closer-three-papers-in-three-months-are-rewriting-the-quantum-threat-timeline/ (lead only); the primary (Gidney 2025) was not opened.
- Why now: the ion-trap paper is 4 Sep; NIST HQC draft (FIPS 207) is overdue and could drop in the window (see note below). Does not expire: the estimates move, the structure (space x time x error) is stable.
- SHOW: a real tiny Shor run (factor 15 or 21 on a simulator we run ourselves), then a space-time plot of the published estimates as points (qubits vs days), each labelled with its paper. Pure diagram; no images needed.
- Format: long film (the trade-off is the story) and a Short ("the zero-knowledge proof that an attack works").
- Overlap: touches "public-key exchange" (idea list); distinct because the subject is the attacker's cost. Does not overlap Shorts list.
- Risk: estimates are paper claims, not machines; do not state a date for "Q-Day". Bitcoin angle must not read as financial advice. Need to read the full text of at least 2609.05625 and open Gidney 2025 before scripting.
- Note (dated event): NIST said (per freenode article of 3 Aug 2026, lead only) it plans a seed-only private key format in the Initial Public Draft of FIPS 207 (HQC-KEM), "expected shortly"; as of 20 Jul no draft was out (polysignal, lead only); a 90-day comment period would follow (NIST statement via search snippet, lead only). If it lands in Oct-Dec it is a hook. Not confirmed on csrc.nist.gov.

## 2. "Space is cold, so a data centre in orbit cools itself"
**It seems** orbit gives free cooling and free power. **But really** in vacuum heat can leave only by radiation (P = A·sigma·T^4), and a 1 GW orbital cluster would be limited as much by its radiators and by the network between satellites as by launch cost; one 2026 analysis finds inference might work, training "unlikely to be competitive".
- Facts:
  - van Berkel (TU Eindhoven), arXiv 2607.14172, 15 Jul 2026, "The Cost and Network Limits of Space-Based AI Compute". Abstract: LEO inference "may be feasible", frontier LLM training "unlikely to be competitive". In the text: Stefan-Boltzmann cooling; at 370 K, 40 kW (Starlink V2 mini class) needs about 38 m2 of radiator area (19 m2 double sided) by his simplified calculation; bisection bandwidth of a terrestrial Clos network 28,800 TB/s vs 2.25 TB/s for a 2D torus of satellites (his Table 3), and a 100+ times increase in training cost as "a rough indication" from a "rather crude model". https://arxiv.org/abs/2607.14172 | read in part (abstract, cooling, network and conclusion sections; downloaded text). Outside window by 2.5 weeks, newly relevant.
  - SpaceX Form S-1, filed 20 May 2026: "We expect to begin deploying our orbital AI compute satellites as early as 2028"; "potentially millions of satellites"; the filing also warns the 100 GW/year timeline "involves unproven or new innovations" (quoted in van Berkel; the sentence in the S-1 itself was not located by me). About 9,600 Starlink satellites as of 31 Mar 2026; Starship V3 satellites "in the second half of 2026". https://www.sec.gov/Archives/edgar/data/0001181412/000162828026036936/spaceexplorationtechnologi.htm | read in part (grep of the full filing, 11.8 MB HTML; the prospectus summary and business sections only).
  - Other 2026 papers found, not opened: arXiv 2604.27197 (Orbital Data Centers: Spacecraft Constraints and Economic Viability), 2604.07760 (Integrated Solar, Compute, Radiator panels): abstract/snippet only (lead only).
- Why now: the S-1 puts the claim in an official filing; an IPO process and Starship V3 flights in H2 2026 keep it in the news. Will age as real hardware flies; the physics will not.
- SHOW: our own simulation from a real run: radiator area vs temperature from the Stefan-Boltzmann law for a 1 MW and a 1 GW load (we compute it, state the formula and inputs), drawn against known object sizes; a torus vs Clos network bisection diagram with the paper's numbers. Real images: Starlink/ISS radiators from NASA (public domain) would need a licence check; none opened yet.
- Format: long film, plus a Short ("space is cold, and that is the problem").
- Overlap: Kessler syndrome (idea list) shares satellite count but is a different question; "why a chip costs billions" no.
- Risk: HIGH for the investment framing (SpaceX IPO). Treat strictly as engineering; no valuation, no "will it work" verdict beyond what the paper measures; the paper is one author, a crude model, the author discloses being a consultant to Snap. Do not claim launch cost per kg from the S-1 beyond what it quotes from NASA ($2,700/kg for the first Falcon 9 in 2010; $18,500/kg historical average; $1,400/kg Falcon Heavy 2018: read in the S-1).

## 3. One number, three forecasts: how much power will data centres use?
**It seems** "AI will use X TWh by 2030" is a measurement. **But really** it is a forecast with a documented chain of assumptions, and the new US national-lab report gives 649 TWh as a central case inside a compounded range of 521 to 843 TWh, while it also lowered its own history.
- Facts: Smith, Hubbard, Newkirk et al., LBNL, "United States Data Center Energy Usage Report: 2025 Update", June 2026 (publication date 2026-06-18, CC BY 4.0, LBNL-2001758, DOI 10.71468/P1RP4F): 2024 use 192 TWh (4.7% of US electricity), revised down from the 2024 report because GPU shipments for 2023-24 were reported lower; Reference Case 649 TWh in 2030 (11.8%); compounded uncertainty 521-843 TWh; the largest single swing is inference idle power and utilization (+20%); AI servers 55% of data centre energy in 2030; national PUE from 1.55 to 1.45 (2024 to 2030 per the text). It compares with EPRI (about 390-800 TWh) and IEA (about 430 TWh). https://escholarship.org/uc/item/33m6w3x0 (PDF copy read from rtoinsider.com mirror) | read in part (executive summary, scenarios, equipment breakdown).
  - IEA "Key Questions on Energy and AI" (Apr 2026): data centre use about 500 TWh in 2025 to 950 TWh in 2030; data centre electricity +17% in 2025, AI-focused +50%, global demand +3%. lead only (search snippet; IEA site returned 403).
- Why now: the report is new and the IEA/EPRI numbers disagree publicly; will age slowly (next LBNL update is not dated).
- SHOW: a fan chart built from the report's own scenario table (we redraw it), the stack of what a server draws (idle vs busy), a tree of the assumptions. No images needed.
- Format: long film (or Short "why forecasts disagree").
- Overlap: none on lists.
- Risk: medium. Numbers are scenario results, label them so; US-only scope (excludes crypto mining, per the report). Do not merge IEA and LBNL figures without noting different scope (global vs US).

## 4. The handshake that got heavier: post-quantum TLS in numbers
**It seems** quantum-safe web encryption is a distant plan. **But really** it already runs on about half of a sample of 32,000 domains, and the price is size: a hybrid key share of 1,216 bytes (the size of the classical-only share must be read from RFC 7748/8446 before comparing; not read here).
- Facts:
  - IETF draft-ietf-tls-ecdhe-mlkem, "published as RFC 10024" on 26 May 2026 (datatracker page): hybrid groups X25519MLKEM768 (client share 1,216 bytes, server 1,120), SecP256r1MLKEM768 (1,249 / 1,153), SecP384r1MLKEM1024 (1,665 / 1,665). https://datatracker.ietf.org/doc/html/draft-ietf-tls-ecdhe-mlkem | read in part (page summary via fetch tool, not RFC text).
  - IESG Last Call in July 2026 for draft-ietf-tls-mlkem (pure ML-KEM) | lead only.
  - Dubey and Varshney, arXiv 2606.16473, 15 Jun 2026: 32,011 domains; about 49.3% support hybrid ML-KEM-768 key exchange; 15.70% still on TLS 1.2; zero hybrid post-quantum certificates seen. https://arxiv.org/abs/2606.16473 | abstract only (outside window, newly relevant).
- Why now: RFC 10024 is fresh; pure ML-KEM Last Call may finish in the window. Slow to expire.
- SHOW: byte-level diagram of a ClientHello with the key share growing; a packet-size bar chart; optionally a real capture we make ourselves on server 2 (own traffic, no licence issue).
- Format: Short ("the handshake got bigger") or part of a longer encryption film.
- Overlap: HIGH with "public-key exchange" on the idea list; treat as a Short/episode of it, not a new subject.
- Risk: low. Verify the RFC text itself and measure sizes ourselves; the 49.3% is one study's sample.

## 5. "Cheaper per token" does not mean "less energy"
**It seems** a lower joules-per-token figure means a more efficient answer. **But really** the same GPU can report 7.46 J/token or 0.72 J/token for the same model just by changing the output length, while the total energy of the request goes up five-fold.
- Facts: Vellaisamy, Lam, Blanton, Shen (Carnegie Mellon), arXiv 2608.28044, 28 Aug 2026: Llama-3.2-1B on H200, batch 16, context 4K: output length 10 to 512 tokens takes energy per token from 7.46 to 0.72 J/token while window energy rises from 1.19 to 5.93 kJ; model E_request = E_fixed + N x E_decode_step; batching gain shrinks with context (6.31x at 512 context to 1.17x at 4K for 10 output tokens); mixture-of-experts raises fixed energy at low concurrency. https://arxiv.org/abs/2608.28044 | read in part (abstract and introduction of the downloaded PDF).
- Why now: paper is 5 weeks old; the "energy per query" argument is live. Slow to expire.
- SHOW: we can run our own small measurement on our own GPU (nvidia-smi power sampling, a small open model): fixed cost vs per-token cost, a real run, plotted. Needs the GPU queue and an open-licence model; fits "simulation from a real run".
- Format: Short ("why the average hides the cost").
- Overlap: borders "AI films in general" and the tokens idea (why a language model cannot see letters) only by the word token; the subject is accounting, not language.
- Risk: low if we measure ourselves; single-lab result on H100/H200; do not quote a "per ChatGPT query" figure.

## 6. Why RAM got expensive: a memory wafer can be HBM or ordinary memory, not both
**It seems** memory prices rise because "AI wants more memory". **But really** the same wafer capacity is being re-allocated to stacked high-bandwidth memory, which costs several wafers' worth of ordinary memory per bit, so ordinary memory gets scarce too.
- Facts:
  - Micron Form 8-K, 30 Sep 2026 (fiscal Q4 2026, ended 3 Sep): revenue $54.23 billion vs $11.32 billion a year earlier; fiscal-year revenue $133.19 billion vs $37.38 billion; gross margin 86.8% (GAAP); capex net $27.37 billion for FY26. https://www.sec.gov/Archives/edgar/data/0000723125/000072312526000018/a2026q4ex991-pressrelease.htm | read in full (press release exhibit, text extracted). The filing does not give HBM wafer ratios.
  - TrendForce, 9 Jul 2026: server DRAM contract prices expected +13-18% QoQ in 3Q26; RDIMM bit supply growth only 15-20% YoY; long-term agreements cap cloud customers' price rises. https://www.trendforce.com/presscenter/news/20260709-13140.html | read in full (fetch summary). TrendForce is a private research firm, not an official statistic.
  - "HBM share of DRAM wafer input 18% in 2025 to 22% in 2026 to about 30% in 2027" and "about 3-to-1 HBM-to-DDR5 wafer conversion": search snippets only (lead only); the primary is not found.
- Why now: dated hooks inside the window: Micron fiscal Q1 2027 results are due in the second half of December 2026 (date not confirmed); TrendForce 4Q26 price calls in early Oct. Numbers move fast.
- SHOW: wafer-to-bits diagram (stacked dies, through-silicon vias), a bar of one wafer allocation from a source we can cite once found; public filings' charts redrawn. Real images: Micron/SK hynix images are copyrighted; use own diagrams or Wikimedia CC images (licence unchecked).
- Format: Short, or a section in a longer film on "why a chip costs billions" (already a backlog Short; this is its sibling about memory).
- Overlap: close to the backlog Short "why a chip costs billions"; keep separate and structural.
- Risk: HIGH on fast-moving numbers and investment reading (record profit figures). Explain mechanism only; no stock talk; the 3-to-1 ratio must be sourced to a primary (company statement or paper) before use.

## 7. The second, the leap second and a vote in Versailles
**It seems** a clock simply counts seconds. **But really** UTC is kept within 0.9 s of Earth's rotation by inserting leap seconds, and on 13-15 Oct 2026 the 28th CGPM votes on a resolution to stop that, plus one on the next definition of the second and one on a Moon time scale.
- Facts:
  - 28th CGPM, Versailles, 13-15 Oct 2026; six draft resolutions; B redefinition path of the second, C continuity of UTC with effective date 20 May 2027 for new arrangements on the UT1-UTC limit, D lunar reference time scale; votes at agenda item 25. https://lunartime.org/news/cgpm-2026-three-time-resolutions/ | lead only (secondary site; the BIPM draft documents were not opened).
  - Resolution 27-5 (2022) on a future redefinition of the second (optical standards) asks CIPM to bring proposals to the 28th CGPM and adopt a new definition at the 2030 meeting: https://www.bipm.org/en/-/resolution-cgpm-27-5 | read in full (fetch summary). It does not itself mention leap seconds.
  - "Abolish the leap second by 2035" is from the 2022 CGPM per search snippets (lead only).
- Why now: dated event inside the window. Expires on 15 Oct unless held until the outcome is known (could be re-used after).
- SHOW: a real data plot of UT1-UTC and the leap-second table (IERS/IANA data, public) redrawn; the 2012 and 2016 leap-second outages are not sourced here, would need a source.
- Format: Short (timely), could feed a longer time film.
- Overlap: PARTIAL with "GPS needs Einstein (v024)" (timekeeping); keep it to UTC and leap seconds, no relativity.
- Risk: medium. Must read the BIPM drafts (not the blog) and report the vote's result only after it happens; if the vote is postponed the hook is gone.

## 8. Dividing a GPU does not isolate it
**It seems** NVIDIA's Multi-Instance GPU gives each customer a private slice of the card. **But really** memory-barrier instructions in one slice delay loads in another across the cache partitions, so a neighbour can infer when your model runs.
- Facts: Gu, Levine, Zhang, Sorensen, Guo, "Behind Bars: A Side-Channel Attack on NVIDIA MIG Cache Partitioning Using Memory Barriers", USENIX Security '26 (Baltimore, Aug 2026), pp. 5373-5392: attacker in one MIG instance infers kernel launch patterns of a victim in another, including LLM inference. https://www.usenix.org/conference/usenixsecurity26/presentation/gu-cheng | abstract only. No accuracy numbers read.
- Why now: published Aug 2026, fits the rental-GPU boom. Slow to expire.
- SHOW: timing trace diagram; a toy we make ourselves (two threads sharing a cache line pair, timing differences on server CPU) as a real run, not a GPU claim.
- Format: Short.
- Overlap: borders on AI films only by LLM mention; none on lists.
- Risk: medium. No vendor response read; must not overstate to "GPUs are unsafe"; need the full paper for the measured leak rate before scripting.

## 9. The grid line: why a power plant waits five years to plug in
**It seems** the limit on new power is building it. **But really** a large share of it is the queue to connect: of capacity that applied in 2000-2020 only 13% reached operation and 75% withdrew.
- Facts: LBNL, "Queued Up: 2026 Edition" (data to end of 2025): about 8,200 projects, 1,312 GW generation plus about 749 GW storage active; 13% of 2000-2020 requests built, 75% withdrawn; withdrawals above 40% even after signing an interconnection agreement; median request-to-operation over 5 years for 2025 projects; active queue volume fell 10%. https://emp.lbl.gov/publications/queued-2026-edition-characteristics | lead only (figures from a search summary; page not opened).
- Why now: pairs with item 3 (data-centre load); regulatory changes on large-load interconnection are being discussed but not sourced here. Slow to expire.
- SHOW: a queue animation from the real dataset (public LBNL data), project-by-project funnel; no images needed.
- Format: long film (with item 3) or Short.
- Overlap: none; adjacent to "heat pump", no.
- Risk: medium. US-specific; must open the report before use.

## 10. "The model already knows what it needs to read" (declarative attention)
**It seems** a language model must read its whole memory of the conversation to answer. **But really** it concentrates on a small part, and one new protocol lets the model declare which part, cutting attended tokens by 52.0% (Gemma-4-31B) and 31.1% (Qwen-3.6-27B) for accuracy drops of 1.27 and 2.75 points.
- Facts: Ho, Ahmad, Koh, Yun, Schuster, dos Santos, "Language Models Can Control Their Own Attention", arXiv 2609.02737, 2 Sep 2026; zero-shot, 15 long-context tasks. https://arxiv.org/abs/2609.02737 | abstract only.
- Why now: 1 month old. Preprint, not peer reviewed (not confirmed); ages fast.
- SHOW: our own attention heat-map from a small open model run on server 2 (real run), versus cache size growing with context.
- Format: Short at most.
- Overlap: edge of "AI films in general" and the tokens idea; the weakest candidate for the brief; included for completeness.
- Risk: preprint claim by authors, no independent replication; do not generalise.

---

## Looked at and rejected
- Battery prices (BNEF/Ember): stale (Dec 2025 data, outside window); lead only
- NIST HQC alone: not published; folded into item 1 as a hook
- Algorithms (STOC/SODA 2026 papers, 2608.13231, 2607.18714): niche; no abstract opened (not reached)
- HBM "crisis" blogs: commercial, secondary
- Weather ML survey (Springer, 11 Sep): survey, no single result
- Protein AI (Nature, Sep 2026): out of category, lead only
- NeurIPS 2026 (Sydney 6-12 Dec, Atlanta 8-13 Dec, Paris 9-13 Dec, search snippet, lead only): event, not a subject
- ICLR 2027 (deadline 25 Sep, held 26-30 Apr 2027 in San Francisco): past/far
- UncoreBleed, Timeslice-Sandwich (USENIX Sec 26): only titles seen
- Cable/sea internet: already on the list
- Launch cost per kg: only the S-1's quoted NASA numbers; one S-1 line, no new study

## Search terms used
NIST post-quantum standard HQC FIPS 207 draft 2026; IEA Energy and AI data centre electricity demand 2026; arXiv September 2026 language model surprising mechanism; SEMI World Fab Forecast equipment billings 2026; IETF RFC 2026 post-quantum TLS hybrid ML-KEM; HBM bottleneck / sodium-ion; LLM inference energy per query joules per token; SpaceX S-1 Starlink launch cost per kilogram; LBNL data center energy report 2026 / interconnection queue; orbital data centers thermal radiator area arXiv; DRAM contract prices Q3 2026 TrendForce HBM; new algorithm breakthrough 2026 STOC FOCS SODA; vulnerability side-channel USENIX Security 2026; BloombergNEF battery storage cost 2026; RSA-2048 qubits resource estimate 2026; csrc.nist.gov FIPS 207 comment period; NeurIPS 2026 dates / ICLR 2027; 28th CGPM leap second; Micron fiscal Q4 2026; "Behind Bars" MIG; Nature August/September 2026 machine learning; Berkeley Lab Queued Up 2026. arXiv API queries: elliptic curve + quantum + qubits; RSA-2048 + qubits + factoring; LLM benchmark contamination.

## Not reached
- SEMI: Q2 2026 equipment billings US$40.53 billion (+23% YoY) and 2026 equipment-spending forecasts (US$139 billion total equipment / US$152 billion fab equipment: two different SEMI series): search snippets only, SEMI pages returned 403. Good source for a "how a fab is paid for" film; not verified.
- IEA Electricity 2026 / Key Questions on Energy and AI: site blocked (403); figures lead only.
- NIST csrc pages (FIPS 207 draft status), IETF RFC 10024 full text, BIPM draft resolutions B/C/D.
- Gidney 2025 RSA paper and full texts of 2609.05625 and 2603.28846.
- Interesting leads not searched: TSMC/ASML filings, High-NA EUV, EU Chips Act, power-grid transformers, submarine-cable repair ships, Starship V3 flight dates, EIA statistics, FERC large-load rulemaking, CA/Browser Forum certificate lifetimes, DNS/BGP incidents, USENIX/CCS November papers, SEC filings of TSMC/NVIDIA (NVIDIA Q3 FY27 results expected late Nov 2026, date not confirmed).
- Dated events in the next 90 days found: CGPM 13-15 Oct; NeurIPS 6-13 Dec; possible NIST FIPS 207 draft; Micron FQ1 results (late Dec, unconfirmed); Starship V3 satellite deployments "H2 2026" (S-1).

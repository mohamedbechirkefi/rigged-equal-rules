<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# RIGGED demo: design plan

Owner request of 2026-11-26 (labs brief `DEMO-BRAND-brief.md`): every lab demo gets its own brand, motion and premium UI. This file is the plan, written before the code, and its review.

## Subject, audience, job

- **Subject.** One common score threshold applied to two abstract groups whose starting distributions differ: who clears the cut, the equal-opportunity gap, and a real-score test that reversed the predicted sign.
- **Audience.** A curious technical reader, an admissions committee reading for care with claims, a fairness researcher checking the design.
- **Primary job.** State the question and the measured answer in one sentence, make the mechanism visible (two distributions, one cut line), then give the evidence with the contradiction at the same weight as the support.

## Direction: the results letter and the measuring rule

Two objects from the world of selection:

1. **The letter.** The hero is a sheet of letter paper laid on a desk: a letterhead with the mark, a "Re:" line carrying the question, a body that answers it with the measured numbers, and the claims boundary as the letter's postscript. Every experiment below is filed as a letter of its own with a printed verdict stamp.
2. **The measuring rule.** A steel rule with engraved ticks runs under the letter. Two score distributions sit on it, Group A as an ink-blue curve, Group B as an ochre one, and one red cut line slides along the rule and settles. Everything to the right of the line is "selected". The rule recurs as the axis style of every chart.

## Colour (light only)

| Name | Hex | Role |
|---|---|---|
| Desk lilac | `#E7E5EE` | page background, a cool lilac-grey desk, never cream |
| Letter white | `#FFFFFF` | letter sheets, charts |
| Violet ink | `#211D33` | text, the rule, the mark |
| Fountain blue | `#2747A8` | Group A (always a circle) |
| Ochre | `#9A5B00` | Group B (always a square) |
| Stamp red | `#B8203A` | the cut line, the 2 pp band edge, "against" verdict stamps; used for nothing else |

Groups keep their shapes (circle, square) so colour never carries the group alone.

## Type

- **Libre Caslon Text** (Pablo Impallari, Rodrigo Fuenzalida; OFL 1.1), 400 and 700. The letters: headings, the hero letter, body prose. A Caslon reads as correspondence and as institutional print.
- **Barlow Semi Condensed** (Jeremy Tribby; OFL 1.1), 500 and 600. The rule: chart labels, numbers with tabular figures, buttons, tags, navigation. A narrow grotesque in the spirit of engraved scale numerals.

Scale: 17 px body, headings 1.333 ratio (22.7, 30.2, 40.3), hero subject line fluid to 52 px. Measure 62 to 70 characters.

## Layout

```
 desk (lilac)
+-----------------------------------------------------------------+
| [mark] Rigged        Overview Explorer Results Assumptions ...  |  sticky, letter white, hairline
+-----------------------------------------------------------------+
|     +-----------------------------------------------+           |
|     | [mark] RIGGED study       letterhead          |           |
|     | Re: Can equal rules yield unequal outcomes    |           |
|     |     under different starting distributions?   |           |
|     | Answer sentence with 6.59 pp [6.20, 6.97] and |           |
|     | the real-score reversal -7.45 pp.             |           |
|     | |~~~~ A ~~~~   ~~~~ B ~~~~   |cut              |  <- rule  |
|     | |''''|''''|''''|''''|''''|''''|''''|''''|      |           |
|     | Illustration, not study data      [Replay]    |           |
|     | P.S. claims boundary                          |           |
|     +-----------------------------------------------+           |
|  Overview: two key findings as stamped slips                    |
|  Explorer: scenario tabs with a sliding indicator, picker grid, |
|            four gap panels on rule axes, subgroup chart         |
|  Results: one letter per experiment, verdict stamp top right    |
|  Assumptions, Method, Sandbox (dashed ochre frame), Footer      |
+-----------------------------------------------------------------+
```

The letter is offset slightly left of centre on wide screens with the rule extending past its right edge, as a rule laid across a sheet would. Text left aligned.

## Motion

- **The one orchestrated moment.** The two curves draw from the rule upward (opacity and a vertical scale from the baseline), then the red cut line slides in from the right edge of the rule and settles with a strong ease-out at the capacity point; the selected area of each curve fills to its right (clip-path inset). The illustration says "Illustration, not study data" and shows no number; the rule has ticks but no numerals. Replay button replays it.
- **Motion that answers the visitor.** The scenario control has a sliding indicator (transform, 240 ms). Picking a cell in the explorer moves the dots and whiskers of the gap charts to their new positions (transform transitions on the marks, 260 ms), so the change between cells is visible. Charts reveal once when scrolled into view. The sandbox shows a progress rail while running. The two key figures count up once from zero, ending on the exact manuscript string.
- **Reduced motion.** The hero shows its final frame, the marks jump without transition, no count-up, no reveal. Hover only under `(hover: hover) and (pointer: fine)`.

## The one memorable thing

The page opens as a letter whose subject line is the research question, and under it a measuring rule on which one red cut line slides across two unequal distributions.

## Review against the generated-page tells, and what changed

- *Cream and terracotta:* the first idea was letter paper on a manila desk with an oxblood seal. That is the cream and clay default. Changed to white sheets on a cool lilac-grey desk, and the only warm accent is the stamp red of the cut line, which has one meaning.
- *Near-black with one acid accent:* no; light page.
- *All-caps tracked eyebrows:* the original page had an uppercase kicker; removed. Verdict stamps are set in Barlow at normal case with a ruled border, not tracked capitals.
- *Mono for data labels:* no mono; numbers use Barlow tabular figures.
- *01/02/03:* none. Experiment ids are real identifiers.
- *Identical rounded cards:* the experiments become letters: square-cornered white sheets with a letterhead row and a stamp; the key findings become narrow slips with a perforated top edge (dashed border), different from the letters.
- *Fade-up on every section:* only charts reveal, once.
- *Other demos:* PARADOX uses ballots and chalk tallies, so no ballot slips or tally marks here; TRUST uses lab labels and star bars; HERD uses a line of people. RIGGED keeps to letters and the rule. FLOW (same session) uses green guide signs and route maps; RIGGED has no green and no route lines.

## Screenshot critique (two passes)

- Pass 1: the mark appeared twice at the top of the page (sticky bar and letterhead). Removed accessory: the lockup in the letterhead, which now reads "Results letter" in the letter face. The clip of the selected areas was offset from the cut line (clip insets are relative to the fill's own box, not the drawing); corrected. At phone width the illustration labels rendered near 8 px; phones now get short labels (A, B, selected, lower, higher) at a larger size. The picker grid wrapped its buttons into four lines at 390 px; tighter padding on phones. The run button was styled like the secondary buttons; it is now the one filled button in the sandbox.
- Pass 2: hero, overview slips, explorer, letters and sandbox checked at 1440 px and 390 px; count-ups end on the exact data strings. Still weak: in the gap charts, very narrow intervals make the whisker caps read as a small block around the dot.

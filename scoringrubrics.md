## Scoring Rubrics (0–5)

General policy: **0–1 = needs attention**, **2–3 = acceptable**, **4–5 = strong**. Include **thresholds and exemplars** to keep consistent.

### CA01 – Filler Usage

- **5** Exceptional: filler_density_per_1k < 5; no consecutive runs; <5% turns start with fillers; transitions clean.
- **4** Strong: <10 per 1k; rare runs; minimal at starts.
- **3** Adequate: 10–20 per 1k; occasional runs; starts <20%.
- **2** Weak: 20–35 per 1k; noticeable runs; starts 20–35%.
- **1** Poor: 35–50 per 1k; frequent runs; starts >35%.
- **0** Very Poor: >50 per 1k; repeated clusters and fillers dominate transitions.

### CA02 – Sentence Length & Complexity

- **5** Clear, well-paced sentences: avg_sentence_length_tokens in target band for audience; long_sentence_share_pct low; fragments rare and purposeful.
- **4** Mostly well-paced; occasional long sentence or fragment, but meaning stays clear.
- **3** Mixed pacing; periodic run-ons or fragments, but overall understandable.
- **2** Frequent run-ons or choppy fragments; reader/listener effort noticeably higher.
- **1** Consistently hard to parse; many long/stacked clauses or frequent broken fragments.
- **0** Severely unclear; sentence structure prevents comprehension.

### CA03 – Ambiguous References

- **5** Near-zero ambiguous_this_that_it_rate; referents consistently named; pronouns always clearly anchored.
- **4** Minor ambiguity; occasional quick fix needed, but meaning typically obvious.
- **3** Some ambiguous referents; requires occasional reread or clarification.
- **2** Regular ambiguity; multiple instances where referent is unclear or shifts mid-paragraph.
- **1** Frequent ambiguity; meaning often depends on guesswork.
- **0** Pervasive ambiguity; intent is largely unclear.

### SC01 – Signposting & Framing

- **5** Clear signposts at open/transition/close; main_point_earliness_index ≥ 0.8.
- **4** Most signposts present; index 0.6–0.79.
- **3** Some signposting; index 0.4–0.59.
- **2** Weak structure; index 0.2–0.39.
- **1** Rambling; index 0.1–0.19.
- **0** No discernible structure; index <0.1.

### SC02 – Topic Drift

- **5** High cohesion_score_adjacent_turns; off_topic_ratio near zero; tangents explicitly parked and returned from.
- **4** Mostly coherent; occasional brief tangent with clear tie-back.
- **3** Some drift; a few responses wander before returning to the point.
- **2** Noticeable drift; frequent tangents or weak linkage between turns/paragraphs.
- **1** Heavy drift; central question often not addressed directly.
- **0** Responses largely off-topic; cohesion is consistently low.

### SC03 – Point Ordering (BLUF)

- **5** Main point appears immediately; main_point_earliness_index ≥ 0.8; supporting points ordered logically; recap is crisp.
- **4** Main point early (0.6–0.79); minor reordering would improve scanability.
- **3** Main point mid-way (0.4–0.59); some front-loading but inconsistent.
- **2** Main point late (0.2–0.39); listener must wade through setup.
- **1** Very late (0.1–0.19); recommendation is buried or implied.
- **0** No main point; cannot identify a recommendation or headline.

### CB01 – Talk-Time Balance

- **5** Balanced speaker_word_share_pct for the context; minimal monologue_streaks; turn-taking invites input naturally.
- **4** Generally balanced; occasional long turn but includes check-ins.
- **3** Acceptable balance; some longer turns without inviting response.
- **2** Noticeable imbalance; frequent long turns or interruptions; limited space for others.
- **1** Heavy imbalance; repeated monologues dominate the interaction.
- **0** Extremely unbalanced; interaction becomes one-sided and inhibits dialogue.

### CB02 – Question Frequency & Quality

- **5** >70th pctile open questions; reflective questions present; purposeful.
- **4** Balanced mix; reflective appears.
- **3** Adequate number; mostly closed.
- **2** Few questions; mostly closed/leading.
- **1** Rare and low quality; interrogative tone without curiosity.
- **0** No questions.

### CB03 – Acknowledgment & Listening

- **5** High paraphrase_presence; acknowledger_terms_rate appropriate; consistently confirms understanding and names key constraints.
- **4** Regular acknowledgments and occasional paraphrase; rare missed opportunities.
- **3** Some acknowledgments; paraphrasing inconsistent; responsiveness is adequate.
- **2** Limited acknowledgment; responses frequently “move on” without showing understanding.
- **1** Often dismissive or non-responsive; many missed opportunities to validate or confirm.
- **0** No acknowledgment; repeatedly talks past others.

### TP01 – Hedging vs Assertiveness

- **5** Clear ownership; hedges used sparingly to soften without obscuring intent.
- **4** Mostly clear; occasional unnecessary hedges.
- **3** Mixed; meaning sometimes diluted.
- **2** Frequent hedging; intent unclear at moments.
- **1** Heavy hedging; low confidence throughout.
- **0** Extreme hedging; avoidance/non-commitment.

### TP02 – Empathy & Validation

- **5** Clear empathy_phrase_presence; validation_frequency appropriate; de-escalates tension while staying direct.
- **4** Warm and responsive; occasional missed moment to validate feelings/constraints.
- **3** Neutral baseline; some empathy, but not consistently deployed.
- **2** Often transactional; empathy rarely expressed even when context calls for it.
- **1** Frequently cold or brusque; responses can escalate frustration.
- **0** Hostile or invalidating; actively undermines rapport.

### TP03 – Politeness & Professionalism

- **5** High politeness_markers_rate without being overly deferential; direct imperatives are softened with context/reason; tone stays respectful.
- **4** Mostly professional; occasional overly blunt phrasing.
- **3** Generally fine; mix of polite and abrupt moments.
- **2** Regularly too blunt; several direct_imperatives_without_softeners.
- **1** Often rude or harsh; professionalism concerns.
- **0** Unacceptable tone; aggressive or consistently disrespectful.

### VE01 – Lexical Diversity

- **5** High diversity (top quartile TTR/MTLD proxy), minimal repetition.
- **4** Above average diversity; mild repetition.
- **3** Average diversity.
- **2** Limited range; notable repetition.
- **1** Very repetitive; clichés dominate.
- **0** Monotone vocabulary; comprehension suffers.

### VE02 – Jargon vs Plain Language

- **5** Low jargon_term_density or jargon consistently defined; jargon_followed_by_definition_rate high; clarity is high for intended audience.
- **4** Mostly plain; occasional jargon that is quickly clarified.
- **3** Some jargon; definitions inconsistent; comprehension varies by reader.
- **2** Frequent jargon; rare definitions; meaning often inaccessible to non-insiders.
- **1** Heavy jargon; clarity suffers significantly.
- **0** Nearly incomprehensible to target audience due to jargon overload.

### VE03 – Precision vs Vagueness

- **5** Low vague_term_rate; numeric_specificity_presence strong where appropriate; commitments have owners, scope, and timelines.
- **4** Mostly concrete; occasional vague term but context resolves it.
- **3** Mixed; some specifics, some vague statements.
- **2** Often vague; key details missing (who/what/when/how much).
- **1** Predominantly vague; hard to infer commitments or constraints.
- **0** Extremely vague; content is not actionable.

### CE01 – Audience Alignment

- **5** reading_level_estimate matches target audience; unexplained_acronym_rate near zero; examples and assumptions are calibrated.
- **4** Mostly aligned; minor mismatches in depth or occasional unexplained acronym.
- **3** Adequate alignment; some parts too technical or too basic.
- **2** Regular mismatch; frequent assumptions or unexplained terms.
- **1** Poor fit; audience likely confused or disengaged.
- **0** Severe mismatch; content fails for intended audience.

### CE02 – Purpose Alignment

- **5** Purpose explicit; strong evidence; CTA crisp and actionable.
- **4** Purpose clear; CTA present.
- **3** Purpose implied; CTA somewhat vague.
- **2** Purpose unclear; weak CTA.
- **1** Mismatch between content and purpose.
- **0** No discernible purpose or CTA.

### CE03 – Register Fit (Formality)

- **5** formality_score matches context; slang_rate appropriate (usually low in professional contexts); greetings/closings fit the channel.
- **4** Mostly appropriate register; occasional too casual or too stiff phrasing.
- **3** Acceptable; some inconsistent formality.
- **2** Often mismatched; noticeable slang or overly formal phrasing for the context.
- **1** Poor register control; distracts from message.
- **0** Inappropriate register; undermines credibility or rapport.

> **Scoring function**: combine **rules metrics** (normalized 0–1) with **LLM judgments** (mapped to 0–1) using weighted averages per skill; keep weights in config so you can recalibrate.
>
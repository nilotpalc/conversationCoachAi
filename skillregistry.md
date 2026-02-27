skills:
  - id: CA01_fillers
    label: Filler Usage
    when_to_use: "User wants clarity, articulation, or disfluency reduction."
    analysis_instructions: |
      Extract metrics:
      - filler_density_per_1k
      - consecutive_filler_runs
      - filler_at_turn_start_rate
      - filler_at_transition_rate
      Provide 3 examples with line refs and 1-sentence impact.
    coaching_instructions: |
      Give 2 strengths, 2 micro-behaviors, 1-sentence why it helps.
    rewrite_instructions: |
      Minimal edits to remove fillers; keep voice and intent.
    output_schema: |
      JSON:
      { "skill":"CA01_fillers","metrics":{...},"examples":[...],"insight":"..." }

  - id: CA02_sentence_complexity
    label: Sentence Length & Complexity
    when_to_use: "User wants clearer sentences, less run-on speech, or better pacing."
    analysis_instructions: |
      Extract metrics:
      - avg_sentence_length_tokens
      - long_sentence_share_pct
      - fragment_rate
      Provide 3 examples (longest sentence, a fragmented sentence, and a well-paced sentence) with line refs and 1-sentence impact.
    coaching_instructions: |
      Give 2 strengths and 2 micro-behaviors (e.g., one-idea-per-sentence, punchy lead sentence), plus 1-sentence why it helps.
    rewrite_instructions: |
      Split run-on sentences and smooth fragments while preserving voice and meaning.
    output_schema: |
      JSON:
      { "skill":"CA02_sentence_complexity","metrics":{...},"examples":[...],"insight":"..." }

  - id: CA03_ambiguous_references
    label: Ambiguous References
    when_to_use: "User gets feedback like 'unclear what this/that refers to' or wants higher precision."
    analysis_instructions: |
      Detect ambiguous deictic references (e.g., this/that/it/they) without clear antecedents.
      Extract metrics:
      - ambiguous_this_that_it_rate
      Provide 3 examples with line refs, inferred intended referent (if possible), and 1-sentence impact.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (name the noun, restate the referent, avoid stacked pronouns) plus 1-sentence why it helps.
    rewrite_instructions: |
      Replace ambiguous pronouns with explicit referents where needed; keep tone and brevity.
    output_schema: |
      JSON:
      { "skill":"CA03_ambiguous_references","metrics":{...},"examples":[...],"insight":"..." }

  - id: SC01_signposting
    label: Signposting & Framing
    when_to_use: "User wants better flow, BLUF openings, or clear transitions."
    analysis_instructions: |
      Detect opening signpost, transitions, closing; compute main_point_earliness_index (0-1).
      Provide 3 examples.
    coaching_instructions: |
      Provide: a BLUF opening template, 2 transition templates, a closing template.
    rewrite_instructions: |
      Rewrite opening and transitions to improve wayfinding.
    output_schema: |
      JSON:
      { "skill":"SC01_signposting","metrics":{...},"examples":[...],"insight":"..." }

  - id: SC02_topic_drift
    label: Topic Drift
    when_to_use: "User wants tighter focus, fewer tangents, or more coherent responses."
    analysis_instructions: |
      Estimate semantic cohesion across turns and detect drift.
      Extract metrics:
      - cohesion_score_adjacent_turns
      - off_topic_ratio
      Provide 3 examples where drift happens (or where coherence is strong) with line refs and 1-sentence impact.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (explicit agenda, parking lot, tie-back statements) plus 1-sentence why it helps.
    rewrite_instructions: |
      Remove or relocate tangents and add tie-back phrases to maintain coherence; preserve intent.
    output_schema: |
      JSON:
      { "skill":"SC02_topic_drift","metrics":{...},"examples":[...],"insight":"..." }

  - id: SC03_point_ordering
    label: Point Ordering (BLUF)
    when_to_use: "User wants to get to the point faster or improve executive communication."
    analysis_instructions: |
      Detect where the main point / recommendation first appears.
      Extract metrics:
      - main_point_earliness_index
      Provide 3 examples (early BLUF, late main point, and a good recap) with line refs and 1-sentence impact.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (BLUF opener, headline + 2 supports) plus 1-sentence why it helps.
    rewrite_instructions: |
      Move the main point earlier and reorder supporting details; keep style and accuracy.
    output_schema: |
      JSON:
      { "skill":"SC03_point_ordering","metrics":{...},"examples":[...],"insight":"..." }

  - id: CB01_talk_time
    label: Talk-Time Balance
    when_to_use: "User wants better turn-taking, less monologuing, or more shared airtime."
    analysis_instructions: |
      If multi-speaker transcript is available, estimate talk-time/word-share by speaker.
      Extract metrics:
      - speaker_word_share_pct
      - monologue_streaks
      Provide 3 examples of long turns or interruptions with line refs and 1-sentence impact.
      If single-speaker, note that talk-time balance is not applicable and skip metrics.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (invite input, pause-and-check, time-box answers) plus 1-sentence why it helps.
    rewrite_instructions: |
      Rewrite selected long turns to be more concise and add check-in questions; preserve meaning.
    output_schema: |
      JSON:
      { "skill":"CB01_talk_time","metrics":{...},"examples":[...],"insight":"..." }

  - id: CB02_questions
    label: Question Frequency & Quality
    when_to_use: "User asks about engagement, curiosity, or stakeholder dialogue."
    analysis_instructions: |
      Classify questions: open, closed, leading, reflective. Compute:
      - question_rate_per_1000
      - open_question_ratio
      - reflective_question_presence
      Provide 3 examples + impact sentence.
    coaching_instructions: |
      Suggest 3 open-question stems tailored to the declared purpose.
    rewrite_instructions: |
      Convert closed/leading to open/non-leading while preserving intent.
    output_schema: "JSON with metrics, examples, insight."

  - id: CB03_acknowledgement
    label: Acknowledgment & Listening
    when_to_use: "User wants to sound more responsive, collaborative, or improve active listening."
    analysis_instructions: |
      Detect acknowledger terms and paraphrasing.
      Extract metrics:
      - acknowledger_terms_rate
      - paraphrase_presence
      Provide 3 examples (acknowledgment, paraphrase, missed opportunity) with line refs and 1-sentence impact.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (name feeling/need, paraphrase + confirm) plus 1-sentence why it helps.
    rewrite_instructions: |
      Add brief acknowledgments/paraphrases to selected lines without changing intent or over-apologizing.
    output_schema: |
      JSON:
      { "skill":"CB03_acknowledgement","metrics":{...},"examples":[...],"insight":"..." }

  - id: TP01_hedging
    label: Hedging vs Assertiveness
    when_to_use: "User wants to sound clearer/confident without aggression."
    analysis_instructions: |
      Detect hedges; compute hedge_term_rate and modal_strength_distribution {weak,medium,strong}.
      Provide 3 examples + impact.
    coaching_instructions: |
      Offer 2 alternatives that increase clarity/ownership without aggression.
    rewrite_instructions: |
      Reduce hedging only where it obscures intent; keep collaborative tone.
    output_schema: "JSON with metrics, examples, insight."

  - id: TP02_empathy
    label: Empathy & Validation
    when_to_use: "User wants warmer tone, better rapport, or to de-escalate tension."
    analysis_instructions: |
      Detect empathy and validation phrases.
      Extract metrics:
      - empathy_phrase_presence
      - validation_frequency
      Provide 3 examples (effective empathy, validation, missed opportunity) with line refs and 1-sentence impact.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (reflect emotion, validate constraints, ask perspective) plus 1-sentence why it helps.
    rewrite_instructions: |
      Add concise empathy/validation where appropriate; avoid overdoing it; keep voice.
    output_schema: |
      JSON:
      { "skill":"TP02_empathy","metrics":{...},"examples":[...],"insight":"..." }

  - id: TP03_politeness
    label: Politeness & Professionalism
    when_to_use: "User wants to be direct but respectful, or reduce perceived harshness."
    analysis_instructions: |
      Detect politeness markers and potentially face-threatening direct imperatives.
      Extract metrics:
      - politeness_markers_rate
      - direct_imperatives_without_softeners
      Provide 3 examples with line refs and 1-sentence impact.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (please + reason, soften commands, appreciation) plus 1-sentence why it helps.
    rewrite_instructions: |
      Rewrite selected lines to keep directness while adding professional softeners where needed.
    output_schema: |
      JSON:
      { "skill":"TP03_politeness","metrics":{...},"examples":[...],"insight":"..." }

  - id: VE01_lexical_diversity
    label: Lexical Diversity
    when_to_use: "User wants richer, less repetitive language."
    analysis_instructions: |
      Compute TTR and an MTLD proxy; list 3 overused terms with counts.
    coaching_instructions: |
      Provide concise synonyms/paraphrases aligned to the stated audience.
    rewrite_instructions: |
      Replace repetitive words with suitable alternatives; preserve meaning.
    output_schema: "JSON with metrics, overused_terms, suggestions."

  - id: VE02_jargon
    label: Jargon vs Plain Language
    when_to_use: "User wants broader comprehension, clearer explanations, or less insider language."
    analysis_instructions: |
      Detect domain-specific jargon and whether it is defined when introduced.
      Extract metrics:
      - jargon_term_density
      - jargon_followed_by_definition_rate
      Provide 3 examples (jargon, defined jargon, and missed definition) with line refs and 1-sentence impact.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (define on first use, swap for plain words, add example) plus 1-sentence why it helps.
    rewrite_instructions: |
      Replace unnecessary jargon with plain language and add brief definitions where jargon is needed.
    output_schema: |
      JSON:
      { "skill":"VE02_jargon","metrics":{...},"examples":[...],"insight":"..." }

  - id: VE03_precision
    label: Precision vs Vagueness
    when_to_use: "User wants more concrete language, clearer commitments, or fewer vague statements."
    analysis_instructions: |
      Detect vague terms and presence of numeric or concrete specifics.
      Extract metrics:
      - vague_term_rate
      - numeric_specificity_presence
      Provide 3 examples (vague phrasing, improved precise version, and missed specificity) with line refs and 1-sentence impact.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (add numbers/dates, name owners, specify scope) plus 1-sentence why it helps.
    rewrite_instructions: |
      Rewrite vague phrases into more specific ones where possible, without inventing facts.
    output_schema: |
      JSON:
      { "skill":"VE03_precision","metrics":{...},"examples":[...],"insight":"..." }

  - id: CE01_audience_alignment
    label: Audience Alignment
    when_to_use: "User wants to match technical depth, tone, and assumptions to the target audience."
    analysis_instructions: |
      Estimate reading level/technicality and check for unexplained acronyms.
      Extract metrics:
      - reading_level_estimate
      - unexplained_acronym_rate
      Provide 3 examples (good match, too technical, too simplistic) with line refs and 1-sentence impact.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (state audience, define acronyms, adjust examples) plus 1-sentence why it helps.
    rewrite_instructions: |
      Rewrite selected lines to better match the stated audience; define acronyms; keep intent.
    output_schema: |
      JSON:
      { "skill":"CE01_audience_alignment","metrics":{...},"examples":[...],"insight":"..." }

  - id: CE02_purpose_alignment
    label: Purpose Alignment (CTA/Evidence)
    when_to_use: "User needs a clearer goal, CTA, or evidence alignment."
    analysis_instructions: |
      Infer purpose (inform/persuade/collaborate), estimate call_to_action_clarity (0-1), evidence_support_presence (bool). Provide examples and gaps.
    coaching_instructions: |
      Provide a purpose-aligned one-sentence CTA and 2 variants.
    rewrite_instructions: |
      Insert/sharpen CTA in closing lines; preserve style.
    output_schema: "JSON with purpose_inferred, CTA clarity, evidence flag, examples."

  - id: CE03_register
    label: Register Fit (Formality)
    when_to_use: "User wants the right level of formality for context (exec update, peer sync, customer call)."
    analysis_instructions: |
      Estimate formality and detect slang/informality markers.
      Extract metrics:
      - formality_score
      - slang_rate
      Provide 3 examples (appropriate register, too casual, too formal) with line refs and 1-sentence impact.
    coaching_instructions: |
      Provide 2 strengths and 2 micro-behaviors (swap slang, adjust greetings/closings, sentence tightening) plus 1-sentence why it helps.
    rewrite_instructions: |
      Rewrite selected lines to match the target register; keep meaning and warmth.
    output_schema: |
      JSON:
      { "skill":"CE03_register","metrics":{...},"examples":[...],"insight":"..." }
rubrics:
  CA01_fillers:
    thresholds:
      "5": "filler_density_per_1k < 5 AND consecutive_filler_runs=0 AND filler_at_turn_start_rate < 0.05"
      "4": "filler_density_per_1k < 10"
      "3": "10 <= density < 20"
      "2": "20 <= density < 35"
      "1": "35 <= density < 50"
      "0": "density >= 50"
  SC01_signposting:
    thresholds:
      "5": "main_point_earliness_index >= 0.8 AND opening_signpost AND closing_summary"
      "4": "0.6 <= index < 0.8"
      "3": "0.4 <= index < 0.6"
      "2": "0.2 <= index < 0.4"
      "1": "0.1 <= index < 0.2"
      "0": "index < 0.1"
  CB02_questions:
    qualitative: "Map open_question_ratio and presence of reflective questions to 0–5 as described."
  TP01_hedging:
    qualitative: "Map hedge_term_rate and modal_distribution to 0–5 as described."
  VE01_lexical_diversity:
    qualitative: "Map TTR/MTLD proxy and repetition to 0–5."
  CE02_purpose_alignment:
    qualitative: "Map CTA clarity, purpose explicitness, evidence presence to 0–5."
weights:
  default: { rules: 0.6, llm_judgment: 0.4 }
# Complexity baseline — oak-park-ai-hub

Generated 2026-08-05 before enforcement. This is a debt inventory, not a request
to mass-refactor existing business logic. New functions may not exceed 10, and
existing entries may not increase without a documented exception.

- Threshold: 10 (classic McCabe cyclomatic complexity)
- Pinned tools: Ruff 0.16.0; ESLint 10.4.0 + typescript-eslint 8.65.0
- Measurement runtime: Node 24.14.0; installed lint dependencies occupied 43 MB locally
  (`node_modules/` is ignored and not committed; `pnpm-lock.yaml` pins the dependency graph).
- Reproducible commands: `ruff check --output-format=concise .` and `pnpm quality:js`
- Findings: 166 total (150 Python, 16 JavaScript/TypeScript)
- Scope: maintained first-party source and tests; dependencies, caches, build artifacts,
  and the vendored `remotion-best-practices` rule assets are excluded.

## Ranked findings (worst first)

| # | Complexity | Language | Function | File:line |
|---:|---:|---|---|---|
| 1 | **185** | Python | `process_one_topic` | `scripts/content_creator/main.py:1488` |
| 2 | **90** | Python | `fetch_all_media` | `scripts/content_creator/carousel_builder.py:3591` |
| 3 | **69** | Python | `check_html_placeholders` | `scripts/content_creator/carousel_reviewer.py:199` |
| 4 | **68** | Python | `_parse_rule_based` | `scripts/content_creator/note_parser.py:370` |
| 5 | **58** | Python | `fix_version_folder` | `scripts/content_creator/fix_existing_images.py:166` |
| 6 | **48** | Python | `main` | `scripts/capture/capture_pipeline.py:4449` |
| 7 | **43** | Python | `_build_brazil_html` | `scripts/content_creator/carousel_builder.py:6677` |
| 8 | **42** | Python | `main` | `scripts/content_creator/main.py:2701` |
| 9 | **36** | Python | `check_built_post` | `scripts/content_creator/carousel_reviewer.py:2543` |
| 10 | **36** | Python | `main` | `scripts/self_heal/orchestrator.py:1263` |
| 11 | **32** | Python | `check_drive_folder` | `scripts/content_creator/carousel_reviewer.py:1557` |
| 12 | **31** | Python | `process_replies` | `scripts/content_creator/approval_handler.py:1791` |
| 13 | **31** | Python | `run` | `scripts/youtube_research.py:897` |
| 14 | **29** | Python | `re_render_post` | `scripts/content_creator/approval_handler.py:1228` |
| 15 | **28** | Python | `generate_opc_per_template_content` | `scripts/content_creator/carousel_builder.py:2053` |
| 16 | **28** | Python | `fetch_template_aware_media` | `scripts/content_creator/carousel_builder.py:4235` |
| 17 | **28** | Python | `build_opc_from_slide_plan` | `scripts/content_creator/carousel_builder.py:5706` |
| 18 | **27** | Python | `run` | `scripts/4am_agent/self_healer.py:455` |
| 19 | **27** | Python | `run_news` | `scripts/capture/capture_pipeline.py:2952` |
| 20 | **24** | JavaScript/TypeScript | `Async function 'getApprovedTopicFromSheet'` | `scripts/blog-generator.js:207` |
| 21 | **23** | Python | `run_phase2` | `scripts/content_creator/opc_proof_post.py:916` |
| 22 | **22** | Python | `execute_resource_jobs` | `scripts/capture/resource_router.py:568` |
| 23 | **22** | Python | `check_slide_plan` | `scripts/content_creator/carousel_reviewer.py:2400` |
| 24 | **22** | Python | `run_person_evidence_mining` | `scripts/research/person_evidence_runner.py:727` |
| 25 | **20** | Python | `_check_system_alerts` | `scripts/4am_agent/main.py:300` |
| 26 | **20** | Python | `save_to_news_folder` | `scripts/capture/capture_pipeline.py:3651` |
| 27 | **20** | Python | `main` | `scripts/capture/capture_queue_processor.py:270` |
| 28 | **20** | Python | `enforce_opc_comparison_parity` | `scripts/content_creator/carousel_builder.py:434` |
| 29 | **20** | Python | `_build_the_case_html` | `scripts/content_creator/carousel_builder.py:7571` |
| 30 | **20** | Python | `check_standalone_content` | `scripts/content_creator/carousel_reviewer.py:2268` |
| 31 | **20** | Python | `send_review_email` | `scripts/content_creator/carousel_reviewer.py:2774` |
| 32 | **20** | Python | `_apify_yt_whisper` | `scripts/research/transcription.py:264` |
| 33 | **19** | Python | `main` | `scripts/4am_agent/main.py:50` |
| 34 | **19** | Python | `build_mom_insight` | `scripts/ads_dashboard.py:359` |
| 35 | **19** | Python | `_check_provenance` | `scripts/content_creator/carousel_reviewer.py:1254` |
| 36 | **19** | Python | `plan_carousel_slides` | `scripts/content_creator/opc_template_chooser.py:823` |
| 37 | **19** | JavaScript/TypeScript | `Arrow function` | `scripts/research.js:506` |
| 38 | **18** | JavaScript/TypeScript | `Async function 'autoApproveIdeasInSheet'` | `scripts/blog-generator.js:103` |
| 39 | **18** | JavaScript/TypeScript | `Function 'buildSheetData'` | `scripts/blog-generator.js:258` |
| 40 | **18** | Python | `download_audio` | `scripts/capture/capture_pipeline.py:1011` |
| 41 | **18** | Python | `_nb2` | `scripts/content_creator/image_providers.py:422` |
| 42 | **18** | Python | `tier_giphy` | `scripts/content_creator/motion_sources.py:790` |
| 43 | **18** | Python | `score_topic` | `scripts/content_creator/topic_picker.py:262` |
| 44 | **18** | Python | `pick_topics` | `scripts/content_creator/topic_picker.py:333` |
| 45 | **18** | Python | `main` | `scripts/daily_content_processor.py:396` |
| 46 | **18** | Python | `scrape_youtube` | `scripts/inspiration_scraper_cloud.py:373` |
| 47 | **17** | JavaScript/TypeScript | `Async function 'generatePost'` | `scripts/blog-generator.js:316` |
| 48 | **17** | Python | `save_to_content_hub` | `scripts/capture/capture_pipeline.py:3531` |
| 49 | **17** | Python | `generate_carousel_content` | `scripts/content_creator/carousel_builder.py:1413` |
| 50 | **17** | Python | `fetch_clips` | `scripts/content_creator/carousel_builder.py:4360` |
| 51 | **17** | Python | `visual_audit` | `scripts/content_creator/carousel_builder.py:8062` |
| 52 | **17** | Python | `main` | `scripts/content_creator/opc_proof_post.py:1378` |
| 53 | **17** | Python | `_tolerant_json_loads` | `scripts/self_heal/orchestrator.py:734` |
| 54 | **17** | Python | `_try_apify_youtube_audio` | `scripts/youtube_research.py:223` |
| 55 | **16** | JavaScript/TypeScript | `Async arrow function` | `scripts/blog-generator.js:628` |
| 56 | **16** | Python | `screenshot_article` | `scripts/capture/article_screenshot.py:92` |
| 57 | **16** | Python | `_try_yt_dlp_slides` | `scripts/capture/capture_pipeline.py:849` |
| 58 | **16** | Python | `main` | `scripts/content_creator/carousel_reviewer.py:2922` |
| 59 | **16** | Python | `_validate_media_images` | `scripts/content_creator/main.py:264` |
| 60 | **16** | Python | `_enforce_news_visual_targets` | `scripts/content_creator/main.py:649` |
| 61 | **16** | Python | `match_opc_photo_candidates` | `scripts/content_creator/photo_matcher.py:242` |
| 62 | **15** | Python | `main` | `scripts/build_carousel_cloud.py:1128` |
| 63 | **15** | Python | `preflight_check` | `scripts/capture/capture_pipeline.py:2658` |
| 64 | **15** | Python | `_web_research` | `scripts/content_creator/carousel_builder.py:1231` |
| 65 | **15** | Python | `build_motion_html` | `scripts/content_creator/carousel_builder.py:4462` |
| 66 | **15** | Python | `_check_image_relevance_drive` | `scripts/content_creator/carousel_reviewer.py:1462` |
| 67 | **15** | Python | `tier_clip_collections` | `scripts/content_creator/motion_sources.py:225` |
| 68 | **15** | Python | `_trim_to_relevant_window` | `scripts/content_creator/motion_sources.py:900` |
| 69 | **15** | Python | `main` | `scripts/content_creator/opc_template_chooser.py:1000` |
| 70 | **15** | Python | `describe_image` | `scripts/photo_catalog_cloud.py:168` |
| 71 | **15** | Python | `_ig_via_apify` | `scripts/research/candidate_collectors.py:494` |
| 72 | **15** | Python | `pick_task` | `scripts/self_heal/orchestrator.py:325` |
| 73 | **14** | Python | `_autonomous_solve` | `scripts/4am_agent/self_healer.py:365` |
| 74 | **14** | Python | `_try_apify_youtube_download` | `scripts/capture/capture_pipeline.py:670` |
| 75 | **14** | Python | `download_video` | `scripts/capture/capture_pipeline.py:1116` |
| 76 | **14** | Python | `run_opc` | `scripts/capture/capture_pipeline.py:3977` |
| 77 | **14** | Python | `_handle_sh104_reply` | `scripts/content_creator/approval_handler.py:541` |
| 78 | **14** | Python | `repair_opc_content` | `scripts/content_creator/carousel_builder.py:555` |
| 79 | **14** | Python | `_remove_background_with_inference_sh` | `scripts/content_creator/carousel_builder.py:3264` |
| 80 | **14** | Python | `_fetch_youtube_clip_apify` | `scripts/content_creator/carousel_builder.py:4108` |
| 81 | **14** | Python | `generate_image_suggestions` | `scripts/content_creator/carousel_builder.py:7991` |
| 82 | **14** | Python | `_flatten_text_from_content` | `scripts/content_creator/carousel_reviewer.py:970` |
| 83 | **14** | Python | `check_resource_images_local` | `scripts/content_creator/carousel_reviewer.py:1394` |
| 84 | **14** | Python | `regenerate_from_feedback` | `scripts/content_creator/image_providers.py:497` |
| 85 | **14** | Python | `extract_slide_texts` | `scripts/content_creator/prompt_builder.py:211` |
| 86 | **14** | Python | `main` | `scripts/opc_media_sorter.py:485` |
| 87 | **14** | Python | `smoke_test` | `scripts/research/_apify_smoke.py:144` |
| 88 | **14** | Python | `delete_after_run` | `scripts/research/face_match.py:181` |
| 89 | **14** | Python | `audit_pre_render` | `scripts/research/manifest_renderer.py:49` |
| 90 | **14** | Python | `_ig_audio_one_attempt` | `scripts/research/transcription.py:485` |
| 91 | **13** | Python | `fetch_reel_metadata` | `scripts/capture/capture_pipeline.py:421` |
| 92 | **13** | Python | `_fetch_carousel_slides_apify_post` | `scripts/capture/capture_pipeline.py:1567` |
| 93 | **13** | Python | `mark_audit_failed_requeue` | `scripts/content/content_auditor.py:569` |
| 94 | **13** | Python | `_derive_standalone_from_tip` | `scripts/content_creator/carousel_builder.py:1915` |
| 95 | **13** | Python | `_build_news_shared_template_html` | `scripts/content_creator/carousel_builder.py:6471` |
| 96 | **13** | Python | `_flush_alerts` | `scripts/content_creator/main.py:178` |
| 97 | **13** | Python | `find_supporting_clips` | `scripts/content_creator/motion_sources.py:1047` |
| 98 | **13** | Python | `update_status_by_niche` | `scripts/content_tracker.py:372` |
| 99 | **13** | Python | `main` | `scripts/drive_map_builder.py:404` |
| 100 | **13** | JavaScript/TypeScript | `Async function 'fetchGSCData'` | `scripts/gsc-sync.js:79` |
| 101 | **13** | JavaScript/TypeScript | `Arrow function` | `scripts/remotion/src/EvidenceCompilation.tsx:297` |
| 102 | **13** | Python | `_ig_via_username` | `scripts/research/candidate_collectors.py:439` |
| 103 | **13** | Python | `llm_json` | `scripts/research/llm_router.py:69` |
| 104 | **12** | JavaScript/TypeScript | `Async function 'callLlmText'` | `scripts/blog-generator.js:18` |
| 105 | **12** | JavaScript/TypeScript | `Function 'fixJsonControlChars'` | `scripts/blog-generator.js:476` |
| 106 | **12** | Python | `_try_pytubefix_download` | `scripts/capture/capture_pipeline.py:782` |
| 107 | **12** | Python | `update_inspiration_library` | `scripts/capture/capture_pipeline.py:2280` |
| 108 | **12** | Python | `research_from_notes` | `scripts/capture/capture_pipeline.py:3251` |
| 109 | **12** | Python | `generate_content_brief` | `scripts/capture/capture_pipeline.py:3382` |
| 110 | **12** | Python | `run_unrouted` | `scripts/capture/capture_pipeline.py:4248` |
| 111 | **12** | Python | `_startup_diagnostics` | `scripts/capture/capture_pipeline.py:4386` |
| 112 | **12** | Python | `main` | `scripts/capture/scheduled_capture_poll.py:216` |
| 113 | **12** | Python | `extract_content_brief` | `scripts/content/content_auditor.py:268` |
| 114 | **12** | Python | `call_haiku` | `scripts/content/content_auditor.py:377` |
| 115 | **12** | Python | `_apply_opc_hook_answer_contract` | `scripts/content_creator/carousel_builder.py:1680` |
| 116 | **12** | Python | `fetch_wikimedia` | `scripts/content_creator/image_providers.py:245` |
| 117 | **12** | Python | `_animate_cover_kling` | `scripts/content_creator/main.py:1350` |
| 118 | **12** | Python | `check_news_source_dual_gate` | `scripts/content_creator/news_source_dual_gate.py:142` |
| 119 | **12** | Python | `run_phase4` | `scripts/content_creator/opc_proof_post.py:1248` |
| 120 | **12** | Python | `score_templates` | `scripts/content_creator/opc_template_chooser.py:357` |
| 121 | **12** | Python | `insert_queue_row` | `scripts/content_creator/topic_picker.py:147` |
| 122 | **12** | Python | `validate_image_bytes` | `scripts/content_creator/vision_validator.py:69` |
| 123 | **12** | Python | `update_in_production` | `scripts/content_tracker.py:189` |
| 124 | **12** | Python | `update_news_in_production` | `scripts/content_tracker.py:280` |
| 125 | **12** | JavaScript/TypeScript | `Async function 'fillWithClaude'` | `scripts/fill-missing.js:172` |
| 126 | **12** | JavaScript/TypeScript | `Arrow function` | `scripts/remotion/src/NewsReel.tsx:232` |
| 127 | **12** | JavaScript/TypeScript | `Async function 'callLlmText'` | `scripts/research.js:324` |
| 128 | **12** | Python | `_ig_via_web_search` | `scripts/research/candidate_collectors.py:573` |
| 129 | **12** | Python | `_extract_ig_media_url` | `scripts/research/transcription.py:402` |
| 130 | **11** | Python | `scrape_all_targets` | `scripts/4am_agent/scraper.py:355` |
| 131 | **11** | Python | `save_scraped_to_inspiration_library` | `scripts/4am_agent/sheets_writer.py:281` |
| 132 | **11** | Python | `build_with_nano_banana_layout` | `scripts/build_carousel_cloud.py:703` |
| 133 | **11** | Python | `build_with_openai_layout` | `scripts/build_carousel_cloud.py:823` |
| 134 | **11** | Python | `llm_text` | `scripts/capture/_llm_fallback.py:116` |
| 135 | **11** | Python | `llm_vision` | `scripts/capture/_llm_fallback.py:274` |
| 136 | **11** | Python | `_try_embed_scrape` | `scripts/capture/capture_pipeline.py:1644` |
| 137 | **11** | Python | `_try_vision_fallback` | `scripts/capture/capture_pipeline.py:1747` |
| 138 | **11** | Python | `_auto_promote_capture_to_content_queue` | `scripts/capture/capture_pipeline.py:2366` |
| 139 | **11** | Python | `create_content_workspace` | `scripts/capture/capture_pipeline.py:3859` |
| 140 | **11** | Python | `detect_project` | `scripts/capture/capture_pipeline.py:4175` |
| 141 | **11** | Python | `search_youtube` | `scripts/capture/video_downloader.py:467` |
| 142 | **11** | Python | `_restore_unchanged_pngs` | `scripts/content_creator/approval_handler.py:1194` |
| 143 | **11** | Python | `_vision_accept` | `scripts/content_creator/carousel_builder.py:309` |
| 144 | **11** | Python | `_fetch_person_photo` | `scripts/content_creator/carousel_builder.py:2870` |
| 145 | **11** | Python | `_download_drive_photo` | `scripts/content_creator/carousel_builder.py:3530` |
| 146 | **11** | Python | `build_html` | `scripts/content_creator/carousel_builder.py:4943` |
| 147 | **11** | Python | `_rerender_and_upload` | `scripts/content_creator/carousel_reviewer.py:738` |
| 148 | **11** | Python | `score_storytelling` | `scripts/content_creator/carousel_reviewer.py:2049` |
| 149 | **11** | Python | `_check_bundle_slide_plan` | `scripts/content_creator/carousel_reviewer.py:2350` |
| 150 | **11** | Python | `render_motion_remotion` | `scripts/content_creator/main.py:1013` |
| 151 | **11** | Python | `render_carousel_reel_remotion` | `scripts/content_creator/main.py:1108` |
| 152 | **11** | Python | `run_motion_only` | `scripts/content_creator/main.py:2604` |
| 153 | **11** | Python | `tier_apify_youtube` | `scripts/content_creator/motion_sources.py:441` |
| 154 | **11** | Python | `tier_archive_org` | `scripts/content_creator/motion_sources.py:651` |
| 155 | **11** | Python | `queue_contains` | `scripts/content_creator/topic_picker.py:100` |
| 156 | **11** | Python | `generate_content` | `scripts/content_queue.py:172` |
| 157 | **11** | Python | `generate_ideas_from_catalog` | `scripts/photo_catalog_cloud.py:354` |
| 158 | **11** | Python | `main` | `scripts/process_approved_cloud.py:70` |
| 159 | **11** | JavaScript/TypeScript | `Arrow function` | `scripts/remotion/export_slides.js:61` |
| 160 | **11** | JavaScript/TypeScript | `Async function 'fetchNews'` | `scripts/research.js:138` |
| 161 | **11** | JavaScript/TypeScript | `Arrow function` | `scripts/research.js:573` |
| 162 | **11** | Python | `_item_has_video_media` | `scripts/research/candidate_collectors.py:267` |
| 163 | **11** | Python | `_tt_via_apify` | `scripts/research/candidate_collectors.py:946` |
| 164 | **11** | Python | `_write_clip_collections` | `scripts/research/person_evidence_runner.py:370` |
| 165 | **11** | Python | `_update_inspiration_library` | `scripts/research/person_evidence_runner.py:528` |
| 166 | **11** | Python | `_ytdlp_whisper_fallback` | `scripts/youtube_research.py:150` |

## Falsifiability check

A deliberately over-threshold throwaway function was added, the relevant command
reported it as a new violation, and the throwaway file was then removed. Existing
findings also keep the baseline command red; CI must therefore compare against this
saved inventory rather than treating today's full-tree exit code as a clean/dirty gate.

## Explicitly deferred

- No source refactor: baseline-only scope.
- No blanket CI failure on the full-tree command: it would block every change because
  this baseline intentionally records pre-existing debt. A differential no-regression
  checker is the next enforcement module.
- Branch decision tables and branch-enumerating fixtures are debt work, prioritized
  from the top of this list and any safety-critical path.
- Ruff also reports one malformed `# noqa` directive in
  `scripts/capture/capture_pipeline.py:1841`; it is not a C901 finding and remains a
  separate cleanup task rather than being mixed into this baseline-only change.

# DATASET_MANIFEST.md Template — Content Creator V2

Use this template after the Apple Photos/job-site index and Package 0 are reconciled.

Do not commit private media files, thumbnails, GPS exports, Apple Photos caches, or personal embeddings to GitHub.

## Purpose

Define the first controlled test set for Content Creator V2 so we can measure whether clip search and post creation are actually improving Priscila's workflow.

## Dataset rules

- Use 20–40 approved OPC clips/photos for the first MVP test.
- Prefer existing job-site index references over raw file copies.
- Original files stay in Apple Photos/Drive/local approved folders.
- GitHub stores only manifest metadata that is safe to store.
- Do not include client-sensitive addresses publicly if repo visibility is public.
- Use stable local aliases like SITE-001, SITE-002 when needed.

## Source buckets

| Bucket | Target count | Why |
| --- | --- | --- |
| Before footage | 3–5 | Tests before/after storytelling |
| In-progress footage | 5–10 | Tests project progress episodes |
| Finished footage | 3–5 | Tests reveal/final result |
| Talking-head Mike/Priscila | 2–5 | Tests Descript/Gling/FFmpeg/talking-head cleanup |
| Exterior/site walkaround | 3–5 | Tests construction b-roll search |
| Tools/materials/workers | 3–5 | Tests object/action retrieval |
| Weak/low-light/shaky clips | 2–3 | Tests quality ranking and rejection |
| Duplicate/near-duplicate clips | 2–3 | Tests duplicate penalty |

## Manifest fields

| Field | Description |
| --- | --- |
| asset_alias | Safe ID, e.g. OPC-TEST-001 |
| source_system | Apple Photos, Drive, local export, Mike phone, etc. |
| safe_site_alias | SITE-001 etc.; avoid sensitive address in public repo |
| captured_date | Date if safe to store |
| media_kind | video/photo |
| orientation | vertical/horizontal/square/unknown |
| duration_seconds | For videos |
| expected_visuals | What a human sees |
| expected_audio | Speech/silence/noisy/music |
| useful_for | progress, before/after, talking head, b-roll, proof, etc. |
| privacy_level | public-safe, internal-only, sensitive |
| local_reference | Private path or Photos identifier; do not commit if sensitive |
| expected_queries | Queries that should find it |
| should_not_match | Queries that should not rank it highly |
| notes | Human notes |

## Example safe row

| asset_alias | source_system | safe_site_alias | media_kind | orientation | expected_visuals | useful_for | expected_queries |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OPC-TEST-001 | Apple Photos | SITE-003 | video | vertical | worker using power tool near unfinished wall | b-roll/process | worker using power tools; unfinished wall; renovation progress |

## Acceptance query set

Use these first:

- Mike inspecting a wall
- concrete being poured
- unfinished kitchen renovation
- before demolition
- worker using power tools
- exterior addition under construction
- project before and after
- job site walkaround
- finished remodel detail
- messy construction site

## Human selection step

Priscila or the content operator should pick the first dataset from clips that are safe to use. If unavailable, use synthetic or non-sensitive footage first.

## Link to Apple Photos index

Record where the private Apple Photos/job-site index lives locally or in Drive, but do not commit the raw GPS/media data to GitHub.

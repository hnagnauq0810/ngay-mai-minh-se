# Editorial & Historical Review Workflow

## Content ownership and control

| Workstream | Owner suggested | Gate |
|---|---|---|
| Narration/dialogue changes | Writer/editor | Language and narrative review |
| Facts, names, dates, claims | Historian/course instructor | Claim-level source verification |
| Historical photos/video/audio | Media editor/rights lead | License and provenance approval |
| Reconstructed scenes | Story team | On-screen 'Tái dựng' label |
| UI integration | Frontend engineer | Semantic labels/accessibility |
| Public release | PM/editorial owner | All gates passed |

## Editorial loop

1. Read the scene in `content/story_manifest.v1.json`.
2. Extract independent factual claims into a structured record.
3. For each claim add source ID, exact document page/paragraph/link, reviewer and review date.
4. Resolve conflicting claims through qualified source comparison. Do not silently choose one.
5. Confirm that fictional dialogue cannot be mistaken for actual spoken quotes.
6. Match media metadata to sources and permissions; display reconstruction labels.
7. Set scene status only after review and preserve diff/audit trail in Git.
8. Run structure checks and the **strict release gate**.

## Content controls

- `status` remains `draft` in the supplied 55 scenes.
- `historical_claim_ids` are intentionally empty; treat claims as **unverified for release**, even if they match the provided summary in broad terms.
- `historical_review_queue.csv`: scene-level review planning.
- `asset_requirements.csv`: storyboard needs; no historical image assets in this package.
- Template registries describe the expected production evidence.
- The supplied release validator is intentionally conservative and requires approval evidence; teams can extend it to source/claim/media integrity according to their own system.

## Possible unit of work for writers

```json
{
  "claim_id": "HIST-1945-001",
  "scene_id": "C04_S04",
  "statement": "[One atomic factual statement]",
  "source_id": "SRC-001",
  "page_or_paragraph": "[Exact location]",
  "reviewer": "[Assigned person]",
  "verification_status": "pending"
}
```

This example is a schema illustration, **not a claim that a historical fact is verified**.

## Publishing notice

The draft banner and `robots: noindex` are required until source mapping, history review, licensing and final sign-off. Afterwards, update them intentionally in source and maintain audit artifacts.

---
name: code-research
description: Researching building codes, zoning and planning constraints without fabrication. Covers verbatim quoting, editions and amendments, jurisdiction, alternative compliance routes and the check_clauses format. Use for code-research and planning-constraints tasks, and any statement about what a regulation requires.
---

# Code research

## Rules that do not bend
1. **Work only from the supplied documents.** The project supplies the code documents in force as plain text in `codes/`, with their editions in `.jap/project.json`.
   - To make that text, extract it from the official PDF (`pdftotext -layout file.pdf codes/file.txt`) or copy it from the official portal.
   - Do not answer from memory. Models produce fluent clauses that do not exist.
2. **Quote verbatim.** The quote is the evidence. A threshold inside a quote is never rounded, converted or reworded.
3. **Name the edition, the amendments and the jurisdiction.** The same clause number means different things in different editions. Local amendments and national annexes change the answer.
4. **Find the whole answer.** Every requirement has exceptions, alternative routes (performance-based or engineered solutions) and transitional provisions. List them.
5. **Escalate.** Fire, structure, accessibility and planning judgements are signed off by a qualified person. The note says who.

## The `code_notes.md` format, read by `check_clauses`
```
### Travel distance, one direction
Clause: 2.14
Edition: <code title>, 2026 edition incorporating amendment 1
Jurisdiction: <city, country>
Quote: "The maximum travel distance in one direction for an office storey shall not exceed 18 m."
Applies because: single-direction escape from the north wing of level 2
```
The checker fails any entry without Clause, Edition, Jurisdiction and a verbatim quote that appears in the supplied text.

## Planning constraints
For each designation, give:
- its source document and date;
- the datum it is measured from (ground level, a road crown, mean sea level);
- the boundary it applies to.

Common traps:
- a height measured from the wrong datum;
- a setback applied to the wrong boundary;
- a missed overlay, such as conservation, heritage, flood, airport or view corridor.

The junior sketches the envelope by hand before the agent's envelope is shown.

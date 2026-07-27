# Styleguide for LLM-Generated Content

## Vault Structure
- Level 1: Course Name
- Level 2: Topic Name
- Level 3: notes.md, exercises.md, exam_questions.md, flashcards.md

## Format Rules
- Use markdown headers (# ## ###)
- Bold for key terms: **concept**
- Bullet points for lists
- Code blocks for formulas/code: ```language```
- No inline HTML
- UTF-8 encoding required
- Use Obsidian wikilinks for cross-topic references: [[Topic Name]]

## Content Quality Standards

### Notes Clarity
- **Concept Clarity**: Explain as if for someone unfamiliar with the topic
- **Density**: Include essential information without bloat
- **Hierarchical Organization**: Big idea → supporting details → examples
- **Retrievability**: Content should be findable and scannable

## For Each Skill

### Grill-Notes (Comprehension Questions)
- Format: Q&A blocks with clear separation
- Test understanding, not just recall
- Include range of difficulty levels (easy, medium, hard)
- Answers should require synthesizing multiple concepts
- Example format:
```
## Question 1 [Easy]
**Q**: [Question text]
**A**: [Answer with reasoning]
```

### Lecture-Enhance (Audio Transcription Enhancement)
- Extract high-density statements (facts, definitions, key relationships)
- Ignore filler and repetition
- Link new content to existing notes with [[wikilinks]]
- Preserve original note structure when adding
- Format: Append to existing notes.md, clearly marked as [FROM LECTURE]

### Slides-Enhance (Slide + Notes Comparison)
- Add visual concepts that text notes miss
- Fill gaps between your notes and slide content
- Flag contradictions or updates to earlier notes using Obsidian callouts:
  `> [!CAUTION]` for contradictions, `> [!INFO]` for updates/clarifications
- Preserve existing note structure

### Review-Notes (Exam Preparation)
- Vary question formats: definition, application, synthesis
- Include difficulty level: [Easy], [Medium], [Hard]
- Include topic tags: #topic-name
- Difficulty should calibrate to user performance
- Format:
```
## Question [Difficulty] #tags
**Format**: [Multiple Choice / Short Answer / Essay]
**Q**: [Question]
**Suggested Answer**: [Answer]
```

## Flashcards Format
- Use: `Question | Answer` format
- One per line for easy parsing
- Include difficulty metadata: `[Easy/Medium/Hard] Question | Answer`

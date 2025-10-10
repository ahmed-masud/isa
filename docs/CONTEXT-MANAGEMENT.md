# Context Management System

## Operating Instructions

### Load Context Command
When user says "load X context":
1. Search `~/dev-notes/` at max depth=2 for files/directories containing 'X'
2. If found: Load and present relevant content
3. If not found: Offer to create new context directory

### Context Creation
When creating new context, determine type:
- **Person**: First/Last name pattern → `contexts/people/[name-slug]/`
- **Place**: Location reference → `contexts/places/[place-slug]/` 
- **Thing**: Technology/Product/Concept → `contexts/things/[thing-slug]/`

### Directory Structure
```
vibe-dev/
├── contexts/
│   ├── people/
│   │   └── [person-name]/
│   │       ├── README.md
│   │       ├── projects.md
│   │       └── notes.md
│   ├── places/
│   │   └── [place-name]/
│   │       ├── README.md
│   │       └── details.md
│   └── things/
│       └── [thing-name]/
│           ├── README.md
│           ├── specs.md
│           └── usage.md
```

### Context Template Structure
Each context README.md should include:
- Overview
- Profile/Details
- Context Details
- Notes
- Related items (projects, companies, technologies)
- Last Updated timestamp

## Active Contexts
- **People**:
  - Ahmed Masud (2025-10-06) - saf.ai co-founder/CEO, self-context
  - Denis Krusos (2025-10-06) - saf.ai investor, problematic/isolating
  - David Malcarney (2025-10-06) - saf.ai co-founder/partner
  - Ling Young (2025-10-06) - saf.ai co-founder/partner & Ahmed's wife
  - Maximillian Schweizer (2025-10-06) - Civitas Group LLC co-founder

## Context Relationships
**saf.ai Founding Team Crisis:**
- Core team: Ahmed Masud, David Malcarney, Ling Young
- Investor pressure: Denis Krusos creating isolation dynamics
- Personal impact: Marriage tension (Ahmed-Ling) due to business conflicts

**Civitas Group Operations:**
- Co-founders: Ahmed Masud, Maximillian Schweizer
- Email connection: ahmed.masud@civitas.one
- Business relationship parallel to saf.ai activities

## Last Updated
2025-10-06

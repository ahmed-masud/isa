# Context Management Feature Specification

## Overview
The Context Management System is a core feature of vibe-dev that allows developers to organize, track, and manage knowledge about people, places, and things relevant to their projects and business relationships.

## Use Cases

### Primary Use Case: Business Relationship Management
**Scenario**: Managing complex business relationships with investors, partners, and team members
- Track key people (investors, co-founders, team members)
- Document relationship dynamics and tensions  
- Maintain strategic context during conflicts
- Separate business and personal relationship impacts

### Secondary Use Cases
- **Technical Context**: Document APIs, services, tools, technologies
- **Project Context**: Track project history, decisions, stakeholders
- **Location Context**: Office locations, deployment regions, compliance zones

## Architecture

### Directory Structure
```
vibe-dev/
├── contexts/
│   ├── people/
│   │   ├── [person-slug]/
│   │   │   ├── README.md (main context)
│   │   │   ├── interactions.md (meeting notes, emails)
│   │   │   ├── strategy.md (approach, tactics)
│   │   │   └── timeline.md (relationship history)
│   ├── places/
│   │   └── [location-slug]/
│   │       ├── README.md
│   │       └── details.md
│   └── things/
│       └── [item-slug]/
│           ├── README.md
│           ├── specs.md
│           └── usage.md
```

### Context Types & Detection
1. **Person**: First/Last name patterns → `people/[name-slug]/`
2. **Place**: Geographic/location references → `places/[place-slug]/`
3. **Thing**: Technology/product/concept → `things/[thing-slug]/`

## CLI Interface

### Core Commands
```bash
# Load existing context
vdev load "denis krusos" context
vdev load "aws" context
vdev load "san francisco office" context

# Create new context (auto-detects type)
vdev create-context "new person name"
vdev create-context "new technology"

# List and search contexts
vdev list-contexts
vdev list-contexts --type person
vdev search-contexts "investor"
vdev search-contexts --tag "problematic"

# Update and manage
vdev update-context "denis krusos"
vdev relate-contexts "denis krusos" "david malcarney" --relationship "investor-pressure"
```

### Context Operations
```bash
# Export contexts
vdev export-context "denis krusos" --format md
vdev export-context "denis krusos" --format pdf

# Context insights
vdev analyze-relationships
vdev context-timeline "denis krusos"
vdev context-impact-analysis "saf.ai"
```

## Context Template Structure

### Person Context Template
```markdown
# [Name] - Context

## Profile
- Type: Person
- Category: [Role/Relationship]
- Company: [Company affiliation]
- Relevance: [Why important]

## Context Details
[Main description]

## Current Dynamics
- Status: [Current relationship state]
- Issues: [Active problems]
- Opportunities: [Potential positive developments]

## Strategic Approach
- Communication Style: [How to interact]
- Leverage Points: [What motivates them]
- Risks: [What to avoid]

## Timeline
[Key events chronologically]

## Related
- People: [Connected individuals]
- Projects: [Associated work]
- Issues: [Problems they're involved in]
```

### Relationship Mapping
```yaml
relationships:
  denis-krusos:
    type: investor
    status: problematic
    impact: high
    connections:
      - david-malcarney: isolation-pressure
      - ling-young: indirect-marriage-tension
      - ahmed-masud: direct-conflict
```

## Implementation Phases

### Phase 2A: CLI Integration (October 2025)
- [ ] **VD-C10** `vdev load <name> context` command
- [ ] **VD-C11** Context type auto-detection
- [ ] **VD-C12** Context creation wizard
- [ ] **VD-C13** Basic listing and search

### Phase 2B: Advanced Features (November 2025)  
- [ ] **VD-C20** Relationship mapping and visualization
- [ ] **VD-C21** Context update notifications
- [ ] **VD-C22** Timeline and history tracking
- [ ] **VD-C23** Export to multiple formats

### Phase 3: Integration & Intelligence (December 2025)
- [ ] **VD-C30** Git integration for context versioning
- [ ] **VD-C31** Context impact analysis
- [ ] **VD-C32** Automated relationship discovery
- [ ] **VD-C33** Context-aware project recommendations

## Success Metrics

### Phase 2 Targets
- [ ] 10+ contexts actively managed
- [ ] Context search working across all content
- [ ] Relationship mapping for saf.ai team dynamics
- [ ] Daily context updates during business conflicts

### Phase 3 Targets
- [ ] Context-driven decision support
- [ ] Automated relationship timeline generation
- [ ] Integration with meeting notes and communication
- [ ] Strategic planning based on context analysis

## Security & Privacy

### Sensitive Information Handling
- Context files stored locally only
- No cloud synchronization by default
- Sensitive sections clearly marked
- Export controls for confidential contexts

### Access Controls
- File-system based permissions
- Optional encryption for sensitive contexts
- Audit logging for context access/modifications
- Secure deletion of outdated sensitive data

## Current Implementation Status

### ✅ Completed (October 6, 2025)
- Context directory structure created
- Initial saf.ai team contexts populated:
  - Ahmed Masud (self-context)
  - Denis Krusos (problematic investor)
  - David Malcarney (co-founder/partner)
  - Ling Young (co-founder/wife)
- Context management documentation
- Template structure defined

### 🔄 Next Steps
1. CLI command integration
2. Context search functionality  
3. Relationship mapping visualization
4. Context update workflows

## Impact on vibe-dev Vision

The Context Management System transforms vibe-dev from a pure development tool into a comprehensive **business intelligence and relationship management system**. This positions vibe-dev as essential infrastructure for:

- **Startup founders** managing complex investor/partner relationships
- **Technical leaders** navigating organizational dynamics
- **Consultants** tracking client relationships and project context
- **Remote teams** maintaining institutional knowledge

This feature differentiates vibe-dev from traditional development tools by addressing the **human and business context** that significantly impacts technical projects.

---

*Last updated: 2025-10-06*
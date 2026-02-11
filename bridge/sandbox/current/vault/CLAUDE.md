# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an Obsidian vault - a personal knowledge management system for storing and connecting notes using markdown files. The vault uses Obsidian's bidirectional linking system to create a networked knowledge base.

## Vault Structure

- **Root Directory**: Contains markdown (.md) files representing individual notes
- **/.obsidian/**: Configuration directory (hidden) containing:
  - Core plugin settings
  - Workspace layout configuration  
  - Graph view settings
  - UI appearance preferences

## Key Obsidian Concepts

### File Organization
- Notes are stored as individual `.md` files in the vault root or subfolders
- Filenames become note titles (spaces and special characters allowed)
- No strict folder hierarchy required - links create the organization

### Linking System
- `[[Note Title]]` creates bidirectional links between notes
- `[[Note Title|Display Text]]` for custom link text
- `[[Note Title#Section]]` links to specific headings
- `![[Note Title]]` embeds content from another note

### Common Note Types
- **Daily Notes**: Timestamped journal entries (if daily-notes plugin enabled)
- **Template Notes**: Reusable note structures (if templates plugin enabled)
- **Index Notes**: Hub notes that organize topics with multiple links
- **Reference Notes**: Permanent notes for important concepts
- **Literature Notes**: Notes about external sources with citations

## Working with This Vault

### Creating Notes
- Create new `.md` files in the vault root or organized subfolders
- Use descriptive filenames that work well as link targets
- Start with clear headings and structure

### Managing Links
- When referencing existing concepts, use `[[wikilinks]]` to create connections
- Check for broken links when renaming or moving files
- Use the graph view to visualize note relationships

### Maintaining Organization
- Use tags (#tag) for categorization across note boundaries
- Create index notes for major topics with links to related notes
- Regular cleanup of orphaned notes (notes with no incoming links)

## Vault Configuration

Current setup includes:
- File explorer, global search, and quick switcher enabled
- Graph view for visualizing note connections
- Backlinks panel to see incoming connections
- Daily notes and templates functionality available
- Canvas feature for visual note organization

## Best Practices for AI Assistance

When helping with this vault:
- Preserve existing linking patterns and note structures
- Use Obsidian markdown syntax (wikilinks, callouts, etc.)
- Maintain consistent heading structures within notes
- Suggest organizational improvements based on note relationships
- Help create meaningful connections between related concepts
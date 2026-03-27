---
notion_id: abc123def456
notion_parent: "Team Documentation"
title: "Architecture Overview"
has_rich_blocks: false
last_synced: 2026-03-28T10:30:00Z
---

This document describes our system architecture.

## Components

- **API Server**: Handles all HTTP requests
- **Database**: PostgreSQL for data persistence
- **Cache**: Redis for session management

## Data Flow

1. Client sends request to API server
2. API server authenticates via Redis
3. Business logic processes request
4. Data persisted to PostgreSQL
5. Response returned to client

## Deployment

We use Docker containers orchestrated with Kubernetes.

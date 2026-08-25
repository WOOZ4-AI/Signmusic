# Song Data Schema

## Purpose

This document defines the initial internal representation used by SIGNMUSIC to store songs and their lyrical structure.

## Design principle

The system must separate:

1. Original lyrics
2. Linguistic structure
3. Semantic interpretation
4. Sign-language representation
5. Animation information

These layers must remain independent.

## Song

A song contains:

- `id`
- `title`
- `language`
- `artist`
- `sections`

## Section

A section contains:

- `id`
- `type`
- `lines`

Possible section types include:

- `intro`
- `verse`
- `pre_chorus`
- `chorus`
- `bridge`
- `outro`

## Line

A line contains:

- `id`
- `text`
- `semantic_units`

## Semantic Unit

A semantic unit represents one meaningful concept or group of concepts.

It may eventually contain:

- `text`
- `concept`
- `emotion`
- `negation`
- `time`
- `person`
- `context`

## Sign Representation

Sign-language representation is intentionally separated from the original lyric.

A future implementation may contain:

- sign identifiers
- grammatical structure
- non-manual markers
- spatial information
- hand configuration
- movement
- facial expression
- timing

## Animation

Animation information will be added in a future development phase.

Possible properties include:

- start time
- end time
- sign sequence
- body movement
- facial expression
- avatar state
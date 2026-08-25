# System Overview

## SIGNMUSIC Architecture

The system is divided into independent modules so each component can evolve without breaking the others.

### Modules

**Input Module**

Receives audio, lyrics or text from the user.

**Lyrics Module**

Stores, validates and prepares song lyrics.

**Semantic Engine**

Interprets the meaning of each sentence instead of translating word by word.

**Sign Representation Engine**

Transforms semantic information into an intermediate sign-language representation.

**Avatar Engine**

Future module responsible for generating animated signing movements.

**Synchronization Engine**

Future module responsible for aligning signs with musical timing and BPM.

### Initial architecture

Input

↓

Lyrics Processing

↓

Semantic Interpretation

↓

Intermediate Sign Representation

↓

Future Avatar Animation

### MVP scope

The first MVP includes only:

* Manual lyrics input
* Text processing
* Semantic segmentation
* Experimental sign representation structure

Audio recognition and 3D animation will be developed in later phases.

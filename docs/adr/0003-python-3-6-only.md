# 3. Python 3.7+ only

Date: 2019-02-15

## Status

Accepted

## Context

Python 2 support will be discontinued in 2020. Python 3.7 is the first version
to natively support `fromisoformat` timestamp parsing which is required here.

## Decision

We make an early decision to only support Python 3.7 and above.

## Consequences

We have a single code base targetting only one major version. We can use
f-strings such as `f"Hello {name}!"`, type annotations, and have more comfortable
timestamp parsing.

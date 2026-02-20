---
name: tdd
description: Strict TDD workflow — red, green, refactor
user_invocable: true
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
argument-hint: "<feature-or-function-description>"
---

Strict test-driven development. Never write production code without a failing test first.

## Workflow

Repeat this cycle for each piece of functionality:

### 1. Red — Write a Failing Test
- Write the smallest test that describes the next piece of behavior
- Run the test suite — confirm it **fails** and fails for the right reason
- If it passes, the behavior already exists — move to the next one

### 2. Green — Make It Pass
- Write the **minimum** production code to make the test pass
- No extra logic, no anticipated features, no "while I'm here" additions
- Run the test suite — confirm it **passes**

### 3. Refactor
- Clean up the code you just wrote (production and test)
- Remove duplication, improve names, simplify logic
- Run the test suite — confirm everything still **passes**

Then repeat from step 1 for the next behavior.

## Getting Started

1. Ask the user to describe the feature or function
2. Identify the test framework already in use (pytest, jest, go test, etc.)
3. Find where tests live in the project
4. Break the feature into small, testable behaviors
5. Start the Red-Green-Refactor cycle

## Rules

- **Never** write production code before a failing test
- **Never** write more production code than needed to pass the current test
- Run tests after **every** change — never assume they pass
- Each test should test one behavior, not one function
- Test names should read as specifications: `test_empty_cart_has_zero_total`
- If you need to refactor existing code to make it testable, write characterization tests first

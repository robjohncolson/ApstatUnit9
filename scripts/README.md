# Capstone Button Analysis & Fix Scripts

This folder contains Python scripts to analyze and fix the button labels in the index.html file's capstone section.

## The Problem

The buttons in the capstone section of index.html have incorrect unit IDs (using units 1 and 3 instead of 8) and unclear labels that don't properly express what content they link to (FRQ, MCQ Part A, or MCQ Part B).

## Scripts Overview

### 1. analyze_capstone_buttons.py

This script analyzes the capstone section of index.html to identify button labeling issues:
- Identifies hardcoded unit IDs that should be changed to unit 8
- Checks if button labels clearly indicate their destinations
- Reports all issues found with line hints

**Usage:**
```bash
python scripts/analyze_capstone_buttons.py
```

### 2. generate_capstone_buttons.py

This script generates improved button label templates that can be used in index.html:
- Provides JavaScript code templates for each quiz type 
- Shows how to correctly label buttons for FRQ, MCQ Part A, and MCQ Part B
- Generates ternary condition templates for consolidated code

**Usage:**
```bash
python scripts/generate_capstone_buttons.py
```

### 3. suggest_capstone_fixes.py

This script identifies specific code blocks that need to be replaced and suggests exact replacements:
- Finds hardcoded unit IDs and incorrect labels
- Shows the surrounding context to help locate the code
- Provides the exact replacement code needed
- Shows a diff view of the changes

**Usage:**
```bash
python scripts/suggest_capstone_fixes.py
```

### 4. find_button_locations.py

This script helps locate all the problematic code sections by line number:
- Shows exact line numbers where fixes are needed
- Groups nearby issues together for easier fixing
- Displays the surrounding context for each issue
- Makes it easy to navigate directly to problem areas in the code

**Usage:**
```bash
python scripts/find_button_locations.py
```

### 5. fix_summary.py

This script provides a comprehensive summary of all recommended fixes in one place:
- Shows the capstone quiz structure
- Lists all unit ID replacements needed
- Provides ready-to-use ternary expression replacements
- Summarizes the recommended button labels for each quiz type

**Usage:**
```bash
python scripts/fix_summary.py
```

## How to Fix the Index.html File

1. First get a comprehensive summary of all needed fixes:
   ```bash
   python scripts/fix_summary.py
   ```

2. Locate the problematic areas in the code:
   ```bash
   python scripts/find_button_locations.py
   ```

3. Run the analysis to understand the issues:
   ```bash
   python scripts/analyze_capstone_buttons.py
   ```

4. Generate suggested button templates:
   ```bash
   python scripts/generate_capstone_buttons.py
   ```

5. Get specific code replacement suggestions:
   ```bash
   python scripts/suggest_capstone_fixes.py
   ```

6. Manually make the changes to index.html based on the suggestions:
   - Replace hardcoded unit IDs (change 1, 3 to 8)
   - Update button labels to clearly indicate their content type
   - Fix ternary operator expressions with the provided templates

## Important Notes

- These scripts do not modify any files automatically - they only provide analysis and suggestions
- Always make a backup of index.html before making manual changes
- Focus on updating the quiz.quizId comparison conditions to use "8-capstone_q1", "8-capstone_q2", etc.
- Ensure button labels clearly indicate whether they link to FRQ, MCQ Part A, or MCQ Part B content 
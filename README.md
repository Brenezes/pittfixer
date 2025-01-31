# PittFixer

*PitFixer* is a Python-based tool designed to automate the correction and adjustment of events in an SQLite database. It is particularly useful for managing and optimizing data related to pits (or cavities) in surfaces, ensuring that dimensions and types are updated according to specific rules.

## Features ##

**Event Correction:**

- Automatically corrects events with in the type column and either width < X or length < X.

- Updates prof, width, and length with values specified ranges.

- Pivot table update, being adaptive.


### Type Updates:

**Converts specific event types to standardized values:**

- Renames corrosion events according to their technical profile and customer needs


### CSV Report:

**Generates a detailed CSV report (log_pitfixer.csv) with the original and updated values for each corrected event, including:**

- Original and new dimensions (prof, width, and length).

- Original and new event types.

- Axial position (posAxi).

- Comments with the original values.

- Flexible Database Input:

- Allows users to specify the SQLite database file at runtime.

- Works with any database that follows the required schema.

## Requirements ##

- Python 3.x installed.
- An SQLite database (prdb) with the catadef table and the necessary columns (id, type, prof, length, width, posAxi, comment).

## How to Run ##

1. *Clone the repository* (if applicable):
   ```bash
   git clone https://github.com/Brenezes/pitttfixer.git
   cd pitfixer

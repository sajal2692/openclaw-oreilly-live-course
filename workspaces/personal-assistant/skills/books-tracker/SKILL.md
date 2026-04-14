---
name: books-tracker
description: Manage the reading list in notes/trackers/reading.md. Add, update, complete, list books, log past reads, and view reading stats. Use when the user asks to add a book, mark a book complete, change a book's status, list books, or show reading stats.
---

# Books Tracker

Manage the reading list in a single markdown file: `notes/trackers/reading.md`.

## File Structure

`notes/trackers/reading.md` contains a markdown table:

```markdown
# Reading Tracker

| Title | Author | Status | Started | Finished | Rating | Notes |
|---|---|---|---|---|---|---|
| Designing Data-Intensive Applications | Martin Kleppmann | reading | 2026-04-05 |  |  | Ch 5 |
| The Three-Body Problem | Liu Cixin | completed | 2026-03-12 | 2026-03-28 | 9 | Worth re-read |
| Antifragile | Nassim Taleb | next_up |  |  |  |  |
| Project Hail Mary | Andy Weir | wishlist |  |  |  |  |
```

**Status values:** `reading`, `paused`, `next_up`, `backlog`, `wishlist`, `completed`, `dropped`

## Available Actions

### 1. Add a book

When the user asks to add a book ("add Project Hail Mary to my list"):

1. Determine status from intent:
   - "start reading" / "currently reading" -> `reading`
   - "next" / "up next" -> `next_up`
   - "wishlist" / "someday" -> `wishlist`
   - Default -> `backlog`
2. If the author is unknown and the user wants metadata, web-search for the title to confirm author
3. Append a new row to the table in `notes/trackers/reading.md`
4. Set `Started` to today if status is `reading`
5. Confirm: "Added: [Title] by [Author] ([status])"

### 2. Mark a book complete

When the user finishes a book:

1. Find the row for the book (fuzzy match on title)
2. Update:
   - `Status` -> `completed`
   - `Finished` -> today (or user-specified date)
   - `Rating` -> ask if they want to add a 1-10 rating
3. Confirm: "Marked complete: [Title] (rated [N]/10)"

### 3. Start a book

When the user starts reading something from the queue:

1. Find the row
2. Update `Status` -> `reading`, `Started` -> today
3. Confirm

### 4. Update status

When the user reorganizes ("pause X", "drop Y", "move Z to next"):

1. Find the row
2. Update `Status` accordingly
3. Confirm

### 5. List books

When the user wants to see their list ("what am I reading", "show my queue"):

1. Read `notes/trackers/reading.md`
2. Filter by status (or group by status if no filter)
3. Format clearly

### 6. Log a past read

When the user mentions a book they read in the past:

1. Web-search for author / genre if not provided
2. Append a row with `Status: completed`, `Finished` set to the year or date provided
3. Optionally ask for rating
4. Confirm

### 7. Show stats

When the user wants stats:

1. Read all rows
2. Compute: total completed, completed this year, by status
3. Optionally compute reading pace (books per month based on completion dates)
4. Format as a brief summary

## Notes

- Always read the file before writing to preserve external edits
- Preserve table formatting (column alignment is for humans, not required for parsing)
- If the user wants richer metadata (genre, ISBN, etc.), add columns. The format is flexible.
- For book lookup (verifying author, year, etc.), Alfred can web-search. No API key required.

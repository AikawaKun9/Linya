# Schema review: Linya

I put my ERD away, then reviewed it against my requirements and my personas, Eddie and Ms. Elena, using the six review questions.

## 1. Coverage: nothing records when a ticket finishes

> **Works well:** every requirement marked *Stores data? = Yes* in `docs/requirements.md` has a table or column. Join (FR-01) uses `visitors` and `tickets`, window numbers (FR-08) use `windows` and `tickets.window_id`, the priority lane (FR-11) uses `tickets.is_priority`, and leaving (FR-10) uses the `left` status instead of deleting the row.
>
> **Problem:** (question 1 and 3) FR-06 asks for average service time, and FR-02 promises an estimated wait. `tickets` stores when a ticket was created and when it was called, but nothing records when staff finished with it, so service time can't be worked out. My first plan was to store a guess in `services.avg_minutes` and use that for the estimate forever.
>
> **Change:** I added `tickets.finished_at` (timestamptz, empty until the ticket is served or marked no-show). Service time is then computed as `finished_at - called_at`, and `avg_minutes` becomes only a starting guess. I updated `schema.md` and the ERD.

## 2. Deletes: a mistaken ticket leaves its visitor behind

> **Works well:** every foreign key uses RESTRICT on purpose, so staff can't accidentally delete a service, window or visitor that old tickets point to. This protects the history that FR-14 needs.
>
> **Problem:** (question 5) FR-13 lets staff hard-delete a ticket made by mistake. The ticket goes, but its `visitors` row stays, with a name and maybe a student ID, and no ticket. That keeps personal data with no purpose, which goes against my Week 1 promise to collect the minimum (NFR-03).
>
> **Change:** the delete-ticket route will also delete the visitor when that visitor has no other tickets. Visitors who still have tickets are kept.

## 3. Bad data: people without an ID are not matched

> **Works well:** `student_id` is optional but checked: UNIQUE and a CHECK for the format YYYY-####, so two visitors cannot share an ID and a typo like `22-457` is refused by the database as well as by Flask.
>
> **Problem:** (questions 2 and 4) I removed email, so a visitor without a student ID has nothing that identifies them. Each time they join, a new `visitors` row is created, so for these people `visitors` is almost a copy of `tickets`. A double tap would also create two tickets for the same person, and a constraint can't catch it because the two visitors look different.
>
> **Change:** I kept the design. People who give a student ID reuse one row, which is the case where a person table helps, and the Week 3 JavaScript already disables the Get a ticket button after the first tap. I considered a rule of one active ticket per visitor per service, but it only works for people with an ID, so I left it for a later week.

## 4. Bad data: the database cannot check who deserves the priority lane

> **Works well:** `is_priority` is on `tickets`, not on `visitors`, because a student may be pregnant or injured on one visit and not the next, so the choice belongs to each visit.
>
> **Problem:** (question 4) any student can tick the priority box, and no constraint can check whether they qualify. That is a policy question, not a database one.
>
> **Change:** no schema change. The join form already says "Show your ID at the window", and the staff dashboard shows a Priority badge so staff can ask for proof. I wrote this limit in my report so it isn't mistaken for a bug.

## Other questions

- **Facts, not results (question 3):** I do not store a position or a wait time. Both are computed.
- **Types (question 6):** every moment in time is a `timestamptz`, `is_priority` is a boolean, and `status` is a short word restricted by a CHECK.
- **Columns no requirement needs:** `visitors.created_at`. I kept it because my Week 1 promise to remove old data after a set period needs a way to tell which rows are old.
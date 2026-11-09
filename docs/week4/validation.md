# Validation: three layers

The same rule is checked in three places. The browser gives fast feedback to users, Flask is the real gatekeeper, and the database is the last line of defense against any bug.

## Browser

I added `maxlength="80"` to the name field and `maxlength="9"` with a pattern to the student ID field, matching `String(80)` and `String(9)`. The form uses `novalidate` so my own messages appear, which means the server must check everything again.

## Flask (curl, skipping the form)

| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| Name, student ID and service are checked | Flask | curl POST /join with empty name, `22-457`, service 999 | HTTP/1.1 400 BAD REQUEST |
| Name is at most 80 characters | Flask | curl POST /join with a 200-character name | HTTP/1.1 400 BAD REQUEST |
| Student ID must be YYYY-#### | Flask | curl POST /join with `2022-45` | HTTP/1.1 400 BAD REQUEST |
| A switched-off service cannot be chosen | Flask | curl POST /join with the id of an inactive service | HTTP/1.1 400 BAD REQUEST |
| Staff routes change data only with POST | Flask | curl GET /staff/tickets/1/delete | HTTP/1.1 405 METHOD NOT ALLOWED |
| Service name and minutes are checked | Flask | curl POST /staff/services with empty name and 0 minutes | HTTP/1.1 302 FOUND |

## Database (psql, skipping Flask)

| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| A ticket needs a real service | Database, FOREIGN KEY | INSERT into tickets with service_id 999 | ERROR:  insert or update on table "tickets" violates foreign key constraint "tickets_service_id_fkey" |
| Status must be one of five values | Database, CHECK | UPDATE tickets SET status = 'lost' | ERROR:  new row for relation "tickets" violates check constraint "ck_tickets_status" |
| One visitor per student ID | Database, UNIQUE | INSERT a visitor with an ID already used | ERROR:  duplicate key value violates unique constraint "visitors_student_id_key" |
| Student ID format | Database, CHECK | INSERT a visitor with ID `22-457` | ERROR:  new row for relation "visitors" violates check constraint "ck_visitors_student_id" |
| A visitor needs a name | Database, NOT NULL | INSERT a visitor with a NULL name | ERROR:  null value in column "name" of relation "visitors" violates not-null constraint |
| A service name is unique | Database, UNIQUE | INSERT a service that already exists | ERROR:  duplicate key value violates unique constraint "services_name_key" |
| Minutes must be above 0 | Database, CHECK | INSERT a service with 0 minutes | ERROR:  new row for relation "services" violates check constraint "ck_services_avg_minutes" |
| A service with tickets cannot be deleted | Database, RESTRICT | DELETE a service that has tickets | ERROR:  update or delete on table "services" violates foreign key constraint "tickets_service_id_fkey" on table "tickets" |

## Defaults filled in by the database

I inserted a ticket with only a visitor and a service. PostgreSQL filled in: status 'waiting', is_priority 'f' and created_at '2026-11-09 03:33:34.38248+00'.

## No SQL in f-strings

`git grep` for f-strings containing SELECT, INSERT, UPDATE or DELETE printed nothing. All queries use SQLAlchemy, which sends values separately from the SQL.

## Most useful PostgreSQL error

`ERROR: new row for relation "tickets" violates check constraint "ck_tickets_status"`

This was the most useful because it names the exact rule that was broken. It showed me that even if my Flask code has a bug and sends a wrong status, the database refuses it, so a typo like `lost` can never be saved.
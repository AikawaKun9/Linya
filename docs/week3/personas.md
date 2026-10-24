# Personas: Linya (Campus Registrar)

Both personas come from my observation at the registrar while requesting my own TOR, from interviews with students waiting there, and from a short conversation with registrar staff.

---

## Eddie, the student waiting

> "Unsay purpose sa mga lingkoranan kung magbarog raman diay japon ta para molinya."
> ("What's the point of the chairs if we end up standing in line anyway?") *(Observation)*

| | |
| --- | --- |
| **Photo or sketch** | None |
| **Age, role and background** | 21, graduating student who needs his TOR for job applications and clearance |
| **Goals** | Get his TOR without missing class; sit down on the benches instead of standing while waiting for his number, know when his turn is coming |
| **Frustrations** | Standing in line for hours although benches are free *(observation)*;  Not knowing how many people are ahead, uncertainty about when his turn is coming *(observation)*; extra waiting when several procedures are needed *(document review)* |
| **Devices and context** | Low-end Android phone, limited mobile data, weak campus Wi-Fi at times, stuck in a noisy crowded hallway outside the registrar |
| **Tech comfort** | High: uses mobile apps daily for payments and school |
| **Accessibility needs** | Light pages for slow data; large, high-contrast queue number readable at arm's length; simple wording in English or Filipino |

### Scenario

During enrollment week, Eddie arrives at the registrar and sees a long line. He scans the QR code posted at the office, enters his name and student ID, and chooses "Transcript of Records". His phone shows ticket #14 and "3 people ahead". He sits on a bench and checks his phone now and then. Later the screen changes to "Called: go to Window 1", and he walks over.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| Join the queue for the TOR | Join | FR-01 |
| Check number and people ahead | My place | FR-02 |
| See the status change without refreshing | My place | FR-04 |
| See which window to go to | My place | FR-08 ★ |
| Leave the queue if called away | My place | FR-10 |

### What this means for my interface

1. Because Eddie sits on a bench and only glances at his phone, his ticket number and "people ahead" must be the biggest things on My place.
2. Because he is told "you will be called" with no updates, the status must change by itself and say which window to go to.
3. Because he has limited data and weak Wi-Fi, pages must be light, with no large images.
4. Because he may be pulled away suddenly, leaving the queue must be one clear button.

---

## Ms. Elena, the registrar counter staff

> "No direct staff quote yet. This persona is based on my observation and what students told me."

| | |
| --- | --- |
| **Photo or sketch** | None |
| **Age, role and background** | Registrar staff who processes TOR requests and other transactions at the counter |
| **Goals** | Call students in order; handle many requests during enrollment; keep service orderly |
| **Frustrations** | High volume of students during enrollment, with several requests to manage at once *(observation)*; students asking staff how long the wait will be *(observation)* |
| **Devices and context** | Desktop computer at the counter, using it between handling requests † |
| **Tech comfort** | Medium: comfortable with browsers and basic school systems † |
| **Accessibility needs** | Clear button labels and strong contrast for fast clicking under pressure |

### Scenario

Ms. Elena finishes processing a TOR and turns to her screen. She opens the Linya dashboard, filters by "Transcript of Records", and clicks "Call next", entering Window 1. Ticket #14 changes to "Called" and she sees the student stand up from the bench. After handing over the document, she clicks "Serve" on ticket #14 and moves on without answering "am I next?" at the counter.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| View the waiting list by service | Staff | FR-09 |
| Call the next student | Staff | FR-03 |
| Mark a ticket served or no-show | Staff | FR-03 |
| Set the window number when calling | Staff | FR-08 ★ |

### What this means for my interface

1. Because staff handle one kind of request at a time, the service filter must be at the top of the dashboard.
2. Because they work fast under pressure, "Call next" must be the largest button, and every action must be one click.
3. Because they scan many rows quickly, each button must name its ticket ("Serve #14"), with a matching aria-label.
4. Because the registrar must verify students, the join form must require a valid Student ID.
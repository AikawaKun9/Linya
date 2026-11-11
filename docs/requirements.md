# Linya requirements

**Setting:** Campus registrar, during enrollment weeks and Transcript of Records (TOR) requests
**People who wait:** Students, such as Eddie (docs/week3/personas.md)
**People who serve:** Registrar counter staff, such as Ms. Elena (docs/week3/personas.md)

**Problem statement:** A student who needs a document from the registrar needs a way to know their place in line and when to go to a window, because without it they stand near the counter for hours even when seats are free.

## Functional requirements

| ID | Requirement | Priority | Stores data? | Status |
| --- | --- | --- | --- | --- |
| FR-01 | A student can join the queue for a transaction type (by scanning a QR code at the office) with a name or nickname and an optional student ID. | Must | Yes | Partly built (Week 3 web form; QR code later) |
| FR-02 | A student can see their number, status, people ahead and, later, an estimated wait. | Must | Yes | Partly built (position yes; estimated wait later) |
| FR-03 | A staff member can call the next ticket and mark a ticket served or no-show. | Must | Yes | Built (Week 3) |
| FR-04 | A student gets an alert when their turn is near. | Should | Yes | Partly built (page updates itself when called) |
| FR-05 ★ | A staff member can issue a ticket for a student without a phone or data. | Should | Yes | Later |
| FR-06 | A registrar head can see peak hours and average service time. | Could | Yes | Later |
| FR-07 | A student can join the queue remotely before arriving. | Won't (this semester) | Yes | Dropped |
| FR-08 ★ | A staff member assigns a window when calling, and the student sees "Go to Window N". | Should | Yes | Built (Week 3) |
| FR-09 | A staff member can filter the waiting list by service. | Must | No | Built (Week 3) |
| FR-10 | A student can leave the queue while waiting. | Should | Yes | Built (Week 3) |
| FR-11 ★ | A PWD, senior citizen or pregnant student can join a priority lane that is called first. | Should | Yes | Built (Week 3) |
| FR-12 | A staff member can add, rename, switch off and delete a service. | Must | Yes | Built (Week 4)|
| FR-13 | A staff member can delete a ticket created by mistake. | Should | Yes | Built (Week 4) |

## Non-functional requirements

| ID | Requirement | Category | Priority |
| --- | --- | --- | --- |
| NFR-01 | The student's position updates within 5 seconds of staff pressing Call next, and the page loads within 3 seconds on 3G. | Performance | Must |
| NFR-02 | A first-time student can join the queue in under 1 minute, in no more than 3 screens, without help. | Usability | Must |
| NFR-03 | Only the minimum data is collected (RA 10173), and students see only their own ticket. Staff login arrives in Week 11. | Privacy | Must |
| NFR-04 | The layout works on Chrome for Android and desktop from 360 px width. | Compatibility | Must |
| NFR-05 | No ticket is lost when Flask or the database restarts. | Reliability | Must |
| NFR-06 | Two people can never get the same ticket number, even if they join at the same moment. | Data integrity | Must |
| NFR-07 | No password or secret key is stored in the repository. | Security | Must |

## MVP

FR-01, FR-02, FR-03, FR-08, FR-09, FR-10, FR-11 and FR-12, with NFR-05 and NFR-06. [In one or two sentences, say why this is the smallest version that still solves the problem.]

## Out of scope this semester

- Remote joining (FR-07), because the registrar wants students physically present so the line stays fair.
- SMS notifications, because of cost.

## Check with a real person

| Who (role only) | What they said | What I changed |
| --- | --- | --- |
| Jen | Confused by the window panel in the staff dashboard | Added indicator that the window panel is about where students will go to  |
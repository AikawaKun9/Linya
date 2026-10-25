# Self-review: Linya wireframes

I reviewed each screen at phone and laptop width against my personas, Eddie (student waiting) and Ms. Elena (registrar staff), and their "Because..., my interface must..." rules.

## Join Frames, Mobile and Laptop

> **Works well:** Every field has a visible label above it, and "Get a ticket" is a large, full-width button, so Eddie can tap it with one thumb in a crowded hallway. This follows my rule that he uses a phone while standing or sitting in the hallway.
>
> **Problem:** The form asks for more than Eddie needs. Email is never used by the app, and Student ID looks required with no hint about its format. This slows a quick phone task and goes against my Week 1 promise to collect only the minimum data (RA 10173, NFR-03). Service, the one thing Eddie came for, is the fourth field. This breaks match between the system and the real world, and error prevention (nothing shows the YYYY-#### format).
>
> **Change:** I removed Email, made Student ID optional with the hint "your number (YYYY-####)", moved Service to the first field, and added "Show your ID at the window" under the priority lane.

## Queue Frames,, Mobile and Laptop

> **Works well:** The ticket number is huge, and the status badge says WAITING in words, followed by "3 people ahead" in large text. Eddie only glances at his phone from a bench, so this follows my rule that number and position must be the biggest things on screen.
>
> **Problem:** "Leave the queue" sits right under the card at the same size as a main action. One careless tap on a crowded phone would make Eddie lose his place after hours of waiting (error prevention).
>
> **Change:** I made it a red outline button so it looks different from safe actions, and added a confirmation: "Leave the queue? You will lose your place." I also noticed that the frames show only people ahead, with no estimated wait, although my Week 1 requirement FR-02 promises one. I kept it out of this week because a good estimate needs real service times, which I can store once the data moves to a database in Week 4.

## Staff Frames,, Mobile and Laptop

> **Works well:** "Call next" is a large dark button at the top, next to the service filter and window number, so Ms. Elena's most frequent action needs no scrolling or searching. Each row button names its ticket ("Serve #12"). This follows my rules that she works fast and handles one service at a time.
>
> **Problem:** Each waiting row has its own "Call #14" button next to the main "Call next". That gives two ways to do the same thing and lets staff call students out of order, against the first-come, priority-first fairness the registrar wants (consistency and error prevention). The table caption also says "Transcript of Records" while the filter says "All services".
>
> **Change:** I removed the per-row Call buttons, so tickets are called only through Call next, which picks the next in order with priority-lane tickets first. I made Serve a solid green button and No-show a red outline so a rushed click is less likely to remove a student. I added a Window column and a Priority badge, and made the caption follow the filter. On the phone, the Actions column still needs sideways scrolling. I kept that on purpose: Ms. Elena works on a desktop PC, so the phone frame only has to avoid breaking the page, and Call next stays above the table.

## Wireframe status

- The wireframes in `wireframes/` show my first design. I made the changes above directly in the build, so the final screens are in the screenshots in my report.
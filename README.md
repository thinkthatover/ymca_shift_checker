# Introduction
YMCACM_Scheduler.py is a program built to help management at the Leominster YMCA keep track of busy upcoming shifts so they can assign extra staff accordingly. When an upcoming shift has a "busy" block, an email is sent to the manager with the day, shift, blocks and number of attendees in the "busy" block.

## Project Overview
The program runs every 15 minutes, calling the Virtuagym API for all events (scheduled exercise blocks) occuring in the next 48 hours as of that moment. The results are filtered by the type of event (ie: excluding cycling, zumba classes) and number of attendees per event. event blocks whose number of attendees is 8 or more are split up by their corresponding shifts and checked against the hash table `y_schedule`. 

`y_schedule` represents a week's days and shifts, and serves to keep track of shifts that already have two people scheduled (ie: Weekday 9-11:30AM shifts), and the number of full blocks in upcoming shifts. Check `default_scheduler()` for more details.

If the number of full blocks in a shift is greater than `y_schedule`'s, an email is sent according to the details in the introduction, and `y_schedule` is updated with the number of full blocks in that shift (preventing future emails being sent given the same number of full blocks in a shift).


This project was tested in python 3.8.0

# Dependencies:
requests - pip install requests

# Future Improvements (in order of difficulty implementing)
- include all blocks for a shift in update email
- send email if a double scheduled block won't be busy within a certain period of time before the shift begins.
- make program more user-friendly (.exe, GUI interface to set parameters such as double scheduled shifts, attendee threshold to send email, etc.)
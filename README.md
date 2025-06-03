# 🎬 Daily Flash Gross Reporter

A simple Python script that automates daily sales reporting for a small two-screen movie theater. This script fetches ticket sales data from the Square API and emails a summary report of daily grosses every night.

## Features

- Connects to the Square API to fetch sales data for the current day.
- Summarizes sales by item, focusing on ticket sales.
- Sends two email reports:
  - **Owner Summary**: Detailed breakdown of all items sold.
  - **Ticket Report**: Summary of ticket-specific sales only.
- Automatically filters relevant ticket items based on a configured category.

## Requirements

- Python 3.9+
- A Square account with API access
- SMTP credentials for sending email
- `.env` file with necessary environment variables

## Installation

1. Clone the repository:
   `git clone https://github.com/yourusername/flash-gross-reporter.git`
   `cd flash-gross-reporter`
2. Install dependencies
  `pip install -r requirements.txt`
3. Create a .env file with the following environment variables:
```
  SQUARE_ACCESS_TOKEN=your_square_access_token
  SQUARE_LOCATION_ID=your_location_id
  SQUARE_TICKET_CAT=category_id_for_ticket_items
  
  EMAIL_USERNAME=your_email@example.com
  EMAIL_PASSWORD=your_email_password
  SMTP_SERVER=smtp.example.com
  SMTP_PORT=587
  
  OWNER_EMAIL=owner@example.com
  REPORT_EMAIL=report@example.com
  CC_EMAIL=cc@example.com
  TICKET_REPORT_SUBJECT="Daily Ticket Sales Report"
```
4. Run the script manually (or set it up with a cron job for automation):
  `python flash_gross_reporter.py`


### Customization
You can modify the email subjects, format, or filtering logic by editing the respective functions:

- send_email() – Email transport and setup
- summarize_line_items() – Sales aggregation
- filter_ticket_items() – Filtering by ticket category
- email_owner_info() – Owner report format
- master_ticket_report() – Ticket report format

### Deployment Suggestion
To automate nightly runs, use a task scheduler like cron (Linux/macOS) or Task Scheduler (Windows). Example cron entry for 11:30 PM daily:
`30 23 * * * /usr/bin/python3 /path/to/flash_gross_reporter.py`




# Project Plan: Telegram English Vocabulary Bot

## 1. Objective

To create a completely free, automated Telegram bot that sends daily English vocabulary questions to two users, sourcing the content from a Google Sheet.

## 2. Core Features

- **Daily Questions:** The bot will send a new set of questions every morning at 7:00 AM.
- **Content Source:** All words, meanings, synonyms, and antonyms will be read directly from a user-provided Google Sheet.
- **Question Variety:** For each word, the bot will randomly generate one of the following question types:
    - **Meaning (MCQ):** "What is the meaning of 'Arduous'?"
    - **Synonyms (MCQ):** "What are the synonyms of 'Miserable'?"
    - **Antonyms (MCQ):** "What are the antonyms of 'Miserable'?"
    - **Unscramble:** "Unscramble the letters to find the correct spelling: 'Icmtaumlae'"
- **Interactive Polls:** The MCQ questions will be sent as Telegram "Quiz" Polls, providing instant feedback when an answer is selected.
- **Sequential Learning:** The bot will go through the words in the Google Sheet sequentially, sending 3 new words each day.
- **Completion Message:** Once all words from the sheet have been used, the bot will send a final message: "No more questions, we are done!".

## 3. Technology Stack (The "Free for Life" Approach)

- **Programming Language:** **Python 3**
  - *Reason:* It is perfect for scripting, has excellent libraries for web requests, and is easy to read and maintain.

- **Data Source:** **Google Sheets API**
  - *Reason:* Allows the bot to read data directly from your Google Sheet for free, making it easy for you to add or edit words anytime without changing any code.

- **Hosting & Automation:** **GitHub Actions**
  - *Reason:* This is the key to the "zero cost" model. Instead of a continuously running server, we use a free GitHub service to run our Python script on a schedule (daily at 7:00 AM).

- **Telegram Integration:** **Python `requests` library**
  - *Reason:* A simple and reliable way to send messages and polls to the Telegram Bot API.

## 4. Workflow

1.  **Scheduled Trigger:** At 7:00 AM daily, a GitHub Actions workflow automatically starts.
2.  **Run Script:** The workflow runs our main Python script.
3.  **Fetch Data:** The script authenticates with the Google Sheets API and reads the next 3 words from your spreadsheet.
4.  **Generate Questions:** It randomly generates the interactive questions for each word as described above.
5.  **Send Messages:** The script sends the questions to the specified Telegram chat IDs using your bot's API token.
6.  **Update Progress:** The script updates a small text file in the repository to remember which words it has already sent, so it knows where to start the next day.
7.  **Shutdown:** The script finishes, and the GitHub Actions runner shuts down. The entire process uses only a minute or two of free computing time.

## 5. How to Add More Words

This project is designed so that you can add new vocabulary words easily without ever needing to modify the code.

1.  **Open your Google Sheet.**
2.  **Add New Rows:** Simply add new words to the rows at the end of your list. Ensure you maintain the same format for the columns: `Word`, `Meaning`, `Synonyms`, `Antonyms`, `Example Sentence`.
3.  **Save the Sheet:** The bot will automatically detect the new words the next time it runs after its current list is exhausted. No further action is needed.

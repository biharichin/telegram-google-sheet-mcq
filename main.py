import gspread
import requests
import random
import os
import json

# --- Configuration ---
# Secrets are loaded from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")

CHAT_IDS = ["7695772994"]
GOOGLE_SHEET_NAME = "english vocab"
PROGRESS_FILE = "progress.txt"

# --- Google Sheets Setup ---
def get_sheet():
    """Connects to Google Sheets and returns the worksheet."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Load credentials from environment variable
        creds_json = json.loads(GOOGLE_CREDENTIALS_JSON)
        client = gspread.service_account_from_dict(creds_json, scopes=scope)
        
        sheet = client.open(GOOGLE_SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        import traceback
        print(f"Error connecting to Google Sheets. The raw error is: {e}")
        print("--- Full Traceback --- ")
        traceback.print_exc()
        print("----------------------")
        return None

# --- Progress Tracking ---
def get_progress():
    """Gets the index of the last word sent."""
    if not os.path.exists(PROGRESS_FILE):
        return 0
    with open(PROGRESS_FILE, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def save_progress(index):
    """Saves the index of the last word sent."""
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(index))

# --- Telegram Functions ---
def send_message(chat_id, text):
    """Sends a text message to a Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Message sent to {chat_id}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to {chat_id}: {e}")

def send_poll(chat_id, question, options, correct_option_id):
    """Sends a quiz poll to a Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPoll"
    payload = {
        "chat_id": chat_id,
        "question": question,
        "options": options,
        "type": "quiz",
        "correct_option_id": correct_option_id,
        "is_anonymous": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Poll sent to {chat_id}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send poll to {chat_id}: {e}")

# --- Question Generation ---
def send_single_question(word_data, all_words):
    """Generates a random question and sends it to all chat IDs."""
    question_type = random.choice(["meaning", "synonym", "antonym", "unscramble"])
    word = word_data["Word"]

    if question_type in ["meaning", "synonym", "antonym"]:
        if question_type == "meaning":
            question = f"What is the meaning of \"{word}\"?"
            correct_answer = word_data["Meaning"]
            distractor_key = "Meaning"
        elif question_type == "synonym":
            question = f"What is a synonym for \"{word}\"?"
            correct_answer = word_data["Synonyms"]
            distractor_key = "Synonyms"
        else: # antonym
            question = f"What is an antonym for \"{word}\"?"
            correct_answer = word_data["Antonyms"]
            distractor_key = "Antonyms"

        # Get 3 wrong answers
        distractors = []
        other_words = [w for w in all_words if w["Word"] != word]
        while len(distractors) < 3 and len(other_words) > 0:
            d = random.choice(other_words)
            if d[distractor_key] != correct_answer and d[distractor_key] not in distractors:
                distractors.append(d[distractor_key])
            other_words.remove(d)
        
        if len(distractors) < 3:
            print(f"Warning: Could not find enough distractors for {word}")
            return

        options = distractors + [correct_answer]
        random.shuffle(options)
        correct_option_id = options.index(correct_answer)

        for chat_id in CHAT_IDS:
            send_poll(chat_id, question, options, correct_option_id)

    elif question_type == "unscramble":
        scrambled_word = "".join(random.sample(word, len(word)))
        question = f"Unscramble the letters to find the word: {scrambled_word}"
        for chat_id in CHAT_IDS:
            send_message(chat_id, question)

# --- Main Execution ---
if __name__ == "__main__":
    worksheet = get_sheet()
    if not worksheet:
        print("Exiting: Could not connect to Google Sheet.")
        exit()

    all_words = worksheet.get_all_records()
    if not all_words:
        print("Exiting: No words found in the sheet.")
        exit()

    start_index = get_progress()
    
    if start_index >= len(all_words):
        print("All questions have been sent.")
        for chat_id in CHAT_IDS:
            send_message(chat_id, "No more questions, we are done!")
        exit()

    end_index = min(start_index + 3, len(all_words))
    words_to_send = all_words[start_index:end_index]

    print(f"Sending words from index {start_index} to {end_index-1}")

    # Send a test message first
    for chat_id in CHAT_IDS:
        send_message(chat_id, "Bot is starting... preparing questions.")

    for word_data in words_to_send:
        for _ in range(3): # Send 3 questions per word
            send_single_question(word_data, all_words)
    
    save_progress(end_index)
    print("Script finished.")

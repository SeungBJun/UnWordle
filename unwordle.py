from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import json
import time
import keyboard

# Initialize Selenium
ser = Service("C:\\Program Files (x86)\chromedriver.exe")
op = webdriver.ChromeOptions()
browser = webdriver.Chrome(service=ser, options=op)

# Load JSON file with possible guesses and solutions
f = json.load(open('words.json'))

# Enter guess
def enter_guess(word):
    keyboard.write(word, delay=0.05)
    keyboard.press_and_release('enter')

# Evaluate guess
def evaluate_guess(game_row):
    row = browser.execute_script('return arguments[0].shadowRoot', game_row)
    tiles = row.find_elements(By.CSS_SELECTOR, "game-tile")
    evaluation = []
    eval_to_int = {
        "correct": 2,
        "present": 1,
        "absent": 0
    }
    for tile in tiles:
        evaluation.append(eval_to_int[tile.get_attribute("evaluation")])
    return evaluation

# Trim down potential solutions
def trim_list_of_guesses(words, selected_word, evaluation):
    for i in range(5):
        if evaluation[i] == 0:
            remove = True
            occurrences = find(selected_word, selected_word[i])
            occurrences.remove(i)
            if len(occurrences) > 0:
                for occurrence in occurrences:
                    if evaluation[occurrence] == 1 or evaluation[occurrence] == 2:
                        remove = False
            if remove:
                for word in list(words):
                    if selected_word[i] in word:
                        words.remove(word)
        elif evaluation[i] == 1:
            for word in list(words):
                if selected_word[i] not in word or selected_word[i] == word[i]:
                    words.remove(word)
        else:
            for word in list(words):
                if selected_word[i] != word[i]:
                    words.remove(word)
    return words

# Return list of occurrences of a character in a string
def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

# Select next word
def select_word(words):
    unique = True
    tmp = []
    for word in words:
        for i in range(len(word)):
            for j in range(i + 1, len(word)):
                if word[i] == word[j]:
                    unique = False
        if unique:
            tmp.append(word)
        unique = True
    if len(tmp) > 0:
        return tmp[0]
    else:
        return words[0]

# Solve Wordle
def unwordle():
    # Set up Selenium browser
    browser.get("https://www.powerlanguage.co.uk/wordle/")

    # Start program when escape key is pressed
    keyboard.wait('esc')

    # Retrieve game rows
    game_app = browser.find_element(By.TAG_NAME, 'game-app')
    board = browser.execute_script("return arguments[0].shadowRoot.getElementById('board')", game_app)
    game_rows = board.find_elements(By.TAG_NAME, 'game-row')

    # Initialize potential solutions
    trimmed_down_list = f['solutions']

    # Initialize first guess
    # https://www.youtube.com/watch?v=fRed0Xmc2Wg
    selected_word = "crate"

    # Initialize counters
    guess_number = 0

    # Iterate for six attempts
    while guess_number < 5:

        # Enter guess
        enter_guess(selected_word)

        # Evaluate guess
        evaluation = evaluate_guess(game_rows[guess_number])

        # Check if Wordle has been solved
        if sum(evaluation) == 10:
            print("Solved in {} attempts!".format(guess_number + 1))
            return

        # Trim down potential solutions
        trimmed_down_list = trim_list_of_guesses(trimmed_down_list, selected_word, evaluation)
        if selected_word in trimmed_down_list:
            trimmed_down_list.remove(selected_word)

        # Select next guess
        selected_word = select_word(trimmed_down_list)

        # Wait for site to reveal result of previous guess
        time.sleep(2)

        # Enter next guess
        enter_guess(selected_word)

        # Increment guess number
        guess_number = guess_number + 1

    # Admit failure
    if guess_number == 5:
        print("Could not guess in six attempts!")

if __name__ == '__main__':
    unwordle()
# Todo:
# - Accuracy calculation
# - Show/hide time
# - Center text (both axes)
# - Use F-keys
# - Fix escape issue on first character
# - Solve cyclomatic complexity for draw_screen() and wpm_test()

import curses
from time import time
from subprocess import run
import re


def calc_wpm(words, current_text, time_elapsed):

    valid_length = 0
    for word_idx in words.keys():
        if words[word_idx]['correct']:
            valid_length += len(words[word_idx]['word'])
    wpm = round((valid_length / (time_elapsed / 60)) / 5)

    return wpm


def get_breaks(target_text, width):

    space_left = width
    words = target_text.split()
    current_index = 0
    breaks = []

    for word in words:
        if len(word) + 1 > space_left:
            breaks.append(current_index)
            space_left = width - len(word)
        else:
            space_left -= len(word) + 1

        current_index += len(word) + 1

    return breaks


def get_words(string, special_chr):

    words = {}
    word = ''
    word_start = 0

    for i in range(len(string)):
        if string[i] in special_chr:
            pass
            if word != '':
                words[word_start] = {'word': word, 'correct': False}
                word = ''
            words[i] = {'word': string[i], 'correct': False}
            word_start = i + 1
        else:
            if word_start == -1:
                word_start = i
            word += string[i]

    if word != '':
        words[word_start] = {'word': word, 'correct': False}
        word = ''

    return words


def update_words(words, current_text):
    for word_idx in words.keys():
        for i, letter in enumerate(words[word_idx]['word']):
            try:
                if current_text[word_idx + i] == letter:
                    words[word_idx]['correct'] = True
                else:
                    words[word_idx]['correct'] = False
                    break
            except IndexError:
                words[word_idx]['correct'] = False
                break


def draw_screen(
    stdscr, words, target_text, current_text, breaks, time_elapsed, wpm,
    test_in_progress
):

    # target text
    y = 0
    x = 0
    for word in words.keys():
        col = curses.color_pair(2)
        if words[word]['correct']:
            col = curses.color_pair(1)
        try:
            if word == breaks[y]:
                y += 1
                x = 0
        except IndexError:
            pass

        stdscr.addstr(y * 2, x, words[word]['word'], col)

        x += len(words[word]['word'])

    # current text
    y = 0
    rev_i = 0
    x = 0
    for i, ch in enumerate(current_text):
        try:
            if i == breaks[y]:
                y += 1
                rev_i = i
                stdscr.addstr((y * 2) + 1, 0, ch)
            else:
                stdscr.addstr((y * 2) + 1, i - rev_i, ch)
        except IndexError:
            stdscr.addstr((y * 2) + 1, i - rev_i, ch)
        # current position
        if (
            i == len(current_text) - 1
            and len(current_text) != len(target_text)
        ):
            y_underscore = y
            rev_underscore = rev_i
            try:
                if i + 1 == breaks[y]:
                    y_underscore += 1
                    rev_underscore = i + 1
            except IndexError:
                pass

            stdscr.addstr((y_underscore * 2) + 1, i - rev_underscore + 1, '_')

    stdscr.addstr(len(breaks) * 2 + 3, 0, f'WPM: {wpm}')
    # stdscr.addstr(len(breaks) * 2 + 4, 0, f'Time: {round(time_elapsed)}')

    if current_text != '' and test_in_progress is False:
        stdscr.addstr(len(breaks) * 2 + 6, 0, 'q = Exit, r = New text')


def get_valid_text(special_chr):

    # reject texts with unexpected chrs
    text_ok = False
    while text_ok is False:
        text_ok = True
    try:
        text = run('fortune', capture_output=True, text=True).stdout
    except FileNotFoundError:  # temporary Docker work-around
        fortune = '/usr/games/fortune'
        text = run(fortune, capture_output=True, text=True).stdout
    for chr in text:
        if chr not in special_chr and not chr.isalnum() and not ' ':
            text_ok = False

    # format text
    text = text.replace('\n', ' ')
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()

    return text


def test_init(stdscr, special_chr):
    current_text = ''
    wpm = 0
    time_elapsed = 0

    target_text = get_valid_text(special_chr)

    words = get_words(target_text, special_chr)
    breaks = get_breaks(target_text, stdscr.getmaxyx()[1])
    test_in_progress = False

    return (
        current_text, wpm, time_elapsed,
        target_text, words, breaks, test_in_progress
    )


def wpm_test(stdscr, special_chr):

    (
        current_text, wpm, time_elapsed, target_text,
        words, breaks, test_in_progress
    ) = test_init(stdscr, special_chr)

    start_time = 0

    while True:

        update_words(words, current_text)

        if test_in_progress:
            if len(current_text) == 1:
                start_time = time()
            time_elapsed = time() - start_time
            wpm = calc_wpm(words, current_text, max(time_elapsed, 1))
            if len(current_text) == len(target_text):
                test_in_progress = False

        stdscr.erase()
        try:
            draw_screen(
                stdscr, words, target_text, current_text, breaks, time_elapsed,
                wpm, test_in_progress
            )
        except curses.error:
            (
                current_text, wpm, time_elapsed,
                target_text, words, breaks, test_in_progress
            ) = test_init(stdscr, special_chr)
        stdscr.refresh()

        try:
            key = stdscr.getkey()
            try:
                if ord(key) == 27:
                    test_in_progress = False
            except TypeError:
                pass
            if key in ('KEY_BACKSPACE', '\b', '\x7f'):
                if len(current_text) > 0:
                    current_text = current_text[:-1]
                    test_in_progress = True
            elif (
                    test_in_progress
                    or (current_text == '' and test_in_progress is False)
                 ):
                current_text = current_text + key
                test_in_progress = True
            elif current_text != '' and test_in_progress is False:
                if key == 'r':
                    (
                        current_text, wpm, time_elapsed,
                        target_text, words, breaks, test_in_progress
                    ) = test_init(stdscr, special_chr)
                elif key == 'q':
                    exit()
        except curses.error:
            pass


def main(stdscr):
    curses.curs_set(0)
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    stdscr.nodelay(True)
    rate = 500
    stdscr.timeout(rate)
    special_chr = (' ', ',', '.', '!', '?', ':', ';', '"', '\'', '(', ')', '-')

    wpm_test(stdscr, special_chr)


curses.wrapper(main)

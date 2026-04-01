import curses
import time
import random
import os
import sys

def load_text(count=15):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_path, "assets/words.txt")
    
    if os.path.exists(path):
        with open(path, "r") as f:
            all_words = f.read().splitlines()
        return " ".join(random.sample(all_words, count))
    return "file not found error message"

def wrap_text(text, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_length = 0

    for word in words: 
        if current_length + len(word) <= max_width:
            current_line.append(word)
            current_length+=len(word)+1
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)+1

    if current_line:
        lines.append(" ".join(current_line))

    return lines

def main(stdsrc):
    
    curses.curs_set(0)
    stdsrc.nodelay(True)

    curses.init_pair(1,curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2,curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3,curses.COLOR_WHITE, curses.COLOR_BLACK)

    target_text = load_text(20)
    user_input = []
    start_time = None
    
    corr = 0
    att = 0

    while True:
        stdsrc.clear()
        height, width = stdsrc.getmaxyx()
        
        max_width = min(width - 10, 60) 
        wrapped_lines = wrap_text(target_text, max_width)

        start_y = height // 2 - len(wrapped_lines) // 2

        if width < len(target_text) + 10 and height < 10:
            stdscr.addstr(0, 0, "Iltimos, terminal oynasini kattalashtiring!")
            stdscr.refresh()
            time.sleep(0.1)
            continue

        elapsed_time = max(time.time()-start_time, 1) if start_time else 0
        wpm = round(corr*60/(5*elapsed_time)) if start_time else 0
        acc = corr / att * 100 if att > 0 else 100
        
        stats_str = f"WPM: {wpm} | Accuracy: {acc:.0f}% | Vaqt: {elapsed_time:.1f}s\n"
        stdsrc.addstr(max(0, start_y-3), (width - len(stats_str))//2, stats_str, curses.A_BOLD)
        
        corr = sum(1 for i, c in enumerate(user_input) if i < len(target_text) and c == target_text[i])
        
        global_idx = 0

        for line_idx, line_text in enumerate(wrapped_lines):
            line_start_x = (width - len(line_text)) // 2
            
            for inline_idx, char in enumerate(line_text):
                color = curses.color_pair(3)
                attr = curses.A_NORMAL
                
                if global_idx < len(user_input):
                    if user_input[global_idx] == char:
                        color = curses.color_pair(1)
                    else:
                        color = curses.color_pair(2)
                        attr = curses.A_UNDERLINE | curses.A_REVERSE
            
                if global_idx == len(user_input):
                    attr = curses.A_BOLD
                try:
                    stdsrc.addch(start_y + line_idx, line_start_x + inline_idx, char, color | attr)
                except curses.error:
                    pass
                global_idx += 1
            global_idx += 1

        exit_msg = "press 'esc' to quit"
        stdsrc.addstr(height - 2, (width - len(exit_msg)) // 2, exit_msg, curses.color_pair(3) | curses.A_DIM)

        stdsrc.refresh()

        if len(user_input) == len(target_text):
            stdsrc.nodelay(False)
            final_msg = f"FINISHED! WPM: {wpm} | ACC: {acc:.0f}%"
            stdsrc.addstr(start_y + (len(target_text)//max_width) + 2, (width - len(final_msg))//2, final_msg, curses.color_pair(1) | curses.A_BOLD)
            stdsrc.getch()
            break

        try:
            key = stdsrc.getch()
        except:
            key = -1

        if key != -1:
            if start_time is None:
                start_time = time.time()

            if key == 27: 
                break
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                if len(user_input) > 0:
                    user_input.pop()
            elif key < 256 and len(user_input) < len(target_text):
                user_input.append(chr(key))
                att+=1
        
        time.sleep(0.01)

curses.wrapper(main)

# Fsc Game

import json, os, textwrap, math
from shutil import move
from tokenize import endpats

# CONSTANTS
TERM_W = int(os.popen('stty size', 'r').read().split()[1])
TERM_H = int(os.popen('stty size', 'r').read().split()[0])
PREV_L = "\033[F"
UP_L = "\033[A"
SEP = "+"+"=" * (TERM_W-2)+"+"
DAYS = 10  # number of days of the holiday
GAME_NAME = "Trippy"
BRIEFING = '''\
A financial game
'''

# dependent variables
no_scene = 0
stats = {
    "dest": "",
    "money": 0,
    "joy": 0,
    "day": 0,
}

# load data from json file
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "options.json"
abs_file_path = os.path.join(script_dir, rel_path)

with open(abs_file_path) as f:
    optionsData = json.load(f)

destinations = optionsData['destinations']


# FUNCTIONS
def distribute(oranges, plates):
    """
        https://stackoverflow.com/questions/54353083/distribute-an-integer-amount-by-a-set-of-slots-as-evenly-as-possible

        >>> distribute(oranges=28, plates=7)
        [4, 4, 4, 4, 4, 4, 4]
        >>> distribute(oranges=29, plates=7)
        [4, 4, 4, 5, 4, 4, 4]
        >>> distribute(oranges=30, plates=7)
        [4, 5, 4, 4, 5, 4, 4]
        >>> distribute(oranges=31, plates=7)
        [4, 5, 4, 5, 4, 5, 4]
        >>> distribute(oranges=32, plates=7)
        [5, 4, 5, 4, 5, 4, 5]
        >>> distribute(oranges=33, plates=7)
        [5, 4, 5, 5, 4, 5, 5]
        >>> distribute(oranges=34, plates=7)
        [5, 5, 5, 4, 5, 5, 5]
        >>> distribute(oranges=35, plates=7)
        [5, 5, 5, 5, 5, 5, 5]
        """
    base, extra = divmod(oranges, plates)  # extra < plates
    if extra == 0:
        L = [base for _ in range(plates)]
    elif extra <= plates // 2:
        leap = plates // extra
        L = [base + (i % leap == leap // 2) for i in range(plates)]
    else:  # plates/2 < extra < plates
        leap = plates // (
            plates - extra
        )  # plates - extra is the number of apples I lent you
        L = [base + (1 - (i % leap == leap // 2)) for i in range(plates)]
    return L

import sys, re
if(sys.platform == "win32"):
    import ctypes
    from ctypes import wintypes
else:
    import termios

def cursorPos():
    if(sys.platform == "win32"):
        OldStdinMode = ctypes.wintypes.DWORD()
        OldStdoutMode = ctypes.wintypes.DWORD()
        kernel32 = ctypes.windll.kernel32
        kernel32.GetConsoleMode(kernel32.GetStdHandle(-10), ctypes.byref(OldStdinMode))
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 0)
        kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(OldStdoutMode))
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    else:
        OldStdinMode = termios.tcgetattr(sys.stdin)
        _ = termios.tcgetattr(sys.stdin)
        _[3] = _[3] & ~(termios.ECHO | termios.ICANON)
        termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, _)
    try:
        _ = ""
        sys.stdout.write("\x1b[6n")
        sys.stdout.flush()
        while not (_ := _ + sys.stdin.read(1)).endswith('R'):
            True
        res = re.match(r".*\[(?P<y>\d*);(?P<x>\d*)R", _)
    finally:
        if(sys.platform == "win32"):
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), OldStdinMode)
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), OldStdoutMode)
        else:
            termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, OldStdinMode)
    if(res):
        return (int(res.group("x")), int(res.group("y")))
    return (-1, -1)

def cls():
    """cls or clear on respective systems"""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def sep():
    print(SEP)

def set_c (x, y=None):
    y = os.get_terminal_size()[1]
    print("\033[%d;%dH" % (y, x))
    return ""

def move_c (x, y=0):
    """needs to add end='' if is used in print()"""
    # y+=1 # to compensate for \n in print()

    if x == -1:
        x =0
    return '\b' * x + y * PREV_L

def nl():
    """newline"""
    print("| " + " " * (TERM_W - 4) + " |")

def input_w(txt):
    a = input("| " + txt + " "*(TERM_W - 4-len(txt)) +" |" + move_c(TERM_W - 2-len(txt)-2+1))
    # move_c(2+len(txt))
    return a

def print_w(txt, starts="| ", ends=" |"):
    """
    Caveat: Prints no newline when empty string is given (due to textwrap)
    However, that should be handled by nl()
    """
    lines = textwrap.wrap(
        txt,
        TERM_W - len(starts) - len(ends),  # max width
        break_long_words=False,
        replace_whitespace=False)
    for i in lines:
        print(starts + i + " " * (TERM_W - len(i) - len(starts) - len(ends)) +
              ends)

def print_wp(txt, seperator="|", starts="| ", ends=" |"):
    """positions a piece of string in the x slot with character enclosing them on one line, where x = len(txt)"""
    def calc_slot(txt):
        return distribute(
            TERM_W - len(starts) - len(ends) - len(seperator) * (len(txt) - 1),
            len(txt))

    if type(txt) == str:  #centers the text
        slot_sizes = TERM_W - len(starts) - len(ends)
        print(starts, end="")
        print(" " * distribute(slot_sizes - len(txt), 2)[0], end="")
        print(txt, end="")
        print(" " * distribute(slot_sizes - len(txt), 2)[1], end="")
        print(ends, end="")
        print()

    else:  # distributes the text
        slot_sizes = calc_slot(txt)  #get number of spaces for each slot

        c = 0  #counter
        for i in txt:
            if c == 0:
                print(starts, end="")
            else:
                print(seperator, end="")
            print(" " * distribute(slot_sizes[c] - len(i), 2)[0], end="")
            print(i, end="")
            print(" " * distribute(slot_sizes[c] - len(i), 2)[1], end="")

            c += 1
        print(ends, end="")
        print()

def new_s():
    """new basic scene"""
    cls()
    sep()
    print_wp(GAME_NAME, "|")
    sep()
    pos = cursorPos() # get current cursor position
    c = 0
    for i in range(TERM_H - pos[1]): # loops all the way to the bottom of the console
        nl()
        c+=1
    print(SEP+move_c(-1,c),end="") # resets cursor to proper position
        
def new_h():
    """New stats header"""
    a = [f"Day {stats['day']}"]
    a.append(f"Destination: {stats['dest']['name']}")
    a.append(f"Balance: {stats['money']}")
    a.append(f"Joy: {stats['joy']}")

    print_wp(a, "|")

def new_sh():
    """
    a function that incorporates numerous other functions to simplify code
    creates a advanced scene with header in addition
    """
    new_s()
    new_h()
    sep()
    nl()


def validate_input(inp, data_type=int, data_range=None):
    """
    validates data with the range and(or) type given
    returns an Exception if invalid, else returns the 
    converted value
    """
    try:
        a = data_type(inp)  #convert
        if (a in data_range) or (data_range == None):
            return a
        else:  # catches wrong values
            return ValueError()

    except (TypeError, ValueError):  # catches wrong type
        return TypeError()


new_s()  #introduction
print_wp("Briefing")
nl()
print_w(BRIEFING)
nl()
input_w("Press ENTER when you are ready ")

new_s()  # choose destination

print_w("Choose a destination for your holiday")
nl()

# main display code
c = 1
for i in destinations.keys():
    info = destinations[i]['info']
    print_w(f"{c}. " + i)  # prints the name of the destination
    print_w(info, "| " + " " * 3)  #prints info with 3 spaces as indent
    nl()
    c += 1  # update counter
c -= 1  # to remove the extra 1 added at the end of the loop

# asks for input and validates it
dest_choice = input_w(f"Choose a destination (1 ~ {c}): ")
validated_data = validate_input(dest_choice, int, range(1, c + 1))
while isinstance(validated_data, Exception):
    # keep looping until valid data is given
    nl()
    sep()
    if isinstance(validated_data, ValueError):  # handles out of range
        print_w("Please enter a valid choice!")
    if isinstance(validated_data, TypeError):  # handles wrong type
        print_w("Please enter a valid Arabic number!")

    # update variables
    dest_choice = input_w(f"Choose a destination (1 ~ {c}): ")
    validated_data = validate_input(dest_choice, int, range(1, c + 1))

# updating stats according to user's choice
# although not very efficient, this reverse search the destination dict with index
stats["dest"] = destinations[list(destinations.keys())[validated_data - 1]] 

# choose a insurance
new_sh()

#choose your flight
new_sh()

# holiday starts
new_sh()

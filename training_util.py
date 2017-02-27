from osc_handler import OSCHandler
import mingus.core.chords as chords
import mingus.core.scales as scales
import curses

settings = ['Note', 'Chord', 'Key', 'Mood', 'Octave', 'Mode']
current_setting = 0
play_notes = 0

setting_counter = {
    'Note':0,
    'Chord':0,
    'Key':0,
    'Mood':0,
    'Octave':0,
    'Mode':0,
}

setting_positions = {
    'Note': (9,10),
    'Chord': (10,10),
    'Key': (11,10),
    'Mood': (12,10),
    'Octave': (13,10),
    'Mode': (14,10),
}

setting_arrays = {
    'Note': scales.Major('A').ascending()[0:-1],
    'Chord': ['minor_triad', 'major_triad', 'diminished_triad', \
    'minor_sixth', 'major_sixth', 'minor_seventh', 'major_seventh', \
    'dominant_seventh', 'minor_major_seventh', 'minor_seventh_flat_five', \
    'diminished_seventh', 'minor_ninth', 'major_ninth', 'dominant_ninth', \
    'minor_eleventh', 'eleventh', 'minor_thirteenth', 'major_thirteenth', \
    'dominant_thirteenth', 'augmented_triad', 'augmented_major_seventh', \
    'augmented_minor_seventh', 'suspended_second_triad', 'suspended_fourth_triad', \
    'suspended_seventh', 'suspended_fourth_ninth', 'suspended_ninth', \
    'dominant_flat_ninth', 'dominant_sharp_ninth', 'dominant_flat_five', \
    'sixth_ninth', 'hendrix_chord'],
    'Key': ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#'],
    'Mood': ['Major', 'Harmonic Major', 'Melodic Minor', 'Harmonic Minor', 'Natural Minor', ],
    'Octave': [i for i in range(10)],
    'Mode': ['Note', 'Chord']
}

def print_setting(setting):
    setting_position = setting_positions[setting]
    array = setting_arrays[setting]
    index = setting_counter[setting]
    if isinstance(array[index], unicode):
        stdscr.addstr(setting_position[0], setting_position[1], \
        setting + ": " + array[index].encode('utf-8') + '\t\t')
    else:
        stdscr.addstr(setting_position[0], setting_position[1], \
        setting + ": " + str(array[index]) + '\t\t')


def add_value_to_setting(value, setting):
    setting_counter[setting] += value
    setting_counter[setting] %= len(setting_arrays[setting])
    print_setting(setting)

def indicate_setting(setting):
    for k,v in setting_positions.items():
        if k != setting:
            stdscr.addstr(v[0], v[1]-5, "\t")
        else:
            stdscr.addstr(v[0], v[1]-5, "->")

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)

stdscr.addstr(0,10,"Hit 'q' to quit")
stdscr.addstr(1,10,"Left/Right to increment current setting")
stdscr.addstr(2,10,"Up/Down to navigate settings (notes/chords/keys/moods/octaves)")
stdscr.addstr(3,10,"Spacebar to confirm selection for image")
stdscr.addstr(4,10,"Tab to toggle playing notes/chords")
stdscr.addstr(5,10,"Enter to play note/chord")
stdscr.addstr(16, 10, "Setting: " + settings[current_setting] + '\n')

for setting in setting_positions.keys():
    print_setting(setting)

stdscr.move(17,10)
stdscr.refresh()

osc_client = OSCHandler('127.0.0.1', 57120)
key = ''

while key != ord('q'):

    indicate_setting(settings[current_setting])
    key = stdscr.getch()
    #stdscr.addstr(15,10, "Detected key: " + str(key) + "\n")

    if key == curses.KEY_RIGHT:
        add_value_to_setting(1, settings[current_setting])

    elif key == curses.KEY_LEFT:
        add_value_to_setting(-1, settings[current_setting])

    #TODO: handle changing keys
    elif key == curses.KEY_DOWN:
        current_setting = (current_setting + 1) % len(settings)
        stdscr.addstr(16, 10, "Setting: " + settings[current_setting] + '\t\t\t\t')

    elif key == curses.KEY_UP:
        current_setting = (current_setting - 1) % len(settings)
        stdscr.addstr(16, 10, "Setting: " + settings[current_setting] + '\t\t\t\t')

    # spacebar, save settings for training
    elif key == 32:
        continue

    # enter, send sound to SC through osc
    elif key == 10:
        # if in chord mode
        if (setting_counter['Mode']):
            stdscr.addstr(20,10, setting_arrays['Chord'][setting_counter['Chord']])
            continue
        # else in note mode
        else:
            note = setting_arrays['Note'][setting_counter['Note']]
            index = setting_arrays['Key'].index(note)
            midi_value = (index + 1) + ((setting_counter['Octave']) * 12)
            stdscr.addstr(17,10, "Midi value: " + str(midi_value) + '\t')
            osc_client.sendMessage('/cnn_midi', [midi_value])

    # tab
    elif key == 9:
        add_value_to_setting(1, 'Mode')


    stdscr.move(17,10)
    stdscr.refresh()
    stdscr.move(17,10)

curses.endwin()

import mingus.core.chords as chords
import mingus.core.scales as scales
import curses, random

from osc_handler import OSCHandler

def intialize_mood_and_key(scale_list, keys):
    # Choose a random scale mood
    scale_index = random.randint(0, len(scale_list)-1)
    random_scale = scale_list[scale_index]

    # Choose a random tonic
    key_index = random.randint(0, len(keys)-1)
    random_key = keys[key_index]

    # Get generator from mingus library
    scale_generator = getattr(scales, random_scale)

    # Generate random scale from tonic
    random_scale = scale_generator(random_key).ascending()[0:-1]
    return (random_scale, scale_index, key_index)

settings = ['Note', 'Chord', 'Key', 'Scale', 'Octave', 'Type']
scale_list = ['Major', 'HarmonicMajor', 'MelodicMinor', 'HarmonicMinor', 'NaturalMinor', ]
keys = ['Ab', 'A', 'A#', 'Bb', 'B', 'C', 'C#', 'Db', 'D#', 'D',  \
'Eb', 'E', 'Gb', 'G', 'F', 'F#', 'G#']

current_setting = 0
play_notes = 0
(scale, scale_index, key_index) = intialize_mood_and_key(scale_list, keys)

setting_counter = {
    'Note':0,
    'Chord':0,
    'Key':key_index,
    'Scale':scale_index,
    'Octave':0,
    'Type':0,
}

setting_positions = {
    'Note': (9,10),
    'Chord': (10,10),
    'Key': (11,10),
    'Scale': (12,10),
    'Octave': (13,10),
    'Type': (14,10),
}

setting_arrays = {
    'Note': scale,
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
    'Key': keys,
    'Scale': scale_list,
    'Octave': [i for i in range(10)],
    'Type': ['Note', 'Chord']
}

def print_setting(setting):
    setting_position = setting_positions[setting]
    array = setting_arrays[setting]
    index = setting_counter[setting]
    stdscr.addstr(setting_position[0], setting_position[1], \
    setting + ": " + str(array[index]) + '\t\t')

def add_value_to_setting(value, setting):
    setting_counter[setting] += value
    setting_counter[setting] %= len(setting_arrays[setting])
    try:
        if(setting == 'Scale') :
            change_scale_mood(setting_arrays[setting][setting_counter[setting]])
        elif(setting == 'Key'):
            change_scale_key(setting_arrays[setting][setting_counter[setting]])
        print_setting(setting)

    except:
        add_value_to_setting(value, setting)



def change_scale_mood(mood):
    # Get generator from mingus library
    scale_generator = getattr(scales, mood)
    current_key = setting_arrays['Key'][setting_counter['Key']]
    new_scale = scale_generator(current_key).ascending()[0:-1]
    setting_arrays['Note'] = new_scale
    setting_counter['Note'] = 0
    print_setting('Note')

def change_scale_key(key):
    current_mood = setting_arrays['Scale'][setting_counter['Scale']]
    scale_generator = getattr(scales, current_mood)
    new_scale = scale_generator(key).ascending()[0:-1]
    setting_arrays['Note'] = new_scale
    setting_counter['Note'] = 0
    print_setting('Note')

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
        # TODO: convert notes to midi
        # if in chord mode
        if (setting_counter['Type']):
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
        add_value_to_setting(1, 'Type')


    stdscr.move(17,10)
    stdscr.refresh()
    stdscr.move(17,10)

curses.endwin()

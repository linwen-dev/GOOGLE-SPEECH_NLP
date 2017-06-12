import os
import re
import string
from datetime import datetime

# Hardcoded value for current user
USER_NAME = 'Faisal'

# EMAIL_ALIASES = {
#     'Victor': 'njutn95@yahoo.com',
#     'Faisal': 'faisal.khalid@icloud.com',
#     'Samreem': 'samreen.ghani@gmail.com',
#     'Mehreen': 'khalid.mehreen@gmail.com'
# }

EMAIL_ALIASES = dict.fromkeys(['viktor', 'victor']
                              , 'njutn95@yahoo.com')
EMAIL_ALIASES.update(dict.fromkeys(['faisal', 'fusil']
                                   , 'faisal.khalid@icloud.com'))
EMAIL_ALIASES.update(dict.fromkeys(['samreen']
                                   , 'samreen.ghani@gmail.com'))
EMAIL_ALIASES.update(dict.fromkeys(['mehreen']
                                   , 'khalid.mehreen@gmail.com'))


interrupted = False
snowboy_model = 'resources/Lily.pmdl'


def sleep(seconds):
    os.system('sleep ' + str(seconds))


def get_raspberry_serial_number():
    """
    Returns the Serial Number of Raspberry Device (or return all zeros if not raspberry device)  
    """
    cpuserial = '0000000000000000'
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
                break
        f.close()
        return cpuserial
    except:
        return cpuserial


def play_audio(file_name):
    """
    Plays the audio file using the MPlayer audio player system command 
    """
    os.system('mplayer ' + file_name)


def play_beep():
    play_audio('beep.mp3')


def strip_punctuation(phrase):
    """
    Removes all punctuations from a string 
    """
    exclude = set(string.punctuation)
    return ''.join(ch for ch in phrase if ch not in exclude)


def strip_trigger_word(phrase):
    return re.sub(pattern=r'(Hey |Hi )?(Lily)', repl='', string=phrase, flags=re.IGNORECASE)


def replace_email_aliases(phrase):
    pattern = re.compile('|'.join(EMAIL_ALIASES.keys()), re.IGNORECASE)
    result = pattern.sub(lambda x: EMAIL_ALIASES[x.group().lower()], phrase)
    return result


def interrupted_callback():
    global interrupted
    print("interrupted_callback")
    return interrupted


def keyword_detected():
    global interrupted
    print("keyword_detected")
    interrupted = True


def get_current_time():
    # return '9:30 am'
    return datetime.now().strftime('%I:%M %p')
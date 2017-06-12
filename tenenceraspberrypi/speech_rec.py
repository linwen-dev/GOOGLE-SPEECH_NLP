#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import closing
from credentials import *
from utils import USER_NAME
from gmail_api import GmailApi
from apiclient import errors

import snowboydecoder
import speech_recognition as sr
import re
import utils
import socket
import select

try:
    HOST, PORT = "127.0.0.1", 10000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.settimeout(3.0)

except socket.error as e:
    print("Connection to NodeJS socket Error: {}".format(e))


def create_wakeup_keyword_pattern():
    """
    Deprecated
    """
    return r"(Hey |Hi )?(Lily|lilies)"


# def record_audio(timeout=None):
#     """
#     Returns the audio sample from memory buffer (Audio Stream)
#     """
#     try:
#         with mic as source:
#             audio = rec.listen(source=source, timeout=timeout)
#         return audio
#     except:
#         return False


# def recognize_speech_google(audio):
#     """
#     Returns the phrase (string) from audio using Google Speech To Text API
#     """
#     try:
#         # This line of code is for API usage. Also removes trigger phrase from start of the phrase.
#         phrase = rec.recognize_google_cloud(audio_data=audio, credentials_json=json_credentials, language='en-GB')
#         # phrase = rec.recognize_google(audio_data=audio, language='en-GB')
#         return phrase
#     except sr.UnknownValueError:
#         print("You: Recognition could not understand audio")
#     except sr.RequestError as e:
#         print("You: Could not request results from Speech Recognition service; {0}".format(e))
#     return False

def recognize_speech_google():
    """
         Returns the phrase (string) from audio using Google Speech To Text API
    """

    try:
        sock.send('Start')
        inputready, outputready, exceptready = select.select([sock], [], [], 3)
        if sock in inputready:
            received = sock.recv(1024)
            if len(received) == '':
                return ""
            else:
                print('received: {}'.format(received))
                return received
        else:
            return ""
    except Exception as e:
        print("Recognize_speech_google Error: {}".format(e))

#
# def recognize_speech_sphinx(audio):
#     """
#     Returns the phrase (string) from audio using Offline PocketSphinx Speech to Text
#     """
#     try:
#         phrase = rec.recognize_sphinx(audio_data=audio, language='en-US', keyword_entries=[('sarah', 0)])
#         return phrase
#     except sr.UnknownValueError:
#         print("You: Recognition could not understand audio")
#     except sr.RequestError as e:
#         print("You: Could not request results from Speech Recognition service; {0}".format(e))
#     return False


def is_in_ignore_list(phrase):
    """
    Returns True if phrase is in ignore list, otherwise False
    """
    phrase = utils.strip_punctuation(phrase)

    # Pattern for thanking
    pattern = r"^(Ok|Okay|Thanks|Got it|Thank you|Sure|Perfect|Excellent|I understand|Fine|Cool|Awesome|Amazing|Love you|You rock)( Lily)?$"
    if re.match(pattern=pattern, string=phrase, flags=re.IGNORECASE):
        # response_phrases = ["You're welcome " + USER_NAME, "No problem", "My pleasure, " + USER_NAME, "You're welcome"]
        # rand_index = randint(0, len(response_phrases)-1)
        # text_to_speech(response_phrases[rand_index])
        return True

    # Pattern for farewell
    pattern = r"^(Ok )?(Bye|Goodbye|Later|See you|Bye for now|I gotta go|I have to go|Gotta go|Got to go|Have to go|Talk later|Talk to you|See you)( now| later)?( Lily)?$"
    if re.match(pattern=pattern, string=phrase, flags=re.IGNORECASE):
        text_to_speech("Ok " + USER_NAME + ".")
        turn_off_device()
        return True
    return False


def send_email(text, subject='', to='voice2mail@tenence.com'):
    """
    Sends an email using Gmail API.
    """
    global gmail
    # In case subject is unset, set the raspberry device ID as subject
    if subject == '':
        subject = 'Message from Raspberry with ID: ' + utils.get_raspberry_serial_number()
    try:
        message = gmail.create_message(sender='voice2mail@tenence.com', to=to, subject=subject, message_text=text)
        gmail.send_message(message)
    except errors.HttpError as error:
        print(error)
        return False
    return True


def check_unread_notifications():
    """
    Checks unread emails grouped by categories:
     - Can't make it
     - Reminder
    """
    # TODO: Try to find a better code styling for specific cases.
    text_to_speech("The usual, " + USER_NAME + ". Working. Let me just check if theres anything to update you on.")
    cant_make_notifications = check_cant_make_notifications()
    reminder_notifications = check_reminder_notifications()
    flag = False
    total_notifications = len(cant_make_notifications) + len(reminder_notifications)
    speech_message = 'Ok. I have ' + str(total_notifications) + ' notifications for you. '
    if total_notifications == 2:
        # Reminders
        if len(reminder_notifications) > 0:
            message_id = reminder_notifications[0]['id']
            message = gmail.get_message_by_id(message_id)
            message_content = gmail.get_message_body(message)
            message_body = re.search(pattern=r'message_body: (.*)', string=message_content)
            if message_body:
                message_body = message_body.group(1)
            else:
                message_body = ''
            reminder_time = re.search(pattern=r'time: (.*)', string=message_content)
            speech_message = 'Hey ' + USER_NAME + ', two things. First, ' + message_body + '... '
            gmail.mark_message_as_read(message_id)

        # Can't make notifications
        if len(cant_make_notifications) > 0:
            message_id = cant_make_notifications[0]['id']
            message = gmail.get_message_by_id(message_id=message_id)
            message_content = gmail.get_message_body(message)
            name = re.search(pattern=r'guest_name: (.*)', string=message_content)
            if name:
                message_from = name.group(1)
            else:
                message_from = 'Unknown'
            meeting_date = re.search(pattern=r'meeting_date: (.*)', string=message_content)
            if meeting_date:
                meeting_date = meeting_date.group(1)
            else:
                meeting_date = ''
            speech_message += 'Second, that meeting you asked for with ' + message_from + ' on ' + meeting_date + ' - they can\'t make it'
        text_to_speech(speech_message)
        return
    if len(cant_make_notifications) > 0:
        flag = True
        speech_message += '. ' + str(len(cant_make_notifications)) + ' I can\'t make it messages '
    if len(reminder_notifications) > 0:
        flag = True
        speech_message += '. ' + str(len(reminder_notifications)) + ' reminders '
    speech_message += 'received today.'
    text_to_speech(speech_message)
    utils.sleep(2)
    if len(cant_make_notifications) > 0:
        for message in cant_make_notifications:
            utils.sleep(2)
            message_id = message['id']
            message = gmail.get_message_by_id(message_id=message['id'])
            message_content = gmail.get_message_body(message)
            name = re.search(pattern=r'guest_name: (.*)', string=message_content)
            if name:
                message_from = name.group(1)
            else:
                message_from = 'Unknown'
            meeting_date = re.search(pattern=r'meeting_date: (.*)', string=message_content)
            if meeting_date:
                meeting_date = meeting_date.group(1)
            else:
                meeting_date = ''
            text_to_speech(
                "Hey, just to let you know. " + message_from + " won't be able to make it to the meeting " + meeting_date)
            gmail.mark_message_as_read(message_id=message_id)
    if len(reminder_notifications) > 0:
        for message in reminder_notifications:
            utils.sleep(2)
            message_id = message['id']
            message = gmail.get_message_by_id(message_id=message['id'])
            message_content = gmail.get_message_body(message)
            message_body = re.search(pattern=r'message_body: (.*)', string=message_content)
            if message_body:
                message_body = message_body.group(1)
            else:
                message_body = ''
            reminder_time = re.search(pattern=r'time: (.*)', string=message_content)
            if reminder_time:
                reminder_time = reminder_time.group(1)
            else:
                reminder_time = ''
            speech_message = message_body
            if reminder_time != '':
                speech_message += ' at ' + reminder_time
            text_to_speech(speech_message)
            gmail.mark_message_as_read(message_id=message_id)
    if flag:
        utils.sleep(2)
        text_to_speech("No more notifications.")


def check_guests_notifications():
    """
    Checks for unread emails that belongs to "I'm here" group
    """
    global gmail
    response = gmail.get_unread_messages(q="subject:I'm here newer_than:1d")
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = gmail.get_unread_messages(page_token=page_token)
        messages.extend(response['messages'])
    return messages


def check_cant_make_notifications():
    """
    Checks for unread emails that belongs to "Can't make it" group
    """
    global gmail
    response = gmail.get_unread_messages(q="subject:can't make it newer_than:1d")
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = gmail.get_unread_messages(page_token=page_token)
        messages.extend(response['messages'])
    return messages


def check_reminder_notifications():
    """
    Checks for unread emails that belongs to "Reminder" group
    """
    global gmail
    response = gmail.get_unread_messages(q="subject:Reminder newer_than:1d")
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = gmail.get_unread_messages(page_token=page_token)
        messages.extend(response['messages'])
    return messages


def text_to_speech(text):
    """
    Plays the audio from text (string) using the Amazon Polly to convert to audio
    And using utils.play_audio() to play it in audio player.
    """
    try:
        response = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Joanna")
        if 'AudioStream' in response:
            with closing(response['AudioStream']) as stream:
                output = 'voice.mp3'
                with open(output, 'wb') as file:
                    file.write(stream.read())
            utils.play_audio(file_name=output)
    except (BotoCoreError, ClientError) as error:
        print(error)


def turn_on_device():
    """
    Changes the global currentMode variable to switch between offline and online voice recognition
    """
    global currentMode
    currentMode = 'awake'
    text_to_speech("How can I help you?")


def turn_off_device(trigger=False):
    """
    Changes the global currentMode variable to switch between offline and online voice recognition
    """
    global currentMode
    currentMode = 'sleep'
    message = "I'm going back to sleep mode. Call me when you need me."
    if trigger:
        message = "Ok then. " + message
        text_to_speech(message)


def check_turn_off_message(phrase):
    """
    Checks if the phrase is intended to turn off the device, calls turn_off_device() and returns True, otherwise False.
    """
    phrase = utils.strip_punctuation(phrase)
    if re.match(
            pattern=r'(Lily )?(Power off|Shut down|Shut up|Please turn off|Please shut down|Please shut up|Turn off|Power down|Please turn off|Go back to sleep)( Lily)?',
            string=phrase, flags=re.IGNORECASE):
        turn_off_device(trigger=True)
        return True
    return False


def check_turn_on_message(phrase):
    """
    Checks if the phrase is intended to turn on the device and returns True, otherwise False.
    """
    global wakeup_pattern
    matches = re.match(pattern=wakeup_pattern, string=phrase, flags=re.IGNORECASE)
    if matches:
        return True
    return False


def check_notifications_message(phrase):
    """
    Checks if the phrase is intended to look for new notifications and returns True, otherwise False.
    """
    print(phrase)
    matches = re.match(
        pattern=r"(What's up|Whats up|WhatsApp|What's new|What is up|What is new|What up|Check mail|Check inbox|Check messages|Check notifications)( Lily)?",
        string=phrase, flags=re.IGNORECASE)
    if matches:
        check_unread_notifications()
        return True
    return False


def check_confirmation_message(phrase):
    """
    Checks if the phrase is confirmation statement and returns True, otherwise False.
    """
    if re.match(
            pattern=r'(Yes|Yea|Yup|Yeah|Ok|Okay|Sure|Fine|That\'s ok|That\'s fine|Cool|Sounds good|Good|Awesome|Ok then|Perfect).*',
            string=phrase, flags=re.IGNORECASE):
        return True
    return False


def check_negation_message(phrase):
    """
    Checks if the phrase if negation statement and returns True, otherwise False.
    """
    if re.match(pattern=r'(No|Nope|Nah|No need|No thanks)', string=phrase, flags=re.IGNORECASE):
        return True
    return False


def check_can_you_ask_message(phrase):
    """
    Checks if the phrase is used for sending "Can you ask" emails and returns True, otherwise False.
    """
    if re.match(pattern=r'.*(come by|come to|see me|drop by).*', string=phrase, flags=re.IGNORECASE):
        send_email(text=phrase, to='hello@lilyoffice.com')
        text_to_speech("Ok, I'll ask them to come now.")
        return True
    return False


def check_can_you_remind_me_message(phrase):
    """
    Checks if the phrase is used for sending "Can you remind me to" emails and returns True, otherwise False.
    """
    match = re.match(pattern=r'Can you remind me to (.*)', string=phrase, flags=re.IGNORECASE)
    if match:
        # Send an email
        send_email(text="Just to remind you to " + match.group(1), to='hello@lilyoffice.com')
        text_to_speech("OK, i got it, i've set a reminder as per your instructions")
        return True
    return False


def check_please_take_notes(phrase):
    """
    Checks if the phrase is used for taking notes and after it's done it sends an email with those notes and returns True, otherwise False.
    """
    if re.match(pattern=r'(Please |Can you )?take notes', string=phrase, flags=re.IGNORECASE):
        text_to_speech("Okay, I'm ready. Please start.")
        notes = ''
        while True:
            # audio = record_audio()
            # if not audio:
            #     continue
            # phrase = recognize_speech_google(audio)

            phrase = recognize_speech_google()
            if not phrase:
                return
            print(phrase)
            if re.match(pattern=r"(.*)(OK )?(that's it|I'm done|I am done|Finished|Shut down( please)?)", string=phrase,
                        flags=re.IGNORECASE):
                break
            notes += phrase + '. '
        text_to_speech("Ok, I've taken notes and will send them to you by email now.")
        if send_email(text=notes, subject="Notes", to='hello@lilyoffice.com'):
            text_to_speech("Email sent")
        else:
            text_to_speech("Email failed to send")
        return True
    return False


def check_can_you_send_email_to(phrase):
    """
    Checks if user wants to send an email to specific person and records the message content until terminated by keyword.
    Returns True if matching, otherwise False.
    """
    match = re.search(pattern=r'(Can you |Please )?Send an email to (\w+).*', string=phrase, flags=re.IGNORECASE)
    if match:
        phrase = utils.replace_email_aliases(phrase=phrase)
        text_to_speech("Email has been sent.")
        send_email(text=phrase)
        return True
    return False


def check_place_order(phrase):
    match = re.match(pattern=r'.*place.{,10}order for (.*)', string=phrase, flags=re.IGNORECASE)
    if match:
        text_to_speech(
            "Ok, I got it. I'll go ahead and order what you asked for. It should be delivered by amazon in the next 24-36 hours at the latest")
        send_email(text="Can you order " + match.group(1) + "?", to='faisal.khalid@icloud.com')
        return True
    return False


def check_travel_hotel(phrase):
    """
    Checks if user wants to book a hotel or travel by containing keywords for flight and/or travel.
    """
    travel_keyword = re.search(pattern=r'.*book.*(flight|train|bus|plane)', string=phrase, flags=re.IGNORECASE)
    travel_keyword = False if not travel_keyword else travel_keyword.group(1)
    hotel_keyword = re.search(pattern=r'.*book.*(hotel|airbnb|room)', string=phrase, flags=re.IGNORECASE)
    hotel_keyword = False if not hotel_keyword else hotel_keyword.group(1)
    if travel_keyword:
        if hotel_keyword:
            # Both are available
            text_to_speech(
                "Ok, I got that. Our travel team will get on this now and should be reaching out to you with options in the next day or sooner.")
            send_email(text=phrase, to='faisal.khalid@icloud.com')
        else:
            # Only travel keyword available
            text_to_speech("Ok, I got that. Did you want me to book a room for you as well?")
            while True:
                # audio = record_audio(timeout=30)
                # confirmation_phrase = recognize_speech_google(audio)
                confirmation_phrase = recognize_speech_google()
                if not confirmation_phrase:
                    return
                if check_turn_off_message(phrase=phrase):
                    return
                if check_confirmation_message(confirmation_phrase):
                    text_to_speech(
                        "Ok, should I book a hotel room, or Airbnb? Also, any idea on where you want to stay and the budget?")
                    while True:
                        # audio = record_audio()
                        # phrase2 = recognize_speech_google(audio)
                        phrase2 = recognize_speech_google()
                        if not phrase2:
                            return
                        if check_turn_off_message(phrase=phrase2):
                            return
                        break
                    text_to_speech(
                        "Ok, understood. Our travel team will get on this now and should be reaching out to you with options in the next day or sooner.")
                    send_email(
                        text=phrase + "\n\nOn question whether to book a hotel room or Airbnb, user replied:\n" + phrase2,
                        to="faisal.khalid@icloud.com")
                    break
                if check_negation_message(confirmation_phrase):
                    text_to_speech(
                        "Ok, understood. Our travel team will get on this now and should be reaching out to you with options in the next day or sooner.")
                    send_email(text=phrase, to='faisal.khalid@icloud.com')
                    break
        return True
    elif hotel_keyword:
        # Only hotel keyword available
        text_to_speech("Ok, I got that. Did you want me to book an airbnb or normal hotel room?")
        while True:
            # audio = record_audio()
            room_choice = recognize_speech_google()
            if not room_choice:
                return
            if check_turn_off_message(phrase=room_choice):
                return
            if re.match(pattern=r".*airbnb.*", string=room_choice, flags=re.IGNORECASE):
                text_to_speech(
                    "Ok, understood. Our travel team will get on this now and should be reaching out to you with options in the next day or sooner")
                break
            if re.match(pattern=r".*hotel.*", string=room_choice, flags=re.IGNORECASE):
                text_to_speech(
                    "Ok, understood. Our travel team will get on this now and should be reaching out to you with options in the next day or sooner")
                break
            text_to_speech("Hm, I didn't quite understand what you said. I'm still learning.")
        send_email(text=phrase + "\n\nOn question whether to book airbnb or hotel room, user replied:\n" + room_choice,
                   to='faisal.khalid@icloud.com')
        return True
    return False


def check_what_time_is_it(phrase):
    if re.match(pattern=r"what time is it(.*)?", string=phrase, flags=re.IGNORECASE):
        current_time = utils.get_current_time()
        text_to_speech("It's " + current_time + " right now")
        return True
    return False


def check_arrange_meeting(phrase):
    if re.match(pattern=r".*(meeting|dinner|coffee|lunch|call|skype|facetime|conference call).*", string=phrase,
                flags=re.IGNORECASE):
        return True
    return False


def check_robot_questions(phrase):
    if re.match(pattern=r'who are you', string=phrase, flags=re.IGNORECASE):
        text_to_speech("your reply")
        return
    if re.match(pattern=r'when were you born', string=phrase, flags=re.IGNORECASE):
        text_to_speech("your reply")
        return
    if re.match(pattern=r'tell me a joke', string=phrase, flags=re.IGNORECASE):
        text_to_speech("your reply")
        return
    if re.match(pattern=r'(whos|who is|whose) your daddy', string=phrase, flags=re.IGNORECASE):
        text_to_speech("your reply")
        return
    if re.match(pattern=r'what can you do', string=phrase, flags=re.IGNORECASE):
        text_to_speech("your reply")
        return
    if re.match(pattern=r'why should I use you', string=phrase, flags=re.IGNORECASE):
        text_to_speech("your reply")
        return
    if re.match(pattern=r'do you love me', string=phrase, flags=re.IGNORECASE):
        text_to_speech("your reply")
        return


# Currently used for Hey Lily trigger word
def offline_recognition(mic, rec):
    """
    Actively listen while the device is turned off and is used for offline recognition to detect the hotword.
    If hotword has been detected, calls the turn_on_device() function.
    """
    global currentMode, wakeup_pattern, snowboy_detector

    # Neat hack that was blocking the device
    if not snowboy_detector:
        snowboy_detector = snowboydecoder.HotwordDetector(utils.snowboy_model, sensitivity=0.5)
    utils.interrupted = False
    snowboy_detector.start(detected_callback=utils.keyword_detected, interrupt_check=utils.interrupted_callback,
                           sleep_time=0.03)
    snowboy_detector.terminate()
    if utils.interrupted:
        snowboy_detector = None
        turn_on_device()


# Used for online recognition
def google_recognition(mic, rec):
    """
    When the device is turned on, it keeps listening for phrases and then decides which action should occur.
    """
    global currentMode
    rec.non_speaking_duration = 0.6
    rec.pause_threshold = 0.6
    # audio = record_audio(timeout=30)
    # if not audio:
    #     return
    # phrase = recognize_speech_google(audio=audio)
    phrase = recognize_speech_google()
    # Checks if phrase is False
    if not phrase:
        return

    if check_turn_on_message(phrase):
        turn_on_device()
        return
    # Strips the trigger keyword
    phrase = str.strip(str(utils.strip_trigger_word(phrase)))

    '''
    This part is for before punctuation has been stripped out.
    Example: Email recognition
    '''
    if check_can_you_send_email_to(phrase=phrase):
        turn_off_device()
        return

    '''
    This part is after the punctuation has been stripped to make regex matching more accurate.
    '''
    phrase = str.strip(utils.strip_punctuation(phrase))
    # In case user only said "Hey|Hi Lily"
    if not phrase:
        return
    if is_in_ignore_list(phrase=phrase):
        return
    if check_turn_off_message(phrase=phrase):
        return
    if check_arrange_meeting(phrase=phrase):
        phrase = utils.replace_email_aliases(phrase=phrase)
        text_to_speech("Ok, I'll get on this, hold on one second.")
        if send_email(text=phrase, to='hello@lilyoffice.com'):
            text_to_speech("Ok, I've sent an email. I'll send out a meeting invite once the meeting is confirmed.")
        else:
            text_to_speech("There has been an error while sending an email.")
        return
    if check_notifications_message(phrase=phrase):
        turn_off_device()
        return
    # Place an order for [supplies]
    if check_place_order(phrase=phrase):
        turn_off_device()
        return
    if check_travel_hotel(phrase=phrase):
        turn_off_device()
        return
    # Can you ask...
    if check_can_you_ask_message(phrase=phrase):
        turn_off_device()
        return
    # Can you remind me to
    if check_can_you_remind_me_message(phrase=phrase):
        turn_off_device()
        return
    # Please take notes
    if check_please_take_notes(phrase=phrase):
        turn_off_device()
        return
    if check_what_time_is_it(phrase=phrase):
        turn_off_device()
        return
    if check_robot_questions(phrase=phrase):
        return
    text_to_speech("I'm afraid I didn't understand. I’m still learning.")
    turn_off_device()


wakeup_pattern = create_wakeup_keyword_pattern()

gmail = GmailApi()

# Snowboy detector
snowboy_detector = snowboydecoder.HotwordDetector(utils.snowboy_model, sensitivity=0.5)

rec = sr.Recognizer()
mic = sr.Microphone(sample_rate=8000)

# with mic as source:
#     rec.adjust_for_ambient_noise(source=source, duration=3)
mic.list_microphone_names()

rec.dynamic_energy_threshold = False

# Default threshold is 300
rec.energy_threshold = 150

# Default pause threshold is 0.8
rec.non_speaking_duration = 0.3
rec.pause_threshold = 0.3

currentMode = 'sleep'
while True:
    if currentMode == 'sleep':
        offline_recognition(mic, rec)
    elif currentMode == 'awake':
        google_recognition(mic, rec)

# stop_listening_func is a function returned by listen_in_background to kill thread when executed.
# stop_listening_func = rec.listen_in_background(source=mic, callback=listen_in_background_callback)

# Forbid the program to end since listen_in_background is daemon thread.
# while True:
#     pass

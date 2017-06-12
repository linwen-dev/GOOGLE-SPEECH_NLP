# Tenenceraspberry


## Dependencies

- Python3
    - On Mac OS install it via `brew install python3`
    - On Linux install it through packet manager `sudo apt-get install python3` on Debian derivative (Ubuntu) or `sudo zypper in python3` on OpenSUSE distribution  
- Pip3 (Python3 package manager)
    - On Mac OS it comes pre-installed with python3
    - On Linux it comes pre-installed with python3, but in case it didn't came together, you can install it as `sudo apt-get install python3-pip` on Debian derivative (Ubuntu) or `sudo zypper in python3-pip` on OpenSUSE distribution
- SpeechRecognition (Used for speech recognition services)
    - On Mac OS install it via `pip3 install SpeechRecognizer`
    - On Linux install it via `pip3 install SpeechRecognizer`
- Boto3 (Amazon Polly SDK)
    - On Mac OS install it via `pip3 install boto3`
    - On Linux install it via `pip3 install boto3`
- Google SDK
    - On Mac OS install it via `pip3 install google-api-python-client`
    - On Linux install it via `pip3 install google-api-python-client`
- PyAudio (Used for manipulations with microphone)
    - On Mac OS install it via `brew install portaudio && sudo brew link portaudio` and then execute `pip3 install pyaudio`
    - On Linux install it through packet manager `sudo apt-get install portaudio19-dev && sudo pip3 install pyaudio` on Debian derivative (Ubuntu) or `sudo zypper in portaudio-devel && sudo pip3 install pyaudio` on OpenSUSE distribution
- MPlayer (Used for sound playback) 
    - On Mac OS install it via `brew install mplayer`
    - On Linux install it through packet manager `sudo apt-get install mplayer` on Debian derivative (Ubuntu) or `sudo zypper in MPlayer` on OpenSUSE distribution
    
## How to use Sarah

Simply run the script through terminal as `python3 speech_rec.py`. After the script is running, it's listening in the background for keyword to wake up.
To wake her up trigger her with `Hey Sarah` or `Hi Sarah`.
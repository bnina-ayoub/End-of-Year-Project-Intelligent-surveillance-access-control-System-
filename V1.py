import pyttsx3

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set the voice to use
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Set the speech rate
engine.setProperty('rate', 150)

# Speak the text
text = "Access approved"
engine.say(text)
engine.runAndWait()

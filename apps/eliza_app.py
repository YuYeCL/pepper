"""Example Application that answers questions posed in natural language using Wikipedia"""

from pepper.framework import *              # Contains Application Building Blocks
from pepper.knowledge import Wikipedia      # Class to Query Wikipedia using Natural Language
from pepper import config                   # Global Configuration File
from pepper.responder import eliza
from pepper.knowledge import sentences, animations



SPEAKER_NAME_THIRD = "Dear patient"
SPEAKER_NAME = "Dear patient"
SPEAKER_FACE = "HUMAN"
DEFAULT_SPEAKER = "Human"
NAME="knee k"
NAME="Sigmund Freud"

LOCATION_NAME = "Weesp, Herensingel 168"

IMAGE_VU = "https://www.vu.nl/nl/Images/VUlogo_NL_Wit_HR_RGB_tcm289-201376.png"
IMAGE_SELENE = "http://wordpress.let.vupr.nl/understandinglanguagebymachines/files/2019/06/7982_02_34_Selene_Orange_Unsharp_Robot_90kb.jpg"
IMAGE_LENKA = "http://wordpress.let.vupr.nl/understandinglanguagebymachines/files/2019/06/8249_Lenka_Word_Object_Reference_106kb.jpg"
IMAGE_BRAM = "http://makerobotstalk.nl/files/2018/12/41500612_1859783920753781_2612366973928996864_n.jpg"
IMAGE_PIEK = "http://www.cltl.nl/files/2019/10/8025_Classroom_Piek.jpg"

MIN_ANSWER_LENGTH = 4
# Override Speech Speed for added clarity!
config.NAOQI_SPEECH_SPEED = 80

images=[1,2,3,4,5,6,7,8,9,10]

class ElizaApplication(AbstractApplication,         # Every Application Inherits from AbstractApplication
                           StatisticsComponent,         # Displays Performance Statistics in Terminal
                           SpeechRecognitionComponent,  # Enables Speech Recognition and the self.on_transcript event
                           TextToSpeechComponent):      # Enables Text to Speech and the self.say method


    def __init__(self, application):
        """Greets New and Known People"""
        self.name_time = {}  # Dictionary of <name, time> pairs, to keep track of who is greeted when

        super(ElizaApplication, self).__init__(application)

        IntroductionIntention(self).speech()
        sleep(2.5)

    def on_transcript(self, hypotheses, audio):
        """
        On Transcript Event.
        Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        hypotheses: List[ASRHypothesis]
            Hypotheses about the corresponding utterance
        audio: numpy.ndarray
            Utterance audio
        """

        # Choose first ASRHypothesis and interpret as question
        answer=""
        for h in hypotheses:

            question = h.transcript

            answer = eliza.analyzefirst(question)

            if answer:
                # Tell Answer to Human
                self.say(answer)

            if answer=="really?":
                self.say("Look at the next situation in your life and tell me what you feel", animations.BOW)

            if answer:
                break

        if answer=="Let me see....":
            question = hypotheses[0].transcript

            answer = eliza.analyze(question)

            if answer:
                # Tell Answer to Human
                self.say(answer)





class IntroductionIntention(AbstractIntention, ElizaApplication):


    def speech(self):
        # 1.1 - Welcome
        self.say("Hello knee k. Welcome to my clinic", animations.BOW)
        self.say("My name is "+NAME)
        self.say("I am your best friend and personal therapist", animations.MODEST)
        self.say("How do you feel today?", animations.FRIENDLY)




if __name__ == "__main__":

    # Get Backend from Global Configuration File
    backend = config.get_backend()


    # Create Application with given Backend
    application = ElizaApplication(backend)

    # Run Application
    application.run()

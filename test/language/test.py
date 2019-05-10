from pepper.language import *
from pepper.brain import LongTermMemory
from pepper.framework import UtteranceHypothesis
from pepper.language.generation.reply import reply_to_question, reply_to_statement


def test():
    utterances = ["who can fly"]
    chat = Chat("Lenka", None)
    brain = LongTermMemory()
    for utterance in utterances:
        chat.add_utterance([UtteranceHypothesis(utterance, 1.0)], False)
        chat.last_utterance.analyze()

        x = chat.last_utterance.triple

        if chat.last_utterance.type == language.UtteranceType.QUESTION:
            brain_response = brain.query_brain(chat.last_utterance)
            reply = reply_to_question(brain_response)
        else:
            brain_response = brain.update(chat.last_utterance, reason_types=True)
            reply = reply_to_statement(brain_response, chat.speaker, brain)

        print(reply)

    return


if __name__ == "__main__":
    test()

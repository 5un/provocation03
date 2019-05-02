from __future__ import print_function
import time
import pyaudio
import dialogflow_v2 as dialogflow
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account
import board
import neopixel
from intent_handler import IntentHandler

def detect_intent_stream(project_id, session_id, language_code):
    """Returns the result of detect intent with streaming audio as input.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    
    handler = IntentHandler()
    
    # Init Cloud SpeechClient
    credentials = service_account.Credentials.from_service_account_file('./secret/cloud-speech.json')
    self.speech_client = speech.SpeechClient(credentials=credentials)

    # Init DialogFlow
    session_client = dialogflow.SessionsClient.from_service_account_file('./secret/dialogflow.json')

    # Note: hard coding audio_encoding and sample_rate_hertz for simplicity.
    audio_encoding = dialogflow.enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16
    SAMPLE_RATE_HERTZ = 16000

    FORMAT = pyaudio.paInt16 # We use 16 bit format per sample
    CHANNELS = 1
    CHUNK = 4096 # 1024 bytes of data read from the buffer
    RESPEAKER_INDEX = 2
    MAX_RECORD_TIME = 10.0 # Play with these

    audio = pyaudio.PyAudio()

    session_path = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session_path))

    def request_generator():
        # query_input = dialogflow.types.QueryInput(audio_config=audio_config)

        # # The first request contains the configuration.
        # yield dialogflow.types.StreamingDetectIntentRequest(
        #     session=session_path, query_input=query_input)

        # Claim the microphone
        stream = audio.open(format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE_HERTZ, 
            input=True,
            input_device_index=RESPEAKER_INDEX)#,
            #frames_per_buffer=CHUNK)

        # Here we are reading small chunks of audio data from a local
        # audio file.  In practice these chunks should come from
        # an audio input device.
        
        record_start_time = time.time()
        while True:
            chunk = stream.read(CHUNK)
            print('chunk')
            if not chunk:
                print('chunk is empty')
                break

            # Yield a CloudSpeech request
            yield types.StreamingRecognizeRequest(audio_content=chunk)

            record_duration = time.time() - record_start_time
            if record_duration > MAX_RECORD_TIME:
                break

        # try to not close the stream?
        stream.stop_stream()
        stream.close()

    while True:

        config = types.RecognitionConfig(
                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=SAMPLE_RATE_HERTZ,
                language_code='en-US')
        streaming_config = types.StreamingRecognitionConfig(config=config)

        requests = request_generator()
        responses = speech_client.streaming_recognize(streaming_config, requests)

        print('=' * 20)
        try:
            collected_text = ''
            for response in responses:
                # Once the transcription has settled, the first result will contain the
                # is_final result. The other results will be for subsequent portions of
                # the audio.
                for result in response.results:
                    print('Finished: {}'.format(result.is_final))
                    print('Stability: {}'.format(result.stability))
                    alternatives = result.alternatives
                    # The alternatives are ordered from most likely to least.
                    max_confidence = 0
                    max_confidence_text = ''
                    for alternative in alternatives:
                        print('Confidence: {}'.format(alternative.confidence))
                        print(u'Transcript: {}'.format(alternative.transcript))
                        if alternative.confidence > max_confidence:
                            max_confidence = alternative.confidence
                            max_confidence_text = alternative.transcript
                    collected_text += ' ' + max_confidence_text

            utterance = collected_text[:min(len(collected_text), 255)]
            print('collected_text:', collected_text)

            # TODO, do text recognition
            # for text in texts:
            if len(collected_text) > 0:
                text_input = dialogflow.types.TextInput(
                    text=utterance, language_code=self.language_code)

                query_input = dialogflow.types.QueryInput(text=text_input)

                response = self.session_client.detect_intent(
                    session=self.session_path, 
                    query_input=query_input)

                query_result = response.query_result

                if query_result is not None:
                    print('=' * 20)
                    print('Query text: {}'.format(query_result.query_text))
                    print('Detected intent: {} (confidence: {})\n'.format(
                        query_result.intent.display_name,
                        query_result.intent_detection_confidence))
                    print('Query Text Sentiment Score: {}\n'.format(
                        response.query_result.sentiment_analysis_result
                        .query_text_sentiment.score))
                    print('Query Text Sentiment Magnitude: {}\n'.format(
                        response.query_result.sentiment_analysis_result
                        .query_text_sentiment.magnitude))
                    handler.handle_intent(query_result)

        except KeyboardInterrupt:
            print('KeyboardInterrupt, exiting...')
            handler.clean_up()
            break
        except Exception as e:
            print('Exception!!', e)

# Initial Blinking
pixels = neopixel.NeoPixel(board.D21, 1)
for i in range(3):
    pixels.fill((255,255,255))
    time.sleep(0.5)
    pixels.fill((0,0,0))
    time.sleep(0.5)
pixels.fill((0,0,0))

detect_intent_stream('provocation03', 'test1', 'en')


from __future__ import print_function
import time
import pyaudio
import audioop
import dialogflow_v2 as dialogflow
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account
from intent_handler import IntentHandler
from led_helper import LEDHelper

leds = LEDHelper()

def detect_intent_stream(project_id, session_id, language_code):
    """Returns the result of detect intent with streaming audio as input.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    global leds
    handler = IntentHandler(leds)
    
    # Init Cloud SpeechClient
    credentials = service_account.Credentials.from_service_account_file('./secret/cloud-speech.json')
    speech_client = speech.SpeechClient(credentials=credentials)

    # Init DialogFlow
    session_client = dialogflow.SessionsClient.from_service_account_file('./secret/dialogflow.json')

    # Note: hard coding audio_encoding and sample_rate_hertz for simplicity.
    audio_encoding = dialogflow.enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16
    SAMPLE_RATE_HERTZ = 16000

    FORMAT = pyaudio.paInt16 # We use 16 bit format per sample
    CHANNELS = 1
    CHUNK = 4096 # 1024 bytes of data read from the buffer
    RESPEAKER_INDEX = 2
    MAX_RECORD_TIME = 50.0 # Play with these
    MAX_IDLE_TIME = 1.5
    VOLUME_RMS_THRESHOLD = 2000
    SHOW_RMS = False

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
        voice_began = False
        idle_time = 0
        while True:
            chunk = stream.read(CHUNK)
            # print('chunk')
            if not chunk:
                print('chunk is empty')
                break

            # Yield a CloudSpeech request
            yield types.StreamingRecognizeRequest(audio_content=chunk)


            rms = audioop.rms(chunk, 2)
            if SHOW_RMS:
                print('rms', rms)
            is_speaking = rms > VOLUME_RMS_THRESHOLD

            if not voice_began:
                # print('  Idle Time', time.time() - timeSinceRecognitionStart)
                if time.time() - record_start_time > MAX_RECORD_TIME:
                    break
                elif is_speaking:
                    voice_began = True
                    idle_time = time.time()
            else:
                # print('   Speak Time', time.time() - idleTime)
                if is_speaking:
                    idle_time = time.time()
                    if time.time() - record_start_time > MAX_RECORD_TIME:
                        break
                else:
                    if time.time() - idle_time > MAX_IDLE_TIME:
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
                    text=utterance, language_code=language_code)

                query_input = dialogflow.types.QueryInput(text=text_input)

                response = session_client.detect_intent(
                    session=session_path, 
                    query_input=query_input)

                query_result = response.query_result

                if query_result is not None:
                    print('=' * 20)
                    print('Query text: {}'.format(query_result.query_text))
                    print('Detected intent: {} (confidence: {})\n'.format(
                        query_result.intent.display_name,
                        query_result.intent_detection_confidence))

                    handler.handle_intent(query_result)

        except KeyboardInterrupt:
            print('KeyboardInterrupt, exiting...')
            handler.clean_up()
            break
        except Exception as e:
            print('Exception!!', e)

# Initial Blinking
leds.knight_rider(num_repeat=3, duration=0.1)
detect_intent_stream('provocation03', 'test1', 'en')


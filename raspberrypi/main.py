from __future__ import print_function
import time
import pyaudio
import audioop
import dialogflow_v2 as dialogflow
import board
import neopixel
from intent_handler import IntentHandler
from led_helper import LEDHelper

leds = LEDHelper()

def detect_intent_stream(project_id, session_id, language_code):
    """Returns the result of detect intent with streaming audio as input.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    
    # Bring intent handler from outside scope
    global leds
    intent_handler = IntentHandler(leds)
    
    session_client = dialogflow.SessionsClient.from_service_account_file('./secret/dialogflow.json')

    # Note: hard coding audio_encoding and sample_rate_hertz for simplicity.
    audio_encoding = dialogflow.enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16
    sample_rate_hertz = 16000

    FORMAT = pyaudio.paInt16 # We use 16 bit format per sample
    CHANNELS = 1
    CHUNK = 4096 # 1024 bytes of data read from the buffer
    RESPEAKER_INDEX = 2
    MAX_RECORD_TIME = 10.0
    MAX_IDLE_TIME = 3.0
    VOLUME_RMS_THRESHOLD = 2000
    SHOW_RMS = True

    audio = pyaudio.PyAudio()

    session_path = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session_path))

    def request_generator(audio_config):
        query_input = dialogflow.types.QueryInput(audio_config=audio_config)

        # The first request contains the configuration.
        yield dialogflow.types.StreamingDetectIntentRequest(
            session=session_path, query_input=query_input)

        # Claim the microphone
        stream = audio.open(format=FORMAT,
            channels=CHANNELS,
            rate=sample_rate_hertz, 
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
            if not chunk:
                print('chunk is empty')
                break

            # The later requests contains audio data.
            yield dialogflow.types.StreamingDetectIntentRequest(
                input_audio=chunk)

            # record_duration = time.time() - record_start_time
            # if record_duration > MAX_RECORD_TIME:
            #     break

            rms = audioop.rms(chunk, 2)
            if SHOW_RMS:
                print('rms', rms)
            is_speaking = rms > VOLUME_RMS_THRESHOLD

            if not voice_began:
                # print('  Idle Time', time.time() - timeSinceRecognitionStart)
                if is_speaking:
                    voice_began = True
                    idle_time = time.time()
            else:
                # print('   Speak Time', time.time() - idleTime)
                if is_speaking:
                    idle_time = time.time()
                else:
                    if time.time() - idle_time > MAX_IDLE_TIME:
                       break 

        stream.stop_stream()
        stream.close()

    audio_config = dialogflow.types.InputAudioConfig(
        audio_encoding=audio_encoding, language_code=language_code,
        sample_rate_hertz=sample_rate_hertz)

    while True:
        requests = request_generator(audio_config)
        responses = session_client.streaming_detect_intent(requests)

        print('=' * 20)
        try:
            for response in responses:
                 print('Intermediate transcript: "{}".'.format(
                        response.recognition_result.transcript))

            # Note: The result from the last response is the final transcript along
            # with the detected content.
            query_result = response.query_result

            print('=' * 20)
            print('Query text: {}'.format(query_result.query_text))
            print('Detected intent: {} (confidence: {})\n'.format(
                query_result.intent.display_name,
                query_result.intent_detection_confidence))
            # print('Fulfillment text: {}\n'.format(
            #     query_result.fulfillment_text))

            if query_result is not None:
                intent_handler.handle_intent(query_result)
        except KeyboardInterrupt:
            print('KeyboardInterrupt, exiting...')
            intent_handler.clean_up()
            break
        except Exception as e:
            print('Exception!!', e)

leds.knight_rider(num_repeat=3, duration=0.1)
detect_intent_stream('provocation03', 'test1', 'en')


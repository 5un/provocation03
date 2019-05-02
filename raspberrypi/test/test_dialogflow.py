from __future__ import print_function
try:
    import time
    import pyaudio
    import dialogflow_v2 as dialogflow
except:
    print("Something didn't import")

def detect_intent_stream(project_id, session_id, language_code):
    """Returns the result of detect intent with streaming audio as input.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    session_client = dialogflow.SessionsClient.from_service_account_file('./secret/dialogflow.json')

    # Note: hard coding audio_encoding and sample_rate_hertz for simplicity.
    audio_encoding = dialogflow.enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16
    sample_rate_hertz = 16000

    FORMAT = pyaudio.paInt16 # We use 16 bit format per sample
    CHANNELS = 1
    CHUNK = 4096 # 1024 bytes of data read from the buffer
    RESPEAKER_INDEX = 2
    MAX_RECORD_TIME = 10.0

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
        while True:
            chunk = stream.read(CHUNK)
            if not chunk:
                break

            # The later requests contains audio data.
            yield dialogflow.types.StreamingDetectIntentRequest(
                input_audio=chunk)

            record_duration = time.time() - record_start_time
            if record_duration > MAX_RECORD_TIME:
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
                if response.recognition_result is not None:
                    print('Intermediate transcript: "{}".'.format(
                            response.recognition_result.transcript))
                else:
                    print('No result available')
                    print(response)

            # Note: The result from the last response is the final transcript along
            # with the detected content.
            query_result = response.query_result

            print('=' * 20)
            print('Query text: {}'.format(query_result.query_text))
            print('Detected intent: {} (confidence: {})\n'.format(
                query_result.intent.display_name,
                query_result.intent_detection_confidence))
            print('Fulfillment text: {}\n'.format(
                query_result.fulfillment_text))
        except KeyboardInterrupt:
            print('KeyboardInterrupt, exiting...')
            break
        except:
            print('Exception!!')


detect_intent_stream('provocation03', 'test1', 'en')
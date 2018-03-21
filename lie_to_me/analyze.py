from random import *
# micro expressions happen in 1/25th of a second or 15 frames

# microexpression_analyzer:
#   Function parameters:
#       **emotions: A dictionary of emotions and their coresponding
#       number value from 1 to 100 and the index is
#       the current frame e.g emotions[0]['anger']
#   Return:
#       The function returns a list of timestamps where a
#       possible micro expression was detechted
#


def microexpression_analyzer(emotions, num_of_frames, fps):
    current_max = 0
    previous_max = 0
    microexpression_loop_counter = 0
    flag = 0
    previous_emotion = ''
    emotion_at_start = ''
    list_of_emotions = ['anger', 'contempt', 'disgust', 'fear', 'happiness', 'joy', 'sadness', 'surprise']
    timestamps = []

    for i in range(num_of_frames):
        # Store current max of emotions
        if not emotions:
            continue

        current_max = max(emotions[i]['anger'],
                          emotions[i]['contempt'],
                          emotions[i]['disgust'],
                          emotions[i]['happiness'],
                          emotions[i]['joy'],
                          emotions[i]['sadness'],
                          emotions[i]['surprise'])

        # Store the current emotion
        for key in emotions[i].keys():
            if current_max == emotions[i][key]:
                current_emotion = key

        if i == 0:
            previous_max = current_max
            previous_emotion = current_emotion
            continue

        # If previous_emotion is not equal to current_emotion then reset the counter and emotion_at_start
        if previous_emotion != current_emotion:
            if microexpression_loop_counter != 15:
                microexpression_loop_counter = 0
                microexpression_loop_counter += 1
                emotion_at_start = previous_emotion

        # Checking to see if the expression stayed the same, if so we increment a
        elif previous_emotion == current_emotion:
            microexpression_loop_counter += 1
        # If the micro expression changed back to the original expression it came from then
        # We have a possible lie and the timestamp is recorded.
        if emotion_at_start == current_emotion and microexpression_loop_counter == 15:
            print('Entered if')
            seconds = i / fps
            minutes = seconds / 60
            if minutes < 1:
                minutes = 0
            timestamps.append('{}:{}'.format(minutes, seconds))
            microexpression_loop_counter = 0
            emotion_at_start = ''
            flag = 0
            continue
        # Record current max and previous max for next the analysis of the next ones
        previous_max = current_max
        previous_emotion = current_emotion

    return timestamps

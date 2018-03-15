""" Utility functions for analysis """

def detect_blinks(eye_closure_list):
    """
        Returns the frames where blinks occured
    """
    eye_cl_thresh = 70          # eye closure >= 70 to be considered closed
    eye_cl_consec_frames = 4    # 4 or more consecutive frames to be considered a blink
    counter = 0

    # Array of frames where blink occured
    blink_frames = []

    for frame_number, eye_thresh in enumerate(eye_closure_list):
        if eye_thresh > eye_cl_thresh:
            counter += 1
        else:
            if counter >= eye_cl_consec_frames:
                blink_frames.append(frame_number)
            counter = 0

    return blink_frames

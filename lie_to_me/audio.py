from math import cos, log10, pi
from numpy import abs
from lie_to_me import thinkdsp

# All the utterances that were collected during tests were
# sampled at 11 kHz and each sample is represented in 8 bits.
# In this analysis the speech signals are divided into
# frames of length 256 samples (.023 sec.).

# Path to files
input_path = 'input.mp4'
audio_path = 'audio.wav'
images_path = 'images/frame%d.jpg'

# Value from the research paper
samples_per_frame = 256


def split(input_file):
    """ Splits audio file into frames
    and applies hamming window.

    :param input_file: path to audio file
    :return: array of waves (frames)
    """
    frames = []
    wave = thinkdsp.read_wave(input_file)

    # Some values that we might need
    totframes = len(wave.ts)
    framerate = wave.framerate
    length = totframes / framerate
    framelength = samples_per_frame / framerate
    numframes = int(length / framelength)

    print('Framelength:', framelength, 'seconds')
    print('Frames to calcuate:', numframes)

    for index in range(numframes):
        print(index)
        currentstart = index * framelength
        frames.append(wave.segment(start=currentstart, duration=framelength))

    return frames


# Computing Hamming Window
def applyhamming(framearray):
    """Multiplying each frame with a hamming window

    :param framearray: array of waves (frames)
    :return: array of hamming window filtered frames
    """
    pi2 = 2 * pi
    hammingwindow = []

    # Setup hamming window array
    for index in range(samples_per_frame):
        hammingwindow.append((0.54 + 0.46 * (cos(pi2 * index / 255))))

    # Multiplying each frame with the hamming window
    for framenumber in range(len(framearray)):
        for samplenumber in range(len(hammingwindow)):
            framearray[framenumber].ys[samplenumber] *= hammingwindow[samplenumber]

    return framearray


# Computing Energy
def energy(framearray):
    """ Calculates the energy of each frame

    :param framearray: array of waves (frames)
    :return: array of energy per frame
    """

    frame_energy = []

    for framenumber in range(len(framearray)):
        frame_energy.append([0])
        for samplenumber in range(samples_per_frame):
            frame_energy[framenumber] += ((framearray[framenumber].ys[samplenumber])**2)
    return frame_energy


# creating spectrums, have to implement so only real
def fourier(framearray):
    """ Fourier transforms all waves from array.
    (Real values only)

    :param framearray: array of waves (frames)
    :return: array of FFT waves (spectrums)
    """

    fourier_frame = []

    for frame in framearray:
        index = frame.make_spectrum()
        fourier_frame.append(index)

    return fourier_frame


# calculating logarithm of magntiude spectrum
def inverse_fourier(fourierarray):
    """ Apply logarithm to magnitude spectrum
    and IFFT to get output of homomorphic operation

    :param fourierarray: array of spectrums (frames)
    :return: array of IFFT spectrums (waves)
    """

    framearray = []

    # Computing logarithm of the magnitude spectrum of the frame
    # 20log10(frame) == 20log10(i) i sample between 0 - 255
    # Other spectral analysis uses 10log10
    for frame in fourierarray:
        framearray.append([])
        for samplenumber in range(len(frame.hs)):
            frame.hs[samplenumber] = 20 * log10(abs(frame.hs[samplenumber]))

    # ifft back
    for framenumber in range(len(framearray)):
        framearray[framenumber] = fourierarray[framenumber].make_wave()

    # fix first sample in first frame
    for frame in framearray:
        frame.ys[0] = 0

    return framearray


# High time sampling for the peak. Different between male and women/children
def sampling(framearray):
    """ High Sample Cepstum depending on Sex
    (Male default)

    :param framearray: array of frames (waves)
    :return framesample: array of sampled cepstums (waves)
    """

    index = 40  # or 20 for female
    framesample = []

    # Split frames and calculate maximum amplitude
    for frame in framearray:
        framesplit = frame.ys[index:int(samples_per_frame / 2)].tolist()
        value = max(framesplit)
        maxindex = framesplit.index(value) + index
        framesample.append(thinkdsp.Wave(frame.ys[maxindex],
                                         frame.ts[maxindex],
                                         frame.framerate))

    # Amplitude of the signal at Pitch Period
    # Pitch Period is index(framesample) (Not sure what this is yet)
    # F(Pitch Period) is frame number with pitch period given.

    return framesample


# Calculate mean energy of utterance
def meanenergy(energyarray):
    """ Mean Energy audio feature:
    Low predictability rate (61%)

    :param energyarray: array of energies per frame (waves)
    :return meanframe: array of mean energies per frame (waves)
    :return meanaudio: average energy throughout file
    """
    meanframe = []
    meanaudio = 0
    for energies in energyarray:
        mean = float(energies/len(energyarray))
        meanaudio += energies
        meanframe.append(mean)

    meanaudio /= len(energyarray)

    return meanframe, meanaudio


def maxpitchamp(framearray):
    """ Max Pitch Amplitude audio feature:
    High Predictability rate (86%)

    :param framearray: array of sampled cepstums (waves)
    :return maxpitch: array of max pitch amplitudes
    :return maxAmp: maximum pitch amplitude
    """

    maxpitch = []

    for frames in framearray:
        maxpitch.append(max(frames.ys))
        print(frames.ts)

    print("Max Pitch Amp stuff:")

    maxamp = max(maxpitch)
    return maxpitch, maxamp


def vowelduration(framearray, maxamp):
    """ Vowel Duration audio feature:
    High Predictability rate (82%)

    :param framearray: array of sampled cepstums (waves)
    :param maxamp: maximum pitch amplitude
    :return vowels: array of vowel durations in msec
    """

    vowels = []
    v = 0

    threshold = 0.1 * maxamp
    for frames in framearray:

        for sample in frames.ys:
            if sample >= threshold:
                v += 1

        vowels.append(0.23*(v/2))
        v = 0

    print("Vowel Duration stuff:")
    return vowels

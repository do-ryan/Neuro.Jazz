from music21 import *
from datavisualization import *
import numpy as np
import glob

'''

takes in two folders of .midi files with just one track (authentic and placeholder non-authentic) and creates one .npy file representing (midi files x velocity x pitch x time), and another representing labels.

'''

def subdivide_notes(pitches, note_offsets, volume, note_durations):
# takes in notes (their pitches) and their respective time offsets, volumes and durations (all in numpy arrays), and returns a 2D numpy array representing one hot encoded pitch vs. time, scaled by volume (volume(pitch, time))

        SUBDIVISION = 24 # rhythm in the midi files can be subdivided into a combination of 16th triplets (1/6 of a quarter note) and 32nd notes (1/8 of quarter notes). Therefore, the time steps in the array will be in increments of 1/24 of a quarter note (least common denominator).

        max_offset = np.amax(note_offsets)
        instance_duration = max_offset + np.max(note_durations) # the duration is bounded by the last note offset + max note duration in the instance

        subdivided_array = np.zeros((int(pitch.Pitch('C10').ps+1), int(instance_duration*SUBDIVISION))) # the size of the time is based on current instance. padding/cropping will occur later by aggregating entire collection of instances.

        for i in range(pitches.shape[0]):
                for sub_beat in range(int(note_durations[i]*SUBDIVISION)):
                        subdivided_array[int(pitches[i]), int(note_offsets[i]*SUBDIVISION+sub_beat)] = volume[i]
        return subdivided_array

def midi_to_npy(midifilepath):
# takes in a midi filepath and returns a volume scaled one-hot encoded 2d npy array pitch x time. The midi file only has one track

        midi_stream = converter.parse(midifilepath).parts[0] # midifiles should only have 1 part (temporarily?)
        pitches, parent_objects = extract_notes(midi_stream.flat.notes) # pitches is a list of floats of all pitch "instances in the midi file, parent_objects is a mix of note/chord objects. chord objects are repeated for each note in the chord

        note_offsets = np.asarray([n.offset for n in parent_objects]) # start time of notes in terms of quarter notes from start
        volume = np.asarray([n.volume.velocityScalar for n in parent_objects])
        note_durations = np.asarray([n.duration.quarterLength for n in parent_objects]) # durations of notes in terms of quarter notes

        return subdivide_notes(np.asarray(pitches), note_offsets, volume, note_durations)

def main():

        authentic_filepaths = glob.glob('training_data/authentic/*.mid*') # authentic midi filepaths
        nonauthentic_filepaths = glob.glob('training_data/nonauthentic/*.mid*') # placeholder nonauthentic midi filepaths
        instances = np.array([])
        labels = np.array([])

        for file in authentic_filepaths:
                print("parsing ", file)
                list.append(instances, midi_to_npy(file))
                list.append(labels, 1) # 1 represents authentic

        for file in nonauthentic_filepaths:
                print("parsing ", file)
                np.append(instances, midi_to_npy(file))
                np.append(labels, 0)

        np.save('./data/instances.npy', instances)
        np.save('./data/labels.npy', labels)
        print('Instances and labels saved.')
        # save data

if __name__ == "__main__":
        main()
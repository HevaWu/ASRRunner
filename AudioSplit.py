# coding=utf-8

from pydub import AudioSegment
from pydub.utils import make_chunks, mediainfo

from ASRRunner import ASRRunner

import math
import os

# If audio file is too large, split it to 5MB for each chunk first, then save merge its result and save to new file
class AudioSplit(object):
    def __init__(self, folder_name, dir_path):
        super().__init__()
        self.folder_name = folder_name
        self.dir_path = dir_path

    def run(self):
        folder_path = os.path.join(self.dir_path, self.folder_name)
        for file_name in os.listdir(folder_path):
            print("Start Handle" + file_name)
            self.process_file(file_name, folder_path)

    def process_file(self, file_name, folder_path):
        file_path = os.path.join(folder_path, file_name)
        file_type = file_name.split('.')[1]
        audio = AudioSegment.from_file(file_path, file_type)

        wav_cache_path = os.path.join(self.dir_path, "audio.wav")
        audio.export(wav_cache_path, format="wav")
        wav_audio = AudioSegment.from_file(wav_cache_path , "wav")

        channel_count = wav_audio.channels    #Get channels
        sample_width = wav_audio.sample_width #Get sample width
        duration_in_sec = len(wav_audio) / 1000#Length of audio in sec
        sample_rate = wav_audio.frame_rate

        print ("sample_width=", sample_width)
        print ("channel_count=", channel_count)
        print ("duration_in_sec=", duration_in_sec)
        print ("frame_rate=", sample_rate)
        bit_rate =16  #assumption , you can extract from mediainfo("test.wav") dynamically

        wav_file_size = (sample_rate * bit_rate * channel_count * duration_in_sec) / 8
        print ("wav_file_size = ",wav_file_size)

        file_split_size = 5000000  # 10Mb OR 10, 000, 000 bytes

        #Get chunk size by following method #There are more than one ofcourse
        #for  duration_in_sec (X) -->  wav_file_size (Y)
        #So   whats duration in sec  (K) --> for file size of 10Mb
        #  K = X * 10Mb / Y

        chunk_length_in_sec = math.ceil((duration_in_sec * file_split_size ) /wav_file_size)   #in sec
        chunk_length_ms = chunk_length_in_sec * 1000
        chunks = make_chunks(wav_audio, chunk_length_ms)


        # chunk_length_ms = 600000 # pydub calculates in millisec, 10 minutes
        # chunks = make_chunks(wav_audio, chunk_length_ms) # Make chunks of one sec

        # Export all of the individual chunks as wav files

        cache_folder_name = "splitCache"
        output_folder_path = os.path.join(self.dir_path, cache_folder_name)
        output_file_name = file_name.split('.')[0]
        for i, chunk in enumerate(chunks):
            chunk_name = output_file_name + "-{0}.wav".format(i)
            print ("exporting", chunk_name)
            chunk_path = os.path.join(output_folder_path, chunk_name)
            chunk.export(chunk_path, format='wav')

        self.process_and_join_split_record(cache_folder_name, output_file_name, len(chunks))

    def process_and_join_split_record(self, cache_folder_name, file_name, split_file_count):
        cache_folder_path = os.path.join(self.dir_path, cache_folder_name)
        runner = ASRRunner(self.dir_path, cache_folder_name)
        runner.run()

        # join all txt file to one file
        data = ""
        for i in range(split_file_count):
            chunk_name = file_name + "-{0}.txt".format(i)
            chunk_path = os.path.join(cache_folder_path, chunk_name)
            with open(chunk_path) as f:
                data += f.read() + "\n"

        # write data to new file
        merge_file_name = file_name + ".txt"
        with open(os.path.join(self.folder_name, merge_file_name), 'w') as f:
            f.write(data)

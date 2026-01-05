# asssuming
# we have 6 files in this case
# all stream has the same frame rate 29.97
# all stream has same lenght 2:40.00 sec
# number of total cross is 15

parameter = {
   "meta_info" : {
      "num_stream": 6,
      "metric": "time",
      "frame_rate": 29.97,
      "num_frames": 0,         # (2 * 60 + 40 + 0 / 60) * 29.97,
      "init_time": 0,          # start at somewhere in the middle
      "duration": 160,          # 2 * 60 + 40 + 0 / 60,
      "num_vector_pair": 3,    # at least 1, maximum 3 recommended
      "num_cross": 15,         # number of crossedit
      "first_stream": 0,       # first stream can be any integer between 0 and 5
      "folder_path": "data/"
   },
   "streams": [
      {
         "file": "sync_ive_baddie_1.mp4",
         "start": 0,
         "end": 0
      },
      {
         "file": "sync_ive_baddie_2.mp4",
         "start": 0,
         "end": 0
      },
      {
         "file": "sync_ive_baddie_3.mp4",
         "start": 0,
         "end": 0
      },
      {
         "file": "sync_ive_baddie_4.mp4",
         "start": 0,
         "end": 0
      },
      {
         "file": "sync_ive_baddie_5.mp4",
         "start": 0,
         "end": 0
      },
      {
         "file": "sync_ive_baddie_6.mp4",
         "start": 0,
         "end": 0
      }
   ],
   "cross_points": [
      {
         "frame_id": 257,      # we can consider time in stead of frame number, I prefer time though
         "next_stream": 1,     # any integer between 0 and 5 except the first one, 0 in this case, previous stream number not rquired. including just for debugging?
         "vector_pairs": [
            {
               "vector1": [100, 200, 120, 210],
               "vector2": [105, 205, 121, 211]
            }
            ((100, 200, 120, 210), ()),  # ( (x11, y11, w11, h11), (x12, y12, w12, h12) ) => (vector in pre stream), (vector in next steam), 1st feature
            ((200, 300, 50, 10), (110, 205, 45, 7)),       # ( (x21, y21, w21, h21), (x22, y22, w22, h22) ) => (vector in pre stream), (vector in next steam), 2nd feature
            ((400, 200, 50, 10), (110, 205, 45, 7))        # ( (x31, y31, x32, y32), (x32, y32, w32, h32) ) => (vector in pre stream), (vector in next steam), 3rd feature
         ],
      },
      {
         "frame_id": 551,     # we can consider time in stead of frame number, I prefer time though
         "next_stream": 5,     # any integer between 0 and 5 except the first one, 0 in this case, previous stream number not rquired. including just for debugging?
         "vector_pairs": [
            ((100, 200, 120, 210), (105, 205, 121, 211)),  # ( (x11, y11, w11, h11), (x12, y12, w12, h12) ) => (vector in pre stream), (vector in next steam), 1st feature
            ((200, 300, 50, 10), (110, 205, 45, 7)),       # ( (x21, y21, w21, h21), (x22, y22, w22, h22) ) => (vector in pre stream), (vector in next steam), 2nd feature
            ((400, 200, 50, 10), (110, 205, 45, 7))        # ( (x31, y31, x32, y32), (x32, y32, w32, h32) ) => (vector in pre stream), (vector in next steam), 3rd feature
         ],
      }
   ],
   "scene_list": [
      [100, 500, 1000, 1500],    # scene list for the stream 0
      [200, 500, 1500, 3000],    # scene list for the stream 1
      [100, 510, 1000, 1500],    # scene list for the stream 2
      [400, 500, 1000, 1500],    # scene list for the stream 3
      [150, 500, 1000, 1500],    # scene list for the stream 4
      [800, 500, 1000, 1500]     # scene list for the stream 5
   ]
}

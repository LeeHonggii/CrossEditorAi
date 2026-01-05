import json

# a = {"ip": "8.8.8.8"}
# print(a)
#
# b = json.dumps(a)
# print(b)
# print(type(b))
#
# # quiz
# c = json.loads(b)
# print(c)
# print(type(c))


# d = '''{
#    "time": "03:53:25 AM",
#    "milliseconds_since_epoch": 1362196405309,
#    "date": "03-02-2013"
# }'''
d = '''{
   "time": [
    {"a":1}, {"b": 2}, {"c": 3}
   ]
}'''

#
# print(type(json.loads(d)))
# e = json.loads(d)
# print(e.values())
# print(list(e.values()))
# print(list(json.loads(d).values()))

# for i in e:
#    print(e[i])
# for i, j in e.items():
#    print(j)
# # for i, j in enumerate(e):
# #    print(e[j])
# print(e['time'])
# print(e['milliseconds_since_epoch'])
# print(e['date'])

parameter = {
    "meta_info": {
        "num_stream": 6,
        "frame_rate:": 29.97,
        "num_frames": 4795.2,  # (2 * 60 + 40 + 0 / 60) * 29.97,
        "duration": 16,  # 2 * 60 + 40 + 0 / 60,
        "num_vector_pair": 3,  # at least 1, maximum 3 recommended
        "num_cross": 15,  # number of crossedit
        "first_stream": 0,  # first stream can be any integer between 0 and 5
        "folder_path": "data"
    },
    "streams": [
        {
            "file": "filepath0",
            "start": 0
        },
        {
            "file": "filepath1",
            "start": 0
        },
        {
            "file": "filepath2",
            "start": 0
        },
        {
            "file": "filepath3",
            "start": 0
        },
        {
            "file": "filepath4",
            "start": 0
        },
        {
            "file": "filepath5",
            "start": 0
        }
    ],
    "cross_points": [
        {
            "frame_id": 257,  # we can consider time in stead of frame number, I prefer time though
            "next_stream": 1, # any integer between 0 and 5 except the first one, 0 in this case, previous stream number not rquired. including just for debugging?
            "vector_pairs": [
                {
                    "vector1": [100, 200, 120, 210],    # [x11, y11, w11, h11] => (vector in pre stream) in 1st feature
                    "vector2": [105, 205, 121, 211]     # [x12, y12, w12, h12] => (vector in post stream)
                },
                {
                    "vector1": [100, 200, 120, 210],
                    "vector2": [105, 205, 121, 211]
                },
                {
                    "vector1": [100, 200, 120, 210],
                    "vector2": [105, 205, 121, 211]
                }
            ],
        },
        {
            "frame_id": 551,  # we can consider time in stead of frame number, I prefer time though
            "next_stream": 5, # any integer between 0 and 5 except the first one, 0 in this case, previous stream number not rquired. including just for debugging?
            "vector_pairs": [
                {
                    "vector1": [100, 200, 120, 210],
                    "vector2": [105, 205, 121, 211]
                },
                {
                    "vector1": [100, 200, 120, 210],
                    "vector2": [105, 205, 121, 211]
                },
                {
                    "vector1": [100, 200, 120, 210],
                    "vector2": [105, 205, 121, 211]
                }
            ],
        }
    ],
    "scene_list": [
        [100, 500, 1000, 1500],  # scene list for the stream 0
        [200, 500, 1500, 3000],  # scene list for the stream 1
        [100, 510, 1000, 1500],  # scene list for the stream 2
        [400, 500, 1000, 1500],  # scene list for the stream 3
        [150, 500, 1000, 1500],  # scene list for the stream 4
        [800, 500, 1000, 1500]   # scene list for the stream 5
    ]
}

# b = json.dumps(parameter)
# json_string = json.dumps(parameter, ensure_ascii=False, indent=4)
b = json.dumps(parameter, ensure_ascii=False, indent=4)

# 파일에 저장
with open("data/output.txt", "w", encoding="utf-8") as file:
    file.write(b)

with open("data/output.txt", "r", encoding="utf-8") as file:
    json_string_from_file = file.read()

parameter_from_file = json.loads(json_string_from_file)
print(parameter_from_file)
print(type(parameter_from_file))

quit()
print("JSON 문자열이 output.txt 파일에 저장되었습니다.")
# # print(b)
# print(type(b))
#
# # quiz
# c = json.loads(parameter)
c = json.loads(b)
# print(c)
print(type(c))
print(c)
# print(c.values())
# print(list(e.values()))
# print(list(json.loads(d).values()))
# print(c["cross_points"]["vector_pairs"][0]["vector1"])
# print(c["cross_points"][0]["vector_pairs"][0]["vector1"])
# a, b, c, d = c["cross_points"][0]["vector_pairs"][0]["vector1"]
# print(a, b, c, d)


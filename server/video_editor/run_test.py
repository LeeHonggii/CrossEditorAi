import json
from video_editor import run_video_editor

if __name__ == "__main__":

    json_file = "data/output-jh6.json"
    with open(json_file, "r", encoding="utf-8") as file:
        json_string_from_file = file.read()
    parameter = json.loads(json_string_from_file)

    run_video_editor(parameter)

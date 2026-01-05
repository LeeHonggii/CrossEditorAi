from moviepy.editor import VideoFileClip, concatenate_videoclips
from math import radians, degrees, sin, cos, acos
from sympy import symbols, Eq, solve
import numpy as np
import bisect
import random
from line_add import prepare_sample

dot_product = lambda v1, v2: v1[0] * v2[0] + v1[1] * v2[1]
cross_product = lambda v1, v2: v1[0] * v2[1] - v1[1] * v2[0]
length = lambda v: (v[0]**2 + v[1]**2)**(1/2)
dist = lambda w, h: (w**2 + h**2)**(1/2)
maxx = max

# def vector_bigger(v1, v2):
#     return length(v1[2:]) >= length(v2[2:])


def calculate_signed_angle(v1, v2):
    dot_prod = dot_product(v1, v2)
    length_v1 = length(v1)
    length_v2 = length(v2)

    cos_theta = dot_prod / (length_v1 * length_v2)
    # print(cos_theta, dot_prod, length_v1, length_v2)
    if cos_theta > 1:
        cos_theta = 1
    angle_radians = acos(cos_theta)
    angle_degrees = degrees(angle_radians)

    cross_prod = cross_product(v1, v2)
    if cross_prod < 0:
        angle_degrees = -angle_degrees
    return angle_degrees


def find_intersection(x1, y1, a, x2, y2, b):
    x, y = symbols('x y')

    eq1 = Eq((x - x1)**2 + (y - y1)**2, a**2)
    eq2 = Eq((x - x2)**2 + (y - y2)**2, b**2)

    solutions = solve((eq1, eq2), (x, y))

    return solutions


def vector_difference(clip, v1, v2):
    width, height = clip.size
    center_x = int(width / 2)
    center_y = int(height / 2)

    x1, y1, w1, h1 = v1
    x2, y2, w2, h2 = v2
    x12, y12 = x1 + w1, y1 + h1
    x22, y22 = x2 + w2, y2 + h2
    # x1, y1, x12, y12 = v1
    # x2, y2, x22, y22 = v2
    # w1, h1 = x12 - x1, y12 - y1
    # w2, h2 = x22 - x2, y22 - y2

    diff_x = x1 - x2
    diff_y = y1 - y2
    distance = dist(diff_x, diff_y)
    length_1 = dist(w1, h1)
    length_2 = dist(w2, h2)
    ratio = length_1 / length_2

    rotate_angle = calculate_signed_angle((w1, h1), (w2, h2))

    return width, height, center_x, center_y, distance, diff_x, diff_y, ratio, rotate_angle, x1, y1, w1, h1, x12, y12, x2, y2, w2, h2, x22, y22


def get_adjusted_clip(clip, v1, v2):
    width, height, center_x, center_y, _, diff_x, diff_y, ratio, rotate_angle, x1, y1, w1, h1, _, _, x2, y2, w2, h2, _, _ = vector_difference(clip, v1, v2)
    # print(f"From [p1({x1}, {y1}), v1({w1}, {h1})] To [p2({x2}, {y2}), v2({w2}, {h2})]")
    # print(f"diff_x: {diff_x:.2f}, diff_y: {diff_y:.2f}, ratio: {ratio:.2f}, angle: {rotate_angle:.2f}")
    # # print(f"distance: {distance:.2f}, diff_x: {diff_x:.2f}, diff_y: {diff_y:.2f}, ratio: {ratio:.2f}, angle: {rotate_angle:.2f}")

    # 1) moving
    clip = clip.on_color(size=(width, height), color=(0, 0, 0), pos=(diff_x, diff_y))

    # 2) rotation
    distance_from_center = dist(x1 - center_x, y1 - center_y)
    if distance_from_center == 0:
        rotated_move_x = 0
        rotated_move_y = 0
    else:
        opposite_side = distance_from_center * sin(radians((abs(rotate_angle) / 2)))
        near_side = distance_from_center * cos(radians((abs(rotate_angle) / 2)))
        solution = find_intersection(x1, y1, opposite_side, center_x, center_y, near_side)
        # print(f"Signed angle between vectors: {rotate_angle:.2f} degrees")
        # print(solution)
        # print(f"distance_from_center: {distance_from_center:.2f} opposite_side: {opposite_side:.2f}, near_side: {near_side:.2f}")
        # print(solution)
        # print(f"rotated_move_x: {rotated_move_x:.2f}, rotated_move_x: {rotated_move_y:.2f}")

        i = 0 if rotate_angle > 0 else 1
        if len(solution) == 1:
            i = 0
        rotated_move_x = (solution[i][0] - x1) * 2
        rotated_move_y = (solution[i][1] - y1) * 2

    clip = clip.rotate(rotate_angle)

    rotated_window_width, rotated_window_height = clip.size
    # print(f"rotated window size: {rotated_window_width} x {rotated_window_height}")
    window_move_x = abs(rotated_window_width - width) / 2
    window_move_y = abs(rotated_window_height - height) / 2

    # 3) resize
    clip = clip.resize(ratio)

    scaled_move_x = x1 * (ratio - 1)
    scaled_move_y = y1 * (ratio - 1)

    # 4) total correction
    total_move_x = (rotated_move_x + window_move_x) * ratio + scaled_move_x
    total_move_y = (rotated_move_y + window_move_y) * ratio + scaled_move_y
    # print(f"rotated_move_x: {rotated_move_x:.1f} + window_move_x: {window_move_x:.1f} + scaled_move_x: {scaled_move_x:.1f} = total_move_x: {total_move_x:.1f}")
    # print(f"rotated_move_y: {rotated_move_y:.1f} + window_move_y: {window_move_y:.1f} + scaled_move_y: {scaled_move_y:.1f} = total_move_y: {total_move_y:.1f}")

    clip = clip.on_color(size=(width, height), color=(0, 0, 0), pos=(-total_move_x, -total_move_y))
    clip = clip.resize(newsize=(width, height))

    return clip


def rotate_window(w, h, theta_degrees):
    theta = radians(abs(theta_degrees))

    w_prime = h / abs(sin(theta) + (h / w) * cos(theta))
    # h_prime = h / abs((h / w) * sin(theta) + cos(theta))
    scale_w = w / w_prime
    # scale_h = h / h_prime

    x1, y1 = 0, 0
    x2, y2 = w, 0
    x3, y3 = w, h
    x4, y4 = 0, h

    x1_new = x1 * cos(theta) - y1 * sin(theta)
    y1_new = x1 * sin(theta) + y1 * cos(theta)

    x2_new = x2 * cos(theta) - y2 * sin(theta)
    y2_new = x2 * sin(theta) + y2 * cos(theta)

    x3_new = x3 * cos(theta) - y3 * sin(theta)
    y3_new = x3 * sin(theta) + y3 * cos(theta)

    x4_new = x4 * cos(theta) - y4 * sin(theta)
    y4_new = x4 * sin(theta) + y4 * cos(theta)

    new_height = max(y1_new, y2_new, y3_new, y4_new) - min(y1_new, y2_new, y3_new, y4_new)
    new_width = max(x1_new, x2_new, x3_new, x4_new) - min(x1_new, x2_new, x3_new, x4_new)

    if x1_new * x2_new * x3_new * x4_new * y1_new * y2_new * y3_new * y4_new < 0:
        print("!!!ALERT wrong new coord:", x1_new, x2_new, x3_new, x4_new, y1_new, y2_new, y3_new, y4_new, f"new_width: {new_width} new_height: {new_height}")
    # if new_width < 0 or new_height < 0:
    #     print("!!!ALERT wrong new coord:", x1_new, x2_new, x3_new, x4_new, y1_new, y2_new, y3_new, y4_new, f"new_width: {new_width} new_height: {new_height}")

    return scale_w, (new_width - w) / 2, (new_height - h) / 2



def vector_interpolation(clip, v1, v2):
    width, height, center_x, center_y, distance, diff_x, diff_y, ratio, rotate_angle, x1, y1, w1, h1, x12, y12, x2, y2, w2, h2, x22, y22 = vector_difference(clip, v1, v2)

    # if x1 == 0:
    #     if y1 == 0:
    #         return v2
    #     else:
    #         print("!!!!ALERT strange JSON", v1, v2)

    move_threshold = 1.10
    scale_threshold = 1.50
    rotate_threshold = 1.20

    rescale_by_move_x = diff_x / width * 2
    rescale_by_move_y = diff_y / height * 2
    rescale_by_movement = max(abs(rescale_by_move_x), abs(rescale_by_move_y)) + 1
    if rescale_by_movement > move_threshold:
        print("==============")
        print(f"!!!ALERT big movement. rescale_by_movement:{rescale_by_movement:.3f}, distance: {distance:.2f}, diff_x: {diff_x}, diff_y: {diff_y}")
        print(f"ratio: {ratio:.2f}, w1: {w1:.2f}, h1: {h1:.2f}, w2: {w2:.2f}, h2: {h2:.2f}")
        print(f"x1: {x1:.2f}, y1: {y1:.2f}, x12: {x12:.2f}, y12: {y12:.2f}, x2: {x2:.2f}, y2: {y2:.2f}, x22: {x22:.2f}, y22: {y22:.2f}")
        print("==============")
    # print(f"big movement. rescale_by_movement:{rescale_by_movement:.3f}, distance: {distance:.2f}, diff_x: {diff_x}, diff_y: {diff_y}")

    if ratio > scale_threshold or 1 / ratio > scale_threshold:
        # print(f"!!!ALERT too big size difference. ratio: {ratio:.2f}. Reset to 1.5")
        print("==============")
        print(f"!!!ALERT too big size difference. ratio: {ratio:.2f}, length_1: {diff_x:.2f}, length_2: {diff_y:.2f}, w1: {w1:.2f}, h1: {h1:.2f}, w2: {w2:.2f}, h2: {h2:.2f}")
        print(f"x1: {x1:.2f}, y1: {y1:.2f}, x12: {x12:.2f}, y12: {y12:.2f}, x2: {x2:.2f}, y2: {y2:.2f}, x22: {x22:.2f}, y22: {y22:.2f}")
        print("==============")

    if ratio >= 1:
        # print(f"ratio:{ratio:.3f}. rescale_by_movement:{rescale_by_movement:.3f}, ratio * rescale_by_movement: {ratio * rescale_by_movement:.3f}")
        # intr_vector = v1
        # ix, iy, iw, ih = intr_vector
        sx1 = x1 * rescale_by_movement
        sy1 = y1 * rescale_by_movement
        sx2 = x12 * rescale_by_movement
        sy2 = y12 * rescale_by_movement

        rescale_ratio = rescale_by_movement * ratio
        tx1 = x2 * rescale_ratio
        ty1 = y2 * rescale_ratio
        tx2 = x22 * rescale_ratio
        ty2 = y22 * rescale_ratio

        ix1 = (sx1 + tx1) / 2
        iy1 = (sy1 + ty1) / 2
        ix2 = (sx2 + tx2) / 2
        iy2 = (sy2 + ty2) / 2

        sdiff_x = ix1 - sx1
        sdiff_y = iy1 - sy1
        centering_x = width * (rescale_by_movement - 1) / 2
        centering_y = height * (rescale_by_movement - 1) / 2
        # centering_x = width * (rescale_ratio - 1) / 2
        # centering_y = height * (rescale_ratio - 1) / 2

        # if dist(sx2-sx1, sy2-sy1) - dist(tx2-tx1, ty2-ty1) > 0.1:
        #     print("!!!===========ALERT wrong calculation", dist(sx2-sx1, sy2-sy1), dist(tx2-tx1, ty2-ty1), dist(sx2-sx1, sy2-sy1) - dist(tx2-tx1, ty2-ty1))
        # else:
        #     print("!!!Good calculation", dist(ix12-ix1, iy12-iy1), dist(tx12-tx1, ty12-ty1), dist(sx12-sx1, sy12-sy1) - dist(tx12-tx1, ty12-ty1))

    else:
        # print(f"ratio:{ratio:.3f}. rescale_by_movement:{rescale_by_movement:.3f}, escale_by_movement / ratio: {rescale_by_movement / ratio:.3f}")
        # sx1 = x2 * rescale_by_movement
        # sy1 = y2 * rescale_by_movement
        # sx2 = x22 * rescale_by_movement
        # sy2 = y22 * rescale_by_movement
        #
        # rescale_ratio = rescale_by_movement / ratio
        # tx1 = x1 * rescale_ratio
        # ty1 = y1 * rescale_ratio
        # tx2 = x12 * rescale_ratio
        # ty2 = y12 * rescale_ratio
        rescale_ratio = rescale_by_movement / ratio
        sx1 = x1 * rescale_ratio
        sy1 = y1 * rescale_ratio
        sx2 = x12 * rescale_ratio
        sy2 = y12 * rescale_ratio

        # rescale_ratio = rescale_by_movement / ratio
        tx1 = x2 * rescale_by_movement
        ty1 = y2 * rescale_by_movement
        tx2 = x22 * rescale_by_movement
        ty2 = y22 * rescale_by_movement

        ix1 = (sx1 + tx1) / 2
        iy1 = (sy1 + ty1) / 2
        ix2 = (sx2 + tx2) / 2
        iy2 = (sy2 + ty2) / 2

        sdiff_x = ix1 - sx1
        sdiff_y = iy1 - sy1
        # centering_x = width * (rescale_by_movement - 1) / 2
        # centering_y = height * (rescale_by_movement - 1) / 2
        centering_x = width * (rescale_ratio - 1) / 2
        centering_y = height * (rescale_ratio - 1) / 2

        # if dist(sx2-sx1, sy2-sy1) - dist(tx2-tx1, ty2-ty1) > 0.1:
        #     print("!!!===========ALERT wrong calculation", dist(sx2-sx1, sy2-sy1), dist(tx2-tx1, ty2-ty1), dist(sx2-sx1, sy2-sy1) - dist(tx2-tx1, ty2-ty1))
        # else:
        #     print("!!!Good calculation", dist(ix12-ix1, iy12-iy1), dist(tx12-tx1, ty12-ty1), dist(sx12-sx1, sy12-sy1) - dist(tx12-tx1, ty12-ty1))


    iw = ix2 - ix1
    ih = iy2 - iy1
    # ix = ix1 - centering_x
    # iy = iy1 - centering_y
    ix = ix1 - centering_x - sdiff_x
    iy = iy1 - centering_y - sdiff_y

    rescale_by_rotation, rotated_window_move_x, rotated_window_move_y = rotate_window(width, height, rotate_angle / 2)
    if rescale_by_rotation > rotate_threshold:
        print(f"big rotation. rescale_by_rotation: rotate_angle:{rotate_angle/2:.2f}, rescale_by_rotation: {rescale_by_rotation:.3f}, rotated_window_move_x:{rotated_window_move_x:.2f}, rotated_window_move_y:{rotated_window_move_y:.2f}")
    # print(f"rotate_angle:{rotate_angle/2:.2f}, rescale_by_rotation: {rescale_by_rotation:.3f}, rotated_window_move_x:{rotated_window_move_x:.2f}, rotated_window_move_y:{rotated_window_move_y:.2f}")

    ix *= rescale_by_rotation
    iy *= rescale_by_rotation
    iw *= rescale_by_rotation
    ih *= rescale_by_rotation

    ix -= rotated_window_move_x
    iy -= rotated_window_move_y
    # centering_x = width * (rescale_by_rotation - 1) / 2
    # centering_y = height * (rescale_by_rotation - 1) / 2
    # ix -= centering_x
    # iy -= centering_y

    if ix < 0 or iy < 0:
        print(f"!!!!ALERT minus ix or iy, v1:{v1}, v2:{v2}, iv:{[ix, iy, iw, ih]}")
        print(f"distance:{distance}, diff_x:{diff_x}, diff_y:{diff_y}, ratio:{ratio:.2f}, rescale_ratio:{rescale_ratio:.2f}, centering_x:{centering_x:.2f}, centering_y:{centering_y:.2f}")
        print(f"rotate_angle:{rotate_angle:.2f}, rescale_by_rotation:{rescale_by_rotation:.2f}, rotated_window_move_x:{rotated_window_move_x:.2f}, rotated_window_move_y:{rotated_window_move_y:.2f}")

    # if round(rotate_angle, 2) != 0:
    #     print(f"!!!!ALERT rotate_angle not zero, v1:{v1}, v2:{v2}, iv:{[ix, iy, iw, ih]}")
    #     print(f"distance:{distance}, diff_x:{diff_x}, diff_y:{diff_y}, ratio:{ratio:.2f}, rescale_ratio:{rescale_ratio:.2f}, centering_x:{centering_x:.2f}, centering_y:{centering_y:.2f}")
    #     print(f"rotate_angle:{rotate_angle:.2f}, rescale_by_rotation:{rescale_by_rotation:.2f}, rotated_window_move_x:{rotated_window_move_x:.2f}, rotated_window_move_y:{rotated_window_move_y:.2f}")

    return [int(ix), int(iy), int(iw), int(ih)]


def transform_vector(v, translation, rotation_matrix, scale_factor):
    v_start = np.array([v[0], v[1]]) + translation
    v_vector = np.array([v[2], v[3]])
    v_end = v_start + v_vector

    v_rotated_vector = np.dot(rotation_matrix, v_vector)
    v_rotated_end = v_start + v_rotated_vector

    v_scaled_vector = v_rotated_vector * scale_factor
    v_scaled_end = v_start + v_scaled_vector

    new_vector = [v_start[0], v_start[1], v_scaled_vector[0], v_scaled_vector[1]]
    return new_vector


def adjust_vector(v1, v2, v3):
    ix1 = (v1[0] + v2[0]) / 2
    iy1 = (v1[1] + v2[1]) / 2
    ix2 = (v1[0] + v2[2] + v2[0] + v2[2]) / 2
    iy2 = (v1[1] + v2[3] + v2[1] + v2[3]) / 2
    v1 = [ix1, iy1, ix2-ix1, iy2-iy1]

    v1_start = np.array([v1[0], v1[1]])
    v1_vector = np.array([v1[2], v1[3]])
    v1_end = v1_start + v1_vector

    v2_start = np.array([v2[0], v2[1]])
    v2_vector = np.array([v2[2], v2[3]])
    v2_end = v2_start + v2_vector

    translation = v1_start - v2_start

    angle_v1 = np.arctan2(v1_vector[1], v1_vector[0])
    angle_v2 = np.arctan2(v2_vector[1], v2_vector[0])
    rotation_angle = angle_v1 - angle_v2

    rotation_matrix = np.array([
        [np.cos(rotation_angle), -np.sin(rotation_angle)],
        [np.sin(rotation_angle), np.cos(rotation_angle)]
    ])

    magnitude_v1 = np.linalg.norm(v1_vector)
    magnitude_v2 = np.linalg.norm(v2_vector)
    scale_factor = magnitude_v1 / magnitude_v2

    x, y, w, h = transform_vector(v3, translation, rotation_matrix, scale_factor)

    return [int(x), int(y), int(w), int(h)]


def find_in_between(sorted_list, x, y):
    start = bisect.bisect_left(sorted_list, x)
    end = bisect.bisect_left(sorted_list, y)

    return sorted_list[start:end]


def line_to_vector(line1, line2):
    x1, y1, x12, y12 = line1
    x2, y2, x22, y22 = line2
    v1 = (x1, y1, x12 - x1, y12 - y1)
    v2 = (x2, y2, x22 - x2, y22 - y2)
    return v1, v2


# a = [1, 2, 3, 4]
# a.insert(0, 100)
# b = [1000, 2000]
# b.append(a)
# print(a)
# print(b)
# a = [3, 4]
# print(a)
# print(b)
# quit()

if __name__ == "__main__":
    s1 = rotate_window(1920, 1080, 10)
    s2 = rotate_window(1920, 1080, 30)
    s3 = rotate_window(1920, 1080, 45)
    s4 = rotate_window(1920, 1080, 60)
    s5 = rotate_window(1920, 1080, 90)
    print(s1, s2, s3, s4, s5)
    quit()
    clip1 = VideoFileClip("data/test_video_4_out.mp4")
    clip2 = VideoFileClip("data/test_video_1_out.mp4")

    v1 = [789, 231, 400, 400]
    v2 = [790, 233, 406, 406]
    v3 = [1323, 484, 78, 78]
    v4 = adjust_vector(clip1, v1, v2, v3)
    print(v1, v2, v3, v4)

    clip1_new = get_adjusted_clip(clip1, v1, v2)
    output_path = f'data/test_video_4_out_new.mp4'
    clip1_new.write_videofile(output_path, codec='libx264', audio_codec='aac')

    final_clip = concatenate_videoclips([clip1_new, clip2])
    output_path = f'data/vector_test_final_{random.randint(0, 999):03d}.mp4'
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

    # # Example usage
    # v1 = [0, 0, 3, 4]  # First vector
    # v2 = [1, 1, 3, 4]  # Second vector to be aligned with the first
    # v3 = [2, 2, 1, 1]  # Third vector to be transformed
    #
    # new_v3 = match_and_transform(v1, v2, v3)
    # print("Transformed third vector:", new_v3)

    # clip1 = VideoFileClip("data/line1.mp4")
    # clip2 = VideoFileClip("data/line2.mp4")
    #
    # # width, height = clip1.size
    # # center_x = int(width / 2)
    # # center_y = int(height / 2)
    # #
    # # # line1 = x1, y1, x12, y12 = (100, 100, 220, 100)
    # # # line2 = x2, y2, x22, y22 = (120, 120, 200, 140)
    # # # line1 = (center_x, center_y, center_x + 200, center_y)
    # # # line2 = (center_x, center_y, center_x + 200, center_y + 100)
    # # # prepare_sample(line1, line2)
    # # # quit()
    #
    # line1 = (100, 100, 220, 100)
    # line2 = (120, 120, 200, 140)
    # v1, v2 = line_to_vector(line1, line2)
    # x1, y1, w1, h1 = v1
    # x2, y2, w2, h2 = v2
    # # v1 = (x1, y1, x12 - x1, y12 - y1)
    # # v2 = (x2, y2, x22 - x2, y22 - y2)
    # # a = 720 / 1080
    # # v1 = (int(788*a), int(229*a), int(395*a), int(395*a))
    # # v2 = (int(790*a), int(233*a), int(406*a), int(406*a))
    # # x1, y1, w1, h1 = v1
    # # x2, y2, w2, h2 = v2
    # # line1 = (x1, y1, x1 + w1, y1 + h1)
    # # line2 = (x2, y2, x2 + w2, y2 + h2)
    # # prepare_sample(line1, line2)
    #
    # # line1 = (center_x, center_y, center_x + 200, center_y)
    # # line2 = (center_x, center_y, center_x + 200, center_y + 100)
    # # v1, v2 = line_to_vector(line1, line2)
    #
    # ratio = 2.0
    # v3 = x1, y1, w1*ratio, h1*ratio
    # temp_clip = get_adjusted_clip(clip2, v1, v2)
    # adjust_clip1 = get_adjusted_clip(temp_clip, v3, v1)
    # adjust_clip2 = get_adjusted_clip(clip2, v3, v2)
    #
    # final_clip = concatenate_videoclips([clip1, adjust_clip1, adjust_clip2])
    #
    # # duration_sum = clip1.duration + adjust_clip1.duration + adjust_clip2.duration
    # # duration_final = final_clip.duration
    # # print(duration_sum, duration_final, duration_sum == duration_final)
    # final_clip.write_videofile("data/adjust_video.mp4", codec='libx264', audio_codec='aac')
    #
    # clip1.close()
    # clip2.close()
    # adjust_clip1.close()
    # adjust_clip2.close()
    # final_clip.close()

import numpy as np


def transform_vector(v, translation, rotation_matrix, scale_factor):
    # Apply translation
    v_start = np.array([v[0], v[1]]) + translation
    v_vector = np.array([v[2], v[3]])
    v_end = v_start + v_vector

    # Apply rotation
    v_rotated_vector = np.dot(rotation_matrix, v_vector)
    v_rotated_end = v_start + v_rotated_vector

    # Apply scaling
    v_scaled_vector = v_rotated_vector * scale_factor
    v_scaled_end = v_start + v_scaled_vector

    # Return the new vector in [x, y, w, h] format
    new_vector = [v_start[0], v_start[1], v_scaled_vector[0], v_scaled_vector[1]]
    return new_vector


def match_and_transform(v1, v2, v3):
    # Extract start points and components
    v1_start = np.array([v1[0], v1[1]])
    v1_vector = np.array([v1[2], v1[3]])
    v1_end = v1_start + v1_vector

    v2_start = np.array([v2[0], v2[1]])
    v2_vector = np.array([v2[2], v2[3]])
    v2_end = v2_start + v2_vector

    # Step 1: Translate v2 to v1's starting point
    translation = v1_start - v2_start

    # Step 2: Rotate v2 to match v1's direction
    angle_v1 = np.arctan2(v1_vector[1], v1_vector[0])
    angle_v2 = np.arctan2(v2_vector[1], v2_vector[0])
    rotation_angle = angle_v1 - angle_v2

    rotation_matrix = np.array([
        [np.cos(rotation_angle), -np.sin(rotation_angle)],
        [np.sin(rotation_angle), np.cos(rotation_angle)]
    ])

    # Step 3: Scale v2 to match v1's magnitude
    magnitude_v1 = np.linalg.norm(v1_vector)
    magnitude_v2 = np.linalg.norm(v2_vector)
    scale_factor = magnitude_v1 / magnitude_v2

    # Transform the third vector
    new_v3 = transform_vector(v3, translation, rotation_matrix, scale_factor)

    return new_v3


# Example usage
v1 = [0, 0, 3, 4]  # First vector
v2 = [1, 1, 3, 4]  # Second vector to be aligned with the first
v3 = [2, 2, 1, 1]  # Third vector to be transformed

new_v3 = match_and_transform(v1, v2, v3)
print("Transformed third vector:", new_v3)

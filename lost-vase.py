import csv
import math

# Constants
PLATFORM_SIZE = 255
CENTER_X = PLATFORM_SIZE / 2
CENTER_Y = PLATFORM_SIZE / 2
INITIAL_DIAMETER = 100
Z_INCREMENT = 0.5  # Vertical increment per stretched layer
EXTRUSION_INCREMENT = 5.0  # Extrusion increment per movement
STEPS_PER_CIRCLE = 10
ANGLE_INCREMENT = 360 / STEPS_PER_CIRCLE
MULTIPLIER = 0.7  # Multiplier factor to utilize more or less of the platform
ANGLE_SHIFT = 0.5  # Angle shift per step to create a spiral effect
VERTICAL_STRETCH_LAYERS = 2  # Number of layers to repeat the same circle
NUM_PARTS = 1  # Number of parts to split the G-code into

# File constants
INPUT_FILE = 'data.tsv'  # Input TSV file
OUTPUT_BASE_NAME = 'output'  # Base name for output G-code files
DELIMITER = '\t'  # Delimiter for the TSV file

def read_csv(file_path):
    percentages = []
    years = []
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file, delimiter=DELIMITER)
        for row in csv_reader:
            year = row['Year']
            embarked = float(row['Embarked'])
            disembarked = float(row['Disembarked'])
            if disembarked != 0:  # Avoid division by zero
                percentage_difference = ((embarked - disembarked) / disembarked) * 100
                percentages.append(percentage_difference)
                years.append(year)
    return percentages, years

def generate_gcode(percentages, years):
    gcode_lines = []
    current_x = CENTER_X
    current_y = CENTER_Y
    angle_offset = 0.0  # Initial angle offset

    total_segments = len(percentages) * VERTICAL_STRETCH_LAYERS * STEPS_PER_CIRCLE
    segments_per_part = total_segments // NUM_PARTS  # Assuming num_parts is 2

    segment_counter = 0
    current_z = 0.0
    current_extrusion = 0.0

    for percentage, year in zip(percentages, years):
        diameter = (INITIAL_DIAMETER + percentage) * MULTIPLIER
        radius = diameter / 2

        for _ in range(VERTICAL_STRETCH_LAYERS):
            for step in range(STEPS_PER_CIRCLE):
                angle_rad = math.radians(step * ANGLE_INCREMENT + angle_offset)
                next_x = CENTER_X + radius * math.cos(angle_rad)
                next_y = CENTER_Y + radius * math.sin(angle_rad)
                current_extrusion += EXTRUSION_INCREMENT

                gcode_lines.append(
                    f"G1 X{next_x:.3f} Y{next_y:.3f} Z{current_z:.1f} E{current_extrusion:.3f} ; Year {year}"
                )

                segment_counter += 1
                if segment_counter >= segments_per_part:
                    # Reset for the next part
                    current_z = 0.0
                    current_extrusion = 0.0
                    segment_counter = 0

            # Shift the angle for the next layer
            angle_offset += ANGLE_SHIFT
            # Increment Z height for each stretched layer
            current_z += Z_INCREMENT

    return gcode_lines

def split_gcode(gcode_lines, output_base_name, num_parts=2):
    template_start = [
        "M105",
        "M109 S0",
        "M82 ;absolute extrusion mode",
        "G28 ;Home",
        "G1 Z15.0 F6000 ;Move the platform down 15mm",
        ";Prime the extruder",
        "G92 E0",
        "G1 F2000 E0",
        "M106 S255",
        "; Movement Start ==============="
    ]

    template_end = [
        "; Movement End ===============",
        "M107",
        "M104 S0",
        "M140 S0",
        ";Retract the filament",
        "G92 E1",
        "G1 E-1 F300",
        "G28 X0 Y0",
        "M84",
        "M82 ;absolute extrusion mode",
        ";End of Gcode"
    ]

    lines_per_part = len(gcode_lines) // num_parts
    for i in range(num_parts):
        start_index = i * lines_per_part
        end_index = (i + 1) * lines_per_part if i < num_parts - 1 else len(gcode_lines)
        part_lines = gcode_lines[start_index:end_index]

        output_file_name = f"{output_base_name}_part{i + 1}.gcode"
        with open(output_file_name, "w") as f:
            for line in template_start:
                f.write(line + "\n")

            for line in part_lines:
                f.write(line + "\n")

            for line in template_end:
                f.write(line + "\n")

        print(f"G-code part {i + 1} has been written to {output_file_name}")


def main():
    percentages, years = read_csv(INPUT_FILE)
    movement_gcode = generate_gcode(percentages, years)   

    # Split and write to output files
    split_gcode(movement_gcode, OUTPUT_BASE_NAME, num_parts=NUM_PARTS)  # Change num_parts as needed

if __name__ == "__main__":
    main()

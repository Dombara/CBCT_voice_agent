import subprocess

def convert_to_mulaw(input_file):
    output_file = input_file.replace(".mp3", ".raw")

    command = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-ar", "8000",
        "-ac", "1",
        "-f", "mulaw",
        output_file
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return output_file
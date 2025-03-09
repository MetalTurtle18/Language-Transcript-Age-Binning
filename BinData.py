import os
import matplotlib.pyplot as plt
import shutil as sh


def clan_command(targets: set[str], strings: list[str], output: str) -> str:
    """
    Constructs a freq command string to run in CLAN for the given targets, strings, and output file.

    :param targets: A set of targets.
    :type targets: set[str]
    :param strings: A list of strings to calculate frequency for.
    :type strings: list[str]
    :param output: The name of the output file without file extension where the results of command execution are saved.
    :type output: str
    :return: A constructed command string ready for execution.
    :rtype: str
    """

    command = 'freq +u '
    for target in targets:
        command += f'+t*{target} '
    for string in strings:
        command += f'+s{string} '
    command += f'*.cha > {output}.cex'
    return command


def convert_age(age_string: str) -> int | None:
    """
    Converts an age string in the format "years;months" into an integer representing
    the total number of months. If the input format is invalid, the function returns None.

    :param age_string: A string representing age formatted as "years;months".
    :type age_string: str
    :return: Total number of months as an integer or None if the input is invalid.
    :rtype: int | None
    """
    if age_string == '': return None
    parts = age_string.split(";")  # Split into year and month
    if len(parts) == 1:  # Only years provided
        year = int(parts[0])
        month = 0
    elif len(parts) == 2:  # Both years and months provided
        year = int(parts[0]) if parts[0] else 0
        month = round(float(parts[1])) if parts[1] else 0
    else:
        return None

    # Calculate total months
    return (year * 12) + month


def test_convert_age() -> None:
    """
    Tests the `convert_age` function.

    :return: None
    """
    assert convert_age("4;6") == 54
    assert convert_age("2;0") == 24
    assert convert_age("0;9") == 9
    assert convert_age("4;6.5") == 54
    assert convert_age("1;0.75") == 13
    assert convert_age("0;3.2") == 3
    assert convert_age("3") == 36
    assert convert_age(";8") == 8
    assert convert_age(";") == 0
    assert convert_age("0;0") == 0
    assert convert_age("") is None


def extract_id_lines(file: str) -> list[str]:
    """
    Extracts all lines from a file that begin with the '@ID' prefix.

    :param file: The path to the file to be read.
    :type file: str
    :return: A list of lines from the file that start with '@ID'.
    :rtype: list[str]
    """

    with open(file, 'r') as file:
        out = []
        for line in file:
            if line.startswith('@ID'):
                out.append(line)
        return out


def extract_speaker(line: str) -> tuple[str, int, str]:
    """
    Extracts specific speaker data from a delimited string line.

    :param line: A string containing the .cha ID line.
    :type line: str
    :return: A tuple containing the speaker's ID, age (in months), and role.
    :rtype: tuple[str, int, str]
    """

    data = line.split('|')
    return data[2], convert_age(data[3]), data[7]


def find_bin(boundaries: list[int], value: int) -> str | None:
    """
    Determines the bin range in which a given value falls based on a list of ordered boundary values.

    :param boundaries: The list of integers representing the boundary values,
        which must be sorted in ascending order. These define the bins.
    :param value: The integer value to determine the range (bin) for.
    :return: A string representation of the range in the format
        "lower-upper" if the value falls within a bin, or None if the
        value does not fall within any defined bin.
    """

    for i in range(len(boundaries) - 1):
        # Check if the value falls into the range [boundaries[i], boundaries[i+1])
        if boundaries[i] <= value < boundaries[i + 1]:
            return f"{boundaries[i]}-{boundaries[i + 1]}"

    # Handle edge case where the value matches the exact upper boundary of the final bin
    if value == boundaries[-1]:
        return f"{boundaries[-2]}-{boundaries[-1]}"

    return None  # Value is out of range


languages = ['Spanish', 'English', 'Japanese']
pronouns = {
    'Spanish': ['yo', 'tú', 'vos', 'usted', 'él', 'ella', 'nosotros', 'nosotras', 'vosotros', 'vosotras', 'ustedes',
                'ellos', 'ellas'],
    'English': ['I', 'you', 'he', 'she', 'we', 'they'],
    'Japanese': ['boku', 'ぼく', 'atashi', 'あたし', 'kimi', 'きみ', 'omae', 'おまえ', 'ore', 'おれ', 'aitsu', 'あいつ',
                 'watashi', 'わたし', 'watakushi', 'わたくし', 'anata', 'あなた', 'tachi', 'たち', 'domo', 'ども',
                 'gata', 'がた', 'ra', 'ら'],
}
japanese_kana_romanization = {
    'ぼく': 'boku',
    'あたし': 'atashi',
    'きみ': 'kimi',
    'おまえ': 'omae',
    'おれ': 'ore',
    'あいつ': 'aitsu',
    'わたし': 'watashi',
    'わたくし': 'watakushi',
    'あなた': 'anata',
    'たち': 'tachi',
    'ども': 'domo',
    'がた': 'gata',
    'ら': 'ra',
}
# age_bins = [0, 18, 30, 48, 72, 96, 150]
age_bins = [0, 9, 18, 24, 30, 39, 48, 60, 72, 84, 96, 123, 150]

if __name__ == '__main__':
    test_convert_age()

    try:
        sh.rmtree('binned')
    except FileNotFoundError:
        print('Directory "binned" does not exist yet. Continuing...\n')
    os.mkdir('binned')

    open('commands.bat', 'w').close()  # Create and/or clear the batch file from any previous runs

    for language in languages:
        target_ids = {'CHI'}
        datasets = os.listdir(language)
        transcripts = []
        ages = []
        try:
            os.mkdir(f'binned/{language}')
        except FileExistsError:
            print(f'Directory "binned/{language}" already exists. Continuing...\n')
        for b in range(len(age_bins) - 1):
            try:
                os.mkdir(f'binned/{language}/{age_bins[b]}-{age_bins[b + 1]}')
            except FileExistsError:
                print(f'Directory "binned/{language}/{age_bins[b]}-{age_bins[b + 1]}" already exists. Continuing...\n')

        # Walk the directory recursively to find every transcript file
        for root, _, files in os.walk(language):
            transcripts.extend([os.path.join(root, t) for t in files if t.endswith('.cha')])
        # Go through every transcript file and extract the child speakers
        for transcript in transcripts:
            id_lines = extract_id_lines(transcript)
            speakers = [extract_speaker(s) for s in id_lines]
            # Filter only the speakers out of the transcript who are designated target child and who have an age
            child_speakers = list(filter(lambda p: p[2] == 'Target_Child' and p[1], speakers))
            target_ids.update([s[0] for s in child_speakers])
            ages.extend([s[1] for s in child_speakers])
            # Move the files around now
            if child_speakers:  # Only copy this transcript if it contains child utterances
                # If there are multiple child speakers, just average their ages
                age = sum([s[1] for s in child_speakers]) // len(child_speakers)
                sh.copy(transcript, f'binned/{language}/{find_bin(age_bins, age)}/{transcript.split("/")[-1]}')

        # Make a batch file with all the commands to run in CLAN
        for age in range(len(age_bins) - 1):
            age_bin = f'{age_bins[age]}-{age_bins[age + 1]}'
            directory = os.path.join('binned', language, age_bin)
            command = clan_command(target_ids, pronouns[language], f'../../pronoun_counts_{language}_{age_bin}')
            with open('commands.bat', 'a') as file:
                file.write(f'cd {directory}\n')
                file.write(f'{command}\n')
                file.write(f'cd ../../../\n')

        _, _, patches = plt.hist(ages, bins=age_bins, color='skyblue', edgecolor='black')
        plt.bar_label(patches)
        plt.xlabel('Age (months)')
        plt.ylabel('No. of transcripts')
        plt.title(f'Age Distribution for {language} Datasets')
        plt.show()

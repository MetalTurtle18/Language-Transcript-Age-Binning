import os


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


if __name__ == '__main__':
    test_convert_age()

    languages = ['Spanish', 'English', 'Japanese']
    pronouns = {
        'Spanish': ['yo', 'tú', 'vos', 'usted', 'él', 'ella', 'nosotros', 'nosotros', 'vosotros', 'vosotras', 'ustedes',
                    'ellos', 'ellas'],
        'English': ['I', 'you', 'he', 'she', 'we', 'they'],
        'Japanese': [],  # TODO
    }

    for language in languages:
        target_ids = {'CHI'}
        datasets = os.listdir(language)
        transcripts = []
        # Walk the directory recursively to find every transcript file
        for root, _, files in os.walk(language):
            transcripts.extend([os.path.join(root, t) for t in files if t.endswith('.cha')])
        # Go through every transcript file and extract the child speakers
        for transcript in transcripts:
            id_lines = extract_id_lines(transcript)
            speakers = [extract_speaker(s) for s in id_lines]
            child_speakers = list(filter(lambda p: p[2] == 'Target_Child', speakers))
            target_ids.update([s[0] for s in child_speakers])

        # Print the full CLAN command to count pronouns in a directory of .cha files for a given language
        print(clan_command(target_ids, pronouns[language], f'pronoun_counts_{language}'))
        print()

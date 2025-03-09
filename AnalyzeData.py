from collections import defaultdict

from BinData import *


def combine_speakers(cex_file):
    words = defaultdict(int)
    tokens = 0
    with open(cex_file, 'r') as file:
        line = file.readline()
        while not line.startswith('Speaker'): line = file.readline()
        for line in file:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            t = line.split(' ', 1)
            if t[1].endswith('(tokens)'):
                tokens += int(t[0])
            elif not t[1].endswith('used') and not t[1].endswith('ratio'):
                words[t[1]] += int(t[0])
    return words, tokens



if __name__ == '__main__':

    for language in ['English', 'Spanish']: # TODO add Japanese once pronouns set
        for age in range(len(age_bins) - 1):
            age_bin = f'{age_bins[age]}-{age_bins[age + 1]}'
            counts_file = f'binned/pronoun_counts_{language}_{age_bin}.cex'
            words, tokens = combine_speakers(counts_file)
            print(words, tokens) # TODO plot instead of printing
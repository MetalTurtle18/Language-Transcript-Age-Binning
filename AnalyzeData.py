from collections import defaultdict
import matplotlib.pyplot as plt

from BinData import *


def combine_speakers(cex_file):
    words_counts = defaultdict(int)
    tokens_total = 0
    with open(cex_file, 'r') as file:
        line = file.readline()
        while not line.startswith('Speaker'): line = file.readline()
        for line in file:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            t = line.split(' ', 1)
            if t[1].endswith('(tokens)'):
                tokens_total += int(t[0])
            elif not t[1].endswith('used') and not t[1].endswith('ratio'):
                words_counts[t[1]] += int(t[0])
    return words_counts, tokens_total


if __name__ == '__main__':
    for language in ['English', 'Spanish']:  # TODO add Japanese once pronouns set
        pronouns_counts = defaultdict(list[float])
        for age in range(len(age_bins) - 1):
            age_bin = f'{age_bins[age]}-{age_bins[age + 1]}'
            counts_file = f'binned/pronoun_counts_{language}_{age_bin}.cex'
            words, tokens = combine_speakers(counts_file)
            for pronoun in pronouns[language]:
                if pronoun in words.keys():
                    #pronouns_counts[pronoun].append(round(words[pronoun] / tokens * 10000))
                    pronouns_counts[pronoun].append(words[pronoun] / tokens)
                else:
                    pronouns_counts[pronoun].append(0)
        for label, values in pronouns_counts.items():
            plt.plot(values, label=label)
        plt.legend()
        plt.xticks(range(len(age_bins) - 1), age_bins[1:])
        plt.xlabel('Age (months)')
        plt.ylabel('Frequency of pronoun (occurrences per total words)')
        plt.show()
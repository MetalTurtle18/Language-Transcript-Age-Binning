from collections import defaultdict

from BinData import *


def combine_speakers(cex_file):
    words_counts = defaultdict(int)
    tokens_total = 0
    with open(cex_file, 'r') as file:
        line = file.readline()
        if line == '':  # Empty file
            return words_counts, tokens_total
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
    for language in languages:
        pronouns_counts = defaultdict(list[float])
        for age in range(len(age_bins) - 1):
            age_bin = f'{age_bins[age]}-{age_bins[age + 1]}'
            counts_file = f'binned/pronoun_counts_{language}_{age_bin}.cex'
            words, tokens = combine_speakers(counts_file)
            for pronoun in pronouns[language]:
                if pronoun in words.keys() and tokens > 0:
                    pronouns_counts[pronoun].append(words[pronoun] / tokens)
                else:
                    pronouns_counts[pronoun].append(0)
        if language == 'Japanese':  # Special handling because of Japanese romanization vs kana
            for kana, romanization in japanese_kana_romanization.items():
                pronouns_counts[romanization] = [i + j for i, j in zip(pronouns_counts[romanization], pronouns_counts[kana])]
                pronouns_counts.pop(kana)

        fig, ax = plt.subplots(constrained_layout=True)
        for label, values in pronouns_counts.items():
            ax.plot(values, label=label)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xticks(range(len(age_bins) - 1), age_bins[1:])
        plt.xlabel('Age (months)')
        plt.ylabel('Frequency of pronoun (occurrences per total words)')
        plt.title(f'Frequency of Pronouns by Child Age in {language}')
        plt.show()

import random

def shuffleString(word):
    substrings = word.split(' ')
    shuffled_substrings = []
    for substring in substrings:
        substring_list = list(substring)
        random.shuffle(substring_list)
        shuffled_substring = ''.join(substring_list)
        shuffled_substrings.append(shuffled_substring)
    return ' '.join(shuffled_substrings).upper()
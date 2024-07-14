import urllib.request
import re
import string
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt


def download_text(url):
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8")


def remove_html_tags(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def clean_text(text):
    text = remove_html_tags(text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\W+", " ", text)
    return text.lower()


def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text):
    text = clean_text(text)
    words = text.split()

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def visualize_top_words(word_counts, top_n=10):
    common_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*common_words)

    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color="skyblue")
    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.title(f"Top {top_n} Most Frequent Words")
    plt.gca().invert_yaxis()
    plt.show()


def main(url, top_n=10):
    try:
        text = download_text(url)

        word_counts = map_reduce(text)

        visualize_top_words(word_counts, top_n)

    except urllib.error.URLError as e:
        print(f"Error fetching data from {url}: {e}")
    except Exception as e:
        print(f"Error processing text: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 task2.py <URL> [<top_n>]")
        sys.exit(1)

    url = sys.argv[1]
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    main(url, top_n)

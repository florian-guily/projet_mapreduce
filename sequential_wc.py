from collections import Counter
import re, time
start = time.time()

f = open('samples/CC-MAIN-20220924151538-20220924181538-00000.warc.wet', 'r')
text = f.read()

words = re.findall(r'[A-Za-z]+', text)
dico = Counter(words)

f.close()

f = open('./results.txt', 'w')
for key, val in dico.items():
    f.write(f"{key} {val}\n")

end = time.time()
print(f"Finished in {end-start} seconds.")
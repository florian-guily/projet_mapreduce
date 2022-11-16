from collections import Counter
import re, time, sys


start = time.time()
data = b""
for i in range(int(sys.argv[1])):
    f = open(f'samples/CC-MAIN-20220924151538-20220924181538-0000{i}.warc.wet', 'rb')
    data += f.read()

data = re.findall(r'[A-Za-z]+', data.decode('utf-8'))
dico = Counter(data)


f.close()

f = open('./results.txt', 'w')
for key, val in dico.items():
    f.write(f"{key} {val}\n")

end = time.time()
print(f"Finished in {end-start} seconds.")
AllWords = []
for line in open("transcript.txt"):
    row = line.split(' ')
    AllWords += list(row)

line_breaker = 20
i = 1

with open("new.txt", 'w') as file:
    for word in AllWords:
        if "." in word or i == line_breaker:
            file.write(word.strip('\n') + "\n")
            i = 0
        else:
            file.write(word.strip('\n') + " ")

        i += 1

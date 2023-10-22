# Generates mahjong tournaments with ~n rounds for 4n players
import time
import copy
import re
currentBest = 0


def inc(dictionary, key):
    dictionary[key] = dictionary.get(key, 0) + 1


def dec(dictionary, key):
    dictionary[key] = dictionary.get(key, 0) - 1


# Simulate the effect of swapping 2 positions
# Return True if it improves the wind allocation
def testSwap(dictionary, match, x, y):
    a = dictionary[x].get(match[x], 0)
    b = dictionary[x].get(match[y], 0)
    c = dictionary[y].get(match[x], 0)
    d = dictionary[y].get(match[y], 0)
    currentScore = a*a + b*b + c*c + d*d
    a -= 1
    b += 1
    c += 1
    d -= 1
    newScore = a*a + b*b + c*c + d*d
    return newScore < currentScore - 0.01


def matchupAudit(matches, playerList):
    matchups = {}
    for match in matches:
        a = match[0]
        b = match[1]
        c = match[2]
        d = match[3]
        inc(matchups, (a, b))
        inc(matchups, (a, c))
        inc(matchups, (a, d))
        inc(matchups, (b, c))
        inc(matchups, (b, d))
        inc(matchups, (c, d))
    file = open("matchupAudit.txt", "w")
    for player1 in playerList:
        file.write("{} vs\n".format(player1))
        for player2 in playerList:
            times = matchups.get((player1, player2), 0) + matchups.get((player2, player1), 0)
            if player1 == player2:
                times = "N/A"
            file.write("{}: {}\n".format(player2, times))
        file.write("\n")


def assign(inputFile):
    file = open(inputFile, "r")
    text = file.read()
    file.close()
    capture = re.findall("\[(.*?), ?(.*?), ?(.*?), ?(.*?)]", text)
    lockedInCapture = copy.deepcopy(capture)
    playerSet = set()
    for x in capture:  # makes a list of players for audit (in case of using names instead of numbers)
        playerSet.add(x[0])
        playerSet.add(x[1])
        playerSet.add(x[2])
        playerSet.add(x[3])
    try:  # if players are numbered, sort by number
        playerList = sorted(playerSet, key=lambda item: int(item))
    except:  # otherwise, sort alphabetically
        playerList = sorted(playerSet)
    matchupAudit(capture, playerList)
    changed = True
    while changed:  # run until the allocation stops improving
        changed = False
        counts = [{}, {}, {}, {}]
        for match in capture:  # calculate current allocation
            inc(counts[0], match[0])
            inc(counts[1], match[1])
            inc(counts[2], match[2])
            inc(counts[3], match[3])
        for index in range(len(capture)):
            if testSwap(counts, capture[index], 0, 1):  # If swapping improves the allocation
                dec(counts[0], capture[index][0])  # then perform the swap
                dec(counts[1], capture[index][1])
                inc(counts[1], capture[index][0])
                inc(counts[0], capture[index][1])
                capture[index] = (capture[index][1], capture[index][0], capture[index][2], capture[index][3])
                changed = True
            if testSwap(counts, capture[index], 0, 2):
                dec(counts[0], capture[index][0])
                dec(counts[2], capture[index][2])
                inc(counts[2], capture[index][0])
                inc(counts[0], capture[index][2])
                capture[index] = (capture[index][2], capture[index][1], capture[index][0], capture[index][3])
                changed = True
            if testSwap(counts, capture[index], 0, 3):
                dec(counts[0], capture[index][0])
                dec(counts[3], capture[index][3])
                inc(counts[3], capture[index][0])
                inc(counts[0], capture[index][3])
                capture[index] = (capture[index][3], capture[index][1], capture[index][2], capture[index][0])
                changed = True
            if testSwap(counts, capture[index], 1, 2):
                dec(counts[1], capture[index][1])
                dec(counts[2], capture[index][2])
                inc(counts[1], capture[index][2])
                inc(counts[2], capture[index][1])
                capture[index] = (capture[index][0], capture[index][2], capture[index][1], capture[index][3])
                changed = True
            if testSwap(counts, capture[index], 1, 3):
                dec(counts[1], capture[index][1])
                dec(counts[3], capture[index][3])
                inc(counts[1], capture[index][3])
                inc(counts[3], capture[index][1])
                capture[index] = (capture[index][0], capture[index][3], capture[index][2], capture[index][1])
                changed = True
            if testSwap(counts, capture[index], 2, 3):
                dec(counts[2], capture[index][2])
                dec(counts[3], capture[index][3])
                inc(counts[2], capture[index][3])
                inc(counts[3], capture[index][2])
                capture[index] = (capture[index][0], capture[index][1], capture[index][3], capture[index][2])
                changed = True
    index = 0
    for match in lockedInCapture:  # find the previous arrangement
        find = "{}, {}, {}, {}".format(match[0], match[1], match[2], match[3])
        match = capture[index]  # replace with new arrangement
        replace = "{}, {}, {}, {}".format(match[0], match[1], match[2], match[3])
        index += 1
        text = text.replace(find, replace)
    file = open("output.txt", "w")
    file.write(text)
    file.close()
    file = open("audit.txt", "w")
    for x in playerList:  # Print out the wind assignment for each player
        file.write("{}\n".format(x))
        file.write("East: {}\n".format(counts[0].get(x, 0)))
        file.write("South: {}\n".format(counts[1].get(x, 0)))
        file.write("West: {}\n".format(counts[2].get(x, 0)))
        file.write("North: {}\n".format(counts[3].get(x, 0)))
        file.write("\n")
    file.close()


def layoutPrint(chosen, n):
    file = open("output.txt", "w")
    index = 1
    matches = len(chosen)
    file.write("{} Players, {} Rounds\n".format(n * 4, matches))
    file.write("Each player meets {} different opponents\n".format(matches*3))
    file.write("0-{}, {}-{}, {}-{} & {}-{} do not meet\n".format(n-1, n, 2*n-1, 2*n, 3*n-1, 3*n, 4*n-1))
    file.write("Sorting players by region prevents nearby opponents from meeting\n\n")
    for match in chosen:
        file.write("Round {}\n".format(index))
        for m in range(n):
            east = m % (n*4)
            south = (n + (m + match[0]) % n) % (n*4)
            west = (2*n + (m + match[1]) % n) % (n*4)
            north = (3*n + (m + match[2]) % n) % (n*4)
            file.write("[{}, {}, {}, {}], ".format(east, south, west, north))
        file.write("\n\n")
        index += 1
    file.close()


def recurse(n, chosen):
    global currentBest
    southCandidateList = set(range(n))
    bestLayout = chosen
    bestScore = len(chosen)
    for round in chosen:
        southCandidateList.discard(round[0])
    for south in southCandidateList:
        westCandidateList = set(range(n))
        for round in chosen:
            westCandidateList.discard(round[1])
            westCandidateList.discard((round[1]-round[0]+south+n) % n)
        for west in westCandidateList:
            northCandidateList = set(range(n))
            for round in chosen:
                northCandidateList.discard(round[2])
                northCandidateList.discard((round[2]-round[1]+west+n) % n)
                northCandidateList.discard((round[2]-round[0]+south+n) % n)
            for north in northCandidateList:
                newChosen = copy.deepcopy(chosen)
                newChosen.append((south,west,north))
                newLayout = recurse(n, newChosen)
                newScore = len(newLayout)
                if newScore > bestScore:
                    endTime = time.time()
                    if endTime - startTime >= 5:
                        raise()
                    if newScore > currentBest:
                        print(newScore)
                        print(newLayout)
                        currentBest = newScore
                        layoutPrint(newChosen, n)
                        if currentBest == n:
                            raise()
                    bestScore = newScore
                    bestLayout = newLayout
        break
    return bestLayout


def easyMode(n):
    chosen = [(0, 0, 0)]
    south = 1 % n
    west = 2 % n
    north = 3 % n
    while south:
        chosen.append((south, west, north))
        south = (south + 1) % n
        west = (west + 2) % n
        north = (north + 3) % n
    layoutPrint(chosen, n)


def run(n):
    remainder = n % 6
    if remainder == 1:
        easyMode(n)
    elif remainder == 5:
        easyMode(n)
    else:
        initial = [(0, 0, 0)]
        print(recurse(n, initial))


startTime = time.time()
print("This will search for 5s, then print the best answer it can find")
try:
    n = 24*4
    if n % 4 == 0:
        run(int(n/4))
    else:
        print("Not Divisible by 4")
except:
    print("Done")
assign("output.txt")

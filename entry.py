from collections import defaultdict

class Entry:
    def __init__(self, user="User", country="Country", artist="Artist", song="Song", draw=0):
        self.user = user
        self.country = country
        self.artist = artist
        self.song = song

        self.draw = draw
        self.isDisqualified = False
        self.points = 0
        self.truePoints = 0
        self.numVoters = 0
        self.pointsList = []

    def addPoints(self, toAdd):
        if toAdd > -1:
            self.truePoints += toAdd
        if self.isDisqualified == False:
            self.points = self.truePoints

        if toAdd > 0:
            self.numVoters += 1

        if toAdd == -1:
            self.pointsList.append("X")
        elif toAdd == 0:
            self.pointsList.append("")
        else:
            self.pointsList.append(toAdd)



    def disqualify(self):
        self.pointsList.append("DQ")
        self.isDisqualified = True
        self.points = -1


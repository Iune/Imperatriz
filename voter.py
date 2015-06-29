class Voter:
    def __init__(self, votes, name="Name", country="Country"):
        self.name = name
        self.country = country
        self.votes = votes

    def vote(self, entries):
        if len(self.votes.keys()) == 0:
            for entry in entries.keys():
                if entries[entry].country == self.name:
                    entries[entry].disqualify()
                    print "*** Disqualified {} ***".format(entries[entry].country)

        for vote in self.votes.keys():
            points = int(self.votes[vote])
            entries[vote].addPoints(points)

        for entry in entries.keys():
            if entry not in self.votes.keys():
                if entries[entry].country == self.name:
                    entries[entry].addPoints(-1)
                else:
                    entries[entry].addPoints(0)
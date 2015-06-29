import unicodecsv

import entry
import voter

class Contest:
    def __init__(self, fileLocation, outputDirectory, name="Name"):
        self.name = name
        self.fileLocation = fileLocation
        self.outputDirectory = outputDirectory

        self.data = self.loadData()
        self.entries = {}
        self.voters = []
        self.numParticipants = 0
        self.numVoters = 0

        self.processData()

    def loadData(self):
        data = []
        csv_reader = unicodecsv.reader(open(self.fileLocation, 'rU'), quotechar='"', delimiter = ';')
        for row in csv_reader:
            data.append(row) 
        return data

    def processData(self):
        # First, we process entries
        count = 1
        for col in self.data[1:]:
            user = col[1]
            country = col[2]
            artist = col[3]
            song = col[4]
            
            key = artist + "_" + song
            self.entries[key] = entry.Entry(user, country, artist, song, count)
            count += 1
        self.numParticipants = count

        # Now, we process voters
        header = self.data[0]
        for i in range(6,len(header)):
            name = header[i]
            votes = {}
            for row in self.data[1:]:
                if row[i] != '' and row[i] != "X":
                    points = row[i]
                    entry_key = row[3] + "_" + row[4]
                    votes[entry_key] = points
            self.voters.append(voter.Voter(votes, name))
        self.numVoters = len(header) - 6

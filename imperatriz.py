from svgwrite.text import TSpan, TRef, TextPath
import copy
import operator
import svgwrite
import json
import subprocess

import entry
import voter
import contest

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def cleanGradients(filename):
    # Due to a bug in svgwrite, we have to clean up the svg file to allow the gradients to appear
    input = open(filename)
    original_file_lines = input.readlines()
    file_lines = copy.copy(original_file_lines)
    for index in range(len(file_lines)):
            line = file_lines[index]
            st = ' none\"'
            su = ' none;\"'
            if st in line:
                file_lines[index] = line.replace(st,'\"')
            if su in line:
                file_lines[index] = line.replace(su, ";\"")
    for index in range(len(file_lines)):
            line = file_lines[index]            
            fnt = '<svg'
            if fnt in line:
                file_lines[index] = line.replace(fnt,'<?xml-stylesheet type="text/css" href="@import url(http://fonts.googleapis.com/css?family=Lato:400,900,400italic&subset=latin,latin-ext"?>\n<svg')

    with open(filename, 'w') as g:
        g.writelines(file_lines)   

def generateImagePastel(flags, results, voter, voterNum, contest, outputDirectory, displayFlags, displayCountries):
    width = 600
    height = 60 + 22.5*(contest.numParticipants/2 + contest.numParticipants%2 - 1) + 10

    dwg = svgwrite.Drawing('{}/{} - {}.svg'.format(outputDirectory, voterNum, voter.name), profile='full', size=(width, height))    

    backColor = "#e3e3e3"
    textColor = "#ecf0f1"

    grey = "#A3A3A3"
    primary = "#3F51B5"
    secondary = "#FF669B"

    primary = "#005293"
    secondary = "#aa5293"

    primary = "#800080"
    secondary = "#ee82ee"

    goldGradient = dwg.linearGradient((0, 0), (1, 0))
    goldGradient.add_stop_color(0, "#e2ac60")
    goldGradient.add_stop_color(1, "#c68c48")
    dwg.defs.add(goldGradient) 
    #secondary = goldGradient.get_paint_server() 


    dwg.add(dwg.rect(insert=(0,0), size=("100%", "100%"), style="fill: {};".format(backColor))) 
    dwg.add(dwg.rect(insert=(0,0), size=("100%", 35), style="fill: {};".format(primary))) 
    dwg.add(dwg.rect(insert=(0,30), size=("100%", 25), style="fill: {};".format(secondary))) 

    dwg.add(dwg.text('{}'.format(str(contest.name)), insert=(15, 20), style="font-size:20px; font-weight:700; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(textColor)))                 
    dwg.add(dwg.text('Now Voting: {} ({}/{})'.format(str(voter.name),voterNum, contest.numVoters), insert=(15, 47.5), style="font-size:16px; font-weight:700; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(textColor)))                 

    songNum = 1
    leftHalf = contest.numParticipants/2 + contest.numParticipants%2 - 1
    for entry in results:
        entryData = dwg.g()
        key = entry.artist + '_' + entry.song
        receivedPoints = False
        for recipient in voter.votes.keys():
            if recipient in key or receivedPoints == True:
                receivedPoints = True

        songText = entry.song
        if (len(entry.artist) + len(entry.song)) > 30:
            cut_off = 30 - len(entry.artist)
            songText = entry.song[:cut_off] + (entry.song[cut_off:] and '...')

        if displayFlags:
            flagOffset = 30
        else:
            flagOffset = 0

        if songNum <= leftHalf:
            rightOffset = 0
            yOffset = songNum-1
        else:
            rightOffset = 290
            yOffset = songNum-leftHalf-1

        if receivedPoints:
            key = entry.artist + '_' + entry.song
            receivedPoints = voter.votes[key]
            entryFillColor = secondary
            receivedText = receivedPoints
        else:
            entryFillColor = grey
            receivedText = ""

        dwg.add(dwg.rect(insert=(15+rightOffset,60+22.5*(yOffset)), size=(250+flagOffset, 20), rx=7, ry=7, style="fill: {};".format(grey))) 
        dwg.add(dwg.rect(insert=(35+rightOffset,60+22.5*(yOffset)), size=(20, 20), style="fill: {};".format(entryFillColor))) 
        dwg.add(dwg.rect(insert=(55+rightOffset,60+22.5*(yOffset)), size=(24, 20), style="fill: {};".format(primary))) 
        if displayFlags:
            dwg.add(dwg.image(insert=(84+rightOffset, 60+22.5*(yOffset)), href="Square/{}.png".format(flags[entry.country].lower()), size=(20, 20)))      
  

        dwg.add(dwg.text('{}'.format(str(songNum)), insert=(25+rightOffset, 74+22.5*(yOffset)), style="font-size:12px; font-weight:300; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00; text-anchor: middle;".format(textColor)))                 

        dwg.add(dwg.text('{}'.format(str(songNum)), insert=(25+rightOffset, 74+22.5*(yOffset)), style="font-size:12px; font-weight:400; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00; text-anchor: middle;".format(textColor)))                 
        dwg.add(dwg.text('{}'.format(str(receivedText)), insert=(45+rightOffset, 74+22.5*(yOffset)), style="font-size:12px; font-weight:700; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00; text-anchor: middle;".format(textColor)))                 
        dwg.add(dwg.text('{}'.format(str(entry.truePoints)), insert=(67+rightOffset, 74+22.5*(yOffset)), style="font-size:12px; font-weight:700; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00; text-anchor: middle;".format(textColor)))                 
        if displayCountries == False:
            dwg.add(dwg.text('{} - {}'.format(str(entry.artist),str(songText)), insert=(110+rightOffset-(30-flagOffset), 74+22.5*(yOffset)), style="font-size:12px; font-weight:400; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(textColor)))                 
        else:
            dwg.add(dwg.text('{}'.format(str(entry.country)), insert=(110+rightOffset-(30-flagOffset), 74+22.5*(yOffset)), style="font-size:12px; font-weight:400; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(textColor)))                 


        songNum += 1
    dwg.save()
    cleanGradients('{}/{} - {}.svg'.format(outputDirectory, voterNum, voter.name))


def generateImageGold(results, voter, voterNum, contest, outputDirectory):
    dwg = svgwrite.Drawing('{}/{} - {}.svg'.format(outputDirectory, voterNum, voter.name), profile='full', size=(655, 120+(25*(int(contest.numParticipants/2) + contest.numParticipants%2))-35 ))    

    goldGradient = dwg.linearGradient((0, 0), (1, 0))
    goldGradient.add_stop_color(0, "#e2ac60")
    goldGradient.add_stop_color(1, "#c68c48")
    dwg.defs.add(goldGradient) 
    gold = goldGradient.get_paint_server() #"#e2ac60"

    dwg.add(dwg.rect(id="background", insert=(0,0), size=("100%", "100%"), style="fill: #333333; stroke: #000000; stroke-opacity: 1; stroke-width:0;")) 
    dwg.add(dwg.text('{}'.format(contest.name), insert=(330, 30), fill=gold, style="text-anchor: middle; font-size:25px; font-family:'Lato'; font-weight:900;"))
    dwg.add(dwg.text('Now Voting: {} ({}/{})'.format(voter.name, voterNum, contest.numVoters), insert=(330, 50), style="text-anchor:middle; font-size:20px; font-family:'Lato'; font-weight:400; fill:#e6e6e6;"))

    songNum = 1
    leftHalf = contest.numParticipants/2 + contest.numParticipants%2
    for entry in results:
        entryData = dwg.g()
        key = entry.artist + '_' + entry.song
        receivedPoints = False
        for recipient in voter.votes.keys():
            if recipient in key or receivedPoints == True:
                receivedPoints = True

        if (len(entry.artist) + len(entry.song)) > 43:
            cut_off = 43 - len(entry.artist)
            entry.song = entry.song[:cut_off] + (entry.song[cut_off:] and '...')

        if songNum <= leftHalf:
            rightOffset = 0
            yOffset = songNum-1
        else:
            rightOffset = 320
            yOffset = songNum-leftHalf-1

        dwg.add(dwg.rect(insert=(rightOffset+25,60+25*(yOffset)), size=(20, 20), fill=gold, rx=5, ry=5))
        dwg.add(dwg.text('{}'.format(songNum), insert=(rightOffset+35, 75+(25*(yOffset))), style="font-size:14px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00; text-anchor: middle;"))
        
        dwg.add(dwg.image(insert=(rightOffset+50, 60+25*(yOffset)), href="Flags/{}.png".format(entry.country), size=(30, 20)))      
        
        dwg.add(dwg.rect(insert=(rightOffset+85,60+25*(yOffset)), size=(160, 20), fill=gold, rx=5, ry=5))
        dwg.add(dwg.text('{}'.format(str(entry.country)), insert=(rightOffset+90, 75+25*(yOffset)), style="font-size:14px; font-weight:600; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00;"))                 
        
        dwg.add(dwg.rect(insert=(rightOffset+275,60+25*(yOffset)), size=(30, 20), fill=gold, rx=5, ry=5))
        
        dwg.add(dwg.text('{}'.format(entry.truePoints), insert=(rightOffset+290, 75+25*(yOffset)), style="text-anchor: middle; font-size:14px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00;"))
        dwg.add(dwg.text('{}'.format(entry.truePoints), insert=(rightOffset+290, 75+25*(yOffset)), style="text-anchor: middle; font-size:14px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00;"))

        if receivedPoints:
            key = entry.artist + '_' + entry.song
            receivedPoints = voter.votes[key]
            
            dwg.add(dwg.rect(insert=(rightOffset+250,60+25*(yOffset)), size=(20, 20), fill=gold, rx=5, ry=5))
            dwg.add(dwg.text('{}'.format(receivedPoints), insert=(rightOffset+260, 75+(25*(yOffset))), style="font-size:14px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00; text-anchor: middle;"))
 
        if voter.name == entry.country:            
            dwg.add(dwg.rect(insert=(rightOffset+250,60+25*(yOffset)), size=(20, 20), fill=gold, rx=5, ry=5))

            if entry.isDisqualified == False:
                dwg.add(dwg.text('X', insert=(rightOffset+260, 75+(25*(yOffset))), style="font-size:14px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00; text-anchor: middle;"))
            else:
                dwg.add(dwg.text('DQ'.format(receivedPoints), insert=(rightOffset+260, 73+(25*(yOffset))), style="font-size:10px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00; text-anchor: middle;"))                
        songNum += 1

    dwg.add(dwg.rect(insert=(25,65+25*(leftHalf)), size=(610, 10), fill="#fafafa", rx=2.5, ry=2.5))
    dwg.add(dwg.rect(insert=(25,65+25*(leftHalf)), size=(610*(float(voterNum)/float(contest.numVoters)), 10), fill=gold, rx=2.5, ry=2.5))

    dwg.save()
    # Due to a bug in svgwrite, we have to clean up the svg file to allow the gradients to appear
    cleanGradients('{}/{} - {}.svg'.format(outputDirectory, voterNum, voter.name))

def generateSummaryGold(results, contest, outputDirectory):

    width = 285 + 25*contest.numVoters+25
    height = 50+(25*contest.numParticipants)
    dwg = svgwrite.Drawing('{}/{} - Summary.svg'.format(outputDirectory, contest.name), profile='full', size=(width, height))    

    goldGradient = dwg.linearGradient((0, 0), (1, 0))
    goldGradient.add_stop_color(0, "#e2ac60")
    goldGradient.add_stop_color(1, "#c68c48")
    dwg.defs.add(goldGradient) 
    gold = goldGradient.get_paint_server() #"#e2ac60"

    dwg.add(dwg.rect(id="background", insert=(0,0), size=("100%", "100%"), style="fill: #333333; stroke: #000000; stroke-opacity: 1; stroke-width:0;")) 
    dwg.add(dwg.text('{}'.format(contest.name), insert=(width/2, 30), fill=gold, style="text-anchor: middle; font-size:25px; font-family:'Lato'; font-weight:900;"))

    songNum = 1
    for entry in results:
        yOffset = songNum - 1
        dwg.add(dwg.rect(insert=(25,60+25*(yOffset)), size=(20, 20), fill=gold, rx=5, ry=5))
        dwg.add(dwg.text('{}'.format(songNum), insert=(35, 75+(25*(yOffset))), style="font-size:14px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00; text-anchor: middle;"))
        
        dwg.add(dwg.image(insert=(50, 60+25*(yOffset)), href="Flags/{}.png".format(entry.country), size=(30, 20)))      
        
        dwg.add(dwg.rect(insert=(85,60+25*(yOffset)), size=(160, 20), fill=gold, rx=5, ry=5))
        dwg.add(dwg.text('{}'.format(str(entry.country)), insert=(90, 75+25*(yOffset)), style="font-size:14px; font-weight:600; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00;"))                 
        
        dwg.add(dwg.rect(insert=(250,60+25*(yOffset)), size=(30, 20), fill=gold, rx=5, ry=5))
        dwg.add(dwg.text('{}'.format(entry.truePoints), insert=(265, 75+25*(yOffset)), style="text-anchor: middle; font-size:14px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00;"))

        for i in range(0, len(contest.voters)):
            vote = entry.pointsList[i]
            voterName = contest.voters[i].name

            dwg.add(dwg.image(insert=(285+25*i, 40), href="Flags/{}.png".format(voterName), size=(20, 13.33)))      
            if vote != "":
                dwg.add(dwg.rect(insert=(285+25*i,60+25*(yOffset)), size=(20, 20), fill=gold, rx=5, ry=5))
                
                if vote != "DQ":
                    dwg.add(dwg.text('{}'.format(vote), insert=(295+25*i, 75+25*(yOffset)), style="text-anchor: middle; font-size:14px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00;"))
                else:
                    dwg.add(dwg.text('DQ'.format(vote), insert=(295+25*i, 73+25*(yOffset)), style="text-anchor: middle; font-size:11px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00;"))                    

        songNum += 1

    dwg.save()
    cleanGradients('{}/{} - Summary.svg'.format(outputDirectory, contest.name))

    print "Generated Summary Image"

def generateImageAirline(flags, results, voter, voterNum, contest, outputDirectory, displayFlags, displayCountries):
    width = 1105
    height = 40+(35*(int(contest.numParticipants/2) + contest.numParticipants%2))-35

    flights = loadFlights()

    dwg = svgwrite.Drawing('{}/{} - {}.svg'.format(outputDirectory, voterNum, voter.name), profile='full', size=(width, height))    

    white="#fdfdfe"
    color="#5054a4"
    font="Helvetica Neue"

    dwg.add(dwg.rect(id="background", insert=(0,0), size=("100%", "100%"), fill=white, style="stroke: {}; stroke-opacity: 1; stroke-width:2px;".format(color))) 
    dwg.add(dwg.rect(insert=(0,0), size=("100%", 50), fill=color)) 

    dwg.add(dwg.text('Pts.', insert=(20, 40), style="font-size:20px; font-family:'{}'; font-weight:900; fill:{}".format(font, white)))
    dwg.add(dwg.text('Flight', insert=(185, 40), style="font-size:20px; font-family:'{}'; font-weight:900; fill:{}".format(font, white)))

    dwg.add(dwg.text('Pts.', insert=(20+550, 40), style="font-size:20px; font-family:'{}'; font-weight:900; fill:{}".format(font, white)))
    dwg.add(dwg.text('Flight', insert=(185+550, 40), style="font-size:20px; font-family:'{}'; font-weight:900; fill:{}".format(font, white)))

    songNum = 1
    leftHalf = contest.numParticipants/2 + contest.numParticipants%2
    for entry in results:
        entryData = dwg.g()
        key = entry.artist + '_' + entry.song
        receivedPoints = False
        for recipient in voter.votes.keys():
            if recipient in key or receivedPoints == True:
                receivedPoints = True

        if songNum <= leftHalf:
            rightOffset = 0
            yOffset = songNum-1
        else:
            rightOffset = 550
            yOffset = songNum-leftHalf-1

        dwg.add(dwg.text(insert=(40+rightOffset, 70+30*yOffset), text='{}'.format(entry.truePoints), fill=color, style="text-anchor:end; font-size:20px; font-family:'{}'; font-weight:900;".format(font)))            

        #dwg.add(dwg.text(insert=(55+rightOffset, 70+30*yOffset), text='12', fill=color, style="text-anchor:middle; font-size:20px; font-family:'{}'; font-weight:300;".format(font)))

        flightCity = flights[entry.country]['city']
        flightAirline = flights[entry.country]['airline']
        flightNum = flights[entry.country]['flight']

        dwg.add(dwg.image(insert=(75+rightOffset,47.5+30*yOffset), href="{}.svg".format(flightAirline), size=(100, 30), fill=color))      
        dwg.add(dwg.text(insert=(185+rightOffset, 70+30*yOffset), text='{} {}'.format(flightAirline,flightNum), fill=color, style="font-size:20px; font-family:'{}'; font-weight:500;".format(font)))
        dwg.add(dwg.text(insert=(270+rightOffset, 70+30*yOffset), text='{}, {}'.format(flightCity, entry.country), fill=color, style="font-size:20px; font-family:'{}'; font-weight:300;".format(font)))

        dwg.add(dwg.line(start=(555,0), end=(555,height), style="stroke: {}; stroke-opacity: 1; stroke-width:1px;".format(color)))

        if receivedPoints:
            key = entry.artist + '_' + entry.song
            receivedPoints = voter.votes[key]
            
            dwg.add(dwg.text(insert=(55+rightOffset, 70+30*yOffset), text='{}'.format(receivedPoints), fill=color, style="text-anchor:middle; font-size:20px; font-family:'{}'; font-weight:300;".format(font)))
 
        if voter.name == entry.country:            
            if entry.isDisqualified == False:
                dwg.add(dwg.text('X', insert=(rightOffset+260, 75+(25*(yOffset))), style="font-size:14px; font-weight:400; font-family:'Lato'; fill:#fafafa; fill-opacity:1.00; text-anchor: middle;"))
            else:
                dwg.add(dwg.text(insert=(55+rightOffset, 70+30*yOffset), text='DQ', fill=color, style="text-anchor:middle; font-size:20px; font-family:'{}'; font-weight:300;".format(font)))


        songNum += 1

    dwg.save()
    cleanGradients('{}/{} - {}.svg'.format(outputDirectory, voterNum, voter.name))

def loadFlights():
    flights = {}
    with open('flights.csv', 'r') as f:
        data = f.read().split('\n')
        
    for line in data:
        info = line.split(',')
        country = info[0]
        airline = info[1]
        flight = info[2]
        city = info[3]

        flights[country] = {'airline': airline, 'flight': flight, 'city': city}
    return flights

def generateImageClean(flags, results, voter, voterNum, contest, outputDirectory, displayFlags, displayCountries):
    width = 600
    height = 100 + (contest.numParticipants/2 + contest.numParticipants%2 - 0.75)*22 + 20

    dwg = svgwrite.Drawing('{}/{} - {}.svg'.format(outputDirectory, voterNum, voter.name), profile='full', size=(width, height))    

    white = "#FFFFFF"
    textColor = "#333333"
    darkGrey = "#5B5B5B"
    lightGrey = "#EEEEEE"
    
    #color = "#4FDEB2" #SFGreen
    #color = "#6755E3" #OneWorldPurple
    color = "#FF7575" #Salmon

    dwg.add(dwg.rect(insert=(0,0), size=("100%", "100%"), style="fill: {};".format(lightGrey))) 
    
    dwg.add(dwg.rect(insert=(20,20), size=(width-40, 60), rx=10, ry=10, style="fill: {};".format(white))) 
    dwg.add(dwg.rect(insert=(20,20), size=(width-40, 30), rx=10, ry=10, style="fill: {};".format(color))) 
    dwg.add(dwg.rect(insert=(20,40), size=(width-40, 10), style="fill: {};".format(color))) 

    dwg.add(dwg.rect(insert=(20,90), size=(270, 20+(contest.numParticipants/2 + contest.numParticipants%2 - 0.75)*22), rx=10, ry=10, style="fill: {};".format(white))) 
    dwg.add(dwg.rect(insert=(20,90), size=(270, 20), rx=10, ry=10, style="fill: {};".format(color))) 
    dwg.add(dwg.rect(insert=(20,100), size=(270, 10), style="fill: {};".format(color))) 

    dwg.add(dwg.rect(insert=(310,90), size=(270, 20+(contest.numParticipants/2 + contest.numParticipants%2 - 0.75)*22), rx=10, ry=10, style="fill: {};".format(white))) 
    dwg.add(dwg.rect(insert=(310,90), size=(270, 20), rx=10, ry=10, style="fill: {};".format(color))) 
    dwg.add(dwg.rect(insert=(310,100), size=(270, 10), style="fill: {};".format(color))) 

    dwg.add(dwg.text('{}'.format(str(contest.name)), insert=(30, 43), style="font-size:20px; font-weight:700; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(white)))                 
    dwg.add(dwg.text('Now Voting: {} ({}/{})'.format(str(voter.name),voterNum, contest.numVoters), insert=(30, 70), style="font-size:16px; font-weight:300; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(textColor)))                 

    songNum = 1
    leftHalf = contest.numParticipants/2 + contest.numParticipants%2 - 1
    for entry in results:
        entryData = dwg.g()
        key = entry.artist + '_' + entry.song
        receivedPoints = False
        for recipient in voter.votes.keys():
            if recipient in key or receivedPoints == True:
                receivedPoints = True

        songText = entry.song
        if (len(entry.artist) + len(entry.song)) > 35:
            cut_off = 35 - len(entry.artist)
            songText = entry.song[:cut_off] + (entry.song[cut_off:] and '...')

        if songNum <= leftHalf:
            rightOffset = 0
            yOffset = songNum-1
        else:
            rightOffset = 290
            yOffset = songNum-leftHalf-1

        if receivedPoints:
            key = entry.artist + '_' + entry.song
            receivedPoints = voter.votes[key]
            receivedText = receivedPoints

        dwg.add(dwg.text('{}.'.format(str(songNum)), insert=(32+rightOffset, 125+22*(yOffset)), style="font-size:12px; font-weight:300; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00; text-anchor: middle;".format(textColor)))                 
        
        if receivedPoints:
            dwg.add(dwg.circle(center=(54+rightOffset,121+22*(yOffset)), r=8, fill=color))
            dwg.add(dwg.text('{}'.format(str(receivedText)), insert=(54+rightOffset, 125+22*(yOffset)), style="font-size:12px; font-weight:700; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00; text-anchor: middle;".format(white)))                 

        dwg.add(dwg.text('{}'.format(str(entry.truePoints)), insert=(85+rightOffset, 125+22*(yOffset)), style="font-size:12px; font-weight:400; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00; text-anchor: end;".format(textColor)))                 
        if displayCountries == False:
            dwg.add(dwg.text('{} - {}'.format(str(entry.artist),str(songText)), insert=(90+rightOffset, 125+22*(yOffset)), style="font-size:12px; font-weight:300; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(textColor)))                 
        else:
            dwg.add(dwg.text('{}'.format(str(entry.country)), insert=(90+rightOffset, 125+22*(yOffset)), style="font-size:12px; font-weight:300; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(textColor)))                 

        if songNum != leftHalf and songNum != contest.numParticipants - 1:
            dwg.add(dwg.line(start=(90+rightOffset,130.5+22*(yOffset)), end=(290+rightOffset,130.5+22*(yOffset)), style="stroke: {}; stroke-opacity: 1; stroke-width:0.5px;".format(lightGrey)))

        songNum += 1
    dwg.save()
    cleanGradients('{}/{} - {}.svg'.format(outputDirectory, voterNum, voter.name))

def generateImageThermometer(flags, results, voter, voterNum, contest, outputDirectory, displayFlags, displayCountries):
    width = 600
    height = 90 + contest.numParticipants*22 + 20

    dwg = svgwrite.Drawing('{}/SVG/{} - {}.svg'.format(outputDirectory, voterNum, voter.name), profile='full', size=(width, height))    

    white = "#FFFFFF"
    textColor = "#333333"
    darkGrey = "#5B5B5B"
    lightGrey = "#EEEEEE"
    
    #color = "#4FDEB2" #SFGreen
    color = "#6755E3" #OneWorldPurple
    #color = "#FF7575" #Salmon
    #color = "#002868" #LaotianBlue

    dwg.add(dwg.rect(insert=(0,0), size=("100%", "100%"), style="fill: {};".format(lightGrey))) 
    
    dwg.add(dwg.rect(insert=(20,20), size=(width-40, 60), rx=10, ry=10, style="fill: {};".format(white))) 
    dwg.add(dwg.rect(insert=(20,20), size=(width-40, 30), rx=10, ry=10, style="fill: {};".format(color))) 
    dwg.add(dwg.rect(insert=(20,40), size=(width-40, 10), style="fill: {};".format(color))) 

    dwg.add(dwg.rect(insert=(20,90), size=(width-40, 20+(contest.numParticipants - 0.75)*22), rx=10, ry=10, style="fill: {};".format(white))) 
    dwg.add(dwg.rect(insert=(20,90), size=(width-40, 20), rx=10, ry=10, style="fill: {};".format(color))) 
    dwg.add(dwg.rect(insert=(20,100), size=(width-40, 10), style="fill: {};".format(color))) 

    dwg.add(dwg.line(start=(290,110), end=(290,110+(contest.numParticipants - 0.75)*22), style="stroke: {}; stroke-opacity: 1; stroke-width:1px;".format(lightGrey)))

    dwg.add(dwg.text('{}'.format(str(contest.name)), insert=(30, 43), style="font-size:18px; font-weight:700; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(white)))                 
    dwg.add(dwg.text('Now Voting: {} ({}/{})'.format(str(voter.name),voterNum, contest.numVoters), insert=(30, 70), style="font-size:14px; font-weight:300; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(textColor)))                 

    songNum = 1
    for entry in results:
        key = entry.artist + '_' + entry.song
        receivedPoints = False
        for recipient in voter.votes.keys():
            if recipient in key or receivedPoints == True:
                receivedPoints = True

        songText = entry.song
        if (len(entry.artist) + len(entry.song)) > 34:
            cut_off = 34 - len(entry.artist)
            songText = entry.song[:cut_off] + (entry.song[cut_off:] and '...')

        yOffset = songNum-1

        if receivedPoints:
            key = entry.artist + '_' + entry.song
            receivedPoints = voter.votes[key]
            receivedText = receivedPoints

        dwg.add(dwg.text('{}.'.format(str(songNum)), insert=(32, 130+22*(yOffset)), style="font-size:12px; font-weight:300; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00; text-anchor: middle;".format(textColor)))                 
        
        if receivedPoints:
            dwg.add(dwg.circle(center=(54,126+22*(yOffset)), r=8, fill=color))
            dwg.add(dwg.text('{}'.format(str(receivedText)), insert=(54, 130+22*(yOffset)), style="font-size:12px; font-weight:700; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00; text-anchor: middle;".format(white)))                 

        dwg.add(dwg.text('{}'.format(str(entry.truePoints)), insert=(85, 130+22*(yOffset)), style="font-size:12px; font-weight:400; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00; text-anchor: end;".format(textColor)))                 
        if displayCountries == False:
            dwg.add(dwg.text('{} - {}'.format(str(entry.artist),str(songText)), insert=(90, 130+22*(yOffset)), style="font-size:12px; font-weight:300; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(textColor)))                 
        else:
            dwg.add(dwg.text('{}'.format(str(entry.country)), insert=(90, 130+22*(yOffset)), style="font-size:12px; font-weight:300; font-family:'Roboto Condensed'; fill:{}; fill-opacity:1.00;".format(textColor)))                 

        if songNum != contest.numParticipants - 1:
            dwg.add(dwg.line(start=(90,135.5+22*(yOffset)), end=(290,135.5+22*(yOffset)), style="stroke: {}; stroke-opacity: 1; stroke-width:1px;".format(lightGrey)))

        if entry.truePoints > 0:
            dwg.add(dwg.rect(insert=(290,118+22*(yOffset)), size=(3,12), style="fill: {};".format(color))) 
            dwg.add(dwg.rect(insert=(290,118+22*(yOffset)), size=((275*float(entry.truePoints)/results[0].truePoints),12), rx=3, ry=3, style="fill: {};".format(color))) 

        songNum += 1
    dwg.save()
    cleanGradients('{}/SVG/{} - {}.svg'.format(outputDirectory, voterNum, voter.name))
    subprocess.call(["svgexport", '{}/SVG/{} - {}.svg'.format(outputDirectory, voterNum, voter.name), '{}/PNG/{} - {}.png'.format(outputDirectory, voterNum, voter.name), "png", "100%", "2x"])

def main():
    flags = {}
    with open("countries.json", "r") as f:
        temp = json.load(f)
    for item in temp:
        flags[item['name']] = item['alpha-2']

    theContest = contest.Contest("niew.csv", "Output", "2010's MC 51: Results")
    voterNum = 1
    for voter in theContest.voters:

        voter.vote(theContest.entries)
        results = sorted(theContest.entries.values(), key=operator.attrgetter('points', 'truePoints', 'numVoters'), reverse=True)
        generateImageThermometer(flags, results, voter, voterNum, theContest, theContest.outputDirectory, True, False)
        print results[0].country
        voterNum += 1
    #generateSummaryGold(results, theContest, theContest.outputDirectory)

if __name__ == "__main__":
    main()
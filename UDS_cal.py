#! /usr/bin/env python
from urllib2 import urlopen
from xml.dom import minidom as xdm
from icalendar import Calendar, Event
from datetime import datetime
import pytz

projectId = 2   # depends on study year
detailLevel = 8 # level of detail for events, highest
calDest = "calendars"


def exportCal(resourceCode):
    cal = Calendar()

    # get SessionID
    raw = urlopen("http://ade52-savoie.grenet.fr/ade/webapi?function=connect&login=ETUDIANT&password=etsa").read()
    xml = xdm.parseString(raw)
    sessionId = xml.documentElement.getAttributeNode('id').nodeValue

    # set ProjectID
    urlopen("http://ade52-savoie.grenet.fr/ade/webapi?sessionId=%s&function=setProject&projectId=%s" % (sessionId, projectId)).read()

    # get Calendar
    raw = urlopen("http://ade52-savoie.grenet.fr/ade/webapi?sessionId=%s&function=getEvents&resources=%s&detail=%s" % (sessionId, resourceCode, detailLevel)).read()
    events = xdm.parseString(raw).getElementsByTagName("event")
    for event in events:
        ev = Event()
        evID = event.getAttributeNode("id").nodeValue
        evSession = event.getAttributeNode("session").nodeValue
        evName = event.getAttributeNode("name").nodeValue
        (evEndH, evEndM) = event.getAttributeNode("endHour").nodeValue.split(":")
        (evStartH, evStartM) = event.getAttributeNode("startHour").nodeValue.split(":")
        evDate = event.getAttributeNode("date").nodeValue

        date = datetime.strptime(evDate, "%d/%m/%Y")
        ev.add('dtstart', datetime(date.year,date.month,date.day,int(evStartH),int(evStartM),0,tzinfo=pytz.timezone("Europe/Paris")))
        ev.add('dtend', datetime(date.year,date.month,date.day,int(evEndH),int(evEndM),0,tzinfo=pytz.timezone("Europe/Paris")))
        ev.add("summary", evName)

        evDescription = ""
        eventResources = event.getElementsByTagName("resource")
        for resource in eventResources:
            rCategory = resource.getAttributeNode("category").nodeValue
            rName = resource.getAttributeNode("name").nodeValue
            if rCategory == "classroom":
                ev.add('location', rName)
            elif rCategory != "trainee":
                evDescription += "%s\n" % (rName)
        ev.add("description", evDescription)

        cal.add_component(ev)

    f = open("%s/%s.ics" % (calDest, resourceCode), "wb")
    f.write(cal.to_ical())
    f.close()


if __name__=="__main__":
    resource = "4295"    # M2-S9-STIC-TR-PRO-1
    print "Exporting cal %s" % (resource)
    exportCal(resource)

#These waypoints are selected from all the paths.
import socket
import sys
import time
from parseMap import *

#postgresql://postgres:123456@docker.for.mac.localhost:33121/apm_missions
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('172.16.165.100', 14555)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

##a = KMLHandler()
##path_key = a.get_closest_path_key(38.967163,-104.819837)
##path = a.polydict[path_key]

#centroid = a.get_centroid(path) #returns (lat,lon)
waypoints = []
waypoints.append(('FLIGHT', 'SET_MISSION_ITEM', 0, 1, 0, 16, 0.0, 0.0, 0.0, 0.0, 38.967163, -104.819837, 2004.4, 1, 0))#Is this the airport?
waypoints.append(('FLIGHT', 'SET_MISSION_ITEM', 1, 0, 3, 22, 0.0, 0.0, 0.0, 0.0, 38.965163, -104.817837, 50.0, 1, 0))#Have to figure the take off out
#waypoints.append(('FLIGHT', 'SET_MISSION_ITEM', 2, 0, 3, 16, 0.0, 0.0, 0.0, 0.0, centroid[1], centroid[0], 50.0, 1, 0))
#waypoints.append(('FLIGHT', 'SET_MISSION_ITEM', 2, 0, 3, 16, 0.0, 0.0, 0.0, 0.0, centroid[1], centroid[0], 2015.110001, 1, 0))

messages = ["('FLIGHT', 'CLEAR_MISSION')",
         "('FLIGHT', 'SET_MISSION_COUNT', 100)",
         str(waypoints[0]),
         str(waypoints[1])]
         #str(waypoints[2])]

#The new idea in version 3 is to build the message bit by bit
#Obviously keep the first 4 messages

more_waypoints = []
a = KMLHandler()
path_key = a.get_closest_path_key(38.967163,-104.819837)
c1 = a.get_centroid(a.polydict[path_key]['points'])
print 'c1', c1
new_key = a.get_closest_path_key(c1[1],c1[0])
print "new key", new_key
c2 = a.get_centroid(a.polydict[new_key]['points'])
print 'c2', c2
third = a.get_closest_path_key(c2[1],c2[0])
print 'third', third
c3 = a.get_centroid(a.polydict[third]['points'])
print 'c3', c3

more_waypoints.append(('FLIGHT', 'SET_MISSION_ITEM', 2, 0, 3, 16, 0.0, 0.0, 0.0, 0.0, c1[0], c1[1], 50.0, 1, 0))
more_waypoints.append(('FLIGHT', 'SET_MISSION_ITEM', 3, 0, 3, 16, 0.0, 0.0, 0.0, 0.0, c2[0], c2[1], 50.0, 1, 0))
more_waypoints.append(('FLIGHT', 'SET_MISSION_ITEM', 4, 0, 3, 16, 0.0, 0.0, 0.0, 0.0, c3[0], c3[1], 50.0, 1, 0))

messages.append(str(more_waypoints[0]))
messages.append(str(more_waypoints[1]))
messages.append(str(more_waypoints[2]))

print messages
#messages = ["('FLIGHT', 'CLEAR_MISSION')",
#            "('FLIGHT', 'SET_MISSION_COUNT', 3)",
#            "('FLIGHT', 'SET_MISSION_ITEM', 0, 1, 0, 16, 0.0, 0.0, 0.0, 0.0, 38.967175, -104.819837, 584.390015, 1, 0)",
#            "('FLIGHT', 'SET_MISSION_ITEM', 1, 0, 3, 22, 0.0, 0.0, 0.0, 0.0, 38.97000, -104.163986, 28.110001, 1, 0)",
#            "('FLIGHT', 'SET_MISSION_ITEM', 2, 0, 3, 16, 0.0, 0.0, 0.0, 0.0, 38.99515, -104.158615, 99.800003, 1, 0)",
#            "('FLIGHT', 'SET_MISSION_CURRENT', 0)",
#            "('FLIGHT', 'ARM')"]#,
#"('FLIGHT', 'SET_MODE', 'AUTO')"]


for msg in messages:
    time.sleep(3)
    print 'sending', msg
    sock.sendall(msg)

    while 1:
        data = sock.recv(4096)
        if data:
            print 'recvd "%s"' % data
            break
print 'closing'
sock.close()








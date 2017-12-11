import socket
import sys
import time
import json

#this is a waypoint planning agent
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 37999)
sock.connect(server_address)

print >> sys.stderr, 'connecting to %s on port %s' % server_address

waypoints = []

waypoints.append(('FLIGHT', 'SET_MISSION_ITEM', 0, 1, 0, 16, 0.0, 0.0, 0.0, 0.0, 38.967163, -104.819837, 2004.4, 1, 0))#Is this the airport?
waypoints.append(('FLIGHT', 'SET_MISSION_ITEM', 1, 0, 3, 22, 0.0, 0.0, 0.0, 0.0, 38.965163, -104.817837, 50.0, 1, 0))#Need something more sensible here


#Just a helper function that might be useful
def compose_message(prefix,message):
    r_dict = {prefix:message}
    r_dict = json.dumps(r_dict) + "\r\n"
    return r_dict



messages = []
#Going to load some messages and get them out of the way first
#These are Forward_Message because they are commands that need to be
#forwarded to mavsim


messages.append(compose_message("forward_message","('FLIGHT', 'CLEAR_MISSION')"))
messages.append(compose_message("forward_message","('FLIGHT', 'SET_MISSION_COUNT', 100)"))
for x in waypoints:
    messages.append(compose_message("forward_message",str(x)))


print messages


lat = 38.967163
lon = -104.81937
t_lat = 38.99343742021595
t_lon = -105.05530266366
#-105.055302663666,38.99343742021595
#Initial setup: send all the messages composed so far
for msg in messages:
    time.sleep(1)#just because but not needed (I don't think).
    print 'sending', msg
    sock.sendall(msg)

    while 1:
        #I actually don't care about the data
        #I'll assume it was recieved ok
        data = sock.recv(4096)
        if data:
            print 'recvd "%s"' % data
            break


#Here I can do some stuff
#Get the nearest path centroid
#which could be an extra waypoint
#{"Map_Request":{"method":"closestPathKey","args":{"lat":38.967163,"lon":-104.819837}}}
current_imagined_lat = lat
current_imagined_lon = lon
data = None

radius = 7300#get me all the paths within a radius of 7.3 km
mission_item = 2
used_paths = [] #Memory?
target_bearing_and_distance_msg = compose_message("Map_Request",{"method":"getBearingAndDistance","args":{"lat1":lat,"lon1":lon,"lat2":t_lat,"lon2":t_lon}})
sock.sendall(target_bearing_and_distance_msg)
print "TARGET"
while 1:
    data = sock.recv(4096)
    if data:
        print 'recvd "%s"' % data
        break


#Simulation loop
for i in range(5):




    msg = compose_message("Map_Request",{"method":"pathInRadius","args":{"lat":lat,"lon":lon,"meters":radius,"exclude_list":used_paths}})
    print 'sending', msg
    sock.sendall(msg)

    while 1: #twisted might be a better solution here
        data = sock.recv(4096)
        if data:
            print '-recvd "%s"' % data
            break
    index = data.rfind("}")
    data = data[:index+1]
    data = json.loads(data)
    #just pick the first path (just cause)
    if "Error" in data:
        break
    path = data.keys()[0]
    used_paths.append(path)
    current_imagined_lat = data[path]['centroid'][0]
    current_imagined_lon = data[path]['centroid'][1]

    msg = compose_message("forward_m(essage","('FLIGHT', 'SET_MISSION_ITEM', " + repr(mission_item) + ", 0, 3, 16, 0.0, 0.0, 0.0, 0.0, " + repr(current_imagined_lat) + ", " + repr(current_imagined_lon) + ", 50.0, 1, 0)")
    print 'sending', msg
    sock.sendall(msg)

    while 1: #twisted might be a better solution here
        data = sock.recv(4096)
        if data:
            print 'recvd "%s"' % data
            break
    mission_item += 1
    radius = 4000

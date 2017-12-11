from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Protocol, DatagramProtocol, ClientFactory
from sys import stdout
import json
import yaml
import parseMap
from collections import OrderedDict

import time

class MasterServerProtocol(LineReceiver):
    delimiter = '\n'
    def __init__(self):
        self.buffer = {}
        self.telemetryProtocol = None #Set by the factory
        self.telemetryMode = "R"
        self.mapInfo = False
        #"R" = request:
        #"D" = Forward them as they arrive

        self.command_map = {'Map_Request':{'setup_map':[self.setupMap]},
                            'Telemetry_Request':{'get_item':'self.sendLine(json.dumps(self.buffer[jLine[\'Telemetry_Request\'][\'get_item\']))'},
                            'Server_Request':{'set_mode':'self.telemetryMode = jLine[\'Server_Request\'][\'set_mode\']'}}

    def getBearingAndDistance(self,lat1,lon1,lat2,lon2):
        if self.mapInfo:
            return self.mapInfo.get_bearing_and_distance(lat1,lon1,lat2,lon2)
        else:
            self.setupMap()
            return self.mapInfo.get_bearing_and_distance(lat1,lon1,lat2,lon2)



    def connectionMade(self):
        self.udpProtocol = UDPClient()
        self.udpProtocol.master = self
        reactor.listenUDP(0, self.udpProtocol)
        print "UDP protocol started."

        self.TelemetryFactory = TelemetryClientFactory(self,self.buffer)
        reactor.connectTCP('localhost', 40999, self.TelemetryFactory)

    def setupMap(self):
        self.mapInfo = parseMap.KMLHandler()

    def closestPathKey(self,lat,lon):
        if self.mapInfo:
            key = self.mapInfo.get_closest_path_key(lat,lon)
            print "KEY", key
        else:
            self.setupMap()
            self.closestPathKey(lat,lon)

    def getClosestPathCentroid(self,lat,lon):
        pass

    def pathInRadius(self,lat,lon,meters=1000,exclude_list=[]):
        if self.mapInfo:
            #value should be list
            value = self.mapInfo.paths_in_radius(lat,lon,meters,exclude_list)
            print "pathInRadius value", value
            #r_dict = {"values":value}
            #something a little richer
            if value:
                r_dict = self.mapInfo.get_enriched_paths_by_names(lat,lon,value)
                #print "R_DICT", r_dict
                #print "dumps", json.dumps(r_dict)
                #print "asdf"
                print "pathInRadius r_dict", r_dict
                return r_dict #self.sendLine(json.dumps(r_dict))
            else:
                return {"Error":"No Paths "}
        else:
            self.setupMap()
            return self.pathInRadius(lat,lon,meters,exclude_list)#self.sendLine(json.dumps(err))

    def do_dict(self, data):
        '''There's probably a better way to walk the dictionary.'''
        r_list = []
        for k, v in data.items():
            #print "k,v:", k, v, type(k)
            if isinstance(k, unicode):
                if not k.isdigit():
                    r_list.append(str(k))
            if isinstance(v, OrderedDict):
                r_list = r_list + self.do_dict(v)
                continue
            else:
                r_list.append(v)
        return r_list
    # def do_dict(self,data):
    #     '''There's probably a better way to walk the dictionary.'''
    #     r_list = []
    #     for k, v in data.items():
    #         r_list.append(k)
    #         if isinstance(v, OrderedDict):
    #             r_list.append(self.do_dict(v))
    #         r_list.append(v)


        #for k, v in data.iteritems():

        
        # if isinstance(data, dict):
        #     for k, v in data.iteritems():
        #         if isinstance(k,str) or isinstance(k,unicode):
        #             if not k[0:3] == 'ppp':
        #                 print "adding k", k
        #                 r_list.append(k.encode('UTF-8'))
        #         if isinstance(v, dict):
        #             print "recursing v", v
        #             r_list = r_list + self.do_dict(v)
        #         else:
        #             if isinstance(v,str) or isinstance(v,unicode):
        #                 print "adding v", v
        #                 r_list.append(v.encode('UTF-8'))
        #             else:
        #                 print "adding v", v
        #                 r_list.append(v)
        #     return r_list
        # return r_list

    def lineReceived(self, line):#
        #Do protocol here
        print "LINE", line
        jLine = None
        try:
            jLine = json.loads(line, object_pairs_hook=OrderedDict)
        except ValueError:
            print 'Line', line, 'is not JSON'
            return 0

        if jLine:
            msg = None
            if 'Map_Request' in jLine:
                method = jLine['Map_Request']['method']
                kwargs = jLine['Map_Request']['args']
                method_to_call = False
                try:
                    method_to_call = getattr(self, method)
                except AttributeError:
                    msg = {'Error':repr(AttributeError)}
                    self.sendLine(json.dumps(msg))
                    return 0
                if method_to_call:
                    msg = method_to_call(**kwargs)
                    print "send33", msg, "from", method
                    self.sendLine(json.dumps(msg))
                    return 0



            elif 'Telemetry_Request' in jLine:
                if jLine['Telemetry_Request'] in self.buffer:
                    self.sendLine(json.dumps(self.buffer[jLine['Telemetry_Request']]))
                else:
                    print "nay"

            elif 'Server_Request' in jLine:
                eval(self.command_map['Server_Request'][jLine['Server_Request']])

            elif 'Forward_Message' in jLine or 'forward_message' in jLine:
                msg = jLine['Forward_Message']

                new_message = ()
                #new_message = (msg.keys()[0].upper().encode('UTF-8'),)
                messages = self.do_dict(msg)
                for x in messages:
                    new_message = new_message + (x,)
                #new_message = new_message + (self.do_dict(msg),)
                print "new_message", new_message
                #new_message = ()
                #new_message = new_message + (msg.keys()[0].upper().encode('UTF-8'),)
                #new_message = new_message + (msg[msg.keys()[0]].encode('UTF-8'),)

                ##msg = msg# + "\r"
                new_message = repr(new_message) #+ "\r"
                #print "new_message", new_message
                self.udpProtocol.transport.write(new_message)#.encode('UTF-8'))




class UDPClient(DatagramProtocol):
    #should have a .master
    def startProtocol(self):
        print "Starting UDP protocol on 34555."
        self.transport.connect('127.0.0.1', 34555)
        #self.transport.write(b"('SIM', 'CLOSE')")

    def datagramReceived(self, datagram, addr):
        print "Datagram received", repr(datagram)
        #Convert the datagram into JSON
        if datagram[0] == '(':
            datagram = eval(datagram)
            print "DATAGRAM", datagram
            #Now it should be a tuple
            r_dict = {datagram[0]: datagram[1]}
        print "Sending", repr(r_dict) + "\r\n"
        self.master.sendLine(json.dumps(r_dict) + "\r\n")
        self.master.sendLine(json.dumps({}) + "\r\n")

        #self.master.sendLine(datagram) #untested


class TelemetryClientFactory(ClientFactory):

    def __init__(self, master, buffer={}):
        self.buffer = buffer
        self.master = master
        self.master.telemetryProtocol = self
        #self.master.factory = self

    def startedConnecting(self, connector):
        print "TCP starting..."

    def buildProtocol(self,addr):
        print "TCP connected."
        p = TelemetryClient()
        p.factory = self
        p.previousMessage = None
        return p

    def clientConnectionLost(self, connector, reason):
        print "Lost connection. Reason", reason

    def clientConnectionFaile(self, connector, reason):
        print "Failed Connection. Reason", reason


class TelemetryClient(Protocol):

    #def __init__(self):
    #    self.mode = 'request'
        #mode can either be 'request' or 'dump'

    #def lineReceived(self, line):
    #    print "Telemetry Line", line



    def dataReceived(self, data):
        #KNOWN - a way to get the ENTIRE message? seems sometimes the message ends early
        #stdout.write(data + '\r\n')
        #print "RECEIVED"
        #print len(self.factory.buffer.keys())
        time.sleep(0.001)#trying to see if that keeps the msg in tact
        if self.previousMessage:
            data = self.previousMessage + data
            self.previousMessage = None
        if "\n" in data[-5:]:
            #print "slash-n",data
            lines = data.splitlines()
            for line in lines:
                #print "LINE", line
                key = line[:line.find(' ')]
                datum = line[line.find(' ') + 1:]
                #print "DATUM", datum
                datum = yaml.load(datum)
                #print "DATUM2", datum
                self.factory.buffer[key] = datum

            if self.factory.master.telemetryMode == 'D':
                self.factory.master.sendLine(data)
        else:
            #print "no no"
            self.previousMessage = data


        #print "LEN", len(lines)
        #key,datum = data.split()
        #self.buffer[key] = datum
        #self.transport.loseConnection()
        #FDOprint "BUFFER", self.factory.buffer

        #if self.mode == 'dump':
        #    for key in self.protocol.buffer:
        #        self.transport.write(self.protocol.buffer[key])




if __name__ == '__main__':
    factory = protocol.ServerFactory()
    factory.protocol = MasterServerProtocol

    reactor.listenTCP(37999, factory)

    reactor.run()


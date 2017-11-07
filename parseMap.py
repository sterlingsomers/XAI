from pykml import parser
from os import path
#import re
import itertools
import math
#import numpy

import json

#kml_file = path.join('destination-with-mountains.kml')

#with open(kml_file) as f:
#    doc = parser.parse(f).getroot().Document.Folder
#polygons = []
#coords = []
#for PG in doc.iterchildren():
#    if hasattr(PG, 'Polygon'):
#        print type(PG.Polygon.outerBoundaryIs.LinearRing.coordinates)
#        poly_str = repr(PG.Polygon.outerBoundaryIs.LinearRing.coordinates)
#        poly = ''.join(c for c in poly_str if (c.isdigit() or c == ' ' or c == ',' or c == '.' or c == '-'))
#        coords = poly.split(' ')
#        coords = [x.split(',') for x in coords]
#        coords = [[float(x[0]),float(x[1]),float(x[2])] for x in coords if len(x) > 1]
#        polygons.append(coords)


#print polygons



class KMLHandler():
    def __init__(self, kml_file_path=''):
        self.kml_file = path.join('multiple-paths1.kml')
        #self.kml_file = path.join('path-1.kml')
        #self.kml_file = path.join('destination-with-mountains.kml')
        with open(self.kml_file) as f:
            self.doc = parser.parse(f).getroot().Document.Folder
        self.polygons = []
        self.polydict = {}
        #self.get_polygons()
        #self.get_polygons2() #changed to load_polygons
        self.load_polygons()

    def classify_bearing(self,bearing):
        north = 0
        north_east = 0
        east = 0
        south_east = 0
        south =0
        south_west = 0
        west = 0
        north_west = 0
        bearing = bearing % 360

        if bearing >= 345 and bearing <= 360:
            north = 1
        if bearing >= 0 and bearing < 15:
            north = 1
        if bearing >= 330 and bearing < 345:
            north = (bearing - 330) / 15.0
            north_west = 1 - (abs((330-bearing))/15.0)
        if bearing >= 15 and bearing < 30:
            north = 2 - (bearing / 15.0)
            north_east = (bearing / 15.0) - 1
        if bearing >= 30 and bearing < 60:
            north_east = 1
        if bearing >= 60 and bearing < 75:
            north_east = 1 - (abs((60-bearing))/15.0)
            east = (bearing - 60) / 15.0
        if bearing >= 75 and bearing < 105:
            east = 1
        if bearing >= 105 and bearing < 120:
            east = 1 - (abs((105-bearing))/15.0)
            south_east = (bearing - 105) / 15.0
        if bearing >= 120 and bearing < 150:
            south_east = 1
        if bearing >= 150 and bearing < 165:
            south_east = 1 - (abs((150-bearing))/15.0)
            south = (bearing - 150) / 15.0
        if bearing >= 165 and bearing < 195:
            south = 1
        if bearing >= 195 and bearing < 210:
            south = 1 - (abs((195-bearing))/15.0)
            south_west = (bearing - 195) / 15.0
        if bearing >= 210 and bearing < 240:
            south_west = 1
        if bearing >= 240 and bearing < 255:
            south_west = 1 - (abs((240-bearing))/15.0)
            west = (bearing - 240) / 15.0
        if bearing >= 255 and bearing < 285:
            west = 1
        if bearing >= 285 and bearing < 300:
            west = 1 - (abs((285-bearing))/15.0)
            north_west = (bearing - 285) / 15.0
        if bearing >= 300 and bearing < 330:
            north_west = 1


        r_dict = {}
        if north:
            r_dict["north"] = north
        if north_east:
            r_dict["north_east"] = north_east
        if east:
            r_dict["east"] = east
        if south_east:
            r_dict["south_east"] = south_east
        if south:
            r_dict["south"] = south
        if south_west:
            r_dict["south_west"] = south_west
        if west:
            r_dict["west"] = west
        if north_west:
            r_dict["north_west"] = north_west



        return r_dict


    def get_bearing_and_distance(self,lat1,lon1,lat2,lon2):
        #Adapted from:
        ## https: // stackoverflow.com / questions / 4913349 / haversine - formula - in -python - bearing - and -distance - between - two - gps - points
        #need to check to see if the distance is accurate enough
        Aaltitude = 2000
        Opposite = 20000
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        base = 6371 * c

        bearing = math.atan2(math.sin(lon2 - lon1) * math.cos(lat2),
                             math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1))
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360

        #bearing = math.atan2(math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1), math.sin(lon2 - lon1) * math.cos(lat2))

        #bearing = math.degrees(bearing)
        #bearing = bearing % 360

        rdict = {"bearing":bearing, "distance":base*1000} #The distance might not be right

        #
        return rdict
        #bearing = math.atan2(math.sin(lon2 - lon1) * math.cos(lat2),
        #                     math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1))
        #bearing = math.degrees(bearing)
        #bearing = bearing % 360#(bearing + 360) % 360
        #print ""
        #print ""
        #print "--------------------"
        #print "Horizontal Distance:"
        #print Base
        #print "--------------------"
        #print "Bearing:"
        #print bearing
        #print "--------------------"

    def get_paths_by_names(self, list_of_names):
        paths = {}
        for path in self.polydict:
            if path in list_of_names:
                paths[path] = self.polydict[path]
                #paths[path]["centroid"] = self.get_centroid(paths[path]['points'])
        return paths

    def get_enriched_paths_by_names(self,lat=0,lon=0,list_of_names=0):
        paths = {}
        for path in self.polydict:
            if path in list_of_names:
                paths[path] = self.polydict[path]
                paths[path]["centroid"] = self.get_centroid(paths[path]['points'])
                if lat and lon:
                    #add a centroid
                    centroid = paths[path]['centroid']
                    #add a distance to centroid
                    bearing_and_distance = self.get_bearing_and_distance(lat,lon,centroid[0],centroid[1])
                    paths[path]['distance'] = bearing_and_distance['distance']
                    #add a bearing to the path centroid
                    paths[path].update(self.classify_bearing(bearing_and_distance['bearing']))

        return paths

    def paths_in_radius(self, lat, lon, meters,exclude_list=[]):
        paths = []
        for path in self.polydict:
            if path in exclude_list:
                continue
            for point in self.polydict[path]['points']:
                #print "piont", point
                distance_to_point = self.get_bearing_and_distance(lat,lon,point[1],point[0])['distance']
                #print "distance to point", distance_to_point
                if distance_to_point <= meters:
                    paths.append(path)
                    break
        if not paths:
            return 0
        return paths

    def point_in_path(self, point_lat, point_lon, path):
        x = [p[0] for p in path]
        y = [p[1] for p in path]
    
        max_x = max(x)
        min_x = min(x)
    
        max_y = max(y)
        min_y = min(y)
        #FDOprint max_x, min_x, point_lon, max_y, min_y, point_lat
        if point_lon <= max_x and point_lon >= min_x:
            return point_lat <= max_y and point_lat >= min_y
        #    return 1
        return 0


    def get_closest_path_key(self, lat, lon):
        '''This will always exclude paths that the lat/lon is in'''
        path_to_difference = {}
        for key in self.polydict.keys():
            if 'path' in key:
                #put a continue here if the lat/lon is in
                if self.point_in_path(lat,lon,self.polydict[key]):
                    #FDOprint "continue"
                    continue
                #for point in self.polydict[key]:
                for point in self.polydict[key]['points']:
                    #FDOprint "POINT", type(point), point
                    dif_lat = abs(lat - point[1])
                    dif_lon = abs(lon - point[0])
                    
                    #path_to_difference[key] = dif_lat + dif_lon
                    if key in path_to_difference:
                        if path_to_difference[key] > dif_lat + dif_lon:
                            path_to_difference[key] = dif_lat + dif_lon
                    else:
                        path_to_difference[key] = dif_lat + dif_lon
                    #if key in path_to_difference:
                        #if dif_lat < path_to_difference[key][0]:
                            #path_to_difference[key][0] = dif_lat
                        #if dif_lon < path_to_difference[key][1]:
                            #path_to_difference[key][1] = dif_lon
                    #else:
                        #path_to_difference[key] = [dif_lat,dif_lon]
        min = None
        r_key = ''
        for key in path_to_difference:
            if min == None:
                min = path_to_difference[key]
                r_key = key
            else:
                if path_to_difference[key] < min:
                    min = path_to_difference[key]
                    r_key = key
        return r_key


    

        #For each path, which one has the values with the least difference?
        
    def to_file(self,file_name='map_chunks.txt'):
        pass
    
    
    def load_polygons(self):
        #FDOprint 'placemark test'
        for pm in self.doc.Placemark:
            coords = []
            #FDOprint pm.name
            if hasattr(pm, 'Polygon'):
                poly_str = repr(pm.Polygon.outerBoundaryIs.LinearRing.coordinates)
                poly = ''.join(c for c in poly_str if (c.isdigit() or c == ' ' or c == ',' or c == '.' or c == '-'))
                coords = poly.split(' ')
                coords = [x.split(',') for x in coords]
                coords = [[float(x[0]),float(x[1]),float(x[2])] for x in coords if len(x) > 1]
                #name_str = json.dumps(pm.name)
                #FDOprint type(pm.name.text)
                #name = json.dumps(pm.name.text)
                self.polydict[pm.name.text] = {}
                self.polydict[pm.name.text]["points"] = coords
                #self.polydict[repr(pm.name)]['descriptoin'] = pm.description
            if hasattr(pm, "description"):
                #name = json.dumps(pm.name.text)
                self.polydict[pm.name.text].update(eval(pm.description.text))
            if hasattr(pm, 'Point'):
                pass
                #FDOprint pm.Point.coordinates
        #self.polydict = json.dumps(self.polydict)
            
    #print 'placemark', PG.Placemark.name
                    #for PM in PG.Placemark.iterchildren():
                    #print PM.name


    def get_polygons(self):
        coords = []
        for PG in self.doc.iterchildren():
            if hasattr(PG, 'Polygon'):
                poly_str = repr(PG.Polygon.outerBoundaryIs.LinearRing.coordinates)
                poly = ''.join(c for c in poly_str if (c.isdigit() or c == ' ' or c == ',' or c == '.' or c == '-'))
                coords = poly.split(' ')
                coords = [x.split(',') for x in coords]
                coords = [[float(x[0]),float(x[1]),float(x[2])] for x in coords if len(x) > 1]
                self.polygons.append(coords)

    def doesIntersect2(self, lat1, lon1, lat2, lon2, latA, lonA, latB, lonB):
        #http://pythonshort.blogspot.com/2015/03/intersection-of-two-line-segments-in.html
        seg1 = [lat1, lon1, lat2, lon2]
        seg2 = [latA, lonA, latB, lonB]
        endpoints = []
        left = max(min(seg1[0],seg1[2]),min(seg2[0],seg2[2]))
        right = min(max(seg1[0],seg1[2]),max(seg2[0],seg2[2]))

        bottom = max(min(seg1[1],seg1[3]),min(seg2[1],seg2[3]))
        top = min(max(seg1[1],seg1[3]),max(seg2[1],seg2[3]))

        if top > bottom or left > right:
            endsponts = []
            #FDOprint 'No intersection'

        elif top == bottom and left == right:
            endpoints.append(left)
            endpoints.append(top)
                
        else:
            endpoints.append(left)
            endpoints.append(bottom)
            endpoints.append(right)
            endpoints.append(top)
            #FDOprint 'Segment Intersection'
        return endpoints


    def doesIntersect(self, lat1, lon1, lat2, lon2, latA, lonA, latB, lonB):
        #https://www.cs.hmc.edu/ACM/lectures/intersections.html
        x1, y1 = lat1, lon1
        x2, y2 = lat2, lon2
        dx1 = x2 - x1
        dy1 = y2 - y1
    
        x, y = latA, lonA
        xB, yB = latB, lonB
        dx = xB - x
        dy = yB - y
    
        DET_TOLERANCE = 0.00000001
        DET = (-dx1 * dy + dy1 * dx)
    
        if math.fabs(DET) < DET_TOLERANCE: return (0,0,0,0,0)

    
        # now, the determinant should be OK
        DETinv = 1.0/DET
    
        # find the scalar amount along the "self" segment
        r = DETinv * (-dy  * (x-x1) +  dx * (y-y1))
    
        # find the scalar amount along the input line
        s = DETinv * (-dy1 * (x-x1) + dx1 * (y-y1))
    
        # return the average of the two descriptions
        xi = (x1 + r*dx1 + x + s*dx)/2.0
        yi = (y1 + r*dy1 + y + s*dy)/2.0
        return ( xi, yi, 1, r, s )
    
    def get_centroid(self, path):
        x = [p[0] for p in path]
        y = [p[1] for p in path]
        return (sum(y) / len(path),sum(x)/len(path))
    
    def get_edge_centers(self, path):
        #The centre of the edges may make more sense
        #especially the edge closest to the previous path
        pass
    
    
    def intersection(self, lon1, lat1, lon2, lat2):
        segments = []
        for polygon in self.polygons:
            #fdoprint 'polygon'
            #sliding window, capturing the segments
            b = []
            for x, y in itertools.izip(polygon, polygon[1:]):
                #I messed up lat and lon, but I'm pretty sure the order (lon lat) below fixes it
                #because doesIntersect2 is actually expecting (lat,lon...)
                a = self.doesIntersect2(lon1,lat1,lon2,lat2,x[0],x[1],y[0],y[1])
                if len(a):
                    segments.append([x,y,a])
            #test the polygon-closing line segment (not working right)
            #NOT NEEDED, already taken care of, the polygons are closed properly
            #print 'polygon...!', polygon, polygon[0][0], polygon[0][1],polygon[len(polygon)-1][0],polygon[len(polygon)-1][1]
            #b = self.doesIntersect2(lon1,lat1,lon2,lat2,polygon[0][0],polygon[0][1],polygon[-1][0],polygon[-1][1])
            #if len(b):
            #    print 'len b', len(b)
            #    segments.append([polygon[0],polygon[-1],b])
    
        #FDOprint 'segments', segments
        return segments



if __name__ == '__main__':
    a = KMLHandler()
    #FDOprint a.polydict, type(a.polydict)
    print 'paths', a.paths_in_radius(38.967163,-104.819837,7300)

    #Try the classifier
    print a.classify_bearing(278)


    #a.get_closest_path_key(38.967163,-104.819837)

    #this should be west.
    print a.get_bearing_and_distance(38.967163,-104.819837,38.99343742021595,-105.05530266366)


#path_key = a.get_closest_path_key(38.967163,-104.819837)
#path = a.polydict[path_key]
#print path
#print a.get_centroid(path)
#x = [p[0] for p in path]
#y = [p[1] for p in path]
#centroid = (sum(x) / len(path), sum(y) / len(path))
#print centroid



#print a.get_closest_path(38.967163,-104.819837)
#print a.polydict
#a.intersection(-104.6849353125215,38.78000172872311,-105.055302663666,38.99343742021595)


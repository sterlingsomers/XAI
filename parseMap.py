from pykml import parser
from os import path
#import re
import itertools
import math
#import numpy

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
        self.kml_file = path.join('path-and-mountains2.kml')
        #self.kml_file = path.join('path-1.kml')
        #self.kml_file = path.join('destination-with-mountains.kml')
        with open(self.kml_file) as f:
            self.doc = parser.parse(f).getroot().Document.Folder
        self.polygons = []
        self.polydict = {}
        #self.get_polygons()
        self.get_polygons2()

    def point_in_path(self, point_lat, point_lon, path):
        x = [p[0] for p in path]
        y = [p[1] for p in path]
    
        max_x = max(x)
        min_x = min(x)
    
        max_y = max(y)
        min_y = min(y)
        print max_x, min_x, point_lon, max_y, min_y, point_lat
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
                    print "continue"
                    continue
                for point in self.polydict[key]:
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
    
    
    def get_polygons2(self):
        print 'placemark test'
        for pm in self.doc.Placemark:
            coords = []
            print pm.name
            if hasattr(pm, 'Polygon'):
                poly_str = repr(pm.Polygon.outerBoundaryIs.LinearRing.coordinates)
                poly = ''.join(c for c in poly_str if (c.isdigit() or c == ' ' or c == ',' or c == '.' or c == '-'))
                coords = poly.split(' ')
                coords = [x.split(',') for x in coords]
                coords = [[float(x[0]),float(x[1]),float(x[2])] for x in coords if len(x) > 1]
                self.polydict[repr(pm.name)] = coords
            if hasattr(pm, 'Point'):
                print pm.Point.coordinates
            
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
            print 'No intersection'

        elif top == bottom and left == right:
            endpoints.append(left)
            endpoints.append(top)
                
        else:
            endpoints.append(left)
            endpoints.append(bottom)
            endpoints.append(right)
            endpoints.append(top)
            print 'Segment Intersection'
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
    
        print 'segments', segments
        return segments



#a = KMLHandler()
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


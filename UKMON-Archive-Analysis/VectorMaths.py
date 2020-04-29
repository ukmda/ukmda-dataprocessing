# vector maths for comparing directions of meteors etc
import numpy as np
import math
import astropy.coordinates as coo

def shortestdistance(s1, b1, s2, b2):
    n = np.cross(e1,e2)
    denom=np.linalg.norm(n)
#    print('n is', n)
#    print('mod n is ', denom)
#    print(s1-s2)
    if denom == 0 :
        print ('parallel lines')
        return 999999
    else:
        d = (np.dot(n, s1-s2))/denom
        return d

def shortestdistance2(a,b,c,d):
    # Lines are L=a+bt, M=c+ds   
    e=a-c
    b2 = np.dot(b,b)
    d2 = np.dot(b,b)
    bd = np.dot(b,d)
    de = np.dot(d,e)
    be = np.dot(b,e)
    db = np.dot(d,b)

    A = -b2*d2+bd*bd
    s = (-b2*de + be*db)/A
    t = (+d2*be - de*db)/A
    D = e + b*t-d*s
    d = math.sqrt(np.dot(D,D))

    return s,t,d

if __name__ == '__main__':
    print('Testing examples')
#    s1=np.array([2,6,-9])
#    s2=np.array([-1,-2,3])
#    e1=np.array([3,4,-4])
#    e2=np.array([2,-6,1])
#    s,t,d = shortestdistance2(s1, e1, s2, e2)
#    print (s, t, d)

    lat1=51.8677
    lon1=-1.3168
    hei1=80
    lat2=50.9388
    lon2=-1.0197
    hei2=158
    # x,y,z is geocentric coords - x-axis through meridian, y east, z north
    loc1= coo.EarthLocation(lat=lat1, lon=lon1, height=hei1)
    loc2= coo.EarthLocation(lat=lat2, lon=lon2, height=hei2)
    s1=np.array([loc1.x.value, loc1.y.value, loc1.z.value])
    s2=np.array([loc2.x.value, loc2.y.value, loc2.z.value])

    # dir is from south, alt is from horizontal
    dir1=251.8
    dir2=198.9
    alt1=48.7
    alt2=31.7
    b1=np.array([np.radians(alt1), np.radians(dir1-180)])
    b2=np.array([np.radians(alt2), np.radians(dir2-180)])

    # this vector is tricky! sin(alti) is x, sin(dir) is y, cos(dir) is z
    e1=np.array([math.sin(b1[0]), math.sin(b1[1]), math.cos(b1[1])])
    e2=np.array([math.sin(b2[0]), math.sin(b2[1]), math.cos(b2[1])])

    d1 = shortestdistance(s1, e1/np.linalg.norm(e1), s2, e2/np.linalg.norm(e2))
    s,t,d = shortestdistance2(s1, e1/np.linalg.norm(e2), s2, e2/np.linalg.norm(e2))
    print (s,t,d/1000,d1/1000)
    pos1=s1+s*e1
    pos2=s2+t+e2
    print(pos1[0], pos1[1],pos1[2])
    mloc1 = coo.EarthLocation.from_geocentric(pos1[0], pos1[1], pos1[2],'m')
    mloc2 = coo.EarthLocation.from_geocentric(pos2[0], pos2[1], pos2[2],'m')
    print(mloc1.geodetic)
    print(mloc2.geodetic)

    

# 
# class to read a single or multiple platepar files
#
import json
import os
import glob


class platepar:
    def __init__(self, plateparfile):
        with open(plateparfile, 'r') as pp:
            self.jsd = json.load(pp)
            try: 
                self.id = self.jsd['station_code']
                # field of view details
                self.alt_centre = self.jsd['alt_centre']
                self.az_centre = self.jsd['az_centre']
                self.Ho = self.jsd['Ho']
                self.fov_h = self.jsd['fov_h']
                self.fov_v = self.jsd['fov_v']
                self.rotation_from_horiz = self.jsd['rotation_from_horiz']
                self.RA_d = self.jsd['RA_d']
                self.dec_d = self.jsd['dec_d']
                self.pos_angle_ref = self.jsd['pos_angle_ref']

                # camera location
                self.lat = self.jsd['lat']
                self.lon = self.jsd['lon']
                self.elev = self.jsd['elev']

                # camera resolution
                self.X_res = self.jsd['X_res']
                self.Y_res = self.jsd['Y_res']

                # Reference time and date
                self.time = 0
                self.JD = self.jsd['JD']
                self.UT_corr =self.jsd['UT_corr']

                # FOV scale (px/deg)
                self.F_scale = self.jsd['F_scale']

            except:
                print('invalid json file')

    def getLocation(self):
        return [self.lat, self.lon, self.elev]

    def getView(self):
        return [self.altcentre, self.azcentre, self.fov_h, self.fov_v, self.rot]

    def getResolution(self):
        return [self.xres, self.yres]


def loadPlatepars(fldr):
    platepars ='{'
    pth = os.path.join(fldr, '*.json')
    pps = glob.glob(pth)
    for pp in pps:
        thispl = platepar(pp)
        if thispl is not None:
            if len(platepars) > 1: # and pp != pps[-1]:
                platepars = platepars + ','
            platepars = platepars + '"' + thispl.id +'": '+ json.dumps(thispl.jsd)
    platepars = platepars + '}'
    #print(platepars)
    ppjson = json.loads(platepars)
    return ppjson


if __name__ == '__main__':
    p = loadPlatepars('c:/temp/platepars')
    #print(p)
    for pp in p:
        print(p[pp]['fov_h'])

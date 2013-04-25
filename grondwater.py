"""
Grondwater modellering volgens bakjesmodel met drempel.

Jack Ha 20130424

Invoer:
- meteo files met verdamping en neerslag per dag
- initiele grondwaterstand
- startdatum

Uitvoer:
- grondwaterstand t+1
"""
from optparse import OptionParser
import datetime
import glob
import os
import csv
import ConfigParser
import math


def f(dt):
    """Datetime format"""
    return dt.strftime('%Y%m%d')


def find_csv(dt, input_dir=''):
    find_path = os.path.join(
        input_dir, '%s-*-METEO_TL.CSV' % f(dt))
    try:
        return glob.glob(find_path)[0]
    except:
        print 'File not found: %s' % find_path
        return None


class Calc(object):
    def __init__(self):
        """Read the configfile"""
        self.config = ConfigParser.RawConfigParser()
        self.config.read('grondwater.cfg')
        self.s = float(self.config.get('model', 's'))
        self.c1 = float(self.config.get('model', 'c1'))
        self.c2 = float(self.config.get('model', 'c2'))
        self.mv = float(self.config.get('model', 'mv'))
        self.d1 = float(self.config.get('model', 'd1'))
        self.d2 = float(self.config.get('model', 'd2'))

        self.c_harm = 1. / (1./self.c1 + 1./self.c2)
        self.d_harm = (
            self.d1 / self.c1 + self.d2 / self.c2) * self.c_harm

    def calc_ht(self, prev_ht, downpour, evaporation, 
                prev_d_harm, prev_c_harm):
        """Calculate 1 timestep.
        """
        #print self.c_harm
        #print self.s
        #return prev_ht + 0.01
        r = (downpour - evaporation) / 1000  # in meters

        # Calc td1: when are we gonna cross the border of drempelhoogte
        # 0..1: fraction of timestep. Other: does not cross.
        t_help = (self.d1 - prev_d_harm - r * prev_c_harm) / (
            prev_ht - prev_d_harm - r * prev_c_harm)
        if t_help > 0:
            td1 = -prev_c_harm * self.s * math.log(t_help)    
        else:
            td1 = 0  # Cannot do ln of negative number

        #print td1
        if (td1 < 0) or (td1 > 1):
            if prev_ht < self.d1:
                d_harm = self.d2
                c_harm = self.c2
            else:
                d_harm = self.d_harm
                c_harm = self.c_harm
            td1 = 0
            one_minus_td1 = 1
        else:
            # we cross the border, so calculate from the crossing
            if prev_ht < self.d1:
                d_harm = self.d_harm
                c_harm = self.c_harm
            else:
                d_harm = self.d2
                c_harm = self.c2
            prev_ht = self.d1
            one_minus_td1 = 1 - td1

        ht = (
            (prev_ht - d_harm) * 
            math.exp(-one_minus_td1 / (c_harm * self.s)) +
            r * c_harm * (
                1 - math.exp(-one_minus_td1 / (c_harm * self.s))
                ) +
            d_harm
            )
        ht = min(self.mv, ht)  # upper limit
        return {
            'ht': ht, 'c_harm': c_harm, 
            'd_harm': d_harm, 'downpour': downpour, 
            'evaporation': evaporation, 'r': r}
    

class MeteoFile(object):
    """
    Represent a csv file like:

$ cat meteo/20130424-20000-METEO_TL.CSV
"Datum","Neerslagsom (mm/24u)","Gemiddelde temperatuur (Celsius)","Weersomschrijving","Verdamping volgens Makkink(mm/d)"
20130423,0.7,10.3,"buien",1.7
20130424,0.0,11.4,"licht bewolkt",3.0
20130425,0.0,12.9,"half bewolkt",2.7
20130426,4.0,7.1,"regen",1.1
20130427,0.0,6.4,"zwaar bewolkt",2.3
20130428,0.0,7.4,"licht bewolkt",3.1
20130429,0.2,9.8,"licht bewolkt",3.0
20130430,1.4,9.2,"buien",2.5
20130501,0.0,8.4,"zwaar bewolkt",2.6
    """

    def __init__(self, filename):
        self._contents = {}
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for i, row in enumerate(reader):  
                if i == 0:
                    continue  # first row is header
                self._contents[row[0]] = {
                    'downpour': float(row[1]),
                    'evaporation': float(row[4])}

    def get(self, dt):
        return self._contents.get(f(dt), None)


def write_output(output_filename, ht):
    """
    read existing csv and overwrite existing dates with new data. new rows are
    appended at the end.

    ht is a dict with dates %Y%m%d as key and content
    {'ht': , 'd_harm':, 'c_harm':, 'downpour', 'evaporation', 'r'}
    """
    data = {}
    if os.path.exists(output_filename):
        print 'Updating existing file...'
        with open(output_filename, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for i, row in enumerate(reader):
                if i > 0:
                    data[row[0]] = row[1:]

    for k, v in ht.items():
        data[k] = [
            k, v['ht'], v['d_harm'], v['c_harm'], 
            v['downpour'], v['evaporation'], v['r']]

    data_sorted = data.items()
    data_sorted.sort()

    print 'writing %s...' % output_filename
    with open(output_filename, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow([
                'datetime', 'ht', 'd_harm', 'c_harm', 
                'downpour[mm]', 'evaporation[mm]', 'r[m]'])
        for k, v in data_sorted:
            writer.writerow(v)
    

if __name__ == '__main__':
    print 'Grondwatermodule.'
    parser = OptionParser()
    parser.add_option(
        '-i', '--inputdir', dest='input_dir',
        help='Input dir, default=meteo', default='meteo')
    parser.add_option(
        '-g', '--groundwaterlevel', dest='groundwaterlevel',
        help='Start grondwaterlevel, default=0.0 or value in outputfile', 
        default=0.0)
    parser.add_option(
        '-o', '--outputfile', dest='output_filename',
        help='Output file, default=groundwater.csv',
        default='grondwater.csv')
    parser.add_option(
        '-s', '--startdate', dest='start_date',
        help='Start date yyyymmdd, default=yesterday', 
        default=f(datetime.datetime.now()-datetime.timedelta(days=1)))
    parser.add_option(
        '-e', '--enddate', dest='end_date',
        help='End date yyyymmdd, default=now', 
        default=f(datetime.datetime.now()))
    (options, args) = parser.parse_args()
    # print options, args
    print 'Initial ground waterlevel %f' % options.groundwaterlevel
    print 'Input dir: %s' % options.input_dir
    print 'Output filename: %s' % options.output_filename
    print 'Start date: %s' % options.start_date
    print 'End date: %s' % options.end_date

    start_date = datetime.datetime.strptime(options.start_date, '%Y%m%d')
    end_date = datetime.datetime.strptime(options.end_date, '%Y%m%d')
    calc = Calc()

    current_dt = start_date
    ht = {}  # key is date
    while current_dt < end_date:
        # print 'working on %s...' % current_dt.strftime('%Y%m%d')
        meteo_filename = find_csv(current_dt, input_dir=options.input_dir)
        calc_values = None
        if meteo_filename:
            meteo_file = MeteoFile(meteo_filename)
            calc_values = meteo_file.get(current_dt)
        if calc_values is None:
            print 'skipped %r' % current_dt
            calc_values = {'downpour': 0.0, 'evaporation': 0.0}

        # testing
        #calc_values = {'downpour': 0.005, 'evaporation': 0.0}

        calc_values2 = ht.get(
            f(current_dt-datetime.timedelta(days=1)), 
            {'ht': 0.0, 
             'c_harm': calc.c2,  # calc.c2 if ht <= d1, else d_harm 
             'd_harm': calc.d2})
        current_ht = calc.calc_ht(
            prev_ht=calc_values2['ht'],
            prev_c_harm=calc_values2['c_harm'],
            prev_d_harm=calc_values2['d_harm'],
            **calc_values)
        ht[f(current_dt)] = current_ht
        print '%s %r' % (f(current_dt), current_ht)

        current_dt += datetime.timedelta(days=1)

    write_output(options.output_filename, ht)

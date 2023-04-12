# Copyright (C) 2018-2023 Mark McIntyre

import pandas as pd
from analysis.showerAnalysis import matchesGraphs


def meteorFlux(startdt, enddt, shwr, outdir):
    cols = ['_M_ut', '_stream','_Nos','_ID1','_vg','_vs','_dur','_LD21','_H1','_H2','_ra_o','_dc_o','_a','_mag','_localtime','_amag', 'dtstamp']
    filt = None
    yr = startdt.year
    matchfile = f's3://ukmon-shared/matches/matchedpq/matches-full-{yr}.parquet.snap'
    mtch = pd.read_parquet(matchfile, columns=cols, filters=filt)
    mtch = mtch[mtch._stream == shwr]
    dur = (enddt - startdt).total_seconds()/3600
    ticksep = 24
    if dur < 73: 
        ticksep = 3
    matchesGraphs(mtch, shwr, outdir, binmins=60, startdt=startdt, enddt=enddt, ticksep=ticksep)

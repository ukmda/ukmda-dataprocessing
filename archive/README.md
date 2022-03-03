UKMON Archive and UKMON Live data flows
=======================================
This diagram shows the overall flow of data from Cameras to websites and out to the public.

```mermaid
    flowchart TD
    A[camera 1] -- realtime --> C[UKMON Live];
    B[camera 2] -- realtime --> C;
    P[camera 3] -- realtime --> C;
    A -- next day --> D[cloud storage];
    B -- next day --> D;
    P -- next day --> D;
    D --> E[matching engine];
    E --> F[reports generator];
    F --> G[opt-in email of matches];
    F --> I[bad-data alerts];
    F --> H[UKMON Archive];
    H -- on demand --> J[other networks];
    H --> M[public];
    C --> M[public];
    C --> N{bright event?};
    N -->|yes| K[social media];
    H -- manual --> K;
    I --> O[camera owners];
    G --> O;
```

Daily Batch Process
===================
This diagram shows the various scripts and processes called, in order

```mermaid
    flowchart TD
    nj[nightlyJob.sh] --> fam[run findAllMatches.sh]
    fam --> don[matches identified]
    don --> rep[send email of Latest Matches]
    rep --> cons2[Consolidate matched data]
    cons2 --> extrs[Create Monthly and Shower extracts]
    extrs --> srch[Create search index and station lists]
    srch --> fbp[Create Fireball Page]
    fbp --> rep2[Create annual and monthly reports of all showers]
    rep2 --> dens[Create Density Plots]
    dens --> rep3[Create reports of current Showers]
    rep3 --> summ[Create summary date for homepage]
    summ --> camst[Create Camera status reports]
    camst --> exch[Create files for exchange with other networks]
    exch --> stats[Create Station Reports]
    stats --> mets[Create Metrics]
    mets --> badc[Send out bad camera emails]
    badc --> d[FINISHED]
```

Find All Matches
================
Flow in findAllMatches.sh

```mermaid
    flowchart TD

    setd[Set the Dates] --> ufo2rms[Convert any UFO data to RMS]
    ufo2rms --> rmssngl[Create RMS single station data files]
    rmssngl --> bkp1[Backup the current trajectory database]
    bkp1 --> rmat[Invoke runMatching]
    rmat --> start[runMatching Start calc engine]
    start --> creat[runMatching Create batch script and copy to server]
    creat --> sync1[runMatching script syncs new ftpdetect files]
    sync1 --> run[runMatching  Then runs the solver]
    run --> sync2[runMatching Then syncs back to S3]
    sync2 --> done[runMatching Stop calc engine]
    done --> repo[Create file of latest matches]
    repo --> stats[Create Stats and sync back to S3]
    stats --> idxpg[Update website index pages]
    idxpg --> gzi[Backup and gzip old trajectory databases]
    gzi --> d[FINISHED]
```
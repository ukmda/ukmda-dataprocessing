Data Processing and Flows
==========================
This diagram shows the overall flow of data from Cameras to websites and out to the public.

```mermaid
    flowchart TD
    A[camera 1] -- realtime --> C[livestream];
    B[camera 2] -- realtime --> C;
    P[camera 3] -- realtime --> C;
    A -- next day --> D[cloud storage];
    B -- next day --> D;
    P -- next day --> D;
    D --> E[matching engine];
    E --> F[reports generator];
    F --> G[opt-in email of matches];
    F --> I[bad-data alerts];
    F --> H[Archive];
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

    setd[Set the Dates] --> rmssngl[Create RMS single station data files]
    rmssngl --> bkp1[Backup the current trajectory database]
    bkp1 --> rmat[Invoke runDistrib]
    rmat --> start[runDistrib Start calc engine]
    start --> creat[runDistrib Create batch script and copy to server]
    creat --> sync1[runDistrib script syncs new ftpdetect files]
    sync1 --> run[runDistrib  Then runs the the Phase 1 solver]
    run --> sync2[runDistrib Then syncs back to S3]
    sync2 --> done[runDistrib Stop calc engine]
    done --> stage2[run the distributed solver phase 2 using ECS and Fargate]
    stage2 --> consol[wait for containers to finish then consolidate the data]
    consol --> repo[Create file of latest matches]
    repo --> stats[Create Stats and sync back to S3]
    stats --> idxpg[Update website index pages]
    idxpg --> gzi[Backup and gzip old trajectory databases]
    gzi --> d[FINISHED]
```

Flow in terms of files
======================
```mermaid
    flowchart LR

    nightly[cronjobs/nightlyJob.sh] --> datasync[utils/dataSync.sh]
    nightly --> findmatches[analysis/findAllMatches.sh]
    findmatches --> rmssngl[analysis/getRMSSingleData.sh]
    findmatches --> srchabl[analysis/createSearchable.sh]
    findmatches --> rundist[analysis/runDistrib.sh]
    rundist --> trajcont[launches docker containers which solve and post directly to the website]
    findmatches --> daily[creates daily report and stats]
    findmatches --> indexes[website/updateIndexPages.sh]
    indexes --> orbidx[website/createOrbitIndex.sh]
    nightly --> consol[analysis/consolidateOutput.sh]
    nightly --> srch2[analysis/createSearchable.sh]
    nightly --> statlist[website/createStationList.sh]
    nightly --> pubrep[website/publishDailyReport.sh]
    nightly --> mthly[website/createMthlyExtracts.sh]
    nightly --> shwr[website/createShwrExtracts.sh]
    nightly --> fireb[website/createFireballPage.sh]
    nightly --> swrepm[analysis/showerReport.sh month]
    swrepm --> repidx[website/createReportIndex.sh]
    nightly --> swrepy[analysis/showerReport.sh year]
    swrepy --> repidx[website/createReportIndex.sh]
    nightly --> activ[analysis/reportActiveShowers.sh]
    activ --> repidx[website/createReportIndex.sh]
    nightly --> summary[website/createSummaryTable.sh]
    nightly --> cammets[create cam metrics]
    nightly --> camstat[website/cameraStatusReport.sh]
    nightly --> statstat[analysis/getBadStations.sh]
    nightly --> costs[website/costReport.sh]
    nightly --> statreps[analysis/stationReports.sh]
    nightly --> databack[utils/dataSyncBack.sh ]
    nightly --> clearsp[utils/clearSpace.sh ]
    nightly --> getlogs[analysis/getLogData.sh]
    nightly --> done[done]


```

Copyright
---------
All code Copyright (C) 2018-2023 Mark McIntyre
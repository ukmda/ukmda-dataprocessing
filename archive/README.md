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
    F --> G[match report on groups.io];
    F --> I[bad-data alerts];
    F --> H[Archive];
    H --> M[website];
    C --> M[website];
    C --> N{bright event?};
    N --> K[social media];
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
    cons2 --> srch[Create Monthly and Shower extracts]
    srch --> fbp[Create Fireball Page]
    fbp --> rep2[Create annual and monthly reports of all showers]
    rep2 --> dens[Create Density Plots]
    dens --> rep3[Create reports of current Showers]
    rep3 --> summ[Create summary date for homepage]
    summ --> camst[Create Camera status reports]
    camst --> exch[Create files for exchange with other networks]
    exch --> badc[Send out bad camera emails]
    badc --> cost[Create Cost Report]
    cost --> stats[Create Station Reports]
    stats --> clsp[Clear space]
    clsp --> mdb[update mariadb tables]
    mdb --> d[FINISHED]
```

Find All Matches
================
Flow in findAllMatches.sh

```mermaid
    flowchart TD

    setd[findAllMatches sets up the date range] --> bkp1[findAllMatches saves the current trajectory database]
    bkp1 --> rmat[findAllMatches then invokes runDistrib]
    rmat --> start[runDistrib Starts the calc engine server]
    start --> creat[runDistrib Creates batch script and copies to calc engine]
    creat --> sync1[runDistrib syncs new ftpdetect files to the calc engine]
    sync1 --> run[runDistrib runs the the Phase 1 solver. This identifies candidate groups]
    run --> sync2[runDistrib syncs data back to the data store]
    sync2 --> done[runDistrib stops calc engine for now, to save cost]
    done --> stage2[runDistrib starts the distributed solver phase 2 using ECS and Fargate]
    stage2 --> consol[runDistrib waits for containers to finish then consolidate the data]
    consol --> repo[runDistrib creates file of latest matches]
    repo --> stats[runDistrib syncs the solved orbit files back to S3 and backs up the data]
    stats --> idxpg[findAllMatches creates some stats, updates website index pages and sends the daily report]
    idxpg --> d[FINISHED]
```

Flow in terms of files
======================
```mermaid
    flowchart LR

    nightly[cronjobs/nightlyJob.sh] --> findmatches[analysis/findAllMatches.sh]
    findmatches --> rundist[analysis/runDistrib.sh]
    rundist --> trajcont[launches docker containers which solve and post directly to the website]
    findmatches --> daily[creates daily report and stats]
    findmatches --> indexes[website/updateIndexPages.sh]
    indexes --> orbidx[website/createOrbitIndex.sh]
    nightly --> consol[analysis/consolidateOutput.sh]
    nightly --> srch2[analysis/createSearchable.sh]
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
    nightly --> clearsp[utils/clearSpace.sh ]
    nightly --> mariadb[utils/loadMatchCsvDB.sh ]
    nightly --> getlogs[analysis/getLogData.sh]
    nightly --> done[done]


```

Copyright
---------
All code Copyright (C) 2018-2023 Mark McIntyre
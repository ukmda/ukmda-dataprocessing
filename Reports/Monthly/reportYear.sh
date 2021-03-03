#!/bin/bash

# monthlyReports collects the data for the given year
# so the other reports can be run
./monthlyReports.sh ALL $1 $2
./createReport.sh QUA $1 $2
./createReport.sh LYR $1 $2
./createReport.sh ETA $1 $2
./createReport.sh SDA $1 $2
./createReport.sh CAP $1 $2
./createReport.sh PER $1 $2
./createReport.sh AUR $1 $2
./createReport.sh SPE $1 $2
./createReport.sh OCT $1 $2
./createReport.sh DRA $1 $2
./createReport.sh EGE $1 $2
./createReport.sh ORI $1 $2
./createReport.sh STA $1 $2
./createReport.sh NTA $1 $2
./createReport.sh LEO $1 $2
./createReport.sh MON $1 $2
./createReport.sh GEM $1 $2
./createReport.sh URS $1 $2

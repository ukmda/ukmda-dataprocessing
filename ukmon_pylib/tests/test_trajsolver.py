# tests for the trajectory solver

import subprocess
import os
import shutil


def test_trajsolverNoLimit():
    targdir = '.\\MaxCams'
    outdir = os.path.join(targdir, 'nolimit')
    shutil.rmtree(outdir)
    os.makedirs(outdir, exist_ok=True)
    subprocess.run(['python', '-m','wmpl.Trajectory.CorrelateRMS', targdir, '-l'])
    subprocess.run(['python', '-m','wmpl.Trajectory.AggregateAndPlot', targdir, '-p', '-s', '30'])
    subprocess.run(['cmd', '/c','move', f'{targdir}\\*.png', outdir])
    subprocess.run(['cmd', '/c','move', f'{targdir}\\trajectories', outdir])
    subprocess.run(['cmd', '/c','move', f'{targdir}\\processed_trajectories.json', outdir])
    subprocess.run(['cmd', '/c','move', f'{targdir}\\trajectory_summary.txt', outdir])
    assert(1!=1)


def test_trajsolverLimit():
    targdir = './MaxCams'
    outdir = os.path.join(targdir, 'limit6')
    shutil.rmtree(outdir)
    os.makedirs(outdir, exist_ok=True)
    subprocess.run(['python', '-m','wmpl.Trajectory.CorrelateRMS', targdir, '-l', '-x', '6'])
    subprocess.run(['python', '-m','wmpl.Trajectory.AggregateAndPlot', targdir, '-p', '-s', '30'])
    subprocess.run(['cmd', '/c','move', f'{targdir}\\*.png', outdir])
    subprocess.run(['cmd', '/c','move', f'{targdir}\\trajectories', outdir])
    subprocess.run(['cmd', '/c','move', f'{targdir}\\processed_trajectories.json', outdir])
    subprocess.run(['cmd', '/c','move', f'{targdir}\\trajectory_summary.txt', outdir])
    assert(1!=1)

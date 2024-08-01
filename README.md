# Animal Tracker

## About

Desktop application for automated tracking and trajectory analysis of rodents in behavioral research.

## Prerequisites

`opencv-python>=4.5.5.64
PyForms-GUI>=5
tqdm>=4.66.2`

## Features

### Preprocessing

Adjust frame preprocessing parameters. Currently, Preprocessing module supports following features:

- **Define tracking interval.** Specify starting and last frames to include in tracking. Interactive player helps you find a specific frame and its number;
- **Resize.** Select a down scaling factor from 1% to 100%;
- **Preview.** Look at the picture of a frame with all preprocessing rules applied for validation.

### Tracking

Tracking module parameters. Supports following features:

- **Background reference computation.** Create and preview a background reference image for specified video file;
- **Adjustable threshold.** Specify threshold value for the segmentation filter.

### Validation

User validation module. Check generated trajectory, make changes and save it to a file. Supports following features:

- **Interactive track editing.** Choose multiple points and change their position by click;
- **Save to file.** Save both starting and result versions of a track to csv.

### ROI

Specify Regions Of Interest. Supports following features:

- **Draw custom region.** Add points by clicking to form a polygon on top of a frame;
- **Include in analysis.** Run separate analysis for specific regions of interest.

### Analysis

Analyse rodent trajectory. Supports following features:

- Movement characteristics. Calculate average speed, total time and path;
- Spatial characteristics. Count number of times subject entered a certain ROI, total time spent in ROI.

## How ot run

1. Install prerequisites:

`pip install -r requirements.txt`

2. Start application:

`python run_app.py`

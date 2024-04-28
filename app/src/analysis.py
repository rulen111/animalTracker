import numpy as np
import cv2
import pandas as pd


def roi_locate(track_report: pd.DataFrame, roi: dict):
    roi_locations = {name: [] for name in roi.keys()}
    for idx, row in track_report.iterrows():
        for name, coords in roi.items():
            poly = np.array(coords)
            x = int(row["X"])
            y = int(row["Y"])
            flag = cv2.pointPolygonTest(poly, (x, y), False)
            roi_locations[name].append(flag >= 0)

    roi_locations = pd.DataFrame.from_dict(roi_locations)
    # track_roi_report = pd.concat([track_report, roi_locations], axis=1)

    return roi_locations


def get_roi_series(roi_locations: pd.DataFrame, null_name="non_roi"):
    roi_loc = roi_locations.copy()
    roi_names = roi_loc.columns.values
    roi_series = pd.Series([null_name] * len(roi_loc), name="roi_location")
    # roi_loc['roi_location'] = null_name
    for region in roi_names:
        # roi_loc['roi_location'][roi_loc[region]] = roi_loc['roi_location'][roi_loc[region]].apply(
        #     lambda x: '_'.join([x, region]) if x != null_name else region
        # )
        mask = roi_loc[region].values
        roi_series.loc[mask] = roi_series.loc[mask].apply(
            lambda x: '_'.join([x, region]) if x != null_name else region
        )
        # series = roi_loc['roi_location'][roi_loc[region]]
        # roi_loc.loc[roi_loc[region], region] = series.apply(
        #     lambda x: '_'.join([x, region]) if x != null_name else region
        # )

    # return roi_loc.loc[:, 'roi_location']
    return roi_series


def roi_transitions(roi_series: pd.Series, include_first=False):
    regions_offset = np.append(roi_series[0], roi_series[0:-1])
    transitions = roi_series != regions_offset
    transitions = transitions.rename("transition")
    if include_first:
        transitions[0] = True

    return transitions


# def roi_transitions_labels(roi_trans: pd.DataFrame):
#     transitions_labels = pd.Series(["in_roi"] * len(roi_loc), name="transitions_labels")
#     trans_idx = roi_trans.index[roi_trans["transition"]].tolist()
#
#     return None


def preprocess_track(track_report: pd.DataFrame, roi: dict, null_name="non_roi", include_first=False):
    roi_locations = roi_locate(track_report, roi)
    roi_series = get_roi_series(roi_locations, null_name)
    transitions = roi_transitions(roi_series, include_first)
    report = pd.concat([track_report, roi_locations, roi_series, transitions], axis=1)

    return report


def generate_summary(reports: dict, roi_names=None):
    summary = {
        "label": [],
        "total_path_px": [],
        "total_time_sec": [],
        "avg_speed_pxsec": []
    }
    if roi_names:
        for roi in roi_names:
            summary[f"{roi} - time_spent_sec"] = []
            summary[f"{roi} - times_entered"] = []

    for label, report in reports.items():
        summary["label"].append(label)
        total_path_px = report["Distance_px"].sum()
        total_time_msec = report["Timestamp_msec"].values[-1] - report["Timestamp_msec"].values[0]
        total_time_sec = total_time_msec / 1000.0
        avg_speed_pxsec = total_path_px / total_time_sec

        summary["total_path_px"].append(total_path_px)
        summary["total_time_sec"].append(total_time_sec)
        summary["avg_speed_pxsec"].append(avg_speed_pxsec)

        # summary[label] = {
        #     "total_path_px": total_path_px,
        #     "total_time_sec": total_time_sec,
        #     "avg_speed_pxsec": avg_speed_pxsec
        # }

        if roi_names:
            # roi_stats = {}
            for roi in roi_names:
                frame_msec = total_time_msec / len(report)
                roi_count = report[roi].sum()
                time_spent_msec = roi_count * frame_msec
                time_spent_sec = time_spent_msec / 1000.0
                times_entered = len(report[(report["roi_location"] == roi) & (report["transition"])])

                # roi_stats[roi] = {
                #     "time_spent_sec": time_spent_sec,
                #     "times_entered": times_entered
                # }

                summary[f"{roi} - time_spent_sec"].append(time_spent_sec)
                summary[f"{roi} - times_entered"].append(times_entered)
            # summary[label]["roi_stats"] = roi_stats
    df_summary = pd.DataFrame.from_dict(summary)

    return df_summary

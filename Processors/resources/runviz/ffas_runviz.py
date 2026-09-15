#!/usr/bin/env python3
"""
ffas_runviz.py - Render an FFAStrans job run as an interactive, self-contained HTML page.

Usage:
    python ffas_runviz.py <job_folder> [<job_folder> ...] [-o OUT] [--open] [--wf-dir DIR]
    python ffas_runviz.py <jobs_root_folder> -o <out_dir>          # every job + index.html

A job folder is <FFAStrans>/Processors/db/cache/jobs/<job_id>/ and normally contains:
    .json               job record (status, start/end time, source file, ...)
    full_log.json       list of log events, one per node action
    finished/*.json     one record per finished split (branch) with its node path
    workflows/*.json    the workflow definition(s) used by the job (node positions)

The page recreates the workflow editor canvas (node boxes at their editor positions),
overlays the run (which nodes ran, how long, which failed), and lets you click any
node to read the log entries that belong to it.

Only the Python standard library is used. Python 3.8+.
"""

import argparse
import glob
import json
import os
import re
import sys
import webbrowser
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

__version__ = "1.1.0"

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(HERE, "runviz_template.html")

# --------------------------------------------------------------------------------------
# FFAStrans facts (from FFAStrans.au3 / Processors/_gui_funcs.au3 / _defaults.au3 / pr.or.core)
# --------------------------------------------------------------------------------------

# Node families and their colour bar, exactly as $a_PROC_FAMILY in _gui_funcs.au3
FAMILY_COLORS = {
    "Monitors":   "#40f840",
    "Decoders":   "#ff4040",
    "Analyzers":  "#ffc0c0",
    "Filters":    "#c080ff",
    "Encoders":   "#ffcf30",
    "Deliveries": "#2080ff",
    "Others":     "#40f3f3",
    "Operations": "#c08040",
    "Workflows":  "#9a9a9a",   # sub_wf has no family colour in the GUI; neutral here
    "Unknown":    "#808080",
}

# type -> (display name, family), from Processors/_defaults.au3 ($a_PROCESSORS)
TYPE_INFO = {
    "sub_wf": ("Workflow", "Workflows"),
    "mon_xf": ("Canon-XF", "Monitors"),
    "dec_avmedia": ("A/V Media", "Decoders"),
    "anal_loudness": ("Loudness", "Analyzers"),
    "avs_a_acmapper": ("ChannelMapper", "Filters"),
    "enc_av_avcintra": ("AVC-Intra", "Encoders"),
    "dest_folder": ("Folder", "Deliveries"),
    "cmd_run": ("Command executor", "Others"),
    "op_cond": ("Conditional", "Operations"),
    "mon_ftp": ("FTP", "Monitors"),
    "mon_p2": ("Panasonic P2", "Monitors"),
    "mon_folder": ("Folder", "Monitors"),
    "avs_v_watermark": ("Watermark", "Filters"),
    "avs_v_videolayer": ("Videolayer", "Filters"),
    "avs_custom": ("Custom AviSynth script", "Filters"),
    "dest_ftp": ("FTP", "Deliveries"),
    "anal_videoq": ("Video quality", "Analyzers"),
    "avs_a_normalize": ("Normalize", "Filters"),
    "avs_v_resize": ("Resize", "Filters"),
    "dec_stills": ("Stills", "Decoders"),
    "enc_stills": ("Stills", "Encoders"),
    "enc_av_uncomp": ("Uncompressed", "Encoders"),
    "enc_av_dv": ("DV/DVCPRO", "Encoders"),
    "avs_v_tc": ("Timecode", "Filters"),
    "avs_av_insertmedia": ("Insert media", "Filters"),
    "avs_av_fade": ("Fade", "Filters"),
    "enc_av_wm": ("Windows Media", "Encoders"),
    "avs_v_pad": ("Pad", "Filters"),
    "avs_v_crop": ("Crop", "Filters"),
    "enc_av_imxd10": ("IMX D-10", "Encoders"),
    "enc_av_xdcamhd": ("XDCAM-HD", "Encoders"),
    "enc_av_dnxhd": ("Avid DNxHD", "Encoders"),
    "enc_av_mp4": ("H.264", "Encoders"),
    "enc_av_customff": ("Custom FFmpeg", "Encoders"),
    "avs_v_deinterlace": ("Deinterlace", "Filters"),
    "avs_v_swapfields": ("Swap Fields", "Filters"),
    "avs_v_reverse": ("Reverse", "Filters"),
    "enc_av_dvd": ("DVD", "Encoders"),
    "dec_youtube": ("YouTube", "Decoders"),
    "avs_v_color": ("Color conversion", "Filters"),
    "avs_v_fpsconv": ("FPS Converter", "Filters"),
    "avs_v_flip": ("Flip", "Filters"),
    "other_textfile": ("Generate text file", "Others"),
    "other_httpsend": ("HTTP communicate", "Others"),
    "other_email": ("Send e-mail", "Others"),
    "op_hold": ("Hold", "Operations"),
    "enc_av_prores": ("Prores AW/KS", "Encoders"),
    "avs_ppxmpcc": ("Premiere CC-comments", "Filters"),
    "enc_av_dnxhr": ("Avid DNxHR", "Encoders"),
    "mon_gopro": ("GoPro", "Monitors"),
    "avs_mos": ("MOS Captions", "Filters"),
    "enc_av_av1": ("AV1", "Encoders"),
    "enc_a_audio": ("Audio extraction", "Encoders"),
    "mon_sequence": ("Image Sequence", "Monitors"),
    "enc_av_265": ("H.265/HEVC", "Encoders"),
    "anal_interlacing": ("Interlacing", "Analyzers"),
    "enc_av_xavc": ("XAVC", "Encoders"),
    "enc_av_mpeg": ("Generic MPEG", "Encoders"),
    "avs_v_safecolorlimiter": ("Safe Color Limiter", "Filters"),
    "avs_v_linear_trans": ("Linear Transformation", "Filters"),
    "op_foreach": ("For each", "Operations"),
    "op_populate": ("Populate variables", "Operations"),
}

PREFIX_FAMILY = [
    ("mon_", "Monitors"), ("dec_", "Decoders"), ("anal_", "Analyzers"), ("avs_", "Filters"),
    ("enc_", "Encoders"), ("dest_", "Deliveries"), ("other_", "Others"), ("cmd_", "Others"),
    ("op_", "Operations"), ("sub_", "Workflows"),
]

DEFAULT_WF_SIZE = 115.0     # $i_BOX_WIDTH default
BOX_ASPECT = 1.6            # $f_BOX_ASPECT

# Error-typed log events that describe an expected outcome rather than a failure.
# They are written with _setlog_error_only() and never set the job error.
# (node type, event) -> explanation shown in the log panel.
BENIGN_ERRORS = {
    ("op_cond", "conditional"): "the conditional had nothing to evaluate and passed the job on (not a failure)",
}
# Error-typed events that mean "the condition evaluated false, the branch ends here" (op_cond/proc.au3).
COND_FALSE_EVENTS = {("op_cond", "conditioner")}
# Events written with _setlog_error_only() while probing media (_proc_helpers.au3): logged, the job carries on.
SOFT_ERROR_EVENTS = {"ffprobe", "mediainfo", "exiftool"}
# Events a node writes when it is (almost) done, so the time before them belongs to that node,
# not to the node before it (op_cond/proc.au3, op_populate/proc.au3).
END_ANCHORED_EVENTS = {"conditional", "conditioner", "pre_evaluation", "populate_variable"}
# FFAStrans 1.4.x logs explicit run boundaries; 1.5 does not (there the times are derived).
NODE_START_EVENT = "node start"
NODE_END_EVENT = "node end"
# $EXIT.abort is 995 in 1.5 (sys.core/_exit_codes.au3); 1.4.x writes code 2 with result 'abort'.
ABORT_CODES = {"995", "2"}
# What a node is doing while it writes nothing, judged by the last entry before the silence.
# kind: "wait" = idle by design or queueing, "work" = an external process is busy.
GAP_KINDS = {
    "_WaitForResources": ("wait", "waiting for resources (CPU roof, storage or work dir)"),
    "hold": ("wait", "hold node sleeping"),
    "sending_http_request": ("work", "waiting for the HTTP response"),
    "priority_set": ("work", "external process running"),
    "run_child": ("work", "external process running"),
    "open_process": ("work", "external process running"),
    "starting_std_stream": ("work", "external process running"),
    "_IPS_SRV_FFMon": ("work", "encoding"),
    "_Simple_MediaOutput": ("work", "encoding"),
    "_detect_interlacing": ("work", "analysing"),
    "dest_folder": ("work", "delivering the file"),
    "node start": ("work", "node starting up"),
    "node start:config 0": ("work", "loading the node configuration"),
}
GAP_MIN_MS = 1000          # silences shorter than this are not worth listing
STALL_NOTE_MS = 5000       # a queue / dispatch wait this long is flagged as an anomaly
# The numeric 'status' a finished record ends with (pr.or.core/_log_helpers.au3 _dump_to_history_log).
STATUS_FLAG = {"0": "finished with error", "1": "finished", "2": "aborted"}


def family_of(node_type):
    info = TYPE_INFO.get(node_type)
    if info:
        return info[1]
    for prefix, fam in PREFIX_FAMILY:
        if node_type.startswith(prefix):
            return fam
    return "Unknown"


def type_name_of(node_type):
    info = TYPE_INFO.get(node_type)
    return info[0] if info else node_type


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------

class Warnings:
    def __init__(self):
        self.items = []

    def add(self, msg):
        self.items.append(msg)
        print("warning: " + msg, file=sys.stderr)


def load_json(path, warnings, what):
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None
    except Exception as exc:  # malformed / truncated file
        warnings.add("%s: cannot parse %s (%s)" % (what, path, exc))
        return None


_TS_FIX = re.compile(r"([+-]\d\d)[.:]?(\d\d)$")
_TS_HAS_TZ = re.compile(r"(Z|[+-]\d\d[.:]?\d\d)$")


def parse_ts(value, default_tz=None):
    """ISO 8601 timestamp -> aware datetime, or None. Tolerates 'Z', '+02.00' and no offset
    (a naive stamp gets default_tz, or UTC when none is known)."""
    if not value or not isinstance(value, str):
        return None
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    s = _TS_FIX.sub(r"\1:\2", s)
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        try:
            dt = datetime.strptime(s[:23], "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            try:
                dt = datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=default_tz or timezone.utc)
    return dt


def tz_of(value):
    """The tzinfo carried by an ISO stamp, or None."""
    dt = parse_ts(value) if isinstance(value, str) and _TS_HAS_TZ.search(value.strip()) else None
    return dt.tzinfo if dt else None


def to_ms(dt):
    return None if dt is None else dt.timestamp() * 1000.0


def iso(dt):
    return None if dt is None else dt.isoformat(timespec="milliseconds")


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def norm_id(value):
    return str(value or "").strip().lower()


def rec_wf_id(rec):
    """Workflow id of a job or split record. 1.5 writes wf_id, 1.4.x a workflow{id,name,path} map."""
    if not isinstance(rec, dict):
        return ""
    wf = rec.get("workflow") if isinstance(rec.get("workflow"), dict) else {}
    return norm_id(rec.get("wf_id") or wf.get("id"))


def rec_wf_name(rec):
    if not isinstance(rec, dict):
        return None
    wf = rec.get("workflow") if isinstance(rec.get("workflow"), dict) else {}
    return rec.get("wf_name") or wf.get("name")


def _plural(n, word):
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


def _fmt_ms(ms):
    if ms is None:
        return "?"
    if ms < 1000:
        return "%d ms" % round(ms)
    s = ms / 1000.0
    if s < 60:
        return ("%.1f s" % s) if s >= 10 else ("%.2f s" % s)
    m = int(s // 60)
    return "%dm %ds" % (m, round(s - m * 60))


def first_line(text, limit=200):
    text = (text or "").replace("\r\n", "\n").strip()
    line = text.split("\n", 1)[0]
    more = len(text) - len(line)
    if len(line) > limit:
        more += len(line) - limit
        line = line[:limit]
    return line + (" \u2026 (%d more chars)" % more if more > 0 else "")


# --------------------------------------------------------------------------------------
# Loading a job folder
# --------------------------------------------------------------------------------------

def resolve_job_dir(arg):
    p = os.path.abspath(arg)
    if os.path.isfile(p):
        return os.path.dirname(p)
    return p


def load_plugin_categories(job_dir, warnings):
    """Custom (plugin) nodes only carry a guid in the workflow; their name and category live in
    <install>/processors/plugin_nodes/custom_nodes/<node>/node.json. A job folder sits at
    <install>/processors/db/cache/jobs/<id>, so walk up and read them when they are there."""
    out = {}
    probe = os.path.abspath(job_dir)
    for _ in range(5):
        probe = os.path.dirname(probe)
        base = os.path.join(probe, "plugin_nodes", "custom_nodes")
        if os.path.isdir(base):
            for f in glob.glob(os.path.join(base, "*", "node.json")):
                raw = load_json(f, warnings, "plugin node.json")
                if isinstance(raw, dict) and raw.get("guid"):
                    out[norm_id(raw["guid"])] = {"name": str(raw.get("name") or ""), "category": str(raw.get("category") or "")}
            break
    return out


def load_workflows(job_dir, extra_dirs, warnings):
    """Return OrderedDict wf_id -> normalized workflow."""
    files = sorted(glob.glob(os.path.join(job_dir, "workflows", "*.json")))
    for d in extra_dirs:
        files += sorted(glob.glob(os.path.join(d, "*.json")))
    plugins = load_plugin_categories(job_dir, warnings)
    wfs = OrderedDict()
    for f in files:
        raw = load_json(f, warnings, "workflow")
        if not isinstance(raw, dict) or not isinstance(raw.get("nodes"), list):
            if raw is not None:
                warnings.add("workflow %s has no 'nodes' list, skipped" % f)
            continue
        wf_id = norm_id(raw.get("wf_id")) or os.path.splitext(os.path.basename(f))[0].lower()
        if wf_id in wfs:
            continue
        try:
            size = float((raw.get("variable") or {}).get("wf_size") or DEFAULT_WF_SIZE)
        except (TypeError, ValueError):
            size = DEFAULT_WF_SIZE
        if size <= 0:
            size = DEFAULT_WF_SIZE
        nodes = []
        for i, n in enumerate(raw["nodes"]):
            if not isinstance(n, dict):
                continue
            ntype = str(n.get("type") or "unknown")
            try:
                px = float(n.get("pos_x") or 0)
                py = float(n.get("pos_y") or 0)
            except (TypeError, ValueError):
                px, py = 0.0, 0.0
            outbounds = []
            for ob in n.get("outbounds") or []:
                if isinstance(ob, dict) and ob.get("id"):
                    outbounds.append({"id": norm_id(ob.get("id")), "type": ob.get("type"), "connection": ob.get("connection")})
                elif isinstance(ob, str):
                    outbounds.append({"id": norm_id(ob), "type": None, "connection": None})
            plugin = plugins.get(norm_id(n.get("custom_proc_guid"))) if n.get("custom_proc_guid") else None
            family = family_of(ntype)
            type_name = type_name_of(ntype)
            if plugin:
                if plugin["category"] in FAMILY_COLORS:
                    family = plugin["category"]
                if plugin["name"]:
                    type_name = plugin["name"] + " (plugin)"
            elif family == "Unknown" and (ntype.startswith("plugin") or n.get("custom_proc_guid")):
                type_name = "Plugin node"
            nodes.append({
                "index": i,
                "id": norm_id(n.get("id")) or ("node-%d" % i),
                "type": ntype,
                "type_name": type_name,
                "family": family,
                "plugin_guid": norm_id(n.get("custom_proc_guid")) or None,
                "name": str(n.get("name") or type_name_of(ntype)),
                "description": str(n.get("description") or ""),
                "pos_x": px,
                "pos_y": py,
                "bypass": bool(n.get("bypass", False)),
                "start_proc": bool(n.get("start_proc", False)),
                "execute_on": str(n.get("execute_on") or "success"),
                "initiation": n.get("initiation"),
                "slots": n.get("slots"),
                "hosts_group": n.get("hosts_group"),
                "custom_proc_guid": n.get("custom_proc_guid") or "",
                "outbounds": outbounds,
                "inbounds": [],
                "properties": n.get("properties"),
            })
        by_id = {n["id"]: n for n in nodes}
        for n in nodes:
            for ob in n["outbounds"]:
                t = by_id.get(ob["id"])
                if t is not None and n["id"] not in t["inbounds"]:
                    t["inbounds"].append(n["id"])
        wfs[wf_id] = {
            "wf_id": wf_id,
            "wf_name": str(raw.get("wf_name") or wf_id),
            "wf_size": size,
            "box_w": size,
            "box_h": size / BOX_ASPECT,
            "description": str(raw.get("description") or ""),
            "updated": raw.get("updated"),
            "version": raw.get("version"),
            "file": os.path.basename(f),
            "nodes": nodes,
        }
    return wfs


def load_split_records(job_dir, warnings):
    """finished/*.json (and any sibling state folders) -> dict split_id -> record."""
    records = OrderedDict()
    for state in ("finished", "running", "failed", "queue", "hold", "queued"):
        folder = os.path.join(job_dir, state)
        if not os.path.isdir(folder):
            continue
        for f in sorted(glob.glob(os.path.join(folder, "*.json"))):
            rec = load_json(f, warnings, "split record")
            if not isinstance(rec, dict):
                continue
            sid = str(rec.get("split_id") or os.path.splitext(os.path.basename(f))[0])
            rec["_file"] = os.path.relpath(f, job_dir)
            rec["_folder"] = state
            if sid in records:
                warnings.add("split %s has more than one record; keeping %s, ignoring %s" % (sid, records[sid]["_file"], rec["_file"]))
                continue
            records[sid] = rec
    return records


def load_events(job_dir, warnings, default_tz):
    raw = load_json(os.path.join(job_dir, "full_log.json"), warnings, "full_log")
    if raw is None:
        warnings.add("full_log.json missing or unreadable; the page shows the recorded node path only")
        return []
    if isinstance(raw, dict):
        for key in ("log", "events", "entries", "data"):   # tolerate {"log": [...]} style wrappers
            if isinstance(raw.get(key), list):
                raw = raw[key]
                break
    if not isinstance(raw, list):
        warnings.add("full_log.json is not a list of events")
        return []
    if default_tz is None:
        for e in raw:
            if isinstance(e, dict):
                default_tz = tz_of(e.get("created"))
                if default_tz:
                    break
    events = []
    bad = 0
    last_dt = None
    for i, e in enumerate(raw):
        if not isinstance(e, dict):
            continue
        node = e.get("node")
        if isinstance(node, dict):
            node_id, node_type, node_name = norm_id(node.get("id")), node.get("type"), node.get("name")
        else:
            node_id, node_type, node_name = norm_id(node), None, None
        dt = parse_ts(e.get("created"), default_tz)
        if dt is None:
            bad += 1
        else:
            last_dt = dt
        events.append({
            "i": i,
            "created": e.get("created"),
            "dt": dt,
            "sort_dt": dt or last_dt,
            "split_id": str(e.get("split_id") or ""),
            "node_id": node_id,
            "node_type": node_type,
            "node_name": node_name,
            "event": str(e.get("event") if e.get("event") is not None else ""),
            "type": str(e.get("type") or "trace"),
            "context": e.get("context"),
            "host": e.get("host"),
            "pid": e.get("pid"),
            "linenum": e.get("linenum"),
            "current_status": e.get("current_status"),
            "user": e.get("user"),
            "runame": e.get("runame"),
            "data": e.get("data"),
        })
    if bad:
        warnings.add("%d log entries have an unreadable 'created' stamp; they keep their file position" % bad)
    # keep file order where stamps are missing, otherwise chronological
    first_dt = next((ev["dt"] for ev in events if ev["dt"]), None)
    events.sort(key=lambda ev: ((ev["sort_dt"] or first_dt).timestamp() if (ev["sort_dt"] or first_dt) else 0.0, ev["i"]))
    return events


# --------------------------------------------------------------------------------------
# Building the model
# --------------------------------------------------------------------------------------

def _path_entries(rec):
    out = []
    for p in rec.get("path") or []:
        if isinstance(p, dict):
            out.append({
                "id": norm_id(p.get("id")),
                "type": p.get("type"),
                "name": p.get("name"),
                # 1.5 calls it split_id, 1.4.x calls it split
                "split_id": str(p.get("split_id") if p.get("split_id") is not None else (p.get("split") or "")),
                "wf_id": norm_id(p.get("wf_id")),
                "wf_name": p.get("wf_name"),
                "connection": p.get("connection"),
                "slots": p.get("slots"),
                "hosts_group": p.get("hosts_group"),
                "branch_lock": p.get("branch_lock"),
            })
    return out


_SPLIT_TAIL = re.compile(r"-\d+-\d+$")


def _split_base(sid):
    return _SPLIT_TAIL.sub("", sid)


def _split_sort_key(sid):
    # sibling order: "1-17-17" -> (1, "1", [17, 17]); children "11-0-0", "12-0-0" sort after "1-..."
    parts = sid.split("-")
    base = parts[0]
    try:
        rest = [int(x) for x in parts[1:]]
    except ValueError:
        rest = [0]
    return (len(base), base, rest)


def _derive_parent(sid, known):
    """Parent of a split from FFAStrans' id scheme (processors.au3: child = parent base + counter + '-0-0').
    Returns the longest known split whose base is a proper prefix of this split's base, or None."""
    base = _split_base(sid)
    best = None
    for other in known:
        if other == sid:
            continue
        ob = _split_base(other)
        if base.startswith(ob) and len(ob) < len(base) and (best is None or len(ob) > len(_split_base(best))):
            best = other
    return best


def _recorded_parent(rec):
    """1.4.x records a subhold ancestry in splits.parent ('\\1-0-0\\112-0-2'); the last segment is the parent."""
    if not isinstance(rec, dict):
        return None
    sp = rec.get("splits")
    if not isinstance(sp, dict):
        return None
    chain = [x for x in str(sp.get("parent") or "").replace("/", "\\").split("\\") if x]
    return chain[-1] if chain else None


def _status_flag(value):
    s = as_text(value).strip()
    return STATUS_FLAG.get(s)


def build_model(job_dir, extra_wf_dirs):
    warnings = Warnings()
    job_dir = os.path.abspath(job_dir)
    job_rec = load_json(os.path.join(job_dir, ".json"), warnings, "job record")
    if job_rec is None:
        warnings.add(".json job record missing; header data will be sparse")
        job_rec = {}
    submit = job_rec.get("submit") if isinstance(job_rec.get("submit"), dict) else {}
    default_tz = tz_of(job_rec.get("start_time")) or tz_of(job_rec.get("end_time")) or tz_of(submit.get("time"))
    workflows = load_workflows(job_dir, extra_wf_dirs, warnings)
    records = load_split_records(job_dir, warnings)
    if default_tz is None:
        for rec in records.values():
            default_tz = tz_of(rec.get("start_time")) or tz_of(rec.get("end_time"))
            if default_tz:
                break
    events = load_events(job_dir, warnings, default_tz)

    node_index = {}   # (wf_id, node_id) -> node
    id_to_wfs = {}    # node_id -> [wf_id]
    for wf_id, wf in workflows.items():
        for n in wf["nodes"]:
            node_index[(wf_id, n["id"])] = n
            id_to_wfs.setdefault(n["id"], []).append(wf_id)

    main_wf_id = rec_wf_id(job_rec)
    if main_wf_id not in workflows:
        if workflows:
            if main_wf_id:
                warnings.add("job workflow %s not found in workflows/; using %s" % (main_wf_id, next(iter(workflows))))
            main_wf_id = next(iter(workflows))
        else:
            warnings.add("no workflow definition found; nodes will be auto-arranged from the run path")

    # ---- splits -------------------------------------------------------------------
    splits = OrderedDict()
    for sid, rec in records.items():
        splits[sid] = {"split_id": sid, "record": rec, "path": _path_entries(rec)}
    for ev in events:
        sid = ev["split_id"]
        if sid and ev["node_id"] and sid not in splits:
            splits[sid] = {"split_id": sid, "record": None, "path": []}
            warnings.add("split %s appears in the log but has no record (still running, or lost?)" % sid)
    if not splits and job_rec.get("split_id"):
        sid = str(job_rec["split_id"])
        splits[sid] = {"split_id": sid, "record": job_rec, "path": _path_entries(job_rec)}

    # (split, node) -> wf_id from the recorded paths (node ids are NOT unique across workflows)
    pathmap = {}
    for sp in splits.values():
        for p in sp["path"]:
            if p["wf_id"]:
                pathmap[(p["split_id"], p["id"])] = p["wf_id"]

    def wf_for(split_id, node_id):
        wf_id = pathmap.get((split_id, node_id))
        if wf_id and (wf_id, node_id) in node_index:
            return wf_id
        cands = id_to_wfs.get(node_id) or []
        if main_wf_id in cands:
            return main_wf_id
        if cands:
            return cands[0]
        return main_wf_id

    # ---- ghost workflow when the definition is missing -------------------------------
    if not workflows:
        ghost_nodes = OrderedDict()
        order = []
        for sp in splits.values():
            for p in sp["path"]:
                if p["id"] and p["id"] not in ghost_nodes:
                    ghost_nodes[p["id"]] = (p["type"] or "unknown", p["name"])
                    order.append(p["id"])
        for ev in events:
            if ev["node_id"] and ev["node_id"] not in ghost_nodes:
                ghost_nodes[ev["node_id"]] = (ev["node_type"] or "unknown", ev["node_name"])
                order.append(ev["node_id"])
        nodes = []
        cols = 6
        for i, nid in enumerate(order):
            ntype, name = ghost_nodes[nid]
            nodes.append({
                "index": i, "id": nid, "type": ntype, "type_name": type_name_of(ntype),
                "family": family_of(ntype), "name": name or type_name_of(ntype), "description": "",
                "pos_x": 75 + (i % cols) * DEFAULT_WF_SIZE * 1.5,
                "pos_y": 75 + (i // cols) * (DEFAULT_WF_SIZE / BOX_ASPECT) * 1.5,
                "bypass": False, "start_proc": False, "execute_on": "success", "initiation": None,
                "slots": None, "hosts_group": None, "custom_proc_guid": "", "outbounds": [], "inbounds": [],
                "properties": None, "ghost": True,
            })
        main_wf_id = main_wf_id or "unknown-workflow"
        workflows[main_wf_id] = {
            "wf_id": main_wf_id, "wf_name": str(job_rec.get("wf_name") or "(workflow definition missing)"),
            "wf_size": DEFAULT_WF_SIZE, "box_w": DEFAULT_WF_SIZE, "box_h": DEFAULT_WF_SIZE / BOX_ASPECT,
            "description": "", "updated": None, "version": None, "file": None, "nodes": nodes, "ghost": True,
        }
        for n in nodes:
            node_index[(main_wf_id, n["id"])] = n
            id_to_wfs.setdefault(n["id"], []).append(main_wf_id)

    # ---- job timing -----------------------------------------------------------------
    all_times = [ev["dt"] for ev in events if ev["dt"]]
    for sp in splits.values():
        rec = sp["record"]
        if rec:
            for k in ("start_time", "end_time"):
                dt = parse_ts(rec.get(k), default_tz)
                if dt:
                    all_times.append(dt)
    job_start = parse_ts(job_rec.get("start_time"), default_tz)
    start_source = "job record"
    if job_start is None and submit.get("time"):
        job_start = parse_ts(submit.get("time"), default_tz)
        start_source = "submit time"
    if job_start is None and all_times:
        job_start = min(all_times)
        start_source = "earliest log entry or split record"
    if start_source != "job record" and job_start is not None:
        warnings.add("job record has no start_time; the job start is taken from the %s" % start_source)
    job_end = parse_ts(job_rec.get("end_time"), default_tz)
    end_source = "job record"
    if job_end is None and all_times:
        job_end = max(all_times)
        end_source = "latest log entry or split record"
    if job_start and job_end and job_end < job_start:
        job_end = job_start
    t0 = to_ms(job_start) if job_start else (to_ms(min(all_times)) if all_times else 0.0)

    def rel(dt):
        return None if dt is None else round(to_ms(dt) - t0, 3)

    # ---- events by (split, node) ---------------------------------------------------
    ev_by_split_node = OrderedDict()
    for ev in events:
        if ev["node_id"]:
            ev_by_split_node.setdefault((ev["split_id"], ev["node_id"]), []).append(ev)

    # ---- runs -----------------------------------------------------------------------
    run_lookup = {}
    split_order = sorted(splits.keys(), key=_split_sort_key)
    ev_by_split = OrderedDict()
    for ev in events:
        ev_by_split.setdefault(ev["split_id"], []).append(ev)
    for sid in split_order:
        sp = splits[sid]
        rec = sp["record"]
        own = [p for p in sp["path"] if p["split_id"] == sid]
        own_ids = set(p["id"] for p in own)
        conn_of = {}
        for p in own:
            conn_of.setdefault(p["id"], p["connection"])

        # parent split = split of the path entry preceding the first own entry
        parent, parent_source = None, None
        if own:
            idx = sp["path"].index(own[0])
            if idx > 0:
                parent, parent_source = sp["path"][idx - 1]["split_id"], "path"
        if parent is None and rec:
            rp = _recorded_parent(rec)          # 1.4.x: splits.parent ancestry
            if rp:
                parent, parent_source = rp, "record"
        if parent is None and rec and isinstance(rec.get("subholds"), list) and rec["subholds"]:
            parent, parent_source = rec["subholds"][-1].get("parent"), "subholds"
        if parent is None:
            parent = _derive_parent(sid, splits.keys())
            parent_source = "split id" if parent else None
        sp["parent"] = parent if parent and parent != sid else None
        sp["parent_source"] = parent_source if sp["parent"] else None

        split_evs = ev_by_split.get(sid) or []
        timed = [ev for ev in split_evs if ev["dt"]]
        split_first = timed[0]["dt"] if timed else None
        split_end = parse_ts(rec.get("end_time"), default_tz) if rec else None
        split_start_rec = parse_ts(rec.get("start_time"), default_tz) if rec else None
        boundaries = [ev for ev in timed if ev["event"] == NODE_START_EVENT and ev["node_id"]]

        def new_run(node_id, node_type, node_name, from_path, start=None, anchor=None):
            return {"node_id": node_id, "node_type": node_type, "node_name": node_name,
                    "wf_id": wf_for(sid, node_id), "from_path": from_path, "connection": conn_of.get(node_id),
                    "evs": [], "start": start, "first": None, "last": None, "end": None,
                    "start_anchor": anchor, "end_anchor": None, "end_payload": None, "split_id": sid}

        if boundaries:
            # FFAStrans 1.4.x logs 'node start' / 'node end': exact boundaries, and a node may run
            # more than once in the same split.
            split_runs = []
            cur = None
            pending = []
            for ev in split_evs:
                if ev["event"] == NODE_START_EVENT and ev["node_id"]:
                    cur = new_run(ev["node_id"], ev["node_type"], ev["node_name"], ev["node_id"] in own_ids,
                                  ev["dt"], "node_start")
                    if pending:
                        cur["evs"].extend(pending)
                        pending = []
                    split_runs.append(cur)
                if cur is None:
                    pending.append(ev)
                    continue
                cur["evs"].append(ev)
                if ev["event"] == NODE_END_EVENT and cur["end"] is None:
                    cur["end"], cur["end_anchor"] = ev["dt"], "node_end"
                    if isinstance(ev["data"], dict):
                        cur["end_payload"] = ev["data"]
            if pending and split_runs:
                split_runs[0]["evs"] = pending + split_runs[0]["evs"]
            # path nodes that never logged a boundary (bypassed, or killed before they started)
            if own:
                merged, ri = [], 0
                for p in own:
                    hit = None
                    for j in range(ri, len(split_runs)):
                        if split_runs[j]["node_id"] == p["id"]:
                            hit = j
                            break
                    if hit is None:
                        merged.append(new_run(p["id"], p["type"], p["name"], True))
                    else:
                        merged.extend(split_runs[ri:hit + 1])
                        ri = hit + 1
                merged.extend(split_runs[ri:])
                split_runs = merged
        else:
            # FFAStrans 1.5 has no boundary events: the path gives the order, the log the times.
            seen = set()
            split_runs = []
            for p in own:
                if p["id"] in seen:
                    warnings.add("split %s visits node %s more than once; its events are attached to the first visit" % (sid, p["id"]))
                    continue
                seen.add(p["id"])
                split_runs.append(new_run(p["id"], p["type"], p["name"], True))
            for (esid, nid), evs in ev_by_split_node.items():
                if esid != sid or nid in seen:
                    continue
                seen.add(nid)
                entry = new_run(nid, evs[0]["node_type"], evs[0]["node_name"], False)
                first = evs[0]["dt"]
                pos = len(split_runs)
                if first:
                    pos = 0
                    for i, r in enumerate(split_runs):
                        revs = ev_by_split_node.get((sid, r["node_id"])) or []
                        if revs and revs[0]["dt"] and revs[0]["dt"] <= first:
                            pos = i + 1
                        elif not revs and pos == i:
                            pos = i + 1
                split_runs.insert(pos, entry)
            for r in split_runs:
                r["evs"] = list(ev_by_split_node.get((sid, r["node_id"])) or [])

        for r in split_runs:
            defn = node_index.get((r["wf_id"], r["node_id"]))
            if defn is not None:
                r["node_name"] = defn["name"]          # the definition's name beats the (often absent) log name
                r["node_type"] = r["node_type"] or defn["type"]
            times = [e["dt"] for e in r["evs"] if e["dt"]]
            r["first"] = min(times) if times else None
            r["last"] = max(times) if times else None
            r["end_anchored"] = bool(r["evs"]) and r["evs"][0]["event"] in END_ANCHORED_EVENTS

        if not boundaries:
            # timing: a run spans from its first log entry to the next node's first entry.
            # Nodes that only log when they are done (END_ANCHORED_EVENTS) own the gap before them.
            prev_last = split_first or split_start_rec or job_start
            for r in split_runs:
                if r["first"] and not r["end_anchored"]:
                    r["start"], r["start_anchor"] = r["first"], "first_entry"
                else:
                    r["start"], r["start_anchor"] = prev_last, ("previous_last" if r["first"] else "previous_last_no_entries")
                if r["start"] and r["first"] and r["start"] > r["first"]:
                    r["start"] = r["first"]
                prev_last = r["last"] or r["start"]
            for k, r in enumerate(split_runs):
                nxt = split_runs[k + 1] if k + 1 < len(split_runs) else None
                if nxt is None:
                    if split_end is not None:
                        r["end"], r["end_anchor"] = split_end, "split_end"
                    else:
                        r["end"], r["end_anchor"] = (r["last"] or r["start"]), "own_last"
                elif nxt["first"] and not nxt["end_anchored"]:
                    r["end"], r["end_anchor"] = nxt["first"], "next_first"
                else:
                    r["end"], r["end_anchor"] = (r["last"] or r["start"]), "own_last"
        else:
            # fill the gaps left by runs without boundary events
            prev_end = split_first or split_start_rec or job_start
            for r in split_runs:
                if r["start"] is None:
                    r["start"], r["start_anchor"] = (r["first"] or prev_end), ("first_entry" if r["first"] else "previous_end")
                prev_end = r["end"] or r["last"] or r["start"] or prev_end
            for k, r in enumerate(split_runs):
                if r["end"] is not None:
                    continue
                nxt = split_runs[k + 1] if k + 1 < len(split_runs) else None
                if nxt is not None and nxt["start"] is not None:
                    r["end"], r["end_anchor"] = nxt["start"], "next_start"
                elif split_end is not None:
                    r["end"], r["end_anchor"] = split_end, "split_end"
                else:
                    r["end"], r["end_anchor"] = (r["last"] or r["start"]), "own_last"

        for k, r in enumerate(split_runs):
            if r["end"] is not None and r["start"] is not None and r["end"] < r["start"]:
                r["end"] = r["last"] if (r["last"] and r["last"] >= r["start"]) else r["start"]
            r["seq"] = k
            r["events"] = [e["i"] for e in r["evs"]]
            r["is_last"] = k == len(split_runs) - 1

        # state per run
        rec_err = (rec or {}).get("error") if isinstance((rec or {}).get("error"), dict) else {}
        rec_err_msg = as_text(rec_err.get("msg")).strip() if rec_err else ""
        rec_err_code = as_text(rec_err.get("code")).strip() if rec_err else ""
        rec_result = as_text((rec or {}).get("result")).strip()
        rec_status = as_text((rec or {}).get("status")).strip()
        aborted = rec is not None and (rec_result.lower() == "abort" or rec_status == "2" or rec_err_code in ABORT_CODES)
        for r in split_runs:
            evs = r["evs"]
            ntype = r["node_type"] or ""
            # 1.4.x: the 'node end' payload states this run's own outcome
            end_status = as_text((r.get("end_payload") or {}).get("status")).strip().lower()
            end_error = first_line(as_text((r.get("end_payload") or {}).get("error")), 240)
            end_code = as_text((r.get("end_payload") or {}).get("code")).strip()
            benign = [e for e in evs if e["type"] == "error" and (ntype, e["event"]) in BENIGN_ERRORS]
            condf = [e for e in evs if e["type"] == "error" and (ntype, e["event"]) in COND_FALSE_EVENTS]
            soft = [e for e in evs if e["type"] == "error" and e["event"] in SOFT_ERROR_EVENTS]
            hard = [e for e in evs if e["type"] == "error" and e not in benign and e not in condf and e not in soft]
            warns = [e for e in evs if e["type"] == "warning"]
            state, reasons, explain = "ok", [], None
            ended_in_error = r["is_last"] and rec is not None and (rec_result.lower() == "error" or bool(rec_err_msg))
            if end_status == "abort":
                state = "aborted"
                reasons.append("this node was stopped by a job abort" + (": " + end_error if end_error else ""))
            elif end_status and end_status not in ("ok", "success", "finished", "done"):
                state = "error"
                reasons.append("the node ended with status '%s'" % end_status + (": " + end_error if end_error else ""))
            elif r["is_last"] and aborted:
                state = "aborted"
                reasons.append("the job was aborted here" + (": " + rec_err_msg if rec_err_msg else ""))
            elif ended_in_error:
                state = "error"
                if rec_err_msg:
                    reasons.append("the branch ended here with an error message")
                if rec_result.lower() == "error":
                    reasons.append("split result is 'error'")
                elif rec_result:
                    explain = ("FFAStrans recorded result '%s' because only the error message was set (the error code is empty, "
                               "which happens for validation errors); the branch still stopped at this node." % rec_result)
                if hard:
                    reasons.append(_plural(len(hard), "error event") + " logged")
            elif condf:
                state = "cond_false"
            elif hard:
                # anything logged as an error by _setlog_error() is the node failing; the branch may still
                # carry on through an "execute on error / any" connector, which the headline says
                state = "error"
                if not r["is_last"]:
                    reasons.append(_plural(len(hard), "error event") + " logged; the branch carried on through the next node")
                elif rec is not None:
                    reasons.append(_plural(len(hard), "error event") + " logged; the split record does not mark the branch as failed")
                else:
                    reasons.append(_plural(len(hard), "error event") + " logged and no split record confirms the outcome")
            elif soft:
                state = "warn"
                reasons.append(_plural(len(soft), "media probe error") + " logged (ffprobe/mediainfo/exiftool); the job carried on")
            elif warns:
                state = "warn"
                reasons.append(_plural(len(warns), "warning") + " logged")
            elif not r["from_path"] and rec is None:
                state = "unknown"
                reasons.append("seen in the log only; no split record yet")
            if state == "error" and ntype == "op_cond" and (condf or end_code in ("-1", "-1.0")
                                                            or (r["is_last"] and rec_err_code in ("-1", "-1.0"))):
                state = "cond_false"
            if state == "cond_false":
                reasons = [("the condition evaluated false, so the branch ended here" if r["is_last"]
                            else "the condition evaluated false; the branch carried on through an \"execute on error\" connector")] + \
                          [x for x in reasons if x.endswith(" logged")]
            if state in ("error", "aborted", "cond_false") and soft:
                reasons.append(_plural(len(soft), "media probe error") + " logged earlier in this run")
            if benign:
                reasons.append(BENIGN_ERRORS[(ntype, benign[0]["event"])])
            evidence = []
            if state in ("error", "aborted") and not hard and evs:
                evidence = [evs[-1]["i"]]   # the last thing the node logged before the branch died
            r["state"] = state
            r["reasons"] = reasons
            r["explain"] = explain
            r["n_events"] = len(evs)
            r["n_errors"] = len(hard) + len(condf)
            r["n_soft"] = len(soft)
            r["n_warnings"] = len(warns)
            r["hard"] = hard
            r["soft"] = soft
            r["warns"] = warns
            r["condf"] = condf
            r["evidence"] = evidence
            statuses = []
            for e in evs:
                cs = e.get("current_status")
                if cs and (not statuses or statuses[-1] != cs):
                    statuses.append(cs)
            r["status_texts"] = statuses[-6:]
        for r in split_runs:
            r["run_id"] = "%s|%s|%d" % (sid, r["node_id"], r["seq"])
            run_lookup[(sid, r["node_id"])] = r
        sp["runs"] = split_runs
        sp["first_event"] = split_first
        sp["end"] = split_end or (split_runs[-1]["end"] if split_runs else None)
        sp["start"] = (split_runs[0]["start"] if split_runs else None) or split_first or split_start_rec
        sp["aborted"] = aborted

    # splits and runs in the order they started
    far = datetime.max.replace(tzinfo=timezone.utc)
    split_order = sorted(splits.keys(), key=lambda s: ((splits[s]["start"] or far), _split_sort_key(s)))
    runs = [r for sid in split_order for r in splits[sid]["runs"]]

    # attach run ids to events; node-less ('sys') events go to the run whose time span contains them
    ev_run = {}
    for r in runs:
        for i in r["events"]:
            ev_run[i] = r["run_id"]
    for ev in events:
        if ev["node_id"] or ev["i"] in ev_run or not ev["split_id"] or ev["dt"] is None or ev["split_id"] not in splits:
            continue
        for r in splits[ev["split_id"]]["runs"]:
            if r["start"] and r["end"] and r["start"] <= ev["dt"] <= r["end"]:
                ev_run[ev["i"]] = r["run_id"]
                r["events"].append(ev["i"])
                r["n_events"] = len(r["events"])
                break

    # ---- traversed edges ------------------------------------------------------------
    edges = OrderedDict()   # (wf, from, to) -> set(splits)
    jumps = []              # sub-workflow transitions
    for sid in split_order:
        sp = splits[sid]
        path = sp["path"]
        if path:
            for a, b in zip(path, path[1:]):
                wa = a["wf_id"] or wf_for(a["split_id"], a["id"])
                wb = b["wf_id"] or wf_for(b["split_id"], b["id"])
                if wa == wb:
                    edges.setdefault((wa, a["id"], b["id"]), set()).add(b["split_id"])
                else:
                    jumps.append({"from_wf": wa, "from": a["id"], "to_wf": wb, "to": b["id"], "split_id": b["split_id"]})
        else:
            rs = sp["runs"]
            for a, b in zip(rs, rs[1:]):
                if a["wf_id"] == b["wf_id"]:
                    edges.setdefault((a["wf_id"], a["node_id"], b["node_id"]), set()).add(sid)
            if sp.get("parent") and sp["parent"] in splits and splits[sp["parent"]].get("runs") and rs:
                pa = splits[sp["parent"]]["runs"][-1]
                if pa["wf_id"] == rs[0]["wf_id"]:
                    edges.setdefault((pa["wf_id"], pa["node_id"], rs[0]["node_id"]), set()).add(sid)
    seen_jumps = set()
    uniq_jumps = []
    for j in jumps:
        key = (j["from_wf"], j["from"], j["to_wf"], j["to"], j["split_id"])
        if key not in seen_jumps:
            seen_jumps.add(key)
            uniq_jumps.append(j)

    # ---- node summaries ---------------------------------------------------------------
    node_runs = {}
    for r in runs:
        node_runs.setdefault((r["wf_id"], r["node_id"]), []).append(r)
    for (wf_id, nid), rs in list(node_runs.items()):
        if (wf_id, nid) in node_index:
            continue
        # node ran but is not in the workflow definition (edited workflow?) -> add a ghost box
        wf = workflows.get(wf_id) or workflows[main_wf_id]
        ntype = rs[0]["node_type"] or "unknown"
        maxx = max([n["pos_x"] for n in wf["nodes"]] + [0])
        maxy = max([n["pos_y"] for n in wf["nodes"]] + [0])
        ghost = {
            "index": len(wf["nodes"]), "id": nid, "type": ntype, "type_name": type_name_of(ntype), "family": family_of(ntype),
            "name": rs[0]["node_name"] or type_name_of(ntype), "description": "(not in workflow definition)",
            "pos_x": maxx + wf["box_w"] * 1.5, "pos_y": maxy, "bypass": False, "start_proc": False,
            "execute_on": "success", "initiation": None, "slots": None, "hosts_group": None,
            "custom_proc_guid": "", "outbounds": [], "inbounds": [], "properties": None, "ghost": True,
        }
        wf["nodes"].append(ghost)
        node_index[(wf["wf_id"], nid)] = ghost
        for r in rs:
            r["wf_id"] = wf["wf_id"]
        warnings.add("node %s (%s) ran in split %s but is not in workflow %s" % (nid, ntype, rs[0]["split_id"], wf["wf_name"]))

    state_rank = {"idle": 0, "unknown": 1, "ok": 2, "warn": 3, "cond_false": 4, "aborted": 5, "error": 6}
    for wf_id, wf in workflows.items():
        for n in wf["nodes"]:
            rs = node_runs.get((wf_id, n["id"])) or []
            state = "idle"
            total = 0.0
            lower_bound = False
            for r in rs:
                if state_rank.get(r["state"], 0) > state_rank[state]:
                    state = r["state"]
                if r["start"] and r["end"]:
                    total += max(0.0, to_ms(r["end"]) - to_ms(r["start"]))
                if r.get("end_anchor") == "own_last" and not r["is_last"]:
                    lower_bound = True
            n["state"] = state
            n["n_runs"] = len(rs)
            n["total_ms"] = round(total, 3)
            n["total_is_lower_bound"] = lower_bound
            n["n_errors"] = sum(r["n_errors"] for r in rs)
            n["run_ids"] = [r["run_id"] for r in rs]

    # ---- silences, time sinks and anomalies -------------------------------------------------
    # gap = ms since the previous entry of the same run (what "Slow steps" filters on)
    ev_obj = {ev["i"]: ev for ev in events}
    ev_gap = {}
    sinks = []
    anomalies = []

    def run_label(r):
        return {"run_id": r["run_id"], "node_name": r["node_name"] or r["node_type"] or r["node_id"], "split_id": r["split_id"]}

    for r in runs:
        evs = sorted((ev_obj[i] for i in r["events"] if ev_obj[i]["dt"]), key=lambda e: e["dt"])
        for a, b in zip(evs, evs[1:]):
            g = round(to_ms(b["dt"]) - to_ms(a["dt"]), 3)
            ev_gap[b["i"]] = g
            if g >= GAP_MIN_MS:
                kind, label = GAP_KINDS.get(a["event"], ("work", "unlogged work"))
                s = dict(run_label(r))
                s.update({"kind": kind, "label": label, "ms": g, "t": rel(a["dt"]), "after_event": a["event"],
                          "status": a.get("current_status"), "event_index": b["i"]})
                sinks.append(s)
        if r["end_anchor"] == "next_first" and r["last"] and r["end"] and r["end"] > r["last"]:
            g = round(to_ms(r["end"]) - to_ms(r["last"]), 3)
            if g >= GAP_MIN_MS:
                s = dict(run_label(r))
                s.update({"kind": "work", "label": "unlogged work until the next node started (encoding, then hand-over)",
                          "ms": g, "t": rel(r["last"]), "after_event": evs[-1]["event"] if evs else None,
                          "status": evs[-1].get("current_status") if evs else None, "event_index": evs[-1]["i"] if evs else None})
                sinks.append(s)
    for sid in split_order:
        sp = splits[sid]
        rs = sp["runs"]
        for a, b in zip(rs, rs[1:]):
            if a["end"] and b["start"] and b["start"] > a["end"]:
                g = round(to_ms(b["start"]) - to_ms(a["end"]), 3)
                if g >= GAP_MIN_MS:
                    s = dict(run_label(b))
                    s.update({"kind": "handover", "label": "between the previous node's end and this node's start (queue, dispatch)",
                              "ms": g, "t": rel(a["end"]), "after_event": None, "status": None, "event_index": None})
                    sinks.append(s)
        parent = splits.get(sp.get("parent")) if sp.get("parent") else None
        if parent and parent.get("end") and sp.get("start") and sp["start"] > parent["end"] and rs:
            g = round(to_ms(sp["start"]) - to_ms(parent["end"]), 3)
            if g >= GAP_MIN_MS:
                s = dict(run_label(rs[0]))
                s.update({"kind": "handover", "label": "between the parent split's end and this split's first node (queue, dispatch)",
                          "ms": g, "t": rel(parent["end"]), "after_event": None, "status": None, "event_index": None})
                sinks.append(s)
    sinks.sort(key=lambda s: -s["ms"])

    for s in sinks:
        if s["kind"] == "wait" and s["after_event"] == "_WaitForResources" and s["ms"] >= STALL_NOTE_MS:
            anomalies.append(dict(s, severity="note", title="Waited %s for resources" % _fmt_ms(s["ms"]),
                                  detail="The node sat in _WaitForResources (CPU roof, storage or work dir)" + (": " + s["status"] if s["status"] else "")))
        elif s["kind"] == "handover" and s["ms"] >= STALL_NOTE_MS:
            anomalies.append(dict(s, severity="note", title="%s before the next node started" % _fmt_ms(s["ms"]), detail=s["label"]))
        elif s["kind"] == "wait" and s["ms"] >= STALL_NOTE_MS:
            anomalies.append(dict(s, severity="info", title="Hold node slept %s" % _fmt_ms(s["ms"]), detail="By design, but it is part of the job time"))
    seen_nodes = {}
    for r in runs:
        key = (r["split_id"], r["node_id"])
        seen_nodes[key] = seen_nodes.get(key, 0) + 1
    for r in runs:
        base = dict(run_label(r), kind="run", ms=r["duration_ms"] if r.get("duration_ms") is not None else None, t=rel(r["start"]), event_index=None)
        if seen_nodes[(r["split_id"], r["node_id"])] > 1 and r["seq"] == min(x["seq"] for x in runs if (x["split_id"], x["node_id"]) == (r["split_id"], r["node_id"])):
            anomalies.append(dict(base, severity="note", title="Node ran %d times in split %s" % (seen_nodes[(r["split_id"], r["node_id"])], r["split_id"]),
                                  detail="A loop or a retry inside one branch"))
        if not r["events"] and r["from_path"]:
            anomalies.append(dict(base, severity="info", title="Nothing logged for this run", detail="Its timing is inferred from its neighbours" + ("; the node is bypassed" if (node_index.get((r["wf_id"], r["node_id"])) or {}).get("bypass") else "")))
        if r.get("start_anchor") == "node_start" and r.get("end_anchor") != "node_end" and r["state"] not in ("aborted",):
            anomalies.append(dict(base, severity="note", title="No 'node end' entry", detail="The node process logged a start but never an end: it was killed or crashed"))
    for sid in split_order:
        sp = splits[sid]
        rec = sp["record"]
        rs = sp["runs"]
        if rec is None and rs:
            anomalies.append(dict(run_label(rs[-1]), kind="split", ms=None, t=rel(sp.get("start")), event_index=None, severity="note",
                                  title="Split %s has no record" % sid, detail="It is still running, or its record was lost; its outcome is unknown"))
        retries = rec.get("retries") if rec and isinstance(rec.get("retries"), dict) else None
        if retries and rs:
            n_retry = 0
            for v in retries.values():
                try:
                    n_retry = max(n_retry, int(v))
                except (TypeError, ValueError):
                    pass
            if n_retry > 0:
                anomalies.append(dict(run_label(rs[-1]), kind="split", ms=None, t=rel(sp.get("start")), event_index=None, severity="note",
                                      title="Split %s was retried (%d)" % (sid, n_retry), detail="The record's retries counter is %s" % json.dumps(retries)))

    # ---- where the time went -----------------------------------------------------------------
    job_ms = (to_ms(job_end) - to_ms(job_start)) if (job_start and job_end) else 0.0
    intervals = sorted((to_ms(r["start"]), to_ms(r["end"])) for r in runs if r["start"] and r["end"] and r["end"] > r["start"])
    busy = 0.0
    cur = None
    for a, b in intervals:
        if cur is None or a > cur[1]:
            if cur:
                busy += cur[1] - cur[0]
            cur = [a, b]
        else:
            cur[1] = max(cur[1], b)
    if cur:
        busy += cur[1] - cur[0]
    idle = max(0.0, job_ms - busy) if job_ms else 0.0
    if job_ms and idle >= max(10000.0, 0.25 * job_ms):
        anomalies.append({"kind": "job", "severity": "note", "title": "%s with no node active" % _fmt_ms(idle),
                          "detail": "%d%% of the job was spent between tickets: queueing, dispatch and holds" % round(100 * idle / job_ms),
                          "ms": idle, "t": None, "run_id": None, "node_name": None, "split_id": None, "event_index": None})
    by_family = {}
    run_total = 0.0
    for r in runs:
        if r["start"] and r["end"] and r["end"] > r["start"]:
            d = to_ms(r["end"]) - to_ms(r["start"])
            fam = (node_index.get((r["wf_id"], r["node_id"])) or {}).get("family") or "Unknown"
            by_family[fam] = by_family.get(fam, 0.0) + d
            run_total += d
    def run_ms(r):
        return (to_ms(r["end"]) - to_ms(r["start"])) if (r["start"] and r["end"] and r["end"] > r["start"]) else 0.0
    top_runs = sorted((r for r in runs if run_ms(r) > 0), key=lambda r: -run_ms(r))[:6]
    time_breakdown = {
        "job_ms": round(job_ms, 3), "busy_ms": round(busy, 3), "idle_ms": round(idle, 3), "run_total_ms": round(run_total, 3),
        "by_family": [{"family": f, "ms": round(v, 3)} for f, v in sorted(by_family.items(), key=lambda x: -x[1])],
        "top_runs": [dict(run_label(r), ms=round(run_ms(r), 3), state=r["state"], lower_bound=(r.get("end_anchor") == "own_last" and not r["is_last"])) for r in top_runs],
    }
    sev_rank = {"note": 0, "info": 1}
    anomalies.sort(key=lambda a: (sev_rank.get(a["severity"], 2), -(a["ms"] or 0)))

    # ---- issues: one card per run that failed / was aborted / stopped on a false condition /
    #      logged errors or warnings but carried on -----------------------------------------
    def ev_brief(e):
        # 1.4.x keeps the message in current_status and leaves data empty; 1.5 does the opposite
        text = as_text(e["data"]).strip() or as_text(e.get("current_status"))
        return {"i": e["i"], "t": rel(e["dt"]), "time": iso(e["dt"]), "event": e["event"], "type": e["type"],
                "status": e.get("current_status"), "context": e.get("context"), "line": first_line(text, 160)}

    def probe_reason(r, e):
        """For a soft probe error, the reason usually sits in the preceding trace event of the same name."""
        evs = ev_by_split_node.get((r["split_id"], r["node_id"])) or []
        for prev in reversed(evs[:evs.index(e)] if e in evs else []):
            if prev["event"] == e["event"] and prev["type"] == "trace" and isinstance(prev["data"], dict):
                err = prev["data"].get("error")
                if isinstance(err, dict) and err.get("string"):
                    return str(err["string"])
                break
        return None

    def dedupe(evs):
        out = []
        for e in evs:
            key = (e["event"], as_text(e["data"]))
            if out and out[-1][0] == key:
                out[-1][1] += 1
            else:
                out.append([key, 1, e])
        return [(x[2], x[1]) for x in out]

    issues = []
    for r in runs:
        sp = splits[r["split_id"]]
        rec = sp["record"] or {}
        err = rec.get("error") if isinstance(rec.get("error"), dict) else {}
        rec_msg = as_text(err.get("msg")).strip()
        rec_code = as_text(err.get("code")).strip()
        rec_result = as_text(rec.get("result")).strip()
        state = r["state"]
        if state not in ("error", "aborted", "cond_false", "warn"):
            continue
        listed = r["hard"] + r["soft"] + r["warns"]
        listed.sort(key=lambda e: (e["dt"].timestamp() if e["dt"] else 0.0, e["i"]))
        evlist = []
        for e, count in dedupe(listed):
            b = ev_brief(e)
            b["count"] = count
            reason = probe_reason(r, e) if e["event"] in SOFT_ERROR_EVENTS else None
            if reason:
                b["reason"] = reason
            evlist.append(b)
        end_msg = first_line(as_text((r.get("end_payload") or {}).get("error")), 400)
        if state in ("error", "aborted"):
            if r["is_last"] and rec_msg:
                message = rec_msg
                source = "split record %s" % rec.get("_file")
            elif end_msg:
                message = end_msg
                source = "the node's 'node end' log entry"
            elif r["hard"]:
                e = r["hard"][-1]
                message = as_text(e["data"]).strip() or as_text(e.get("current_status")) or e["event"]
                source = "log event %s" % e["event"]
            else:
                message = "no error message was recorded"
                source = "split record" if r["is_last"] and sp["record"] else "log"
            headline = ("Job aborted" if state == "aborted"
                        else ("Branch ended in error" if r["is_last"] else "Node failed"))
        elif state == "cond_false":
            if r["is_last"] and rec_msg:
                message, source = rec_msg, "split record %s" % rec.get("_file")
            elif r["condf"]:
                e = r["condf"][-1]
                message = as_text(e["data"]).strip() or as_text(e.get("current_status")) or "condition evaluated false"
                source = "log event %s" % e["event"]
            elif end_msg:
                message, source = end_msg, "the node's 'node end' log entry"
            else:
                message, source = "condition evaluated false", "log"
            headline = "Condition false, branch stopped" if r["is_last"] else "Condition false, branch carried on via the error connector"
        else:
            e = listed[0] if listed else None
            message = (evlist[0].get("reason") or as_text(e.get("current_status")) or evlist[0]["line"]) if e else "warning"
            source = "log"
            headline = ("Media probe errors, job carried on" if r["soft"] and not r["hard"] and not r["warns"]
                        else "Logged errors, job carried on" if r["hard"] else "Warnings logged")
        issues.append({
            "kind": state,
            "severity": state,
            "headline": headline,
            "time": iso(r["end"] if state != "warn" else (listed[0]["dt"] if listed and listed[0]["dt"] else r["start"])),
            "t": rel(r["end"] if state != "warn" else (listed[0]["dt"] if listed and listed[0]["dt"] else r["start"])),
            "split_id": r["split_id"],
            "node_id": r["node_id"],
            "wf_id": r["wf_id"],
            "node_name": r["node_name"] or r["node_type"] or r["node_id"],
            "message": first_line(message, 400) if len(message) > 400 else message,
            "message_source": source,
            "record_result": rec_result or None,
            "record_code": rec_code or None,
            "explain": r.get("explain"),
            "events": evlist,
            "evidence": r["evidence"],
            "run_id": r["run_id"],
        })
    issues.sort(key=lambda x: (x["t"] if x["t"] is not None else float("inf")))

    # ---- serialize -----------------------------------------------------------------------
    def ser_run(r):
        return {
            "run_id": r["run_id"], "split_id": r["split_id"], "wf_id": r["wf_id"], "node_id": r["node_id"],
            "node_type": r["node_type"], "node_name": r["node_name"], "seq": r["seq"], "from_path": r["from_path"],
            "connection": r.get("connection"), "is_last": r["is_last"], "state": r["state"], "reasons": r["reasons"],
            "explain": r.get("explain"),
            "start": iso(r["start"]), "end": iso(r["end"]), "t0": rel(r["start"]), "t1": rel(r["end"]),
            "first": rel(r["first"]), "last": rel(r["last"]),
            "start_anchor": r.get("start_anchor"), "end_anchor": r.get("end_anchor"), "end_payload": r.get("end_payload"),
            "duration_ms": (round(to_ms(r["end"]) - to_ms(r["start"]), 3) if r["start"] and r["end"] else None),
            "duration_is_lower_bound": r.get("end_anchor") == "own_last" and not r["is_last"],
            "events": sorted(r["events"]), "evidence": r["evidence"], "n_events": len(r["events"]), "n_errors": r["n_errors"],
            "n_soft": r["n_soft"], "n_warnings": r["n_warnings"], "status_texts": r["status_texts"],
        }

    def ser_split(sp):
        rec = sp["record"] or {}
        err = rec.get("error") if isinstance(rec.get("error"), dict) else None
        last = sp["runs"][-1] if sp["runs"] else None
        return {
            "split_id": sp["split_id"], "parent": sp.get("parent"), "parent_source": sp.get("parent_source"),
            "has_record": sp["record"] is not None, "record_file": rec.get("_file"), "folder": rec.get("_folder"),
            "wf_id": rec_wf_id(rec) or None, "wf_name": rec_wf_name(rec),
            "start": iso(sp.get("start")), "end": iso(sp.get("end")), "t0": rel(sp.get("start")), "t1": rel(sp.get("end")),
            "record_start": rec.get("start_time"), "record_end": rec.get("end_time"),
            "result": (rec.get("result").strip() if isinstance(rec.get("result"), str) else rec.get("result")),
            "status": rec.get("status"), "status_flag": _status_flag(rec.get("status")),
            "state": last["state"] if last else ("ok" if sp["record"] else "unknown"),
            "aborted": sp.get("aborted", False), "success": rec.get("success"),
            "error": err, "branch_pri": rec.get("branch_pri"),
            "subholds": rec.get("subholds") if isinstance(rec.get("subholds"), list) else (rec.get("splits") if isinstance(rec.get("splits"), dict) else None),
            "variables": rec.get("variables") if isinstance(rec.get("variables"), list) else None,
            "sources": rec.get("sources"), "retries": rec.get("retries"),
            "path": sp["path"], "runs": [r["run_id"] for r in sp["runs"]],
        }

    def ser_event(ev):
        return {
            "i": ev["i"], "created": ev["created"], "t": rel(ev["dt"]), "split_id": ev["split_id"], "node_id": ev["node_id"],
            "node_type": ev["node_type"], "event": ev["event"], "type": ev["type"], "host": ev["host"], "pid": ev["pid"],
            "linenum": ev["linenum"], "current_status": ev["current_status"], "user": ev["user"], "runame": ev["runame"],
            "context": ev["context"], "data": ev["data"], "run_id": ev_run.get(ev["i"]), "gap": ev_gap.get(ev["i"]),
            "benign": ev["type"] == "error" and (ev["node_type"] or "", ev["event"]) in BENIGN_ERRORS,
            "soft": ev["type"] == "error" and ev["event"] in SOFT_ERROR_EVENTS,
        }

    def ser_wf(wf):
        return {
            "wf_id": wf["wf_id"], "wf_name": wf["wf_name"], "wf_size": wf["wf_size"], "box_w": wf["box_w"], "box_h": wf["box_h"],
            "description": wf["description"], "updated": wf["updated"], "version": wf["version"], "file": wf["file"],
            "ghost": wf.get("ghost", False), "nodes": [dict(n) for n in wf["nodes"]],
        }

    sources = job_rec.get("sources") if isinstance(job_rec.get("sources"), dict) else {}
    hosts = sorted(set(str(ev["host"]) for ev in events if ev["host"]))
    n_err_events = sum(1 for ev in events if ev["type"] == "error")
    n_benign = sum(1 for ev in events if ev["type"] == "error" and (ev["node_type"] or "", ev["event"]) in BENIGN_ERRORS)
    model = {
        "generator": "ffas_runviz.py %s" % __version__,
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "job_dir": job_dir,
        "family_colors": FAMILY_COLORS,
        "job": {
            "job_id": job_rec.get("job_id") or os.path.basename(job_dir),
            "wf_id": main_wf_id,
            "wf_name": rec_wf_name(job_rec) or (workflows[main_wf_id]["wf_name"] if main_wf_id in workflows else None),
            "status": job_rec.get("status"),
            "start_time": iso(job_start), "end_time": iso(job_end), "start_source": start_source, "end_source": end_source,
            "duration_ms": (round(to_ms(job_end) - to_ms(job_start), 3) if job_start and job_end else None),
            "priority": job_rec.get("priority"), "log_level": job_rec.get("log_level"),
            "keep_all": job_rec.get("keep_all"), "keep_failed": job_rec.get("keep_failed"),
            "submit": job_rec.get("submit"), "log_path": job_rec.get("log_path"),
            "split_id": job_rec.get("split_id"), "build_version": job_rec.get("build_version"),
            "source": {
                "pretty_name": sources.get("pretty_name"), "original_file": sources.get("original_file"),
                "current_file": sources.get("current_file"), "localized_file": sources.get("localized_file"),
            },
            "hosts": hosts,
        },
        "main_wf_id": main_wf_id,
        "workflows": [ser_wf(wf) for wf in workflows.values()],
        "splits": [ser_split(splits[sid]) for sid in split_order],
        "runs": [ser_run(r) for r in runs],
        "events": [ser_event(ev) for ev in events],
        "edges": [{"wf_id": k[0], "from": k[1], "to": k[2], "splits": sorted(v, key=_split_sort_key)} for k, v in edges.items()],
        "jumps": uniq_jumps,
        "issues": issues,
        "anomalies": anomalies,
        "time_sinks": sinks,
        "time_breakdown": time_breakdown,
        "benign_errors": [[k[0], k[1], v] for k, v in BENIGN_ERRORS.items()],
        "cond_false_events": [[k[0], k[1]] for k in COND_FALSE_EVENTS],
        "soft_error_events": sorted(SOFT_ERROR_EVENTS),
        "summary": {
            "n_events": len(events), "n_error_events": n_err_events, "n_benign_events": n_benign,
            "n_splits": len(splits), "n_runs": len(runs), "n_issues": len(issues),
            "n_anomalies": sum(1 for a in anomalies if a["severity"] == "note"),
            "exact_timing": sum(1 for r in runs if r.get("start_anchor") == "node_start"),
            "n_fatal": sum(1 for x in issues if x["severity"] == "error"),
            "n_aborted": sum(1 for x in issues if x["severity"] == "aborted"),
            "n_cond_false": sum(1 for x in issues if x["severity"] == "cond_false"),
            "n_warn": sum(1 for x in issues if x["severity"] == "warn"),
            # a node can fail while the branch carries on through an "execute on error" connector,
            # so count the branches that actually ended badly separately
            "n_failed_branches": sum(1 for sp in splits.values() if sp["runs"] and sp["runs"][-1]["state"] == "error"),
            "n_aborted_branches": sum(1 for sp in splits.values() if sp["runs"] and sp["runs"][-1]["state"] == "aborted"),
            "n_nodes_run": len([1 for wf in workflows.values() for n in wf["nodes"] if n["n_runs"]]),
            "n_nodes": sum(len(wf["nodes"]) for wf in workflows.values()),
        },
        "warnings": warnings.items,
    }
    return model


# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------

def render_html(model, template_path=TEMPLATE_FILE):
    with open(template_path, "r", encoding="utf-8") as fh:
        template = fh.read()
    payload = json.dumps(model, ensure_ascii=False, separators=(",", ":"), default=str)
    payload = payload.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    title = "%s - %s" % (model["job"].get("wf_name") or "FFAStrans run", model["job"]["job_id"])
    html = template.replace("__RUNVIZ_TITLE__", title.replace("&", "&amp;").replace("<", "&lt;"))
    if "__RUNVIZ_DATA__" not in html:
        raise RuntimeError("template is missing the __RUNVIZ_DATA__ placeholder")
    return html.replace("__RUNVIZ_DATA__", payload)


def default_output(model, out_arg, multi):
    job_id = model["job"]["job_id"]
    name = "runviz_%s.html" % job_id
    if not out_arg:
        return os.path.abspath(name)
    if multi or os.path.isdir(out_arg) or out_arg.endswith(("/", "\\")):
        os.makedirs(out_arg, exist_ok=True)
        return os.path.join(out_arg, name)
    return out_arg


def is_job_dir(path):
    return (os.path.isfile(os.path.join(path, "full_log.json")) or os.path.isfile(os.path.join(path, ".json"))
            or os.path.isdir(os.path.join(path, "finished")) or os.path.isdir(os.path.join(path, "workflows")))


def expand_targets(args):
    """Accept job folders, files inside them, or a jobs root folder (.../db/cache/jobs) holding many jobs."""
    out = []
    for a in args:
        p = resolve_job_dir(a)
        if is_job_dir(p) or not os.path.isdir(p):
            out.append(p)
            continue
        subs = [os.path.join(p, d) for d in sorted(os.listdir(p)) if os.path.isdir(os.path.join(p, d))]
        jobs = [s for s in subs if is_job_dir(s)]
        if jobs:
            skipped = [os.path.basename(s) for s in subs if s not in jobs]
            print("%s: jobs root with %d job folders%s" % (
                p, len(jobs), ("; skipped %d without job files: %s" % (len(skipped), ", ".join(skipped[:5]) + (" ..." if len(skipped) > 5 else ""))) if skipped else ""),
                file=sys.stderr)
            out.extend(jobs)
        else:
            out.append(p)
    return out


INDEX_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FFAStrans runs</title>
<style>
:root{color-scheme:light dark;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--surface:#fcfcfb;--page:#f3f3f0;--hair:#e1e0d9;--accent:#2a78d6;--critical:#d03b3b;--warning:#b57a00;--good:#0ca30c}
@media (prefers-color-scheme:dark){:root{--ink:#fff;--ink2:#c3c2b7;--surface:#1a1a19;--page:#0d0d0d;--hair:#2c2c2a;--accent:#3987e5}}
body{margin:0;padding:16px;background:var(--page);color:var(--ink);font:13px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}
h1{font-size:18px;margin:0 0 10px} input{font:inherit;padding:4px 8px;border:1px solid var(--hair);border-radius:6px;background:var(--surface);color:inherit;min-width:260px}
table{border-collapse:collapse;width:100%;background:var(--surface);margin-top:10px} th,td{padding:5px 8px;border-bottom:1px solid var(--hair);text-align:left;vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);cursor:pointer;white-space:nowrap} td.n{text-align:right;font-variant-numeric:tabular-nums}
.mono{font-family:ui-monospace,Consolas,monospace;font-size:12px} .src{color:var(--ink2);font-size:12px;overflow-wrap:anywhere} a{color:var(--accent)}
.bad{color:var(--critical);font-weight:600} .cond{color:var(--warning)} .ok{color:var(--good)} .m{color:var(--muted)}
</style></head><body>
<h1>FFAStrans runs (__COUNT__ jobs)</h1>
<input id="q" type="search" placeholder="Filter by workflow, file, job id, status\u2026"> <span class="m" id="cnt"></span>
<table id="t"><thead><tr><th data-k="start">Started</th><th data-k="wf">Workflow</th><th>Source file</th><th data-k="status">Status</th><th data-k="dur" class="n">Duration</th><th data-k="splits" class="n">Splits</th><th data-k="runs" class="n">Node runs</th><th data-k="fatal" class="n">Node failures</th><th data-k="branches" class="n">Branches failed</th><th data-k="aborted" class="n">Aborted</th><th data-k="cond" class="n">Cond. false</th><th data-k="warn" class="n">Warnings</th><th>Job</th></tr></thead><tbody></tbody></table>
<p class="m">Generated __GENERATED__ by __GENERATOR__.</p>
<script id="idx" type="application/json">__ROWS__</script>
<script>
(function(){var R=JSON.parse(document.getElementById('idx').textContent),tb=document.querySelector('#t tbody'),q=document.getElementById('q'),sortK='start',dir=-1;
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function dur(ms){if(ms==null)return'\u2013';var s=ms/1000;if(s<60)return s.toFixed(1)+' s';var m=Math.floor(s/60);return m+'m '+Math.round(s-m*60)+'s'}
function render(){var f=q.value.trim().toLowerCase();var rows=R.filter(function(r){return!f||(r.wf+' '+r.src+' '+r.job+' '+r.status).toLowerCase().indexOf(f)>=0});
rows.sort(function(a,b){var x=a[sortK],y=b[sortK];if(x==null)x=-Infinity;if(y==null)y=-Infinity;return(x<y?-1:x>y?1:0)*dir});
tb.innerHTML=rows.map(function(r){var st=String(r.status).toLowerCase();var cls=r.fatal?'bad':(st==='finished'?'ok':'');return'<tr><td class="mono">'+esc((r.start||'').replace('T',' ').slice(0,19))+'</td><td>'+esc(r.wf)+'</td><td class="src">'+esc(r.src)+'</td><td class="'+cls+'">'+esc(r.status)+(r.fatal?' \u00b7 '+r.fatal+' failed':'')+'</td><td class="n">'+dur(r.dur)+'</td><td class="n">'+r.splits+'</td><td class="n">'+r.runs+'</td><td class="n '+(r.fatal?'bad':'')+'">'+r.fatal+'</td><td class="n '+(r.branches?'bad':'')+'">'+r.branches+'</td><td class="n">'+r.aborted+'</td><td class="n '+(r.cond?'cond':'')+'">'+r.cond+'</td><td class="n">'+r.warn+'</td><td><a class="mono" href="'+esc(r.file)+'">'+esc(r.job)+'</a></td></tr>'}).join('');
document.getElementById('cnt').textContent=rows.length+' of '+R.length}
q.addEventListener('input',render);document.querySelectorAll('th[data-k]').forEach(function(th){th.addEventListener('click',function(){var k=th.getAttribute('data-k');if(sortK===k)dir=-dir;else{sortK=k;dir=k==='start'?-1:1}render()})});render()})();
</script></body></html>
"""


def write_index(entries, out_dir):
    rows = []
    for e in entries:
        j, s = e["job"], e["summary"]
        rows.append({
            "file": e["file"], "job": j["job_id"], "wf": j.get("wf_name") or "?",
            "src": (j.get("source") or {}).get("original_file") or (j.get("source") or {}).get("pretty_name") or "",
            "status": j.get("status") or "?", "start": j.get("start_time"), "dur": j.get("duration_ms"),
            "splits": s["n_splits"], "runs": s["n_runs"], "fatal": s["n_fatal"], "aborted": s["n_aborted"],
            "branches": s.get("n_failed_branches", s["n_fatal"]), "cond": s["n_cond_false"], "warn": s["n_warn"],
        })
    payload = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c")
    html = (INDEX_HTML.replace("__COUNT__", str(len(rows))).replace("__ROWS__", payload)
            .replace("__GENERATED__", datetime.now().astimezone().isoformat(timespec="seconds"))
            .replace("__GENERATOR__", "ffas_runviz.py " + __version__))
    path = os.path.join(out_dir, "index.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render an FFAStrans job folder as an interactive HTML run visualization.")
    ap.add_argument("job", nargs="+", help="job folder(s) (.../Processors/db/cache/jobs/<job_id>), a file inside one, or the jobs root folder to render every job")
    ap.add_argument("-o", "--output", help="output .html file (single job) or directory (several jobs; an index.html is written too)")
    ap.add_argument("--wf-dir", action="append", default=[],
                    help="extra folder with workflow .json files (e.g. Processors/db/cache/wfs) used when the job has no workflows/ copy")
    ap.add_argument("--open", action="store_true", help="open the result in the default browser")
    ap.add_argument("--json", action="store_true", help="also write the extracted model next to the html (for debugging)")
    ap.add_argument("--template", default=TEMPLATE_FILE, help=argparse.SUPPRESS)
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)

    if not os.path.isfile(args.template):
        print("error: template not found: %s" % args.template, file=sys.stderr)
        return 2

    rc = 0
    targets = expand_targets(args.job)
    multi = len(targets) > 1
    entries = []
    out_dir = None
    for job_dir in targets:
        if not os.path.isdir(job_dir):
            print("error: not a folder: %s" % job_dir, file=sys.stderr)
            rc = 1
            continue
        try:
            model = build_model(job_dir, args.wf_dir)
            html = render_html(model, args.template)
        except Exception as exc:
            print("error: %s: %s" % (job_dir, exc), file=sys.stderr)
            rc = 1
            continue
        out = default_output(model, args.output, multi)
        out_dir = os.path.dirname(os.path.abspath(out))
        os.makedirs(out_dir, exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(html)
        if args.json:
            with open(os.path.splitext(out)[0] + ".json", "w", encoding="utf-8") as fh:
                json.dump(model, fh, ensure_ascii=False, indent=1, default=str)
        entries.append({"file": os.path.basename(out), "job": model["job"], "summary": model["summary"]})
        s = model["summary"]
        j = model["job"]
        dur = j["duration_ms"]
        print("%s -> %s  [%s | %s | %s | %d splits, %d node runs, %d events | %d node failures (%d branches), %d aborted, %d cond. false, %d warnings%s]" % (
            os.path.basename(job_dir.rstrip("\\/")), out, j.get("wf_name") or "?", j.get("status") or "?",
            ("%.1f s" % (dur / 1000.0)) if dur is not None else "duration ?",
            s["n_splits"], s["n_runs"], s["n_events"], s["n_fatal"], s.get("n_failed_branches", 0),
            s["n_aborted"], s["n_cond_false"], s["n_warn"],
            (" | %d generator warnings" % len(model["warnings"])) if model["warnings"] else ""))
        if args.open and not multi:
            webbrowser.open("file:///" + os.path.abspath(out).replace("\\", "/"))
    if multi and entries and out_dir:
        idx = write_index(entries, out_dir)
        print("index -> %s" % idx)
        if args.open:
            webbrowser.open("file:///" + os.path.abspath(idx).replace("\\", "/"))
    return rc


if __name__ == "__main__":
    sys.exit(main())

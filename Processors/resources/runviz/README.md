# FFAStrans run visualizer (`ffas_runviz.py`)

Turns one FFAStrans job folder into a single, self-contained HTML page that shows the run on top of the workflow
canvas: which nodes ran, in which order and branch (split), how long each took, where it failed, and the log entries
behind every node.

Works with job folders from **FFAStrans 1.4.x and 1.5.x** (see *Version differences* below).
No third-party packages are needed. Python 3.8 or newer.

## Usage

```
python tools/runviz/ffas_runviz.py <job_folder> [-o out.html] [--open]
python tools/runviz/ffas_runviz.py <job_folder_1> <job_folder_2> ... -o <out_dir>
python tools/runviz/ffas_runviz.py Processors/db/cache/jobs -o <out_dir>       # every job + index.html
```

A job folder is `Processors/db/cache/jobs/<job_id>/`. You can also point at any file inside it
(for example `full_log.json`), or at the jobs root to render every job at once. The folder is expected to contain:

| File / folder        | Used for                                                                  |
|----------------------|---------------------------------------------------------------------------|
| `.json`              | job record: workflow id/name, status, start and end time, source file     |
| `full_log.json`      | the log: one entry per node action (`trace`, `error`, `warning`, `sys`)   |
| `finished/*.json`    | one record per finished split (branch): node path, result, error message  |
| `workflows/*.json`   | the workflow definition(s) the job ran, with node positions               |
| `sys/` (1.4.x)       | ignored                                                                   |

Missing pieces degrade gracefully (a warning is printed and shown on the page). If the job folder has no
`workflows/` copy, pass `--wf-dir Processors/db/cache/wfs` (or any folder holding workflow `.json` files).

Options:

| Option          | Meaning                                                                                  |
|-----------------|------------------------------------------------------------------------------------------|
| `-o PATH`       | output file (single job) or directory (several jobs). Default: `./runviz_<job_id>.html`   |
| `--open`        | open the page (or the index) in the default browser                                      |
| `--json`        | also write the extracted model next to the page (`runviz_<job_id>.json`) for debugging   |
| `--wf-dir DIR`  | extra folder with workflow `.json` files; may be repeated                                 |

When several jobs are rendered into a directory an `index.html` is written with one sortable, filterable row per job
(failed branches, aborted, conditions false, warnings).

## What the page shows

* **Canvas** - the workflow exactly as laid out in the FFAStrans editor: same node positions, box size
  (`variable.wf_size`, aspect 1.6), title bar, family colour bar, in/out connectors (green = execute on success,
  red = on error, yellow = on any), description area, straight connection lines and the editor grid. Nodes that did
  not run are dimmed. Nodes that ran carry a badge inside the lower part of the node: the run result as an icon and
  colour, plus the time spent in them (`xN` when a node ran in several splits, `>=` when the figure is a lower
  bound). The outline around a node marks the selection, nothing else. The path the job took is drawn as thin glowing
  blue lines. Selecting a node brightens every route that led into it, starting at the job's first node and following the parent
  splits, and stops at the node; a node reached by several branches shows all of them. Selecting one run shows only
  that run's route, and selecting a split keeps its whole branch. Everything else the job traversed is dimmed. Sub-workflows get their own tab. The page opens fitted to the nodes that ran; drag to pan,
  wheel to zoom, `F` fits everything, `R` fits the run. Clicking a node never moves the canvas; selecting one from
  the panel or the timeline pans only if it is off-screen, by the smallest amount and without changing the zoom, so
  the view never jumps under you. Selecting a node also focuses its log. A node with one run opens that run, just like its timeline bar; a node with several runs
  shows their combined log, with run cards to select an individual run. Double-click a workflow node to open its
  referenced workflow tab when that workflow is included in the report. Tabs follow each workflow's earliest
  timestamped log entry; workflows without timestamped entries follow afterward, with log order breaking ties.
* **Panel** (right) - the run overview: issues grouped into *branches that ended in error*, *aborted by user*,
  *conditionals that evaluated false* and *logged errors the job carried on from*, each card with the recorded message,
  where it came from, and the error entries of that run. Then the split tree and the full log. Click a node, a split,
  a timeline bar or an issue card to see its details and only its log entries. Every log entry expands to its payload
  (ffprobe JSON, AviSynth script, ffmpeg report, command line, ...). The filter box searches inside payloads too.
  The `?` button in the header explains the terms.
* **Timeline** (bottom) - one bar per node run, grouped by split in start order, on the job's time axis. Ticks mark
  error entries (red), probe errors and warnings (orange) and the last entry before a branch died (dashed).

Summary stats sit on the right side of the header. The *Node failures*, *Aborted*, *Cond. false*, *Warnings* and
*Anomalies* tiles are navigators: each click opens the next item of that kind and reveals the log entry behind it.
Drag the divider between canvas and overview to change their widths, or the divider above the timeline to change
its height. The dividers also work with arrow keys when focused (`Shift` for larger steps). On narrow screens the
canvas and overview stack, and their divider adjusts their heights.

### Finding errors and anomalies

* **Issues** are the failures: nodes that failed, branches aborted, conditionals that evaluated false, probe errors
  the job carried on from. **Anomalies** are the things that are not failures but usually explain a slow or odd run:
  waits in `_WaitForResources`, long queue or dispatch gaps between nodes or between a parent split and its child,
  nodes that ran several times in one split, retried tickets, splits without a record, runs that logged nothing, and
  (1.4.x) a `node start` without a `node end`, which means the node process died. Holds and silent runs are listed
  under "expected but time-consuming" so they do not drown the real ones.
* **Where the time went**: how much of the job had a node running versus nothing running (queueing, dispatch, holds
  between tickets), time inside nodes by family, and the longest node runs. Click a run to open it.
* **Timeline**: waiting inside a run (hold, resources) and queue time before a run are hatched, so a long bar that
  is mostly hatched was idle, not working. `Ctrl`+wheel zooms the time axis around the pointer, double-click resets,
  and *Fit split* zooms to the selected split. Hovering a bar or a card lights up the node on the canvas.
* **Log list**: *Errors only* keeps error and warning entries plus the last entry of a failed run; *Slow steps* keeps
  entries that came 1 s or more after the previous entry of their run, which is the end of every silence (encoding,
  a probe, a hold). The Δ column is that gap. Inside an expanded payload, lines that look like an error are
  highlighted and the pane scrolls to the first one; the filter text is marked too.
* **Keyboard**: `n` / `p` step through the flagged entries of the list on screen (errors, warnings, last-before-death,
  slow steps), `/` focuses the filter, `F` / `R` fit the canvas, `Esc` goes back to the overview.
* **Copy summary** (overview) puts a plain-text digest of the run on the clipboard: outcome, issues with messages,
  anomalies, longest runs and the job folder, ready for a ticket or a forum post. **Copy link** copies a deep link to
  the current selection.

Deep links: `#node=<node id>`, `#split=<split id>`, `#run=<split id>|<node id>|<seq>`, `&ev=<entry index>` to open
one log entry, optionally `&wf=<wf id>` and `&fit=run` / `&fit=all`. The URL hash follows your selection, so a link
can be pasted into a bug report.

## How the run is reconstructed

FFAStrans does not log "node started / node finished". The page derives them:

* **Node runs** come from each split record's `path` (the nodes the ticket visited, with the split id at every
  step). Log entries are attached by `(split_id, node id)`; node names come from the workflow definition. Nodes that
  appear only in the log (no record yet) are added in log order. Entries without a node (`sys`) are attached to the
  run whose time span contains them. When the log has `node start` / `node end` entries (1.4.x) those define the runs
  instead, so repeated visits to the same node are separate runs and path nodes that never started are still shown.
* **Timing (1.4.x)** - `node start` to `node end`, the node's own execution time. The gap until the next node of the
  split starts is reported in the run card rather than folded into the duration.
* **Timing (1.5.x)** - a run starts at its first log entry and ends when the next node of the same split writes its first
  entry; the last node of a split ends at the split's recorded `end_time`. Encoders log their last entry before the
  encode starts, so the encode time is counted for the encoder, which is what you want. Nodes that only log when they
  are done (`conditional`, `populate_variable`) start at the previous node's last entry instead, so a Conditional after
  an analyser gets its own evaluation time. When the next node logged nothing at all, the run ends at its own last
  entry and the duration is shown as a lower bound (`>=`). Each run card names its start and end anchors, the longest
  gap between its entries, and the time after its last entry until the next node took over.
* **Result per run**
  * `Error` - the node's `node end` entry reports an error (1.4.x), an error entry written with `_setlog_error`
    (anything except the media probes and the op_cond "nothing to evaluate" entry), or the split ended at this
    node with `result: error` or an error message in the record. A failed node does not always end the branch:
    an "execute on error / any" connector can carry it on, and the card says so. FFAStrans writes
    `result: Success` next to an error message when only the message was set (validation errors leave the error code
    empty); the page says so explicitly instead of showing the two side by side.
  * `Aborted` - the record says `result: abort`, carries status flag 2, or an abort error code (995 in 1.5.x, 2 in
    1.4.x); in 1.4.x the aborted node is named by its own `node end` payload. The user stopped the job; the node did
    not fail. Counted separately from failures.
  * `Condition false` - an `op_cond` whose condition evaluated false (`conditioner` error, code -1). The branch stops
    there by design, so it is shown in yellow rather than red.
  * `Warning (carried on)` - error or warning entries were logged, but the branch went on. ffprobe / mediainfo /
    exiftool probe errors are written with `_setlog_error_only` and never fail a branch; they are shown in orange and
    listed inside the card of the run they belong to. The op_cond "nothing was evaluated" entry is informational.
  * `OK` / `Did not run` / `Unknown` (seen in the log only, no record yet).
* **Issues** - one card per run that failed, was aborted, stopped on a false condition, or logged errors and carried
  on. *Node failures* counts runs, not error entries; the tile also says how many branches actually ended.
  The message is taken from the split record, the `node end` payload or the log entry, whichever is the real source,
  and the card says which one it used.
* **Splits** - the parent of a split is the split of the path entry right before its first own node (`1-17-17`
  branches into `11-0-0`, `12-0-0`, `13-0-0`), or the recorded ancestry (`splits.parent` in 1.4.x). A split without a
  record yet (still running) gets its parent from the id scheme (`121-0-0` -> `12-0-0`), marked "derived from id".
  Node ids are not unique across workflows (copied workflows keep them), so each path entry's `wf_id` decides which
  canvas a node belongs to.
* **Job start** - from the job record; when a manually submitted job has none, the submit time is used and a warning
  says so.

## Version differences (1.4.x vs 1.5.x)

Both layouts are read by the same code; the page adapts to what the data offers.

| | FFAStrans 1.4.x | FFAStrans 1.5.x |
|---|---|---|
| Job record | `workflow: {id, name, path}` | `wf_id`, `wf_name` |
| Path entry | `split`, plus a node `index` | `split_id` |
| Run boundaries | `node start` / `node end` entries in the log | none; boundaries are derived |
| Per-run outcome | the `node end` payload (`{status, code, error}`) | only the split record |
| Error message | usually in the entry's `current_status`, payload empty | usually in the entry's payload |
| Abort | `error.code` 2, `result` "abort", status flag 2 | `error.code` 995 |
| Branch ancestry | `splits.parent` (`\1-0-0\112-0-2`) | `subholds[].parent` |
| Branching | the parent split carries on along the first outbound; extra outbounds get child splits (`112-2-1`) | the parent split ends at the branching node; every outbound gets a child split (`11-0-0`, `12-0-0`, ...) |
| Files | JSON with a UTF-8 BOM, `sys/` folder present | JSON without BOM |

Custom (plugin) nodes only carry a guid in the workflow file. When the job folder sits inside an FFAStrans
install (`<install>/processors/db/cache/jobs/<id>`), the tool reads `<install>/processors/plugin_nodes/custom_nodes/*/node.json`
to give them their real name and family colour; otherwise they are drawn grey as "Plugin node".

Because 1.4.x logs real run boundaries, its durations are the node's **actual execution time** and the wait before
the next node starts is reported separately; the same node may legitimately appear several times in one split.
For 1.5.x the durations are reconstructed (see below) and the page says so in the `?` help.

A 1.4.x node can fail while the branch continues through an "execute on error" connector, so the page counts
**node failures** and **branches that ended** separately.

## Notes and limits

* Times come from the log's `created` stamps and the records' `end_time`; clock skew between hosts is not corrected.
  Stamps without a timezone offset are read in the job's offset; unreadable stamps keep their file position.
* If a split visits the same node twice, the log entries are attached to the first visit (a warning is printed).
* Plugin (custom) nodes are drawn with a neutral colour when their type is not one of the built-in node types.
* The page is plain HTML/CSS/JS with the run data embedded as JSON; it works from `file://` and needs no server.

"""Re-collect check fields (and results if missing) for finished Stage 2 runs without solving."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "stage1"))
import baseline as B
sys.modules.setdefault("baseline", B)
import stage2_runs, stage2_contact_runs  # noqa
for rid in sys.argv[1:]:
    run = B.RUN_BY_ID[rid]; outdir = B.RESULTS / rid; f = outdir / "record.json"
    if not f.exists():
        print(rid, "no record"); continue
    rec = json.loads(f.read_text())
    rec["check"] = B._check_files(outdir, len(run["temps"]))
    if not rec.get("ok"):
        try:
            rec["result"] = B.contact_result(run, outdir) if run.get("kind") == "contact" else B.u_history(run, outdir); rec["ok"] = True
        except Exception as exc:
            rec["error"] = f"{type(exc).__name__}: {exc}"
    f.write_text(json.dumps(rec, indent=1, default=float))
    print(rid, "all_ok", rec["check"]["all_ok"], "errors", rec["check"]["n_error_messages"], "ok", rec["ok"])

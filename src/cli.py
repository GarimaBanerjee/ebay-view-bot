import argparse, sys
from rich import print
from pathlib import Path

from ingest_reports import ingest_report, summarize, save_csv as save_ingest
from seo_audit import audit_titles, merge_audit
from rank_check import snapshot as rank_snapshot, save_csv as save_rank
from price_watch import watch as watch_prices
from src_alerts.alerts import notify_all

def cmd_ingest(args):
    df = ingest_report(args.path)
    out = summarize(df) if args.summarize else df
    save_ingest(out, args.out)
    print(f"[green]Wrote {args.out}[/] rows={len(out)}")

def cmd_audit(args):
    perf = ingest_report(args.input)
    titles = audit_titles(perf, primary_kw=args.keyword)
    merged = merge_audit(perf, titles)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.out, index=False)
    print(f"[green]Wrote {args.out}[/] rows={len(merged)}")

def cmd_rank(args):
    df = rank_snapshot(args.keyword, args.market, args.limit)
    save_rank(df, args.out)
    print(f"[green]Wrote {args.out}[/] rows={len(df)}")

def cmd_watch(args):
    out = watch_prices(args.list, args.out)
    print(f"[green]Wrote {args.out}[/] rows={len(out)}")

def cmd_alerts(args):
    subject = args.subject
    body = Path(args.body).read_text(encoding="utf-8") if Path(args.body).exists() else args.body
    notify_all(subject, body)
    print("[green]Alerts sent (where configured).[/]")

def build_parser():
    p =

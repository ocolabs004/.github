#!/usr/bin/env python3
"""ocolabs 조직 전체 레포에 표준 이슈 라벨을 동기화한다.

- 매니페스트(labels/standard-labels.json)를 SSOT로 사용.
- 비파괴: rename(기본/변형 라벨 → 표준명, 대상 라벨이 없을 때만, 이슈 연결 보존)
  + 누락 표준 라벨 생성 + 색/설명 통일. 프로젝트 전용 라벨은 건드리지 않는다.
- 비보관(non-archived) org 레포 전체를 동적으로 대상화 → 신규 레포 자동 포함.

사용:
  python3 scripts/sync-labels.py            # dry-run (변경 없음)
  python3 scripts/sync-labels.py --apply    # 실제 적용
환경: gh CLI + GH_TOKEN(org 레포 라벨 쓰기 권한: classic repo / fine-grained Issues:write).
"""
import json, os, subprocess, sys, pathlib

OWNER = os.environ.get("ORG", "ocolabs004")
ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / "labels" / "standard-labels.json").read_text(encoding="utf-8"))
CANON = {l["name"]: (l["color"], l["description"]) for l in MANIFEST["labels"]}
ORDER = [l["name"] for l in MANIFEST["labels"]]
RENAME = MANIFEST.get("rename", {})
EXCLUDE = set(MANIFEST.get("exclude_repos", []))


def run(args):
    return subprocess.run(args, capture_output=True, text=True)


def all_repos():
    r = run(["gh", "repo", "list", OWNER, "--no-archived", "--limit", "1000",
             "--json", "name"])
    r.check_returncode()
    return [x["name"] for x in json.loads(r.stdout) if x["name"] not in EXCLUDE]


def labels(repo):
    r = run(["gh", "label", "list", "-R", f"{OWNER}/{repo}", "--limit", "200",
             "--json", "name,color,description"])
    if r.returncode != 0:
        return None
    return {x["name"]: x for x in json.loads(r.stdout)}


def main():
    apply = "--apply" in sys.argv
    repos = all_repos()
    print(f"대상 레포: {len(repos)} (apply={apply})")
    tot_r = tot_c = tot_u = 0
    fails = []  # (repo, op, stderr) — 실패를 수집해 run 종료 코드에 반영
    for repo in repos:
        cur = labels(repo)
        if cur is None:
            print(f"  ! {repo}: label list 실패(skip)")
            continue
        names = set(cur.keys())
        plan_rename = []
        for src, dst in RENAME.items():
            if src in names and dst not in names:
                plan_rename.append((src, dst))
                names.discard(src); names.add(dst)
        creates, updates = [], []
        for n in ORDER:
            color, desc = CANON[n]
            if n in names:
                ex = cur.get(n)
                if not ex or ex.get("color", "").upper() != color.upper() or (ex.get("description") or "") != desc:
                    updates.append(n)
            else:
                creates.append(n)
        if not (plan_rename or creates or updates):
            continue
        print(f"  {repo}: rename {len(plan_rename)} / create {len(creates)} / update {len(updates)}")
        tot_r += len(plan_rename); tot_c += len(creates); tot_u += len(updates)
        if not apply:
            continue

        def attempt(op, args):
            r = run(args)
            if r.returncode != 0:
                fails.append((repo, op, (r.stderr or "").strip()))

        for src, dst in plan_rename:
            color, desc = CANON[dst]
            attempt(f"rename {src}→{dst}",
                    ["gh", "label", "edit", src, "-R", f"{OWNER}/{repo}",
                     "--name", dst, "--color", color, "--description", desc])
        for n in creates:
            color, desc = CANON[n]
            attempt(f"create {n}",
                    ["gh", "label", "create", n, "-R", f"{OWNER}/{repo}",
                     "--color", color, "--description", desc, "--force"])
        for n in updates:
            color, desc = CANON[n]
            attempt(f"update {n}",
                    ["gh", "label", "edit", n, "-R", f"{OWNER}/{repo}",
                     "--color", color, "--description", desc])
    print(f"합계: rename {tot_r} / create {tot_c} / update {tot_u}")
    if fails:
        print(f"\n실패 {len(fails)}건 (워크플로 실패 처리):")
        for repo, op, err in fails:
            print(f"  ! {repo}: {op} — {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()

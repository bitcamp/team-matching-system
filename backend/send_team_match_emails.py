#!/usr/bin/env python3
"""Send team match emails to members listed in matches.json via AWS SES.

Usage examples:
  python send_team_match_emails.py --source "Bitcamp <hello@bit.camp>" --dry-run
  python send_team_match_emails.py --source "Bitcamp <hello@bit.camp>" --send

By default, the script runs in dry-run mode to avoid accidental sends.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import boto3
from botocore.exceptions import BotoCoreError, ClientError


@dataclass(frozen=True)
class TeamMember:
    name: str
    email: str


@dataclass(frozen=True)
class TeamAssignment:
    team_id: str
    members: list[TeamMember]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send team assignment emails from matches.json via AWS SES"
    )
    parser.add_argument(
        "--matches-file",
        default="matches.json",
        help="Path to matches JSON file (default: matches.json)",
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region for SES (default: us-east-1)",
    )
    parser.add_argument(
        "--source",
        default=os.getenv("TEAM_MATCH_EMAIL_SOURCE", ""),
        help="SES verified source email/name, e.g. 'Bitcamp <hello@bit.camp>'",
    )
    parser.add_argument(
        "--reply-to",
        default=os.getenv("TEAM_MATCH_EMAIL_REPLY_TO", ""),
        help="Optional reply-to address",
    )
    parser.add_argument(
        "--subject",
        default="Bitcamp Team Match: Your Team Has Been Decided",
        help="Email subject line",
    )
    parser.add_argument(
        "--sleep-ms",
        type=int,
        default=120,
        help="Milliseconds to sleep between sends (default: 120)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only process the first N recipients (default: all)",
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--send",
        action="store_true",
        help="Actually send emails",
    )
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview output without sending (default mode)",
    )

    args = parser.parse_args()
    if not args.send and not args.dry_run:
        args.dry_run = True

    if not args.source:
        parser.error(
            "--source is required (or set TEAM_MATCH_EMAIL_SOURCE environment variable)."
        )

    if args.sleep_ms < 0:
        parser.error("--sleep-ms must be >= 0")

    if args.limit < 0:
        parser.error("--limit must be >= 0")

    return args


def load_assignments(path: Path) -> list[TeamAssignment]:
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    teams_raw = raw.get("Teams")
    if not isinstance(teams_raw, list):
        raise ValueError("Invalid matches JSON: expected top-level 'Teams' array")

    assignments: list[TeamAssignment] = []
    for team_obj in teams_raw:
        if not isinstance(team_obj, dict) or len(team_obj) != 1:
            continue

        team_id = next(iter(team_obj))
        members_raw = team_obj.get(team_id)
        if not isinstance(members_raw, list):
            continue

        members: list[TeamMember] = []
        for row in members_raw:
            if not (isinstance(row, list) and len(row) >= 2):
                continue
            name = str(row[0]).strip()
            email = str(row[1]).strip()
            if not name or "@" not in email:
                continue
            members.append(TeamMember(name=name, email=email))

        if members:
            assignments.append(TeamAssignment(team_id=team_id, members=members))

    return assignments


def first_name(full_name: str) -> str:
    parts = full_name.strip().split()
    return parts[0] if parts else "there"


def team_member_block(members: Iterable[TeamMember]) -> str:
    return "\n".join(f"- {m.name} ({m.email})" for m in members)


def build_email_text(assignment: TeamAssignment, recipient: TeamMember) -> str:
    teammates = [m for m in assignment.members if m.email.lower() != recipient.email.lower()]
    teammate_count = len(teammates)

    if teammate_count:
        teammate_section = team_member_block(teammates)
    else:
        teammate_section = "- No teammates were assigned yet."

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return (
        f"Hi {first_name(recipient.name)},\n\n"
        "The Bitcamp organizing team has finalized team matching, and your team has been decided!\n\n"
        "These matches are meant to help you get started, but they are ultimately up to you to keep. "
        "If you feel another participant is a better fit for your goals, interests, or working style, "
        "you are welcome to connect with others and form your preferred team.\n\n"
        f"Team size: {len(assignment.members)}\n\n"
        "Your full team:\n"
        f"{team_member_block(assignment.members)}\n\n"
        "Your teammates:\n"
        f"{teammate_section}\n\n"
        "Suggested next steps:\n"
        "1. Reach out to your teammates and set up a group chat.\n"
        "2. Align on project idea, scope, and responsibilities.\n"
        "3. Share availability and schedule your first planning session.\n\n"
        "If you think there is an issue with your assignment, reply to this email and we will review it.\n\n"
        "Disclaimer: We tried our best to match participants with similar interests, goals, and preferences.\n\n"
        "See you at Bitcamp!\n"
        "- The Bitcamp Organizing Team\n\n"
    )


def send_email(
    ses_client,
    source: str,
    recipient: TeamMember,
    subject: str,
    body_text: str,
    reply_to: str = "",
) -> str:
    message = {
        "Subject": {"Data": subject, "Charset": "UTF-8"},
        "Body": {"Text": {"Data": body_text, "Charset": "UTF-8"}},
    }

    kwargs = {
        "Source": source,
        "Destination": {"ToAddresses": [recipient.email]},
        "Message": message,
    }

    if reply_to:
        kwargs["ReplyToAddresses"] = [reply_to]

    response = ses_client.send_email(**kwargs)
    return response.get("MessageId", "")


def main() -> int:
    args = parse_args()
    matches_path = Path(args.matches_file)

    if not matches_path.exists():
        raise FileNotFoundError(f"matches file not found: {matches_path}")

    assignments = load_assignments(matches_path)
    if not assignments:
        print("No valid teams found. Nothing to send.")
        return 0

    recipients: list[tuple[TeamAssignment, TeamMember]] = []
    for assignment in assignments:
        for member in assignment.members:
            recipients.append((assignment, member))

    if args.limit:
        recipients = recipients[: args.limit]

    ses = boto3.client("ses", region_name=args.region)

    sent = 0
    failed = 0

    print(
        f"Mode={'DRY_RUN' if args.dry_run else 'SEND'} | "
        f"teams={len(assignments)} | recipients={len(recipients)}"
    )

    for assignment, recipient in recipients:
        body_text = build_email_text(assignment, recipient)

        if args.dry_run:
            print("-" * 80)
            print(f"[DRY RUN] To: {recipient.name} <{recipient.email}> | Team: {assignment.team_id}")
            print(body_text)
            sent += 1
            continue

        try:
            message_id = send_email(
                ses_client=ses,
                source=args.source,
                recipient=recipient,
                subject=args.subject,
                body_text=body_text,
                reply_to=args.reply_to,
            )
            print(
                f"[SENT] To: {recipient.name} <{recipient.email}> | "
                f"Team: {assignment.team_id} | MessageId: {message_id}"
            )
            sent += 1
        except (ClientError, BotoCoreError) as exc:
            print(
                f"[FAILED] To: {recipient.name} <{recipient.email}> | "
                f"Team: {assignment.team_id} | Error: {exc}"
            )
            failed += 1

        if args.sleep_ms:
            time.sleep(args.sleep_ms / 1000.0)

    print("=" * 80)
    print(f"Done. success={sent} failed={failed} total={len(recipients)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

import json
import os
import sys

# Avoid importing vendored package folders from this directory (e.g. backend/numpy),
# which can shadow the active environment and break binary imports.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path[:] = [p for p in sys.path if os.path.abspath(p or os.getcwd()) != CURRENT_DIR]

import numpy as np
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
from sklearn.metrics.pairwise import cosine_similarity

TARGET_TEAM_SIZE = 4


def normalize_team_size(value):
    if isinstance(value, Decimal):
        value = int(value)

    if isinstance(value, str):
        mapping = {"one": 1, "two": 2, "three": 3, "four": 4}
        lowered = value.strip().lower()
        if lowered in mapping:
            value = mapping[lowered]
        elif lowered.isdigit():
            value = int(lowered)
        else:
            return 1

    if not isinstance(value, int):
        return 1

    return max(1, min(TARGET_TEAM_SIZE, value))


# Fetch data from DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
TEAM_MATCHING_TABLE = os.getenv('TEAM_MATCHING_TABLE', 'portal-prd-team-matching')
REGISTRATION_TABLE = os.getenv('REGISTRATION_TABLE', 'portal-prd-registration')
WAITLIST_FIELD = os.getenv('WAITLIST_FIELD', 'waitlist')

team_matching_table = dynamodb.Table(TEAM_MATCHING_TABLE)
registration_table = dynamodb.Table(REGISTRATION_TABLE)


def fetch_waitlist_by_email():
    waitlist_by_email = {}
    try:
        response = registration_table.scan(
            ProjectionExpression='email, #waitlist',
            ExpressionAttributeNames={'#waitlist': WAITLIST_FIELD}
        )
        items = response['Items']
        while 'LastEvaluatedKey' in response:
            response = registration_table.scan(
                ProjectionExpression='email, #waitlist',
                ExpressionAttributeNames={'#waitlist': WAITLIST_FIELD},
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response['Items'])

        for item in items:
            email = item.get('email')
            if not email:
                continue
            waitlist_by_email[email.lower()] = bool(item.get(WAITLIST_FIELD, False))

        return waitlist_by_email
    except ClientError as e:
        print(f"Error fetching waitlist data from registration table: {e}")
        return {}

def fetch_teams(): 
    try:
        waitlist_by_email = fetch_waitlist_by_email()

        response = team_matching_table.scan()
        items = response['Items']
        while 'LastEvaluatedKey' in response:
            response = team_matching_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        teams = {}
        for item in items:
            email = item.get('email')
            if not email:
                continue
            first_name = item.get('first_name', '').strip()
            last_name = item.get('last_name', '').strip()
            display_name = f"{first_name} {last_name}".strip() or email
            team_size = item.get('num_team_members', 0)
            team_size = normalize_team_size(team_size)
            skills = item.get('languages', [])
            if isinstance(skills, str):
                skills = [skills] if skills else []
            skills_wanted = item.get('skills_wanted', [])
            if isinstance(skills_wanted, str):
                skills_wanted = [skills_wanted] if skills_wanted else []
            projects = item.get('projects', [])
            if isinstance(projects, str):
                projects = [projects] if projects else []
            prizes = item.get('prizes', [])
            if isinstance(prizes, str):
                prizes = [prizes] if prizes else []
            working_preferences = item.get('working_preferences', ['In-person'])
            if isinstance(working_preferences, str):
                working_preferences = [working_preferences] if working_preferences else ['In-person']
            is_waitlisted = waitlist_by_email.get(email.lower(), False)
            teams[email] = {
                "name": display_name,
                "team_size": team_size,
                "email": email,
                "primary_track": item.get('track', 'N/A'),
                "skills": skills,
                "skills_wanted": skills_wanted,
                "avg_skill_level": item.get('skill_level', 'N/A'),
                "projects": projects,
                "prizes": prizes,
                "working_preferences": working_preferences,
                "commitment": item.get('commitment', 'I want to win'),
                "team_size": team_size,
                "is_waitlisted": is_waitlisted,
            }
        return teams
    except ClientError as e:
        print(f"Error fetching data from DynamoDB: {e}")
        return {}

# Encoding helpers
def convert_skill_level(skill_level):
    skill_map = {'Beginner': 1, 'Intermediate': 3, 'Advanced': 5, 'N/A': 3}
    return skill_map.get(skill_level, 3)

def encode_skills(skills_list, all_possible_skills):
    skill_vectors = []
    for skills in skills_list:
        skill_vector = [1 if skill in skills else 0 for skill in all_possible_skills]
        skill_vectors.append(skill_vector)
    return np.array(skill_vectors)

def encode_categorical(categories_list):
    all_cats = sorted(set(x for sublist in categories_list for x in sublist))
    matrix = []
    for cat_list in categories_list:
        row = [1 if cat in cat_list else 0 for cat in all_cats]
        matrix.append(row)
    return np.array(matrix)

def get_similarity_matrix(features):
    return cosine_similarity(features)

# Match scoring
def get_combined_match_score(i, j, skills_weight=0.7, general_similarity_weight=0.6):
    skill_match_score = skills_match_sim[i][j]
    general_similarity = (
        primary_track_sim[i][j] * 0.45 +
        avg_skill_sim[i][j] * 0.45 +
        project_sim[i][j] * 0.6 +
        prize_sim[i][j] * 0.5 +
        working_pref_sim[i][j] * 0.4 +
        commitment_sim[i][j] * 0.5
    )
    return skill_match_score * skills_weight + general_similarity * general_similarity_weight

# Get top matches
def get_top_matches(team_index, top_n=None):
    if top_n is None:
        top_n = len(teams) - 1
    team_email = team_ids[team_index]
    team_size = normalize_team_size(teams[team_email]["team_size"])
    match_scores = []
    compatible_indices = [
        i for i in range(len(teams))
        if i != team_index and
        team_size + normalize_team_size(teams[team_ids[i]]["team_size"]) <= TARGET_TEAM_SIZE
    ]
    for i in compatible_indices:
        if i != team_index:
            score = get_combined_match_score(team_index, i)
            match_email = team_ids[i]
            team_info = {
                "name": teams[match_email]["name"],
                "email": match_email,
                "score": float(score),  # Ensure float for JSON
                "info": dict(teams[match_email])
            }
            match_scores.append(team_info)
    return sorted(match_scores, key=lambda x: x["score"], reverse=True)[:top_n]

# Custom serialization function for JSON
def json_serializable(obj):
    if isinstance(obj, set):
        return list(obj)  # Convert sets to lists
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)  # Convert NumPy floats to Python floats
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)  # Convert Decimal to int or float
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

def form_team(name, email, teammates_count, matches):
    global visited

    if (name, email) in visited:
        return []

    team = []
    current_team_size = normalize_team_size(teammates_count)

    visited.add((name, email))
    team.append((name, email))
    filled_size = current_team_size

    if filled_size >= TARGET_TEAM_SIZE:
        return team

    for m in matches:
        if filled_size >= TARGET_TEAM_SIZE:
            return team

        match_size = normalize_team_size(m["info"].get("team_size", 1))

        if (m["name"], m["email"]) not in visited and filled_size + match_size <= TARGET_TEAM_SIZE:
            visited.add((m["name"], m["email"]))
            team.append((m["name"], m["email"]))
            filled_size += match_size
    
    return team


def rebalance_single_member_teams(team_members):
    team_entries = [list(members) for members in team_members if members]

    def member_size(member):
        _, email = member
        return normalize_team_size(teams[email].get("team_size", 1))

    def team_size(members):
        return sum(member_size(member) for member in members)

    # Merge teams only when their weighted sizes complement exactly to 4.
    merged = True
    while merged:
        merged = False
        for i in range(len(team_entries)):
            if not team_entries[i]:
                continue
            size_i = team_size(team_entries[i])
            if size_i >= TARGET_TEAM_SIZE:
                continue
            for j in range(i + 1, len(team_entries)):
                if not team_entries[j]:
                    continue
                size_j = team_size(team_entries[j])
                if size_i + size_j == TARGET_TEAM_SIZE:
                    team_entries[i].extend(team_entries[j])
                    team_entries[j].clear()
                    merged = True
                    break
            if merged:
                break

    # If possible, move a single member to complete a target team exactly to 4.
    changed = True
    seen_states = set()
    while changed:
        changed = False

        # Guard against cyclic reshuffles between equivalent states.
        state = tuple(
            sorted(tuple(member[1] for member in members) for members in team_entries if members)
        )
        if state in seen_states:
            break
        seen_states.add(state)

        for i in range(len(team_entries)):
            if not team_entries[i]:
                continue
            size_i = team_size(team_entries[i])
            if size_i >= TARGET_TEAM_SIZE:
                continue

            needed = TARGET_TEAM_SIZE - size_i
            donor_found = False
            for j in range(len(team_entries)):
                if i == j or not team_entries[j]:
                    continue

                for k, candidate in enumerate(team_entries[j]):
                    cand_size = member_size(candidate)
                    donor_after = team_size(team_entries[j]) - cand_size
                    # Only move when donor team is fully dissolved by the transfer.
                    # This avoids A<->B oscillation where teams keep swapping members.
                    if cand_size == needed and donor_after == 0:
                        team_entries[i].append(candidate)
                        del team_entries[j][k]
                        changed = True
                        donor_found = True
                        break

                if donor_found:
                    break

            if changed:
                break

    # Keep only teams that still have at least one member and never return overfilled teams.
    cleaned = [members for members in team_entries if members and team_size(members) <= TARGET_TEAM_SIZE]
    return cleaned


def generate_matches_for_pool(pool_teams, start_index=0):
    global teams, team_ids, primary_track_sim, avg_skill_sim, project_sim, prize_sim, working_pref_sim, skills_match_sim, commitment_sim, visited

    teams = pool_teams
    team_ids = list(teams.keys())

    for team in teams.values():
        team["avg_skill_level"] = convert_skill_level(team["avg_skill_level"])

    all_possible_skills = set()
    for t_data in teams.values():
        all_possible_skills.update(t_data["skills"])
        all_possible_skills.update(t_data["skills_wanted"])
    all_possible_skills = list(all_possible_skills)

    primary_tracks = [teams[email]["primary_track"] for email in team_ids]
    skills = [teams[email]["skills"] for email in team_ids]
    skills_wanted = [teams[email]["skills_wanted"] for email in team_ids]
    projects = [teams[email]["projects"] for email in team_ids]
    prizes = [teams[email]["prizes"] for email in team_ids]
    working_preferences = [teams[email]["working_preferences"] for email in team_ids]
    commitments = [teams[email]["commitment"] for email in team_ids]
    avg_skill_levels = [teams[email]["avg_skill_level"] for email in team_ids]

    encoded_skills = encode_skills(skills, all_possible_skills)
    encoded_skills_wanted = encode_skills(skills_wanted, all_possible_skills)
    encoded_projects = encode_categorical(projects)
    encoded_prizes = encode_categorical(prizes)
    encoded_working_preferences = encode_categorical(working_preferences)

    primary_track_sim = np.array([
        [1 if primary_tracks[i] == primary_tracks[j] else 0 for j in range(len(team_ids))]
        for i in range(len(team_ids))
    ])
    avg_skill_sim = cosine_similarity(np.array(avg_skill_levels).reshape(-1, 1))
    project_sim = get_similarity_matrix(encoded_projects)
    prize_sim = get_similarity_matrix(encoded_prizes)
    working_pref_sim = get_similarity_matrix(encoded_working_preferences)
    skills_match_sim = cosine_similarity(encoded_skills_wanted, encoded_skills)

    commitment_levels = {"I want to win": 3, "I'm doing this to learn": 2, "I'm doing this for fun": 1}
    commitment_values = np.array([commitment_levels.get(teams[email]["commitment"], 2) for email in team_ids]).reshape(-1, 1)
    commitment_sim = cosine_similarity(commitment_values)

    visited = set()
    team_members = []
    for i in range(len(team_ids)):
        matches = get_top_matches(i)
        team_email = team_ids[i]
        team = form_team(teams[team_email]["name"], team_email, teams[team_email]["team_size"], matches)
        if len(team) > 0:
            team_members.append(team)

    team_members = rebalance_single_member_teams(team_members)
    team_logs = [
        {f"team{start_index + idx}": members}
        for idx, members in enumerate(team_members)
    ]
    return team_logs, start_index + len(team_logs)
        
# Generate matches and save to JSON
def generate_matches():
    global teams

    teams = fetch_teams()
    if not teams:
        print("No teams found in database")
        return

    non_waitlisted = {email: team for email, team in teams.items() if not team.get("is_waitlisted", False)}
    waitlisted = {email: team for email, team in teams.items() if team.get("is_waitlisted", False)}

    team_logs = []
    next_team_index = 0

    if non_waitlisted:
        logs, next_team_index = generate_matches_for_pool(non_waitlisted, start_index=next_team_index)
        team_logs.extend(logs)

    if waitlisted:
        logs, next_team_index = generate_matches_for_pool(waitlisted, start_index=next_team_index)
        team_logs.extend(logs)
        print("Waitlisted teams:")
        for team_obj in logs:
            team_id, members = next(iter(team_obj.items()))
            member_names = ", ".join([name for name, _ in members])
            print(f"- {team_id}: {member_names}")
    else:
        print("Waitlisted teams: none")

    output = {"Teams": team_logs}

    with open('matches.json', 'w') as f:
        json.dump(output, f, indent=2, default=json_serializable)
    print("Matches saved to matches.json")

if __name__ == "__main__":
    generate_matches()
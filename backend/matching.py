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
table = dynamodb.Table('portal-prd-team-matching')

def fetch_teams(): 
    try:
        response = table.scan()
        items = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        teams = {}
        for item in items:
            email = item.get('email')
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
                "team_size": team_size
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


def rebalance_single_member_teams(team_logs):
    team_entries = []
    for team_obj in team_logs:
        team_id, members = next(iter(team_obj.items()))
        team_entries.append([team_id, list(members)])

    # Move members from singleton teams into existing non-full teams.
    # We only add to teams with 2-3 visible members to avoid singleton-to-singleton shuffling.
    singleton_indices = [
        idx for idx, (_, members) in enumerate(team_entries)
        if len(members) == 1
    ]

    for singleton_idx in singleton_indices:
        if not team_entries[singleton_idx][1]:
            continue

        target_idx = next(
            (
                idx for idx, (_, members) in enumerate(team_entries)
                if idx != singleton_idx and 1 < len(members) < TARGET_TEAM_SIZE
            ),
            None,
        )

        if target_idx is None:
            continue

        moved_member = team_entries[singleton_idx][1].pop(0)
        team_entries[target_idx][1].append(moved_member)

    # Merge 2-person teams into 4-person teams where possible (2 + 2).
    two_person_indices = [
        idx for idx, (_, members) in enumerate(team_entries)
        if len(members) == 2
    ]

    while len(two_person_indices) >= 2:
        idx_a = two_person_indices.pop(0)
        idx_b = two_person_indices.pop(0)

        if not team_entries[idx_a][1] or not team_entries[idx_b][1]:
            continue

        team_entries[idx_a][1].extend(team_entries[idx_b][1])
        team_entries[idx_b][1].clear()

    # For any remaining 2-person teams, distribute members into 3-person teams.
    # This turns 3-person teams into 4-person teams when available.
    remaining_two_indices = [
        idx for idx, (_, members) in enumerate(team_entries)
        if len(members) == 2
    ]

    for two_idx in remaining_two_indices:
        members_to_place = list(team_entries[two_idx][1])
        if not members_to_place:
            continue

        target_three_indices = [
            idx for idx, (_, members) in enumerate(team_entries)
            if idx != two_idx and len(members) == 3
        ]

        for target_idx in target_three_indices:
            if not members_to_place:
                break

            member = members_to_place.pop(0)
            team_entries[target_idx][1].append(member)

        team_entries[two_idx][1] = members_to_place

    # Keep only teams that still have at least one member.
    team_entries = [entry for entry in team_entries if entry[1]]

    # Rebuild stable team ids after rebalancing.
    return [{f"team{i}": members} for i, (_, members) in enumerate(team_entries)]
        
# Generate matches and save to JSON
def generate_matches():
    global teams, team_ids, primary_track_sim, avg_skill_sim, project_sim, prize_sim, working_pref_sim, skills_match_sim, commitment_sim, visited
    
    teams = fetch_teams()
    if not teams:
        print("No teams found in database")
        return

    for team in teams.values():
        team["avg_skill_level"] = convert_skill_level(team["avg_skill_level"])
    team_ids = list(teams.keys())

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
    commitment_values = np.array([commitment_levels[teams[email]["commitment"]] for email in team_ids]).reshape(-1, 1)
    commitment_sim = cosine_similarity(commitment_values)

    visited = set()
    all_matches = {}
    team_logs = []
    for i in range(len(team_ids)):
        matches = get_top_matches(i)
        team_email = team_ids[i]  # Use email as key
        # team_logs.append({"name": teams[team_email]["name"], "email": team_email, "# of teammates": teams[team_email]["team_size"], "matches": [(m["name"], m["score"]) for m in matches]})
        team = form_team(teams[team_email]["name"], team_email, teams[team_email]["team_size"], matches)
        
        if len(team) > 0:
            team_logs.append({f"team{i}": team})

    team_logs = rebalance_single_member_teams(team_logs)

    output = {"Teams": team_logs}

    with open('matches.json', 'w') as f:
        json.dump(output, f, indent=2, default=json_serializable)
    print("Matches saved to matches.json")

if __name__ == "__main__":
    generate_matches()
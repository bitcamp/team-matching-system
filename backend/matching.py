import json
import numpy as np
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
from sklearn.metrics.pairwise import cosine_similarity

# Fetch data from DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('team-matching-system-dev-new')

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
            if isinstance(team_size, Decimal):
                team_size = int(team_size)
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
    team_size = teams[team_email]["team_size"]
    match_scores = []
    if team_size == 1:
        compatible_indices = [i for i in range(len(teams)) if teams[team_ids[i]]["team_size"] in [1, 2, 3]]
    elif team_size == 2:
        compatible_indices = [i for i in range(len(teams)) if teams[team_ids[i]]["team_size"] in [1, 2]]
    elif team_size == 3:
        compatible_indices = [i for i in range(len(teams)) if teams[team_ids[i]]["team_size"] == 1]
    else:
        compatible_indices = [i for i in range(len(teams)) if i != team_index]
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

# Generate matches and save to JSON
def generate_matches():
    global teams, team_ids, primary_track_sim, avg_skill_sim, project_sim, prize_sim, working_pref_sim, skills_match_sim, commitment_sim
    
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

    all_matches = {}
    team_logs = []
    for i in range(len(team_ids)):
        matches = get_top_matches(i)
        team_email = team_ids[i]  # Use email as key
        cleaned_matches = [{"name": m["name"], "email": m["email"], "score": m["score"], "info": m["info"]} for m in matches]
        all_matches[team_email] = cleaned_matches  # Key is now email
        team_logs.append({"team": teams[team_email]["name"], "matches": [m["name"] for m in matches]})

    output = {"matches": all_matches, "logs": team_logs}

    with open('matches.json', 'w') as f:
        json.dump(output, f, indent=2, default=json_serializable)
    print("Matches saved to matches.json")

if __name__ == "__main__":
    generate_matches()
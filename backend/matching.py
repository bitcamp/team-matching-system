import json
import numpy as np
import boto3
from botocore.exceptions import ClientError
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
# how to run this:
#   python3 -m venv venv
#   source venv/bin/activate
#   pip install boto3 numpy scikit-learn
#   serverless invoke local --function matchTeams
# step 1: read in from dynamodb
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('team-matching-system-dev')
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
            teams[email] = {
                "name": display_name,
                "email": email,
                "primary_track": item.get('track', 'N/A'),
                "skills": item.get('languages', []),
                "skills_wanted": item.get('skills_wanted', []),
                "avg_skill_level": item.get('skill_level', 'N/A'),
                "projects": item.get('projects', []),
                "prizes": item.get('prizes', []),
                "working_preferences": item.get('working_preferences', ['In-person']),
                "commitment": item.get('commitment', 'I want to win'),
                "team_size": item.get('num_team_members', 0)
            }
        return teams
    except ClientError as e:
        print(f"Error fetching data from DynamoDB: {e}")
        return {}
# initializing teams
teams = fetch_teams()
# step 2: encoding all categories
# convert a skill level string to a numeric value
def convert_skill_level(skill_level):
    skill_map = {'Beginner': 1, 'Intermediate': 3, 'Advanced': 5, 'N/A': 3}
    return skill_map.get(skill_level, 3)
# flatten the list of category lists and one-hot encode them
def encode_categorical(categories):
    flattened = [item for sublist in categories for item in sublist]
    encoder = OneHotEncoder(sparse_output=False)
    encoded = encoder.fit_transform(np.array(flattened).reshape(-1, 1))
    return encoded
# return a binary matrix where each row represents a team and each column a possible skill
def encode_skills(skills_list, all_possible_skills):
    skill_vectors = []
    for skills in skills_list:
        skill_vector = [1 if skill in skills else 0 for skill in all_possible_skills]
        skill_vectors.append(skill_vector)
    return np.array(skill_vectors)
# step 3: doing the actual cosine similarity stuff
# compute a similarity matrix using cosine similarity
def get_similarity_matrix(features):
    return cosine_similarity(features)
# compute the final match score for teams i and j
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
    final_score = skill_match_score * skills_weight + general_similarity * general_similarity_weight
    return final_score
# step 4: getting matches
# return the top matches for each team w/ their info
def get_top_matches(team_index, top_n=len(teams) - 1):
    # team_ids are emails
    team_email = team_ids[team_index]
    team_size = teams[team_email]["team_size"]
    match_scores = []
    # filtering by team size
    if team_size == 1:
        compatible_indices = [i for i in range(len(teams)) if teams[team_ids[i]]["team_size"] in [1, 2, 3]]
    elif team_size == 2:
        compatible_indices = [i for i in range(len(teams)) if teams[team_ids[i]]["team_size"] in [1, 2]]
    elif team_size == 3:
        compatible_indices = [i for i in range(len(teams)) if teams[team_ids[i]]["team_size"] == 1]
    else:
        compatible_indices = [i for i in range(len(teams)) if i != team_index]
    # getting and storing the info
    for i in compatible_indices:
        if i != team_index:
            score = get_combined_match_score(team_index, i)
            match_email = team_ids[i]
            team_info = {
                "name": teams[match_email]["name"],
                "email": match_email,
                "score": score,
                "info": teams[match_email]
            }
            match_scores.append(team_info)
    # sorting info by compatibility score
    sorted_matches = sorted(match_scores, key=lambda x: x["score"], reverse=True)
    return sorted_matches[:top_n]
# step 5: lambda handler
def lambda_handler(event, context):
    global teams, team_ids, primary_track_sim, avg_skill_sim, project_sim, prize_sim, working_pref_sim, skills_match_sim, commitment_sim
    teams = fetch_teams()
    if not teams:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'No teams found in database'})
        }
    # convert avg_skill_level to numeric values
    for team in teams.values():
        team["avg_skill_level"] = convert_skill_level(team["avg_skill_level"])
    # team_ids list contains emails (unique IDs)
    team_ids = list(teams.keys())
    # extract category values
    all_possible_skills = set()
    for team in teams.values():
        all_possible_skills.update(team["skills"])
        all_possible_skills.update(team["skills_wanted"])
    all_possible_skills = list(all_possible_skills)
    primary_tracks = [teams[email]["primary_track"] for email in team_ids]
    skills = [teams[email]["skills"] for email in team_ids]
    skills_wanted = [teams[email]["skills_wanted"] for email in team_ids]
    projects = [teams[email]["projects"] for email in team_ids]
    prizes = [teams[email]["prizes"] for email in team_ids]
    working_preferences = [teams[email]["working_preferences"] for email in team_ids]
    commitments = [teams[email]["commitment"] for email in team_ids]
    avg_skill_levels = [teams[email]["avg_skill_level"] for email in team_ids]
    team_sizes = [teams[email]["team_size"] for email in team_ids]
    # encode features
    encoded_skills = encode_skills(skills, all_possible_skills)
    encoded_skills_wanted = encode_skills(skills_wanted, all_possible_skills)
    encoded_projects = encode_categorical(projects)
    encoded_prizes = encode_categorical(prizes)
    encoded_working_preferences = encode_categorical(working_preferences)
    # compute similarities
    primary_track_sim = np.array([[1 if primary_tracks[i] == primary_tracks[j] else 0
                                   for j in range(len(team_ids))]
                                  for i in range(len(team_ids))])
    avg_skill_sim = cosine_similarity(np.array(avg_skill_levels).reshape(-1, 1))
    project_sim = get_similarity_matrix(encoded_projects)
    prize_sim = get_similarity_matrix(encoded_prizes)
    working_pref_sim = get_similarity_matrix(encoded_working_preferences)
    skills_match_sim = cosine_similarity(encoded_skills_wanted, encoded_skills)
    # compute commitment similarity
    commitment_levels = {
        "I want to win": 3,
        "I'm doing this to learn": 2,
        "I'm doing this for fun": 1
    }
    commitment_values = np.array([commitment_levels[teams[email]["commitment"]] for email in team_ids]).reshape(-1, 1)
    commitment_sim = cosine_similarity(commitment_values)
    # compute matches for all teams and collect log entries
    all_matches = {}
    team_logs = []
    for i in range(len(team_ids)):
        matches = get_top_matches(i)
        # team name is key when output displayed
        display_name = teams[team_ids[i]]["name"]
        all_matches[display_name] = matches
        log_entry = {"team": display_name, "matches": [match["name"] for match in matches]}
        team_logs.append(log_entry)
    # prepare final output including matches and logs; pretty-print JSON
    output = {
        "matches": all_matches,
        "logs": team_logs
    }
    # pretty print the output
    pretty_output = json.dumps(output, default=lambda o: list(o) if isinstance(o, set) else o, indent=2)
    print(pretty_output)
    # return {
    #     'statusCode': 200,
    #     'body': pretty_output
    # }
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder

# step 1: define teams 
teams = {
    "Team A": {
        "primary_track": "Machine Learning", "skills": ["html", "css", "javascript"],  "skills_wanted": ["python", "flask"], "avg_skill_level": 3, 
        "projects": ["Robotics", "AI"], "prizes": ["Innovation", "AI"], 
        "working_preferences": ["In-person", "Remote"], "commitment": "I want to win", "team_size": 3
    },
    "Team B": {
        "primary_track": "Machine Learning", "skills": ["flask", "react", "python"], "skills_wanted": ["javascript", "css"], "avg_skill_level": 2, 
        "projects": ["Robotics", "AI"], "prizes": ["Tech Excellence"], 
        "working_preferences": ["Remote"], "commitment": "I'm doing this for fun", "team_size": 1
    },
    "Team C": {
        "primary_track": "Cybersecurity", "skills": ["flask", "AI", "react"], "skills_wanted": ["django", "SQL"], "avg_skill_level": 4,
        "projects": ["Healthcare", "Deep Learning"], "prizes": ["Healthcare Excellence"], 
        "working_preferences": ["In-person"], "commitment": "I'm doing this to learn", "team_size": 3
    },
    "Team D": {
        "primary_track": "Quantum", "skills": ["python", "django"], "skills_wanted": ["html", "react", "javascript"], "avg_skill_level": 5, 
        "projects": ["AI", "Deep Learning"], "prizes": ["Innovation"], 
        "working_preferences": ["Flexible", "Remote"], "commitment": "I want to win", "team_size": 2
    },
    "Team E": {
        "primary_track": "App Development", "skills": ["java"], "skills_wanted": ["python", "SQL"], "avg_skill_level": 3,
        "projects": ["AI", "Deep Learning"], "prizes": ["Innovation"], 
        "working_preferences": ["Remote"], "commitment": "I'm doing this to learn", "team_size": 2
    },
    "Team F": {
        "primary_track": "Quantum", "skills": ["python"], "skills_wanted": ["flask", "SQL"], "avg_skill_level": 4,
        "projects": ["Healthcare", "AI"], "prizes": ["Tech Excellence"], 
        "working_preferences": ["In-person"], "commitment": "I'm doing this to learn", "team_size": 1
    },
    "Team G": {
        "primary_track": "App Development", "skills": ["react", "SQL"], "skills_wanted": ["html", "python"], "avg_skill_level": 5,
        "projects": ["AI", "Deep Learning"], "prizes": ["AI Excellence"], 
        "working_preferences": ["Flexible", "Remote"], "commitment": "I want to win", "team_size": 1
    },
    "Team H": {
        "primary_track": "Cybersecurity", "skills": ["python", "java"], "skills_wanted": ["java", "python", "react"], "avg_skill_level": 2,
        "projects": ["Healthcare", "Medical Robotics"], "prizes": ["Healthcare Excellence"], 
        "working_preferences": ["In-person"], "commitment": "I'm doing this for fun", "team_size": 1
    }
}

# step 2: define encoding functions

# define all possible skills
all_possible_skills = list(set(skill for team in teams.values() for skill in team["skills"] + team["skills_wanted"]))

# encode categories (everything but skills) using one hot encoding --> transform into binary vector (ex. AI = [1 0 0], Healthcare = [0 1 0], etc)
def encode_categorical(categories):
    flattened = [item for sublist in categories for item in sublist]
    encoder = OneHotEncoder(sparse_output=False)
    encoded = encoder.fit_transform(np.array(flattened).reshape(-1, 1))
    return encoded

# encode skills using one hot encoding --> binary vector for each skill
def encode_skills(skills_list, all_possible_skills):
    skill_vectors = []
    for skills in skills_list:
        skill_vector = [1 if skill in skills else 0 for skill in all_possible_skills]
        skill_vectors.append(skill_vector)
    return np.array(skill_vectors)

# extract category values
team_names = list(teams.keys())
primary_tracks = [team["primary_track"] for team in teams.values()]
skills = [team["skills"] for team in teams.values()]
skills_wanted = [team["skills_wanted"] for team in teams.values()]
projects = [team["projects"] for team in teams.values()]
prizes = [team["prizes"] for team in teams.values()]
working_preferences = [team["working_preferences"] for team in teams.values()]
commitments = [team["commitment"] for team in teams.values()]
avg_skill_levels = [team["avg_skill_level"] for team in teams.values()]
team_sizes = [team["team_size"] for team in teams.values()]

# encode features
encoded_skills = encode_skills(skills, all_possible_skills)
encoded_skills_wanted = encode_skills(skills_wanted, all_possible_skills)
encoded_projects = encode_categorical(projects)
encoded_prizes = encode_categorical(prizes)
encoded_working_preferences = encode_categorical(working_preferences)

# step 3: compute cos similarity for everything 
def get_similarity_matrix(features):
    return cosine_similarity(features)

primary_track_sim = np.array([[1 if primary_tracks[i] == primary_tracks[j] else 0 for j in range(len(team_names))] for i in range(len(team_names))])
avg_skill_sim = cosine_similarity(np.array(avg_skill_levels).reshape(-1, 1))
project_sim = get_similarity_matrix(encoded_projects)
prize_sim = get_similarity_matrix(encoded_prizes)
working_pref_sim = get_similarity_matrix(encoded_working_preferences)
skills_match_sim= cosine_similarity(encoded_skills_wanted, encoded_skills)

# encode commitment levels numerically
commitment_levels = {
    "I want to win": 3,
    "I'm doing this to learn": 2,
    "I'm doing this for fun": 1
}

commitment_values = np.array([commitment_levels[teams[team]["commitment"]] for team in team_names]).reshape(-1, 1)
commitment_sim = cosine_similarity(commitment_values)

# step 4: compute final match score with weighting for each
def get_combined_match_score(i, j, skills_weight=0.7, general_similarity_weight=0.6):
    skill_match_score = skills_match_sim[i][j]
    
    # compute general similarity score (multiplied by weights that take care of prioritizing)
    general_similarity = (
        primary_track_sim[i][j] * 0.45 +
        avg_skill_sim[i][j] * 0.45 +
        project_sim[i][j] * 0.6 +
        prize_sim[i][j] * 0.5 +
        working_pref_sim[i][j] * 0.4 +
        commitment_sim[i][j] * 0.5
    )

    # combine skills and general similarity scores
    final_score = skill_match_score * skills_weight + general_similarity * general_similarity_weight
    return final_score

# step 5: find top matches considering team size
def get_top_matches(team_index, top_n=len(teams)-1):
    team_name = team_names[team_index]
    team_size = teams[team_name]["team_size"]
    match_scores = []

    # filter teams based on team size
    if team_size == 1:
        compatible_teams = [i for i in range(len(teams)) if teams[team_names[i]]["team_size"] in [1, 2, 3]]
    elif team_size == 2:
        compatible_teams = [i for i in range(len(teams)) if teams[team_names[i]]["team_size"] in [1, 2]]
    elif team_size == 3:
        compatible_teams = [i for i in range(len(teams)) if teams[team_names[i]]["team_size"] == 1]

    for i in compatible_teams:
        if i != team_index:
            score = get_combined_match_score(team_index, i)
            match_scores.append((team_names[i], score))

    sorted_matches = sorted(match_scores, key=lambda x: x[1], reverse=True)
    return sorted_matches[:top_n]

# print top matches for a specific team
team_index = team_names.index("Team H")
top_matches = get_top_matches(team_index)
print(f"Top matches for {team_names[team_index]}:", top_matches)

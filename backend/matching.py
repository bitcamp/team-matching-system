import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder

# step 1: define teams -- just to test, now including team size
teams = {
    "Team A": {
        "primary_track": "AI", "skills": ["html", "css", "javascript"], "avg_skill_level": 3, 
        "projects": ["Robotics", "AI"], "prizes": ["Innovation", "AI"], 
        "working_preferences": ["In-person", "Remote"], "team_size": 3
    },
    "Team B": {
        "primary_track": "AI", "skills": ["flask", "react", "python"], "avg_skill_level": 2, 
        "projects": ["Robotics", "AI"], "prizes": ["Tech Excellence"], 
        "working_preferences": ["Remote"], "team_size": 3
    },
    "Team C": {
        "primary_track": "Healthcare", "skills": ["flask", "AI", "react"], "avg_skill_level": 4,
        "projects": ["Healthcare", "Deep Learning"], "prizes": ["Healthcare Excellence"], 
        "working_preferences": ["In-person"], "team_size": 3
    },
    "Team D": {
        "primary_track": "AI", "skills": ["python", "django", "Robotics"], "avg_skill_level": 5, 
        "projects": ["AI", "Deep Learning"], "prizes": ["Innovation"], 
        "working_preferences": ["Flexible", "Remote"], "team_size": 2
    },
    "Team E": {
        "primary_track": "AI", "skills": ["AI", "Robotics", "css"], "avg_skill_level": 3,
        "projects": ["AI", "Deep Learning"], "prizes": ["Innovation"], 
        "working_preferences": ["Remote"], "team_size": 2
    },
    "Team F": {
        "primary_track": "Healthcare", "skills": ["Healthcare", "Robotics"], "avg_skill_level": 4,
        "projects": ["Healthcare", "AI"], "prizes": ["Tech Excellence"], 
        "working_preferences": ["In-person"], "team_size": 1
    },
    "Team G": {
        "primary_track": "AI", "skills": ["AI", "Machine Learning", "Data Science"], "avg_skill_level": 5,
        "projects": ["AI", "Deep Learning"], "prizes": ["AI Excellence"], 
        "working_preferences": ["Flexible", "Remote"], "team_size": 1
    },
    "Team H": {
        "primary_track": "Healthcare", "skills": ["Healthcare", "Deep Learning"], "avg_skill_level": 2,
        "projects": ["Healthcare", "Medical Robotics"], "prizes": ["Healthcare Excellence"], 
        "working_preferences": ["In-person"], "team_size": 1
    }
}

# step 2: define encoding for categories

# encoding categories (everything but skills) using one hot encoding --> transform into binary vector (ex. AI = [1 0 0], Healthcare = [0 1 0], etc)
def encode_categorical(categories):
    flattened = [item for sublist in categories for item in sublist]
    encoder = OneHotEncoder(sparse_output=False)
    encoded = encoder.fit_transform(np.array(flattened).reshape(-1, 1))
    return encoded

# encoding skills using one hot encoding --> binary vector for each skill
def encode_skills(skills_list, all_possible_skills):
    encoder = OneHotEncoder(sparse_output=False)
    skill_vectors = []
    for skills in skills_list:
        skill_vector = [1 if skill in skills else 0 for skill in all_possible_skills]
        skill_vectors.append(skill_vector)
    
    encoded_skills = encoder.fit_transform(np.array(skill_vectors))
    return encoded_skills

# extracting category values 
team_names = list(teams.keys())
primary_tracks = [team["primary_track"] for team in teams.values()]
avg_skill_levels = [team["avg_skill_level"] for team in teams.values()]
projects = [team["projects"] for team in teams.values()]
prizes = [team["prizes"] for team in teams.values()]
working_preferences = [team["working_preferences"] for team in teams.values()]
skills = [team["skills"] for team in teams.values()]
team_sizes = [team["team_size"] for team in teams.values()]  # Team sizes

# defining skills
all_possible_skills = ["AI", "Robotics", "Deep Learning", "Healthcare", "Tech Excellence", "html", "css", "python", "react", "flask", "javascript", "django"]

# encode skills 
encoded_skills = encode_skills(skills, all_possible_skills)

# encode categorical features
encoded_projects = encode_categorical(projects)
encoded_prizes = encode_categorical(prizes)
encoded_working_preferences = encode_categorical(working_preferences)

# step 3: compute cos similarity for everything other than skills 
def get_similarity_matrix(features):
    return cosine_similarity(features)

# calc cos sim per category
primary_track_sim = np.array([[1 if primary_tracks[i] == primary_tracks[j] else 0 for j in range(len(team_names))] for i in range(len(team_names))])
avg_skill_sim = cosine_similarity(np.array(avg_skill_levels).reshape(-1, 1))
project_sim = get_similarity_matrix(encoded_projects)
prize_sim = get_similarity_matrix(encoded_prizes)
working_pref_sim = get_similarity_matrix(encoded_working_preferences)

# step 4: do inverse similarity for complementary skills
def get_complementary_skill_matching(team_index, top_n=len(teams)-1):
    team_skills = np.array(encoded_skills[team_index])
    all_other_teams = np.array([encoded_skills[i] for i in range(len(team_names)) if i != team_index])

    # 1 - cos_similarity = inverse similarity
    sim_matrix = cosine_similarity([team_skills], all_other_teams)[0]
    complementary_scores = 1 - sim_matrix 

    # sort teams based on complementarity
    sorted_indices = np.argsort(complementary_scores)[::-1]
    best_matches = [(team_names[i], round(complementary_scores[i], 3)) for i in sorted_indices[:top_n]]
    
    return best_matches

# step 5: compute final match score for complementary skills and general similarity with weighting for each
def get_combined_match_score(i, j, complementary_weight=0.7, similarity_weight=0.6):
    # compute complementary score
    complementary_score = get_complementary_skill_matching(i, top_n=len(teams)-1)
    complementary_score = next((score for team, score in complementary_score if team == team_names[j]), 0)

    # compute general similarity score (multiplied by weights that take care of prioritizing)
    general_similarity = (
        primary_track_sim[i][j] * 0.45 +
        avg_skill_sim[i][j] * 0.45 +
        project_sim[i][j] * 0.55 +
        prize_sim[i][j] * 0.45 +
        working_pref_sim[i][j] * 0.35
    )

    # combine complementary skills and general similarity scores
    final_score = complementary_score * complementary_weight + general_similarity * similarity_weight

    return final_score

# step 6: find top matches based on team size
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

    # sort by combined match score
    sorted_matches = sorted(match_scores, key=lambda x: x[1], reverse=True)

    return sorted_matches[:top_n]

# example -- print by team
team_index = team_names.index("Team F")         
top_matches = get_top_matches(team_index)
print(f"Top matches for {team_names[team_index]}:", top_matches)

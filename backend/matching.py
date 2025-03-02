import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder

# Step 1: Define Teams with Criteria
teams = {
    "Team A": {
        "primary_track": "AI", "skills": ["html", "css", "javascript"], "avg_skill_level": 3, 
        "projects": ["Robotics", "AI"], "prizes": ["Innovation", "AI"], 
        "working_preferences": ["In-person", "Remote"]
    },
    "Team B": {
        "primary_track": "AI", "skills": ["flask", "react", "python"], "avg_skill_level": 2, 
        "projects": ["Robotics", "AI"], "prizes": ["Tech Excellence"], 
        "working_preferences": ["Remote"]
    },
    "Team C": {
        "primary_track": "Healthcare", "skills": ["flask", "AI", "react"], "avg_skill_level": 4,
        "projects": ["Healthcare", "Deep Learning"], "prizes": ["Healthcare Excellence"], 
        "working_preferences": ["In-person"]
    },
    "Team D": {
        "primary_track": "AI", "skills": ["medicare", "django", "Robotics"], "avg_skill_level": 5, 
        "projects": ["AI", "Deep Learning"], "prizes": ["Innovation"], 
        "working_preferences": ["Flexible", "Remote"]
    },
    "Team E": {
        "primary_track": "AI", "skills": ["AI", "Robotics", "css"], "avg_skill_level": 3,
        "projects": ["AI", "Deep Learning"], "prizes": ["Innovation"], 
        "working_preferences": ["Remote"]
    },
    "Team F": {
        "primary_track": "Healthcare", "skills": ["Healthcare", "Robotics"], "avg_skill_level": 4,
        "projects": ["Healthcare", "AI"], "prizes": ["Tech Excellence"], 
        "working_preferences": ["In-person"]
    },
    "Team G": {
        "primary_track": "AI", "skills": ["AI", "Machine Learning", "Data Science"], "avg_skill_level": 5,
        "projects": ["AI", "Deep Learning"], "prizes": ["AI Excellence"], 
        "working_preferences": ["Flexible", "Remote"]
    },
    "Team H": {
        "primary_track": "Healthcare", "skills": ["Healthcare", "Deep Learning"], "avg_skill_level": 2,
        "projects": ["Healthcare", "Medical Robotics"], "prizes": ["Healthcare Excellence"], 
        "working_preferences": ["In-person"]
    }
}

# Step 2: Define the Encoding and Cosine Similarity Calculation
def encode_categorical(categories):
    # Flatten the list of lists into a single list
    flattened = [item for sublist in categories for item in sublist]
    
    encoder = OneHotEncoder(sparse_output=False)
    encoded = encoder.fit_transform(np.array(flattened).reshape(-1, 1))
    return encoded

def encode_skills(skills_list, all_possible_skills):
    # OneHotEncoder expects a 2D array where each entry is a list.
    encoder = OneHotEncoder(sparse_output=False)
    # We create a binary vector indicating the presence of each skill.
    skill_vectors = []
    for skills in skills_list:
        skill_vector = [1 if skill in skills else 0 for skill in all_possible_skills]
        skill_vectors.append(skill_vector)
    
    # Fit and transform the skills data
    encoded_skills = encoder.fit_transform(np.array(skill_vectors))
    return encoded_skills

# Convert criteria into vectors
team_names = list(teams.keys())
primary_tracks = [team["primary_track"] for team in teams.values()]
avg_skill_levels = [team["avg_skill_level"] for team in teams.values()]
projects = [team["projects"] for team in teams.values()]
prizes = [team["prizes"] for team in teams.values()]
working_preferences = [team["working_preferences"] for team in teams.values()]
skills = [team["skills"] for team in teams.values()]

# Define all possible skills in your dataset
all_possible_skills = ["AI", "Robotics", "Deep Learning", "Healthcare", "Tech Excellence"]

# Encode skills (binary vectors indicating the presence of each skill)
encoded_skills = encode_skills(skills, all_possible_skills)

# Encode categorical features (projects, prizes, working preferences)
encoded_projects = encode_categorical(projects)
encoded_prizes = encode_categorical(prizes)
encoded_working_preferences = encode_categorical(working_preferences)


# Step 3: Compute Similarity for Non-Skill Criteria
def get_similarity_matrix(features):
    return cosine_similarity(features)

# Similarity for primary track, average skill level, projects, prizes, and preferences
primary_track_sim = np.array([[1 if primary_tracks[i] == primary_tracks[j] else 0 for j in range(len(team_names))] for i in range(len(team_names))])
avg_skill_sim = cosine_similarity(np.array(avg_skill_levels).reshape(-1, 1))
project_sim = get_similarity_matrix(encoded_projects)
prize_sim = get_similarity_matrix(encoded_prizes)
working_pref_sim = get_similarity_matrix(encoded_working_preferences)

# Step 4: Complementary Skills Matching (Inverse Similarity)
def get_complementary_skill_matching(team_index, top_n=len(teams)-1):
    team_skills = np.array(encoded_skills[team_index])
    all_other_teams = np.array([encoded_skills[i] for i in range(len(team_names)) if i != team_index])

    # Cosine similarity between teams' skills
    sim_matrix = cosine_similarity([team_skills], all_other_teams)[0]
    complementary_scores = 1 - sim_matrix  # Inverse similarity (higher is more complementary)

    # Sort teams based on complementarity
    sorted_indices = np.argsort(complementary_scores)[::-1]
    best_matches = [(team_names[i], round(complementary_scores[i], 3)) for i in sorted_indices[:top_n]]
    
    return best_matches

# Step 5: Combine All Similarity Scores
def get_combined_match_score(i, j, complementary_weight = 0.4):
    # Combine similarity scores (you can use weights to adjust importance)
    combined_score = (
        primary_track_sim[i][j] * 0.2 +
        avg_skill_sim[i][j] * 0.2 +
        project_sim[i][j] * 0.2 +
        prize_sim[i][j] * 0.2 +
        working_pref_sim[i][j] * 0.2
    )
    complementary_score = get_complementary_skill_matching(i, top_n=1)[0][1]  # Get the complementary score
    combined_score += complementary_score * complementary_weight
    return combined_score

# Step 6: Find Best Matches Based on All Criteria
def get_top_matches(team_index, top_n=len(teams)-1):
    team_name = team_names[team_index]
    match_scores = []

    for i in range(len(team_names)):
        if i != team_index: 
            score = get_combined_match_score(team_index, i)
            match_scores.append((team_names[i], score))

    # Sort by combined score
    sorted_matches = sorted(match_scores, key=lambda x: x[1], reverse=True)
    
    # Now, prioritize complementary skills
    complementary_matches = get_complementary_skill_matching(team_index)

    # Combine both sets: top matches and complementary matches, but exclude duplicates
    combined_matches = complementary_matches + sorted_matches[:top_n]

    # Remove duplicates (keeping only unique teams)
    final_matches = []
    seen_teams = set()
    for match in combined_matches:
        if match[0] not in seen_teams:
            if match[0] != team_names[team_index]:
                final_matches.append(match)
                seen_teams.add(match[0])

    return sorted(final_matches, key=lambda x: x[1], reverse=True) # ligma skibidi

# Example: Find Best Matches for "Team A"
team_index = team_names.index("Team A")
top_matches = get_top_matches(team_index)
print(f"Top matches for {team_names[team_index]}:", top_matches)

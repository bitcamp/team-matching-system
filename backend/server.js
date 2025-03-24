const express = require("express");
const cors = require("cors");
const AWS = require("aws-sdk");


const app = express();
app.use(cors());
app.use(express.json()); 

AWS.config.update({
  region: "us-east-1", 
});

const dynamoDB = new AWS.DynamoDB.DocumentClient();
const TABLE_NAME = "team-matching-system-dev"; // Change this to your DynamoDB table name

// POST route to handle form submissions
app.post("/register", async (req, res) => {
  const formData = req.body;

  // Define the item to be stored in DynamoDB
  const params = {
    TableName: TABLE_NAME,
    Item: {
      email: formData.email, // Primary Key
      first_name: formData.first_name,
      last_name: formData.last_name,
      year: formData.year,
      track: formData.track,
      languages: formData.languages,
      experience: formData.experience,
      skills_wanted: formData.skills_wanted,
      skill_level: formData.skill_level,
      projects: formData.projects,
      prizes: formData.prizes,
      serious: formData.serious,
      collab: formData.collab,
      num_team_members: formData.num_team_members,
    },
  };

  try {
    await dynamoDB.put(params).promise();
    res.status(200).json({ message: "Registration successful!" });
  } catch (error) {
    console.error("DynamoDB Error:", error);
    res.status(500).json({ error: "Error saving data to DynamoDB" });
  }
});

// Start the server
const PORT = 5001;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

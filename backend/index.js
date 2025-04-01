const express = require("express");
const cors = require("cors");
const AWS = require("aws-sdk");
const serverless = require("serverless-http");

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
  console.log("Received Data:", req.body); // Debugging
  const formData = req.body;

  if (!formData.email) {
    return res.status(400).json({ error: "Email is required!" });
  }

  // Check for missing fields
  for (let key in formData) {
    if (formData[key] === undefined) {
      console.error(`Missing field: ${key}`);
    }
  }

  const params = {
    TableName: TABLE_NAME,
    Item: {
      email: formData.email, // Primary Key
      first_name: formData.first_name || "N/A",
      last_name: formData.last_name || "N/A",
      year: formData.year || "N/A",
      track: formData.track || "N/A",
      languages: formData.languages || [],
      experience: formData.experience || "N/A",
      skills_wanted: formData.skills_wanted || [],
      skill_level: formData.skill_level || "N/A",
      projects: formData.projects || [],
      prizes: formData.prizes || [],
      serious: formData.serious || false,
      collab: formData.collab || false,
      num_team_members: formData.num_team_members || 0,
    },
  };

  try {
    console.log("Saving to DynamoDB:", params); // Debugging
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

module.exports.handler = serverless(app);
const express = require("express");
const cors = require("cors");
const AWS = require("aws-sdk");
const serverless = require("serverless-http");

const app = express();
app.use(cors()); // ✅ Enable CORS for all routes
app.use(express.json()); // ✅ Parse JSON bodies

AWS.config.update({ region: "us-east-1" });

const dynamoDB = new AWS.DynamoDB.DocumentClient();
const TABLE_NAME = "team-matching-system-dev-new"; // Replace with your actual table name

// ✅ POST /register — create or update a profile
app.post("/register", async (req, res) => {
  const formData = req.body;

  if (!formData.email) {
    return res.status(400).json({ error: "Email is required!" });
  }

  const params = {
    TableName: TABLE_NAME,
    Item: {
      email: formData.email,
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
      username: formData.username || "N/A",
      password: formData.password || "N/A"
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

// ✅ DELETE /delete — remove profile by email
app.delete("/delete", async (req, res) => {
  const { id } = req.body; // 👈 expects { id: 'user@example.com' }

  if (!id) {
    return res.status(400).json({ error: "Missing id in request body" });
  }

  const params = {
    TableName: TABLE_NAME,
    Key: {
      email: id,
    },
  };

  try {
    await dynamoDB.delete(params).promise();
    res.status(200).json({ message: "Profile deleted successfully." });
  } catch (error) {
    console.error("DynamoDB Delete Error:", error);
    res.status(500).json({ error: "Failed to delete profile" });
  }
});

// Optional: Add other routes here

// ✅ Export the Lambda-compatible handler
module.exports.handler = serverless(app);

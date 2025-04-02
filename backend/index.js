const { DynamoDBClient, PutItemCommand } = require("@aws-sdk/client-dynamodb");

const client = new DynamoDBClient({ region: "us-east-1" });
const TABLE_NAME = process.env.TEAM_MATCHING_TABLE || "team-matching-system-dev";

exports.handler = async (event) => {
  const formData = JSON.parse(event.body);
  console.log("Received Data:", formData);

  if (!formData.email) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ error: "Email is required!" }),
    };
  }

  const params = {
    TableName: TABLE_NAME,
    Item: {
      email: { S: formData.email },
      first_name: { S: formData.first_name || "N/A" },
      last_name: { S: formData.last_name || "N/A" },
      year: { N: (formData.year || 0).toString() }, // Number
      track: { S: formData.track || "N/A" },
      hackathon: { S: formData.hackathon || "N/A" },
      languages: { SS: Array.isArray(formData.languages) && formData.languages.length ? formData.languages : ["N/A"] },
      experience: { S: formData.experience || "N/A" },
      skill_level: { S: formData.skill_level || "N/A" },
      skills_wanted: { SS: Array.isArray(formData.skills_wanted) && formData.skills_wanted.length ? formData.skills_wanted : ["N/A"] },
      projects: { SS: Array.isArray(formData.projects) && formData.projects.length ? formData.projects : ["N/A"] },
      prizes: { SS: Array.isArray(formData.prizes) && formData.prizes.length ? formData.prizes : ["N/A"] },
      serious: { S: formData.serious || "N/A" }, // String (e.g., "win")
      collab: { SS: Array.isArray(formData.collab) && formData.collab.length ? formData.collab : ["N/A"] }, // Array
      num_team_members: { N: (formData.num_team_members || 0).toString() }, // Number
      ...(formData.looking && { looking: { S: formData.looking } }), // Optional
    },
  };

  try {
    console.log("Saving to DynamoDB:", params);
    await client.send(new PutItemCommand(params));
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ message: "Registration successful!" }),
    };
  } catch (error) {
    console.error("DynamoDB Error:", error);
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ error: "Error saving data to DynamoDB" }),
    };
  }
};
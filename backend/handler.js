const AWS = require("aws-sdk");
const UUID = require('uuid');
const withSentry = require("serverless-sentry-lib");
const { IncomingWebhook } = require("@slack/webhook");
AWS.config.update({ region: "us-east-1" });
const HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Credentials': true,
  'Access-Control-Allow-Headers': '*',
};
const withSentryOptions = {
  captureErrors: true,
  captureUnhandledRejections: true,
  captureUncaughtException: true,
  captureMemory: true,
  captureTimeouts: true,
};
module.exports.register = withSentry(withSentryOptions, async (event) => {
  const body = JSON.parse(event.body);
  const ddb = new AWS.DynamoDB.DocumentClient();
  
  const requiredFields = [
    'email',
    'first_name',
    'last_name',
    'year',
    'track',
    'hackathon',
    'languages',
    'experience',
    'skill_level',
    'skills_wanted',
    'projects',
    'prizes',
    'serious',
    'collab',
    'num_team_members',
    'looking'
  ];

  const missingFields = requiredFields.filter(field => !body[field] || 
    (Array.isArray(body[field]) && body[field].length === 0));

  if (missingFields.length > 0) {
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        error: "Missing required fields",
        fields: missingFields 
      }),
      headers: HEADERS,
    };
  }

  const existingReg = await ddb.get({
    TableName: process.env.TEAM_MATCHING_TABLE,
    Key: {email: body.email.toLowerCase()}
  }).promise();

  var params = {
    TableName: process.env.TEAM_MATCHING_TABLE,
    Item: {
      email: body.email.toLowerCase(),
      first_name: body.first_name,
      last_name: body.last_name,
      year: body.year,
      track: body.track,
      hackathon: body.hackathon,
      languages: body.languages,
      experience: body.experience,
      skill_level: body.skill_level,
      skills_wanted: body.skills_wanted,
      projects: body.projects,
      prizes: body.prizes,
      serious: body.serious,
      collab: body.collab,
      num_team_members: body.num_team_members,
      looking: body.looking
    },
  };

  await ddb.put(params).promise();

  return {
    statusCode: 200,
    body: JSON.stringify(params.Item),
    headers: HEADERS,
  };
}); 
// makeAddon generates a random string of `length`
// const makeAddon = (length) => {
//   var result = [];
//   var chars = "abcdefghjkmnpqrstuvwxyz23456789"; // avoid i, l , o, 0, 1
//   for (var i = 0; i < length; i++) {
//     result.push(chars.charAt(Math.floor(Math.random() * chars.length)));
//   }
//   return result.join("");
// };
// sendConfirmationEmail uses AWS SES to send a confirmation email to the user
// const sendConfirmationEmail = async (user) => {
//   const ses = new AWS.SES();
//   // As of right now, Bitcamp does not use a referral link
//   // const referralLink = "https://register.gotechnica.org/" + referralID;
//   const reregisterLink = "https://register.bit.camp?redo=" + user.email;
//   // Capitalize track
//   const track = user.track
//     .split('_')
//     .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
//     .join(' ');
//   // Keep this the same as in RegistrationForm.vue
//   const school_year_options = [
//     { value: "less than high school", text: "Less than Secondary / High School" },
//     { value: "high school", text: "Secondary / High School" },
//     { value: "undergrad 2 year", text: "Undergraduate University (2 year - community college or similar)" },
//     { value: "undergrad 3+ year", text: "Undergraduate University (3+ year)" },
//     { value: "grad", text: "Graduate University (Masters, Professional, Doctoral, etc)" },
//     { value: "bootcamp", text: "Code School / Bootcamp" },
//     { value: "vocational", text: "Other Vocational / Trade Program or Apprenticeship" },
//     { value: "postdoc", text: "Post Doctorate" },
//     { value: "other", text: "Other" },
//     { value: "not a student", text: "I'm not currently a student" },
//     { value: "prefer not to answer", text: "Prefer not to answer" },
//   ];
//   // School year text
//   const schoolYear = school_year_options
//     .find(option => option.value === user.school_year).text;
//   // All caps t shirt size
//   const tShirtSize = user.tshirt_size.toUpperCase();
//   const params = {
//     Destination: { ToAddresses: [user.email] },
//     Source: "Bitcamp <hello@bit.camp>",
//     ConfigurationSetName: "registration-2024",
//     Template: "DetailedHackerRegistrationConfirmation",
//     TemplateData: `{\"firstName\":\"${user.first_name}\",\"reregisterLink\":\"${reregisterLink}\",\"email\":\"${user.email}\",\"name\":\"${user.name}\",\"age\":\"${user.age}\",\"track\":\"${track}\",\"phone\":\"${user.phone}\",\"school_type\":\"${schoolYear}\",\"school\":\"${user.school}\",\"address\":\"${user.address}\",\"tshirt_size\":\"${tShirtSize}\"}`,
//   };
//   return await ses.sendTemplatedEmail(params).promise();
// };
// const sendReferralNotificationEmail = async (fullName, email, referralID, referralName) => {
//   const ses = new AWS.SES();
//   const referralLink = "https://register.gotechnica.org/" + referralID;
//   const firstName = fullName.split(" ")[0];
//   const params = {
//     Destination: { ToAddresses: [email] },
//     Source: "Technica <hello@gotechnica.org>",
//     ConfigurationSetName: "registration-2021",
//     Template: "ReferralNotificationEmail3",
//     TemplateData: `{\"firstName\":\"${firstName}\",\"referralLink\":\"${referralLink}\",\"ReferralName\":\"${referralName}\",\"email\":\"${email}\"}`,
//   };
//   return await ses.sendTemplatedEmail(params).promise();
// };
// // =============================================================================
// // POST /upload_resume - Uploads hacker resume to S3 bucket
// module.exports.upload_resume = withSentry(async (event) => {
//   const body = JSON.parse(event.body);
//   if (!body.filename) {
//     return {
//       statusCode: 500,
//       body: '/upload_resume is missing filename',
//     };
//   }
//   const s3 = new AWS.S3();
//   const folder = UUID.v4();
//   const filePath = `${folder}/${body.filename}`;
//   const params = {
//     Bucket: 'bitcamp-2024-resumes',
//     Key: filePath,
//     Expires: 600,
//     ContentType: 'multipart/form-data',
//   };
//   const s3Result = s3.getSignedUrl('putObject', params);
//   return {
//     statusCode: 200,
//     body: JSON.stringify({ putUrl: s3Result, uploadUrl: `https://bitcamp-2024-resumes.s3.amazonaws.com/${filePath}` }),
//     headers: HEADERS,
//   };
// });
// // POST /upload_resume_text - Uploads text format of hacker resume to DynamoDB table
// module.exports.upload_resume_text = withSentry(async (event) => {
//   const body = JSON.parse(event.body);
//   if (!body.user_id || !body.resume_text) {
//     return {
//       statusCode: 500,
//       body: '/upload_resume_text is missing user_id or resume_text',
//     };
//   }
//   const ddb = new AWS.DynamoDB.DocumentClient();
//   const params = {
//     TableName: process.env.RESUMES_TABLE,
//     Item: {
//       id: body.user_id,
//       submitted: new Date().getTime(),
//       resume_text: body.resume_text,
//     },
//   };
//   await ddb.put(params).promise();
//   return {
//     statusCode: 200,
//     body: 'success',
//     headers: HEADERS,
//   };
// });
// // POST /track - Keeps track of various user actions
// module.exports.track = withSentry(async (event) => {
//   const body = JSON.parse(event.body);
//   const ddb = new AWS.DynamoDB.DocumentClient();
//   // Checks if any field is missing
//   if (!body.random_id && !body.referral_id) {
//     return {
//       statusCode: 500,
//       body: "/track is missing a field",
//     };
//   }
//   // Handle "how i found out about technica"
//   if (body.key.startsWith("hf")) {
//     body.value = event.requestContext.identity.sourceIp;
//     await logStatistic(ddb, body.key, 1);
//   }
//   // Log user's ip
//   if (body.key === "open-registration") {
//     body.value = event.requestContext.identity.sourceIp;
//     await logStatistic(ddb, "page-view", 1);
//   }
//   // Find user's random id from referral id
//   if (!body.random_id) {
//     var resp = await ddb
//       .query({
//         TableName: process.env.TRACKING_TABLE,
//         IndexName: "referralsIndex",
//         KeyConditionExpression: "referral_id = :v_refer",
//         ExpressionAttributeValues: { ":v_refer": body.referral_id },
//       })
//       .promise();
//     body.random_id = resp.Items[0].random_id;
//   }
//   // Append key:value pair to the user's row
//   await ddb
//     .update({
//       TableName: process.env.TRACKING_TABLE,
//       Key: { random_id: body.random_id },
//       ReturnValues: "ALL_NEW",
//       UpdateExpression: "set #key = :value",
//       ExpressionAttributeNames: { "#key": body.key },
//       ExpressionAttributeValues: { ":value": body.value },
//     })
//     .promise();
//   // Return success
//   return {
//     statusCode: 200,
//     headers: HEADERS,
//   };
// });
// const logStatistic = (ddb, stat) => {
//   return ddb
//     .update({
//       TableName: process.env.STATISTICS_TABLE,
//       Key: { statistic: stat },
//       ReturnValues: "NONE",
//       UpdateExpression: "add #key :value",
//       ExpressionAttributeNames: { "#key": "value" },
//       ExpressionAttributeValues: { ":value": 1 },
//     })
//     .promise();
// };
// const normalizeReferral = (referred_by) => {
//     // check for illegal characters
//     const givenChunks = referred_by.split('-');
//     return (givenChunks[0] + '-' + givenChunks[1].substring(0,3));  
// }
// const logReferral = async (ddb, referred_by, referralName) => {
//   var referralQuery = {
//     TableName: process.env.REGISTRATION_TABLE,
//     IndexName: "referralsIndex",
//     KeyConditionExpression: "referral_id = :v_refer",
//     ExpressionAttributeValues: { ":v_refer": referred_by },
//   };
//   const resp = await ddb.query(referralQuery).promise();
//   // await sendReferralNotificationEmail(resp.Items[0].name, resp.Items[0].email, referred_by, referralName)
//   return ddb
//     .update({
//       TableName: process.env.REGISTRATION_TABLE,
//       Key: { email: resp.Items[0].email },
//       ReturnValues: "NONE",
//       UpdateExpression: "add #key :value",
//       ExpressionAttributeNames: { "#key": "referral_count" },
//       ExpressionAttributeValues: { ":value": 1 },
//     })
//     .promise();
// };
// // /update - Sends an update to slack
// module.exports.update = withSentry(async () => {
//   const ddb = new AWS.DynamoDB.DocumentClient();
//   const statsTable = process.env.STATISTICS_TABLE;
//   const registrationTable = process.env.REGISTRATION_TABLE;
//   const mentorTable = process.env.MENTOR_TABLE;
//   const volunteerTable = process.env.VOLUNTEER_TABLE;
//   // Can't simply scan a table to get the count once it's over 1mb in size (~950 registrations)
//   // must use pagination instead, so the following doesn't work:
  
//   // const hackers = await ddb.scan({
//   //   TableName: registrationTable,
//   //   Select: "COUNT",
//   // }).promise();
  
  
//   let scanParams = {
//     TableName: registrationTable,
//     Select: "COUNT",
//   };
//   let hackersCount = 0;
//   let hackers;
  
//   // must use pagination to get full size of hacker registration table
//   // "LastEvaluatedKey" is where the last scan left off, so it keeps going until this doesn't exist
//   do {
//     hackers = await ddb.scan(scanParams).promise();
//     hackersCount += hackers.Count;
//     scanParams.ExclusiveStartKey = hackers.LastEvaluatedKey;
//   } while (hackers.LastEvaluatedKey);
//   const mentors = await ddb.scan({
//     TableName: mentorTable,
//     Select: "COUNT",
//   }).promise();
//   const volunteers = await ddb.scan({
//     TableName: volunteerTable,
//     Select: "COUNT",
//   }).promise();
//   const params = {
//     TableName: statsTable,
//     Select: "ALL_ATTRIBUTES",
//   };
//   // Prepare the slack webhook
//   const webhookUrl = "https://hooks.slack.com/services/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";
//   const webhook = new IncomingWebhook(webhookUrl);
//   // Collect statistic data
//   const trackArr = [];
//   const hfArr = [];
//   let registrations = 0;
//   let pageViews = 0;
//   let volunteerRegistrations = 0;
//   let mentorRegistrations = 0;
//   const stats = await ddb.scan(params).promise();
//   stats.Items.forEach((stat) => {
//     if (stat.statistic === "registrations") { // save for later
//       registrations = hackersCount;
//       volunteerRegistrations = volunteers.Count;
//       mentorRegistrations = mentors.Count;
//     } else if (stat.statistic === "page-view") {
//       pageViews = stat.value;
//     } else if (stat.statistic.startsWith("track-")) {
//       let track = stat.statistic.replace("track-", "");
//       let waitlist = false;
//       if (track.startsWith("waitlist-")) {
//         waitlist = true;
//         track = track.replace("waitlist-", "");
//       }
//       track = track.split('_')
//         .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
//         .join(' ');
//       if (waitlist) {
//         track = `Waitlist (${track})`;
//       }
//       trackArr.push(`${stat.value} ${track}`);
//     } else if (stat.statistic.startsWith("hf-")) {
//       let hf = stat.statistic.replace("hf-", "");
//       hf = hf.charAt(0).toUpperCase() + hf.slice(1);
//       hfArr.push(`${stat.value} ${hf}`);
//     }
//   });
//   // Sort strings ignoring the statistic value
//   const sortWithoutStatisticValue = ((a,b) => {
//     a = a.replace(/[0-9]/g, '');
//     b = b.replace(/[0-9]/g, '');
//     return a.localeCompare(b);
//   });
//   // Format statistic update
//   let statArr = [];
//   statArr.push(`*${registrations} Hacker Registrations*`);
//   statArr.push(`*${mentorRegistrations} Mentor Registrations*`);
//   statArr.push(`*${volunteerRegistrations} Volunteer Registrations*`);
//   statArr.push("~~~~~~~~~~~");
//   statArr = statArr.concat(trackArr.sort(sortWithoutStatisticValue));
//   statArr.push("~~~~~~~~~~~");
//   statArr = statArr.concat(hfArr.sort(sortWithoutStatisticValue));
//   statArr.push(`${pageViews} Page Views`)
//   // Send the statistic update to slack
//   await webhook.send({
//     text:
//       `Registration update for ` +
//       `${new Date().toLocaleString("en-US", {
//         timeZone: "America/New_York",
//         dateStyle: "short",
//         timeStyle: "short"
//       })} ET:\n\n` +
//       `${Array.from(statArr).join("\n")}`,
//   });
// });
<template>
    <div class="instructions-popup">
        <p>
            <ol>
                <li>Click Sign Up to create an account.</li>
                <li>Enter the email you would like your account to be associated with and complete all required fields.</li>
                <li>Once completed, you can browse potential compatible teammates on the tiles page.</li>
                <li>Reach out to them via email or Slack to connect.</li>
                <li>After forming a team, delete your profile to remove yourself from the pool:</li>
                <ul>
                    <li>Click the profile icon to go to the Edit Profile page.</li>
                    <li>Enter the same email you used during sign-up.</li>
                    <li>Scroll down and click Delete Profile.</li>
                </ul>
            </ol>
        </p>
    </div>
  </template>
  
  <script setup>
  // keep it simple for now
  </script>
  
  <style scoped>
  .instructions-popup {
    background: white;
    border: 1px solid #ccc;
    padding: 1rem;
    position: absolute;
    top: 60px;
    right: 0px;
    width: 300px;
    z-index: 1000;
    border-radius: 8px;
  }
  </style>
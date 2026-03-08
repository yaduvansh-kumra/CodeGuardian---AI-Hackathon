# 🛡️ Code Guardian: AWS AI for Bharat Hackathon

An educational VS Code extension designed to stop the "mindless AI copy-paste" habit. Code Guardian intercepts AI-generated code and forces developers to explain the logic before they can move on. 

### ✨ Core Features (MVP)
* **AI-Powered Grading:** Uses Google Gemini (via AWS Lambda) to grade the user's explanation of the code (0-100 scale).
* **The 70% Threshold:** Users must score 70% or higher to prove understanding.
* **The "3-Strike" ELI5 Fallback:** If a user fails to explain the code 3 times, the extension switches to an "Explain Like I'm 5" mode, using real-world analogies to teach the concept.
* **Cloud Logging:** All sessions, scores, and strikes are logged in Amazon DynamoDB.

### 👨‍💻 How to Run Locally (For Judges)
To test this extension on your local machine:
1. Clone this repository and open the folder in VS Code.
2. Open a terminal and run: `npm install`
3. Compile the code by running: `npm run compile`
4. Press **F5** (or click the "Run and Debug" play button). A new "Extension Development Host" window will open.
5. In the new window, paste some code, highlight it, and trigger the `Code Guardian: Evaluate Code` command via the Command Palette (`Ctrl+Shift+P`).

### 🚀 Future Scope
While our MVP proves the core AI grading logic, our production roadmap includes:
* **Auto-Paste Interception:** Hooking into VS Code's clipboard API to automatically trigger the prompt the moment code is pasted, rather than relying on manual highlighting.
* **Multilingual Support:** Allowing users to explain code and receive ELI5 analogies in native regional languages (Hindi, Tamil, etc.) to support Bharat's diverse developer base.
* **Voice-to-Explain (Audio Transcription):** Integrating audio input so users can verbally explain the code instead of typing.
* **Gamification:** Awarding "Knowledge Points" and streaks for successful explanations to make learning addictive.
* **Interview Prep Mode:** Dynamically generating technical Q&A rounds based on the specific code snippet the user is trying to use.
* **AI Code Optimization & Bonus Tips:** Providing contextual pop-ups (e.g., "Fun Fact: Using this String library is O(1) time complexity!") alongside the ELI5 explanation.

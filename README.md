🏅 Hackathon Details
Event: AWS AI for Bharat Hackathon 2026

Track: Student Track 1 – AI for Learning and Developer Productivity

Submission Date: February 15, 2026

Problem Statement: Build an AI-powered solution that helps people learn faster, work smarter, or become more productive while building or understanding technology.


# 🛡️ CodeGuardian: AI Learning Enforcer for Bharat

[![AWS AI for Bharat Hackathon 2026](https://img.shields.io/badge/AWS-AI%20for%20Bharat%202026-orange)]()
[![Track](https://img.shields.io/badge/Track-Student%20Track%201-blue)]()

## 🎯 Problem Statement

70% of Indian CS students rely on AI-generated code without understanding fundamentals, leading to high technical interview failure rates.

Current tools (GitHub Copilot, ChatGPT) enable blind copy-pasting with zero learning verification, creating a generation of "prompt engineers" who cannot code independently.

## 💡 Our Solution

**CodeGuardian** is a VS Code extension that intercepts AI-generated code and forces students to demonstrate understanding before execution.

### How It Works

1. **Detect** – Identifies AI-generated code insertions via pattern analysis.  
2. **Challenge** – Prompts the student: *"Explain this code in your words"* (text or voice in Hindi/English).  
3. **Verify** – AWS Bedrock grades explanation quality (0–100 score).  
4. **Unlock** – Code executes only if the score is ≥ 70%.  
5. **Track** – Weekly reports show AI dependency ratio and interview readiness.

---

## 🏗️ AWS Architecture

![System Architecture](architecture-diagram.png)

### AWS Services Used

- **Amazon Bedrock** (Claude 3.5 Sonnet) – Grade explanation quality  
- **AWS Lambda** – Real-time code analysis and orchestration  
- **Amazon Transcribe** – Hindi voice input support  
- **Amazon DynamoDB** – User progress tracking  
- **AWS Amplify** – Web dashboard hosting  
- **Amazon Comprehend** – Plagiarism detection  
- **AWS KMS** – Encryption for sensitive data at rest  

---

## 📊 Expected Impact

| Metric                          | Target                      |
|---------------------------------|-----------------------------|
| Students Supported              | 100,000 in Phase 1          |
| AI Dependency Reduction         | 70% → 30% in 30 days        |
| Interview Pass Rate Improvement | +40%                        |
| Student Retention               | 80% after 2 weeks           |
| Cost per Student                | < ₹5/month (AWS Free Tier)  |

---

## 🇮🇳 Bharat Focus

- **Hindi Voice Support** – Amazon Transcribe enables Tier 2–3 city students to explain in their native language.  
- **Government Alignment** – Supports India AI Mission's 13,500 scholar upskilling initiative.  
- **Affordable Pricing** – ₹299/month premium tier (vs ₹5,000+ international tools).  
- **Cultural Context** – No student shaming; gamified progressive difficulty to build confidence.  

---

## 🏆 Unique Differentiators

- **First AWS Bedrock-powered learning guardrail** (not just content delivery).  
- **Real-time prevention** (not post-assessment like LeetCode).  
- **Outcome-driven metrics** (interview readiness, not just grades).  
- **Inclusive design** (Hindi support for non–English-first learners).  

---

## 📁 Repository Structure

```
CodeGuardian-AI-Hackathon/

├── requirements.md          # Functional & non-functional requirements
├── design.md                # System architecture & AWS design
├── architecture-diagram.png # AWS components visual
├── README.md                # This file
└── docs/
    └── presentation.pdf     # Hackathon pitch deck
```
👥 Team Name - The Sentinels

Member 1 - Abhinav Khare
(https://github.com/Cosmicloader)
(www.linkedin.com/in/abhinav-khare-91369726b)

Member 2 - Nishtha Taneja
(https://github.com/nishtha-taneja-27)
(https://www.linkedin.com/in/nishtha-taneja-889721374/)

Member 3 - Yaduvansh Kumra
(https://github.com/yaduvansh-kumra)
(https://www.linkedin.com/in/yaduvansh-kumra-9a1248380/)





Built with ❤️ for India's 1.5M CS students graduating annually.


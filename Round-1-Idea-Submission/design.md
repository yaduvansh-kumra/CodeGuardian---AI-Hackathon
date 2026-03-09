# 🛡️ Design Document — CodeGuardian VS Code Extension

## Overview

CodeGuardian is a VS Code extension that prevents blind usage of AI-generated code by requiring students to demonstrate understanding before execution.

When AI-generated code is detected, the extension locks execution and asks the student to explain the code in English or Hindi. An AI grader evaluates the explanation and unlocks execution only if sufficient understanding is demonstrated.

The system targets Indian CS students (ages 18–22) and aims to reduce AI dependency while improving technical interview readiness.

---

## Problem Statement

AI tools like GitHub Copilot and ChatGPT are causing students to:

- Copy code without understanding  
- Lose problem-solving ability  
- Become dependent on AI assistance  
- Perform poorly in technical interviews  

Current tools generate code but do not verify learning.

---

## Proposed Solution

CodeGuardian introduces an **AI Learning Guardrail** that enforces understanding before code execution.

### Core Flow

**Detect → Explain → Verify → Execute**

Additionally, if students fail to explain after retries:

## 🔥 ELI5 Mode activates

The AI teaches the concept in simple terms before allowing execution.

This transforms the system from a blocker into a learning assistant.

---

## System Architecture

### Client — VS Code Extension

Core components:

- AI Code Detector  
- Explanation UI  
- Code Execution Gate  
- Local Progress Tracker  

### Backend — AWS Services

- Amazon Bedrock (Claude 3.5 Sonnet) — grading & tutoring  
- AWS Lambda — request handling  
- Amazon Transcribe — voice input  
- Amazon Comprehend — plagiarism detection  
- DynamoDB — session storage  
- AWS Amplify — web dashboard  

---

## High-Level Architecture

```
VS Code Extension
      ↓
  API Gateway
      ↓
 Lambda Functions
      ↓
Bedrock / Transcribe / Comprehend
      ↓
DynamoDB + Amplify Dashboard
```

---

## Core Workflow

1. Student pastes AI-generated code  
2. Extension detects AI patterns  
3. Code execution is locked  
4. Student submits explanation  
5. AI grades understanding  
6. If score ≥ 70 → unlock  
7. Else → hints + retry  
8. After 3 failures → ELI5 Mode  

---

## 🔥 ELI5 Guided Learning Mode (Unique Feature)

When students fail to demonstrate understanding after retries, the system switches from evaluation to teaching.

ELI5 Mode provides:

- Simple explanations  
- Real-world analogies  
- Step-by-step concept breakdown  
- Practice question to verify learning  

Code unlocks only after concept comprehension.

This ensures learning instead of punishment.

---

## Key Features

### AI Code Detection
Identifies pasted AI-generated code using behavior and pattern analysis.

### Explanation Verification
Students explain code via text or voice in English or Hindi.

### Execution Control
Prevents running code without understanding.

### Retry & Hint System
Guided hints help students improve explanations.

### Progress Tracking
Tracks AI dependency and interview readiness.

---

## AWS Usage

### Amazon Bedrock
Evaluates explanations and powers ELI5 tutoring.

### Amazon Transcribe
Supports Hindi and English voice explanations.

### Amazon Comprehend
Detects copied explanations.

### DynamoDB
Stores sessions and metrics securely.

### AWS Amplify
Hosts the progress dashboard.

---

## Feasibility for Hackathon MVP

Phase 1 implementation will include:

- AI code detection  
- Explanation grading  
- Execution lock/unlock  
- Retry system  
- ELI5 Mode  
- Basic dashboard  

Designed to run within AWS free-tier credits.

---

## Expected Impact

CodeGuardian aims to:

- Reduce AI dependency from 70% → 30%  
- Improve interview performance  
- Promote real learning  
- Support students across Tier 1–3 cities  

---

## Future Scope

- Educator dashboards  
- Offline mode  
- Gamification  
- Institutional deployment  

---

## Conclusion

CodeGuardian converts AI from a shortcut into a learning tool by ensuring that students understand code before using it. With bilingual support and guided teaching through ELI5 Mode, the system addresses the growing problem of AI dependency among students while remaining practical to build within hackathon constraints.

# Design Document: CodeGuardian VS Code Extension

## Overview

CodeGuardian is a VS Code extension that intercepts AI-generated code, prompts students to demonstrate understanding through explanations, and uses AWS Bedrock (Claude 3.5 Sonnet) to grade comprehension before allowing code execution. The system is designed to reduce AI dependency among Indian CS students from 70% to 30% within 30 days while improving technical interview pass rates by 40%.

The architecture follows a client-server model where the VS Code extension acts as the client, and AWS services provide the backend infrastructure for AI grading, voice transcription, data storage, and web dashboard hosting. The design prioritizes low latency (<2s for grading), cost efficiency (₹5/student/month), and bilingual support (English and Hindi).

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     VS Code Extension (Client)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ AI Code      │  │ Explanation  │  │ Code Execution       │  │
│  │ Detector     │  │ UI Component │  │ Gate                 │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────────────┘  │
│         │                  │                  │                  │
│  ┌──────┴──────────────────┴──────────────────┴───────────────┐ │
│  │           Extension Core (State Management)                 │ │
│  └──────────────────────────┬──────────────────────────────────┘ │
└─────────────────────────────┼────────────────────────────────────┘
                              │ HTTPS/TLS 1.3
                              │
┌─────────────────────────────┼────────────────────────────────────┐
│                    AWS Backend Services                          │
│                              │                                    │
│  ┌───────────────────────────┼──────────────────────────────┐   │
│  │         API Gateway + Lambda (Request Router)             │   │
│  └───┬───────────┬───────────┬──────────────┬────────────┬───┘   │
│      │           │           │              │            │       │
│  ┌───▼────┐  ┌──▼─────┐  ┌──▼──────┐  ┌───▼─────┐  ┌──▼─────┐ │
│  │Bedrock │  │Transcr-│  │Compreh- │  │DynamoDB │  │Amplify │ │
│  │Claude  │  │ibe     │  │end      │  │         │  │Web     │ │
│  │3.5     │  │(Voice) │  │(Plagia- │  │(Data)   │  │Dashbrd │ │
│  │Sonnet  │  │        │  │rism)    │  │         │  │        │ │
│  └────────┘  └────────┘  └─────────┘  └────┬────┘  └────────┘ │
│                                             │                    │
│                                        ┌────▼────┐               │
│                                        │AWS KMS  │               │
│                                        │(Encrypt)│               │
│                                        └─────────┘               │
└──────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**VS Code Extension Components:**

1. **AI Code Detector**
   - Monitors clipboard and paste events
   - Analyzes code patterns to detect AI-generated code
   - Distinguishes between AI code, manual typing, and educational resources
   - Triggers explanation prompt when AI code is detected

2. **Explanation UI Component**
   - Displays modal dialog for explanation input
   - Provides text and voice input options
   - Supports English and Hindi language selection
   - Shows character counter and real-time transcription feedback
   - Displays grading results, scores, and hints

3. **Code Execution Gate**
   - Intercepts code execution attempts (Run button, terminal commands)
   - Maintains locked/unlocked state for code blocks
   - Persists lock state across VS Code restarts
   - Displays inline decorations for locked code

4. **Extension Core**
   - Manages application state and session data
   - Handles authentication and token management
   - Coordinates communication between components
   - Implements offline queue for pending submissions
   - Manages local storage and caching

**AWS Backend Components:**

1. **AWS Lambda Functions**
   - `gradeExplanation`: Routes explanation to Bedrock and processes response
   - `transcribeVoice`: Handles voice-to-text conversion via Transcribe
   - `checkPlagiarism`: Detects copied content using Comprehend
   - `saveSession`: Stores session data in DynamoDB
   - `getProgress`: Retrieves student metrics and calculates scores
   - `syncOfflineData`: Processes queued offline submissions

2. **Amazon Bedrock (Claude 3.5 Sonnet)**
   - Evaluates explanation quality and depth
   - Generates Understanding_Score (0-100)
   - Provides specific feedback on strengths and gaps
   - Generates progressive hints based on identified gaps

3. **Amazon Transcribe**
   - Converts Hindi and English voice to text
   - Provides real-time streaming transcription
   - Handles accent variations across Indian regions

4. **Amazon Comprehend**
   - Detects plagiarism by comparing against known sources
   - Identifies copied content patterns
   - Supports English and Hindi text analysis

5. **DynamoDB Tables**
   - Stores student profiles, session history, and progress metrics
   - Provides fast read/write access (<100ms)
   - Supports auto-scaling for variable load

6. **AWS Amplify**
   - Hosts web-based Progress Dashboard
   - Provides responsive UI for mobile and desktop
   - Handles authentication and API integration

7. **AWS KMS**
   - Encrypts data at rest in DynamoDB
   - Manages encryption keys for sensitive data
   - Ensures compliance with data protection regulations

## AWS Architecture Diagram

### Complete System Architecture with Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              STUDENT'S VS CODE EDITOR                            │
│                                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  AI Code     │    │ Explanation  │    │ Code Exec    │    │  Progress    │ │
│  │  Detector    │───▶│ UI Component │───▶│ Gate         │───▶│  Tracker     │ │
│  │  (Local)     │    │ (Modal)      │    │ (Lock/Unlock)│    │  (Local)     │ │
│  └──────────────┘    └──────┬───────┘    └──────────────┘    └──────┬───────┘ │
│                              │                                        │         │
│  [1] Paste Code ──▶ [2] Detect AI ──▶ [3] Prompt Explanation        │         │
│                              │                                        │         │
└──────────────────────────────┼────────────────────────────────────────┼─────────┘
                               │                                        │
                               │ [4] Submit Explanation                 │ [10] Fetch
                               │     (Text or Voice)                    │      Progress
                               │                                        │
                               │ HTTPS/TLS 1.3                          │
                               │ Authorization: Bearer <JWT>            │
                               │                                        │
┌──────────────────────────────▼────────────────────────────────────────▼─────────┐
│                                                                                  │
│                            AWS API GATEWAY                                       │
│                         (Regional Endpoint)                                      │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐    │
│  │  Lambda Authorizer: Validate JWT Token                                 │    │
│  │  - Check signature and expiration                                      │    │
│  │  - Cache validation for 5 minutes                                      │    │
│  └────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└──────────┬───────────────────┬───────────────────┬──────────────────┬───────────┘
           │                   │                   │                  │
           │ [5a] Text         │ [5b] Voice        │ [5c] Check       │ [11] Get
           │     Explanation   │      Audio        │      Plagiarism  │      Progress
           │                   │                   │                  │
┌──────────▼─────────┐  ┌──────▼──────────┐  ┌────▼──────────┐  ┌───▼──────────────┐
│                    │  │                 │  │               │  │                  │
│  Lambda Function:  │  │ Lambda Function:│  │Lambda Function│  │Lambda Function:  │
│  gradeExplanation  │  │ transcribeVoice │  │checkPlagiarism│  │  getProgress     │
│                    │  │                 │  │               │  │                  │
│  [6] Prepare       │  │ [6b] Stream     │  │ [6c] Analyze  │  │ [12] Query       │
│      Bedrock       │  │      to         │  │      text     │  │      DynamoDB    │
│      prompt        │  │      Transcribe │  │      patterns │  │      tables      │
│                    │  │                 │  │               │  │                  │
└──────────┬─────────┘  └──────┬──────────┘  └────┬──────────┘  └───┬──────────────┘
           │                   │                   │                 │
           │ [7] Invoke        │ [7b] Convert      │ [7c] Detect     │
           │     Claude        │      Speech       │      Copied     │
           │                   │      to Text      │      Content    │
           │                   │                   │                 │
┌──────────▼─────────┐  ┌──────▼──────────┐  ┌────▼──────────┐     │
│                    │  │                 │  │               │     │
│  Amazon Bedrock    │  │    Amazon       │  │   Amazon      │     │
│  Claude 3.5 Sonnet │  │   Transcribe    │  │  Comprehend   │     │
│                    │  │                 │  │               │     │
│  - Evaluate        │  │ - Hindi Support │  │ - Entity      │     │
│    explanation     │  │ - English       │  │   Detection   │     │
│  - Generate score  │  │   Support       │  │ - Sentiment   │     │
│  - Create feedback │  │ - Real-time     │  │   Analysis    │     │
│  - Generate hints  │  │   Streaming     │  │               │     │
│                    │  │                 │  │               │     │
└──────────┬─────────┘  └──────┬──────────┘  └────┬──────────┘     │
           │                   │                   │                │
           │ [8] Return        │ [8b] Return       │ [8c] Return    │
           │     Score +       │      Text         │      Plagiarism│
           │     Feedback      │                   │      Flag      │
           │                   │                   │                │
           └───────────────────┴───────────────────┘                │
                               │                                    │
                               │ [9] Save Session Data              │
                               │                                    │
                    ┌──────────▼────────────┐                       │
                    │                       │                       │
                    │  Lambda Function:     │                       │
                    │  saveSession          │                       │
                    │                       │                       │
                    │  - Store session      │                       │
                    │  - Update metrics     │                       │
                    │  - Calculate scores   │                       │
                    │                       │                       │
                    └──────────┬────────────┘                       │
                               │                                    │
                               │ [10] Write/Read                    │
                               │                                    │
┌──────────────────────────────▼────────────────────────────────────▼─────────────┐
│                                                                                  │
│                              AMAZON DYNAMODB                                     │
│                          (On-Demand Capacity)                                    │
│                                                                                  │
│  ┌────────────────────────┐  ┌────────────────────────┐  ┌──────────────────┐  │
│  │  StudentProfile Table  │  │  SessionHistory Table  │  │ ProgressMetrics  │  │
│  │                        │  │                        │  │     Table        │  │
│  │  PK: studentId         │  │  PK: studentId         │  │ PK: studentId    │  │
│  │                        │  │  SK: sessionId         │  │ SK: periodId     │  │
│  │  - email               │  │                        │  │                  │  │
│  │  - name                │  │  - codeSnippet (enc)   │  │ - totalSessions  │  │
│  │  - university          │  │  - explanation (enc)   │  │ - aiDependency   │  │
│  │  - aiDependencyRatio   │  │  - score               │  │ - avgScore       │  │
│  │  - readinessScore      │  │  - passed              │  │ - languageStats  │  │
│  │  - preferredLanguage   │  │  - attemptCount        │  │                  │  │
│  │                        │  │  - feedback            │  │                  │  │
│  │  GSI: university-      │  │  - programmingLanguage │  │ GSI: periodId-   │  │
│  │       lastActiveAt     │  │  - inputMethod         │  │      readiness   │  │
│  │                        │  │  - ttl (90 days)       │  │                  │  │
│  └────────────────────────┘  └────────────────────────┘  └──────────────────┘  │
│                                                                                  │
│  ┌────────────────────────┐                                                     │
│  │  Achievements Table    │         Encryption at Rest:                         │
│  │                        │         ┌──────────────────────────────┐            │
│  │  PK: studentId         │         │        AWS KMS               │            │
│  │  SK: achievementId     │◀────────│  (Customer Managed Keys)     │            │
│  │                        │         │                              │            │
│  │  - type                │         │  - codeguardian-pii-key      │            │
│  │  - title               │         │  - codeguardian-code-key     │            │
│  │  - completed           │         │  - codeguardian-metrics-key  │            │
│  │  - earnedAt            │         │                              │            │
│  └────────────────────────┘         │  Auto-rotation: 365 days     │            │
│                                     └──────────────────────────────┘            │
│                                                                                  │
│  DAX (DynamoDB Accelerator) - Caching Layer                                     │
│  - Cache TTL: 5 minutes for profiles, 1 minute for sessions                     │
│  - Read latency: <1ms for cached data                                           │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ [13] Dashboard queries
                                       │      progress data
                                       │
┌──────────────────────────────────────▼───────────────────────────────────────────┐
│                                                                                   │
│                              AWS AMPLIFY                                          │
│                         (Web Dashboard Hosting)                                   │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    Progress Dashboard (React SPA)                        │    │
│  │                                                                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │    │
│  │  │ AI Dependency│  │  Interview   │  │   Weekly     │  │ Language   │ │    │
│  │  │   Trends     │  │  Readiness   │  │   Streak     │  │ Breakdown  │ │    │
│  │  │   Chart      │  │   Score      │  │   Counter    │  │  Stats     │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │    │
│  │                                                                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │    │
│  │  │ Recent       │  │ Achievements │  │  Session     │  │ Improvement│ │    │
│  │  │ Sessions     │  │   & Badges   │  │  History     │  │ Suggestions│ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │    │
│  │                                                                          │    │
│  │  [14] Student views progress, trends, and achievements                  │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
│  CloudFront CDN Distribution                                                     │
│  - Global edge locations for low latency                                         │
│  - HTTPS only with TLS 1.3                                                       │
│  - Gzip compression for assets                                                   │
│                                                                                   │
│  S3 Static Hosting                                                               │
│  - React build artifacts                                                         │
│  - Versioned deployments                                                         │
│  - Automatic invalidation on deploy                                              │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘


DATA FLOW SUMMARY:
═══════════════════

[1] Student pastes AI-generated code in VS Code
[2] AI Code Detector analyzes locally (<500ms)
[3] Explanation modal appears with text/voice options
[4] Student submits explanation (text or voice)
[5a] Text explanation sent to API Gateway → gradeExplanation Lambda
[5b] Voice audio sent to API Gateway → transcribeVoice Lambda
[5c] Explanation sent to checkPlagiarism Lambda
[6] Lambda prepares Bedrock prompt with code context
[6b] Lambda streams audio to Amazon Transcribe
[6c] Lambda sends text to Amazon Comprehend
[7] Bedrock evaluates explanation and generates score + feedback
[7b] Transcribe converts speech to text (Hindi/English)
[7c] Comprehend detects plagiarism patterns
[8] Bedrock returns Understanding_Score (0-100) + feedback + hints
[8b] Transcribe returns transcribed text
[8c] Comprehend returns plagiarism flag
[9] saveSession Lambda stores session data in DynamoDB
[10] DynamoDB persists encrypted session, updates metrics
[11] getProgress Lambda queries DynamoDB for student metrics
[12] DynamoDB returns progress data (AI ratio, readiness score, trends)
[13] Amplify dashboard fetches progress via API Gateway
[14] Student views comprehensive progress dashboard with charts

SECURITY LAYERS:
═══════════════

• TLS 1.3 encryption for all data in transit
• JWT token authentication on all API requests
• AWS KMS encryption for data at rest in DynamoDB
• Field-level encryption for code snippets and explanations
• IAM roles with least privilege for Lambda functions
• VPC endpoints for private AWS service communication
• CloudWatch logging with PII redaction
• Rate limiting and DDoS protection via API Gateway
```

### Data Flow

**Primary Flow: Code Interception → Explanation → Grading → Unlock**

1. Student pastes code in VS Code
2. AI Code Detector analyzes code patterns (local, <500ms)
3. If AI-generated, Code Execution Gate locks the code
4. Explanation modal appears with text/voice options
5. Student submits explanation (text or voice)
6. If voice: Lambda calls Transcribe → text conversion
7. Lambda calls Comprehend for plagiarism check
8. Lambda calls Bedrock with explanation + code context
9. Bedrock returns Understanding_Score + feedback
10. Lambda saves session to DynamoDB
11. Response sent to extension with score and feedback
12. If score ≥70%: unlock code; else: show hints and retry option

## Sequence Diagrams

### 1. Code Interception and Lock Flow

```
Student    Extension    AI_Detector    Code_Gate    Lambda    DynamoDB
  │            │             │            │           │          │
  │──Paste─────>│            │            │           │          │
  │            │──Analyze───>│            │           │          │
  │            │             │            │           │          │
  │            │<─AI Code────│            │           │          │
  │            │             │            │           │          │
  │            │─────────Lock Code───────>│           │          │
  │            │             │            │           │          │
  │<─Show Modal│             │            │           │          │
  │            │             │            │           │          │
  │            │─────────────────────Create Session──>│          │
  │            │             │            │           │──Save───>│
  │            │             │            │           │<─OK──────│
  │            │             │            │           │          │
```

### 2. Explanation Grading Flow (Text Input)

```
Student  Extension  Lambda:grade  Bedrock  Comprehend  DynamoDB
  │         │            │          │          │          │
  │─Submit──>│           │          │          │          │
  │  Text   │           │          │          │          │
  │         │──POST─────>│          │          │          │
  │         │ /grade     │          │          │          │
  │         │            │          │          │          │
  │         │            │──Check──>│          │          │
  │         │            │ Plagiar. │          │          │
  │         │            │<─Result──│          │          │
  │         │            │          │          │          │
  │         │            │──Grade──────────────>│          │
  │         │            │ Explanation          │          │
  │         │            │<─Score + Feedback────│          │
  │         │            │          │          │          │
  │         │            │─────────────────Save Session───>│
  │         │            │          │          │          │
  │         │<─Response──│          │          │          │
  │         │ {score:85} │          │          │          │
  │<─Unlock─│            │          │          │          │
  │  Code   │            │          │          │          │
```

### 3. Voice Input Flow

```
Student  Extension  Lambda:transcribe  Transcribe  Lambda:grade  Bedrock
  │         │              │               │            │           │
  │─Record──>│             │               │            │           │
  │  Voice  │             │               │            │           │
  │         │──POST───────>│              │            │           │
  │         │ /transcribe  │              │            │           │
  │         │              │──Stream─────>│            │           │
  │         │              │  Audio       │            │           │
  │         │              │<─Text────────│            │           │
  │         │<─Realtime────│              │            │           │
  │         │  Feedback    │              │            │           │
  │         │              │              │            │           │
  │─Submit──>│             │              │            │           │
  │         │──────────────────────POST──────────────>│           │
  │         │              │              │  /grade    │           │
  │         │              │              │            │──Eval────>│
  │         │              │              │            │<─Score────│
  │         │<─────────────────────Response────────────│           │
  │         │              │              │            │           │
```

### 4. Retry and Hint Flow

```
Student  Extension  Lambda:grade  Bedrock  DynamoDB
  │         │            │          │          │
  │─Submit──>│           │          │          │
  │ Attempt1│──POST─────>│          │          │
  │         │            │──Grade──>│          │
  │         │            │<─Score:45│          │
  │         │            │  Gaps:[] │          │
  │         │            │──Save───────────────>│
  │         │            │ attempt=1│          │
  │         │<─Response──│          │          │
  │<─Show───│ score:45   │          │          │
  │  Hint1  │ hint:20%   │          │          │
  │         │            │          │          │
  │─Submit──>│           │          │          │
  │ Attempt2│──POST─────>│          │          │
  │         │            │──Grade──>│          │
  │         │            │<─Score:60│          │
  │         │            │──Save───────────────>│
  │         │            │ attempt=2│          │
  │         │<─Response──│          │          │
  │<─Show───│ score:60   │          │          │
  │  Hint2  │ hint:40%   │          │          │
  │         │            │          │          │
  │─Submit──>│           │          │          │
  │ Attempt3│──POST─────>│          │          │
  │         │            │──Grade──>│          │
  │         │            │<─Score:75│          │
  │         │            │──Save───────────────>│
  │         │            │ attempt=3│          │
  │         │<─Response──│          │          │
  │<─Unlock─│ score:75   │          │          │
  │  Code   │ SUCCESS!   │          │          │
```

### 5. Offline Mode and Sync Flow

```
Student  Extension  LocalStorage  Lambda:sync  DynamoDB
  │         │            │             │           │
  │─Submit──>│           │             │           │
  │ (Offline)│          │             │           │
  │         │──Queue────>│            │           │
  │         │            │            │           │
  │<─Pending│            │            │           │
  │  Status │            │            │           │
  │         │            │            │           │
  │         │            │            │           │
  │         │◄─Network Restored───────┤           │
  │         │            │            │           │
  │         │──Get Queue─>│           │           │
  │         │<─Sessions──│            │           │
  │         │            │            │           │
  │         │──POST──────────────────>│           │
  │         │ /sync (batch)           │           │
  │         │            │            │──Bulk────>│
  │         │            │            │  Insert   │
  │         │            │            │<─OK───────│
  │         │<─Response──────────────│            │
  │         │            │            │           │
  │         │──Clear─────>│           │           │
  │         │   Queue    │           │           │
  │<─Synced─│            │           │           │
  │  Status │            │           │           │
```

## Components and Interfaces

### VS Code Extension Components

#### 1. AI Code Detector

**Purpose:** Identify AI-generated code through pattern analysis

**Interface:**
```typescript
interface AICodeDetector {
  /**
   * Analyzes pasted code to determine if it's AI-generated
   * @param code - The code snippet to analyze
   * @param language - Programming language (js, python, java)
   * @returns Detection result with confidence score
   */
  analyzeCode(code: string, language: ProgrammingLanguage): Promise<DetectionResult>;
  
  /**
   * Distinguishes AI code from educational resources
   * @param code - The code snippet
   * @param source - Optional source URL or identifier
   */
  classifySource(code: string, source?: string): CodeSource;
}

interface DetectionResult {
  isAIGenerated: boolean;
  confidence: number; // 0-100
  patterns: string[]; // Detected AI patterns
  timestamp: Date;
}

enum CodeSource {
  AI_GENERATED = 'ai',
  MANUAL_TYPED = 'manual',
  EDUCATIONAL_RESOURCE = 'educational',
  UNKNOWN = 'unknown'
}

enum ProgrammingLanguage {
  JAVASCRIPT = 'javascript',
  PYTHON = 'python',
  JAVA = 'java'
}
```

**Detection Heuristics:**
- Paste event with >10 lines of code
- Perfect formatting and consistent style
- Presence of AI-specific comment patterns
- Unusual variable naming conventions
- Complete function implementations without incremental edits
- Clipboard metadata analysis

#### 2. Explanation UI Component

**Purpose:** Collect student explanations via text or voice

**Interface:**
```typescript
interface ExplanationUI {
  /**
   * Shows explanation modal dialog
   * @param codeSnippet - The locked code requiring explanation
   * @param language - UI language (English or Hindi)
   */
  showExplanationModal(codeSnippet: string, language: UILanguage): Promise<ExplanationSubmission>;
  
  /**
   * Displays grading results and feedback
   */
  showGradingResult(result: GradingResult): void;
  
  /**
   * Shows progressive hints after failed attempts
   */
  showHint(hint: Hint, attemptNumber: number): void;
}

interface ExplanationSubmission {
  text: string;
  inputMethod: 'text' | 'voice';
  language: 'en' | 'hi';
  duration: number; // seconds spent on explanation
  characterCount: number;
}

interface GradingResult {
  score: number; // 0-100
  passed: boolean; // score >= 70
  feedback: string;
  strengths: string[];
  gaps: string[];
  attemptNumber: number;
}

interface Hint {
  level: number; // 1, 2, or 3
  detailPercentage: number; // 20%, 40%, 60%
  content: string;
  focusAreas: string[];
}

enum UILanguage {
  ENGLISH = 'en',
  HINDI = 'hi'
}
```

#### 3. Code Execution Gate

**Purpose:** Control code execution based on understanding verification

**Interface:**
```typescript
interface CodeExecutionGate {
  /**
   * Locks a code block preventing execution
   */
  lockCode(codeBlock: CodeBlock): void;
  
  /**
   * Unlocks code after successful verification
   */
  unlockCode(codeBlock: CodeBlock, sessionId: string): void;
  
  /**
   * Checks if code block is currently locked
   */
  isLocked(codeBlock: CodeBlock): boolean;
  
  /**
   * Intercepts execution attempts
   */
  interceptExecution(executionAttempt: ExecutionAttempt): ExecutionResult;
  
  /**
   * Persists lock state across restarts
   */
  persistLockState(): Promise<void>;
  
  /**
   * Restores lock state on extension activation
   */
  restoreLockState(): Promise<void>;
}

interface CodeBlock {
  id: string;
  content: string;
  startLine: number;
  endLine: number;
  filePath: string;
  language: ProgrammingLanguage;
}

interface ExecutionAttempt {
  codeBlock: CodeBlock;
  method: 'run_button' | 'terminal' | 'debug';
  timestamp: Date;
}

interface ExecutionResult {
  allowed: boolean;
  reason?: string;
  sessionId?: string;
}
```

#### 4. Extension Core (State Management)

**Purpose:** Coordinate components and manage application state

**Interface:**
```typescript
interface ExtensionCore {
  /**
   * Initializes extension and restores state
   */
  activate(context: vscode.ExtensionContext): Promise<void>;
  
  /**
   * Handles authentication and token management
   */
  authenticate(): Promise<AuthToken>;
  
  /**
   * Manages offline queue for pending submissions
   */
  queueOfflineSubmission(submission: ExplanationSubmission): void;
  
  /**
   * Syncs offline data when connectivity restored
   */
  syncOfflineData(): Promise<SyncResult>;
  
  /**
   * Retrieves student progress metrics
   */
  getProgressMetrics(): Promise<ProgressMetrics>;
  
  /**
   * Updates AI dependency ratio
   */
  updateAIDependencyRatio(manualLines: number, aiLines: number): void;
}

interface AuthToken {
  token: string;
  expiresAt: Date;
  studentId: string;
}

interface SyncResult {
  syncedCount: number;
  failedCount: number;
  errors: string[];
}

interface ProgressMetrics {
  aiDependencyRatio: number; // 0-100
  interviewReadinessScore: number; // 0-100
  averageUnderstandingScore: number;
  totalSessions: number;
  weeklyTrend: TrendData[];
  languageBreakdown: LanguageMetrics;
}

interface TrendData {
  week: string;
  aiRatio: number;
  manualRatio: number;
}

interface LanguageMetrics {
  javascript: LanguageStats;
  python: LanguageStats;
  java: LanguageStats;
}

interface LanguageStats {
  sessionsCount: number;
  averageScore: number;
  aiDependency: number;
}
```

### AWS Lambda Function Interfaces

#### 1. Grade Explanation Function

**Endpoint:** `POST /api/grade`

**Request:**
```typescript
interface GradeExplanationRequest {
  studentId: string;
  sessionId: string;
  codeSnippet: string;
  explanation: string;
  language: 'en' | 'hi';
  programmingLanguage: ProgrammingLanguage;
  attemptNumber: number;
  previousGaps?: string[]; // From previous attempts
}
```

**Response:**
```typescript
interface GradeExplanationResponse {
  score: number; // 0-100
  passed: boolean;
  feedback: string;
  strengths: string[];
  gaps: string[];
  hint?: Hint;
  sessionId: string;
  timestamp: string;
}
```

**Processing Logic:**
1. Validate request and authenticate token
2. Check plagiarism via Comprehend
3. If plagiarism detected: reduce score by 50%
4. Send to Bedrock with prompt template
5. Parse Bedrock response
6. Generate hint if score < 70
7. Save session to DynamoDB
8. Return response

#### 2. Transcribe Voice Function

**Endpoint:** `POST /api/transcribe`

**Request:**
```typescript
interface TranscribeVoiceRequest {
  studentId: string;
  audioData: string; // Base64 encoded audio
  language: 'en' | 'hi';
  format: 'webm' | 'mp3' | 'wav';
}
```

**Response:**
```typescript
interface TranscribeVoiceResponse {
  text: string;
  confidence: number;
  duration: number; // seconds
  language: string;
}
```

#### 3. Save Session Function

**Endpoint:** `POST /api/session`

**Request:**
```typescript
interface SaveSessionRequest {
  studentId: string;
  sessionId: string;
  codeSnippet: string;
  explanation: string;
  score: number;
  passed: boolean;
  attemptCount: number;
  language: 'en' | 'hi';
  programmingLanguage: ProgrammingLanguage;
  inputMethod: 'text' | 'voice';
  duration: number;
}
```

**Response:**
```typescript
interface SaveSessionResponse {
  success: boolean;
  sessionId: string;
  updatedMetrics: {
    aiDependencyRatio: number;
    interviewReadinessScore: number;
  };
}
```

#### 4. Get Progress Function

**Endpoint:** `GET /api/progress/{studentId}`

**Response:**
```typescript
interface GetProgressResponse {
  studentId: string;
  metrics: ProgressMetrics;
  recentSessions: SessionSummary[];
  achievements: Achievement[];
  weeklyStreak: number;
}

interface SessionSummary {
  sessionId: string;
  timestamp: string;
  score: number;
  passed: boolean;
  programmingLanguage: string;
  attemptCount: number;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  earnedAt: string;
  icon: string;
}
```

#### 5. Sync Offline Data Function

**Endpoint:** `POST /api/sync`

**Request:**
```typescript
interface SyncOfflineDataRequest {
  studentId: string;
  sessions: SaveSessionRequest[];
}
```

**Response:**
```typescript
interface SyncOfflineDataResponse {
  syncedCount: number;
  failedSessions: string[]; // sessionIds that failed
  updatedMetrics: ProgressMetrics;
}
```


## Data Models

### DynamoDB Table Schemas

#### 1. StudentProfile Table

**Purpose:** Store student account information and preferences

**Table Name:** `CodeGuardian_StudentProfile`

**Schema:**
```typescript
interface StudentProfile {
  // Partition Key
  studentId: string; // PK: "STUDENT#{uuid}"
  
  // Attributes
  email: string;
  name: string;
  university: string;
  enrollmentDate: string; // ISO 8601
  preferredLanguage: 'en' | 'hi';
  tier: 1 | 2 | 3; // City tier
  
  // Metrics (updated periodically)
  aiDependencyRatio: number;
  interviewReadinessScore: number;
  totalSessions: number;
  weeklyStreak: number;
  
  // Settings
  passingThreshold: number; // Default 70
  notificationsEnabled: boolean;
  
  // Timestamps
  createdAt: string;
  updatedAt: string;
  lastActiveAt: string;
}
```

**Indexes:**
- Primary Key: `studentId` (Partition Key)
- GSI: `university-lastActiveAt-index` for institutional queries

**Capacity:**
- On-demand billing mode
- Encryption at rest via AWS KMS


#### 2. SessionHistory Table

**Purpose:** Store individual explanation sessions and grading results

**Table Name:** `CodeGuardian_SessionHistory`

**Schema:**
```typescript
interface SessionHistory {
  // Partition Key
  studentId: string; // PK: "STUDENT#{uuid}"
  
  // Sort Key
  sessionId: string; // SK: "SESSION#{timestamp}#{uuid}"
  
  // Attributes
  codeSnippet: string; // Encrypted
  explanation: string; // Encrypted
  score: number; // 0-100
  passed: boolean;
  attemptCount: number; // 1-3
  
  // Context
  programmingLanguage: 'javascript' | 'python' | 'java';
  inputMethod: 'text' | 'voice';
  language: 'en' | 'hi';
  
  // Feedback
  feedback: string;
  strengths: string[];
  gaps: string[];
  hintsProvided: string[];
  
  // Metadata
  duration: number; // seconds
  characterCount: number;
  plagiarismDetected: boolean;
  
  // Timestamps
  createdAt: string;
  completedAt: string;
  
  // TTL for data retention (90 days)
  ttl: number; // Unix timestamp
}
```

**Indexes:**
- Primary Key: `studentId` (PK), `sessionId` (SK)
- GSI: `studentId-createdAt-index` for chronological queries
- LSI: `studentId-programmingLanguage-index` for language-specific queries

**TTL Configuration:**
- Detailed session data expires after 90 days
- Aggregated metrics retained for 1 year


#### 3. ProgressMetrics Table

**Purpose:** Store aggregated weekly and monthly metrics for dashboard

**Table Name:** `CodeGuardian_ProgressMetrics`

**Schema:**
```typescript
interface ProgressMetrics {
  // Partition Key
  studentId: string; // PK: "STUDENT#{uuid}"
  
  // Sort Key
  periodId: string; // SK: "WEEK#{YYYY-WW}" or "MONTH#{YYYY-MM}"
  
  // Aggregated Metrics
  totalSessions: number;
  passedSessions: number;
  averageScore: number;
  averageAttempts: number;
  
  // Code Metrics
  aiCodeLines: number;
  manualCodeLines: number;
  aiDependencyRatio: number; // (aiCodeLines / totalLines) * 100
  
  // Language Breakdown
  javascriptSessions: number;
  pythonSessions: number;
  javaSessions: number;
  
  // Language-specific scores
  javascriptAvgScore: number;
  pythonAvgScore: number;
  javaAvgScore: number;
  
  // Engagement
  activeDays: number;
  totalDuration: number; // seconds
  voiceInputUsage: number; // percentage
  hindiUsage: number; // percentage
  
  // Interview Readiness Components
  interviewReadinessScore: number;
  manualCodingFrequency: number;
  consistencyScore: number;
  
  // Timestamps
  periodStart: string;
  periodEnd: string;
  calculatedAt: string;
}
```

**Indexes:**
- Primary Key: `studentId` (PK), `periodId` (SK)
- GSI: `periodId-interviewReadinessScore-index` for leaderboards

**Calculation Frequency:**
- Weekly metrics: Calculated every Sunday at midnight IST
- Monthly metrics: Calculated on 1st of each month


#### 4. Achievements Table

**Purpose:** Track student achievements and gamification progress

**Table Name:** `CodeGuardian_Achievements`

**Schema:**
```typescript
interface Achievement {
  // Partition Key
  studentId: string; // PK: "STUDENT#{uuid}"
  
  // Sort Key
  achievementId: string; // SK: "ACHIEVEMENT#{type}#{timestamp}"
  
  // Achievement Details
  type: AchievementType;
  title: string;
  description: string;
  icon: string;
  
  // Progress
  currentValue: number;
  targetValue: number;
  completed: boolean;
  
  // Timestamps
  earnedAt?: string;
  createdAt: string;
}

enum AchievementType {
  FIRST_70_SCORE = 'first_70_score',
  SEVEN_DAY_STREAK = '7_day_streak',
  FIFTY_PERCENT_AI_REDUCTION = '50_percent_reduction',
  HUNDRED_SESSIONS = '100_sessions',
  PERFECT_SCORE = 'perfect_score',
  MULTILINGUAL = 'multilingual', // Used both English and Hindi
  VOICE_MASTER = 'voice_master', // 50 voice explanations
}
```

**Indexes:**
- Primary Key: `studentId` (PK), `achievementId` (SK)
- LSI: `studentId-earnedAt-index` for recent achievements


### Data Encryption Strategy

**Encryption at Rest (DynamoDB):**
- All tables use AWS KMS encryption
- Customer-managed CMK (Customer Master Key)
- Separate keys for different data sensitivity levels:
  - `codeguardian-pii-key`: For student profiles and emails
  - `codeguardian-code-key`: For code snippets and explanations
  - `codeguardian-metrics-key`: For aggregated metrics

**Encryption in Transit:**
- All API calls use TLS 1.3
- Certificate pinning in VS Code extension
- HTTPS-only for Amplify dashboard

**Field-Level Encryption:**
- Code snippets encrypted before DynamoDB storage
- Explanations encrypted before storage
- Decryption only in Lambda execution context

**Key Rotation:**
- Automatic key rotation every 365 days
- Manual rotation capability for security incidents


## API Endpoint Specifications

### Authentication

All API endpoints require authentication via JWT token in the `Authorization` header.

**Header Format:**
```
Authorization: Bearer <jwt_token>
```

**Token Structure:**
```typescript
interface JWTPayload {
  studentId: string;
  email: string;
  university: string;
  iat: number; // Issued at
  exp: number; // Expires at (24 hours)
}
```

**Token Generation:**
- Tokens issued by AWS Cognito or custom Lambda authorizer
- 24-hour expiration
- Refresh token mechanism for seamless renewal


### Endpoint: Grade Explanation

**URL:** `POST /api/grade`

**Request Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
X-Request-ID: <uuid>
```

**Request Body:**
```json
{
  "studentId": "STUDENT#abc123",
  "sessionId": "SESSION#1234567890#xyz",
  "codeSnippet": "function add(a, b) { return a + b; }",
  "explanation": "This function takes two parameters and returns their sum",
  "language": "en",
  "programmingLanguage": "javascript",
  "attemptNumber": 1,
  "previousGaps": []
}
```

**Success Response (200 OK):**
```json
{
  "score": 85,
  "passed": true,
  "feedback": "Good explanation covering the basic functionality. You correctly identified the parameters and return value.",
  "strengths": [
    "Identified function parameters",
    "Explained return value",
    "Clear and concise"
  ],
  "gaps": [],
  "sessionId": "SESSION#1234567890#xyz",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Failure Response (score < 70):**
```json
{
  "score": 45,
  "passed": false,
  "feedback": "Your explanation is incomplete. Consider discussing data types, edge cases, and potential use cases.",
  "strengths": [
    "Identified basic operation"
  ],
  "gaps": [
    "No mention of data types",
    "Missing edge case discussion",
    "No explanation of practical use"
  ],
  "hint": {
    "level": 1,
    "detailPercentage": 20,
    "content": "Think about what happens when you pass different types of values to this function.",
    "focusAreas": ["data types", "type coercion"]
  },
  "sessionId": "SESSION#1234567890#xyz",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**

**401 Unauthorized:**
```json
{
  "error": "UNAUTHORIZED",
  "message": "Invalid or expired token"
}
```

**429 Too Many Requests:**
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Maximum 10 requests per minute exceeded",
  "retryAfter": 30
}
```

**500 Internal Server Error:**
```json
{
  "error": "INTERNAL_ERROR",
  "message": "Failed to process explanation",
  "requestId": "req-xyz123"
}
```


### Endpoint: Transcribe Voice

**URL:** `POST /api/transcribe`

**Request Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "studentId": "STUDENT#abc123",
  "audioData": "base64_encoded_audio_data...",
  "language": "hi",
  "format": "webm"
}
```

**Success Response (200 OK):**
```json
{
  "text": "यह फ़ंक्शन दो संख्याओं को जोड़ता है",
  "confidence": 0.95,
  "duration": 3.5,
  "language": "hi-IN"
}
```

**Error Responses:**

**400 Bad Request:**
```json
{
  "error": "INVALID_AUDIO",
  "message": "Audio format not supported or corrupted"
}
```

**413 Payload Too Large:**
```json
{
  "error": "AUDIO_TOO_LARGE",
  "message": "Audio duration exceeds 60 seconds limit"
}
```


### Endpoint: Save Session

**URL:** `POST /api/session`

**Request Body:**
```json
{
  "studentId": "STUDENT#abc123",
  "sessionId": "SESSION#1234567890#xyz",
  "codeSnippet": "function add(a, b) { return a + b; }",
  "explanation": "This function adds two numbers",
  "score": 85,
  "passed": true,
  "attemptCount": 1,
  "language": "en",
  "programmingLanguage": "javascript",
  "inputMethod": "text",
  "duration": 45
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "sessionId": "SESSION#1234567890#xyz",
  "updatedMetrics": {
    "aiDependencyRatio": 65.5,
    "interviewReadinessScore": 72.3
  }
}
```


### Endpoint: Get Progress

**URL:** `GET /api/progress/{studentId}`

**Query Parameters:**
- `period`: `week` | `month` | `all` (default: `week`)
- `language`: Filter by programming language (optional)

**Success Response (200 OK):**
```json
{
  "studentId": "STUDENT#abc123",
  "metrics": {
    "aiDependencyRatio": 65.5,
    "interviewReadinessScore": 72.3,
    "averageUnderstandingScore": 78.5,
    "totalSessions": 45,
    "weeklyTrend": [
      {"week": "2024-W01", "aiRatio": 70, "manualRatio": 30},
      {"week": "2024-W02", "aiRatio": 65.5, "manualRatio": 34.5}
    ],
    "languageBreakdown": {
      "javascript": {
        "sessionsCount": 20,
        "averageScore": 80,
        "aiDependency": 60
      },
      "python": {
        "sessionsCount": 15,
        "averageScore": 75,
        "aiDependency": 70
      },
      "java": {
        "sessionsCount": 10,
        "averageScore": 78,
        "aiDependency": 68
      }
    }
  },
  "recentSessions": [
    {
      "sessionId": "SESSION#1234567890#xyz",
      "timestamp": "2024-01-15T10:30:00Z",
      "score": 85,
      "passed": true,
      "programmingLanguage": "javascript",
      "attemptCount": 1
    }
  ],
  "achievements": [
    {
      "id": "first_70_score",
      "title": "First Success",
      "description": "Achieved 70% score for the first time",
      "earnedAt": "2024-01-10T14:20:00Z",
      "icon": "🎯"
    }
  ],
  "weeklyStreak": 5
}
```


### Endpoint: Sync Offline Data

**URL:** `POST /api/sync`

**Request Body:**
```json
{
  "studentId": "STUDENT#abc123",
  "sessions": [
    {
      "sessionId": "SESSION#offline1",
      "codeSnippet": "def multiply(x, y): return x * y",
      "explanation": "Multiplies two numbers",
      "score": 0,
      "passed": false,
      "attemptCount": 0,
      "language": "en",
      "programmingLanguage": "python",
      "inputMethod": "text",
      "duration": 30,
      "createdAt": "2024-01-15T08:00:00Z"
    }
  ]
}
```

**Success Response (200 OK):**
```json
{
  "syncedCount": 1,
  "failedSessions": [],
  "updatedMetrics": {
    "aiDependencyRatio": 66.0,
    "interviewReadinessScore": 71.8,
    "averageUnderstandingScore": 77.5,
    "totalSessions": 46
  }
}
```

**Partial Success Response (207 Multi-Status):**
```json
{
  "syncedCount": 2,
  "failedSessions": ["SESSION#offline3"],
  "errors": [
    {
      "sessionId": "SESSION#offline3",
      "error": "INVALID_DATA",
      "message": "Code snippet exceeds maximum length"
    }
  ],
  "updatedMetrics": {
    "aiDependencyRatio": 66.0,
    "interviewReadinessScore": 71.8
  }
}
```


### Rate Limiting

**Per-Endpoint Limits:**
- `/api/grade`: 10 requests/minute per student
- `/api/transcribe`: 5 requests/minute per student
- `/api/session`: 20 requests/minute per student
- `/api/progress`: 30 requests/minute per student
- `/api/sync`: 2 requests/minute per student

**Implementation:**
- Token bucket algorithm
- Limits stored in DynamoDB with TTL
- 429 response with `Retry-After` header when exceeded

**Abuse Prevention:**
- IP-based rate limiting for unauthenticated requests
- Exponential backoff for repeated violations
- Temporary account suspension after 10 violations in 1 hour


## Security Considerations

### Authentication and Authorization

**Token-Based Authentication Flow:**

1. **Initial Login:**
   - Student enters email/password in VS Code extension
   - Extension sends credentials to `/api/auth/login`
   - Lambda validates credentials against StudentProfile table
   - Returns JWT token with 24-hour expiration
   - Extension stores token securely in VS Code SecretStorage API

2. **Token Refresh:**
   - Extension checks token expiration before each request
   - If expiring within 1 hour, requests refresh via `/api/auth/refresh`
   - Refresh token valid for 30 days
   - Seamless renewal without user interaction

3. **Token Validation:**
   - API Gateway Lambda authorizer validates JWT signature
   - Checks expiration and student status
   - Caches validation results for 5 minutes
   - Returns 401 for invalid/expired tokens

**Authorization Levels:**
- **Student:** Access own data only
- **Educator:** Access class-aggregated data (Phase 2)
- **Admin:** Access system-wide metrics and configuration (Phase 2)


### Data Privacy and GDPR Compliance

**Data Collection Transparency:**
- Clear consent during extension installation
- Privacy policy accessible from extension settings
- Explanation of what data is collected and why
- Opt-out options for non-essential features (leaderboard, achievements)

**Data Minimization:**
- Only collect data necessary for core functionality
- No tracking of non-AI code content
- Anonymize data for aggregated analytics
- No third-party data sharing without explicit consent

**Right to Access:**
- Students can download all their data via dashboard
- Export format: JSON with human-readable structure
- Includes all sessions, metrics, and achievements

**Right to Deletion:**
- "Delete Account" option in extension settings
- Permanent deletion within 24 hours
- Cascade delete across all DynamoDB tables
- Confirmation email after deletion
- Retention of anonymized aggregated metrics only

**Data Retention:**
- Detailed session data: 90 days (TTL in DynamoDB)
- Aggregated metrics: 1 year
- Account data: Until deletion request
- Audit logs: 2 years (compliance requirement)

**Cross-Border Data Transfer:**
- All data stored in AWS Asia Pacific (Mumbai) region
- No data transfer outside India without consent
- Compliance with Indian data protection regulations


### Security Best Practices

**Input Validation:**
- Sanitize all user inputs (code, explanations, voice data)
- Maximum length limits enforced:
  - Code snippets: 10,000 characters
  - Explanations: 1,000 characters
  - Audio files: 60 seconds
- Reject malformed requests with 400 Bad Request

**SQL Injection Prevention:**
- Use DynamoDB parameterized queries only
- No raw query construction from user input
- Input validation before database operations

**XSS Prevention:**
- Sanitize all text displayed in extension UI
- Content Security Policy in Amplify dashboard
- Escape HTML entities in user-generated content

**CSRF Protection:**
- CSRF tokens for state-changing operations
- SameSite cookie attribute for session cookies
- Origin validation for API requests

**Secrets Management:**
- AWS Secrets Manager for API keys and credentials
- No hardcoded secrets in code
- Automatic secret rotation every 90 days
- Least privilege IAM roles for Lambda functions

**Logging and Monitoring:**
- CloudWatch Logs for all Lambda invocations
- Structured logging with request IDs
- Alert on suspicious patterns:
  - Multiple failed authentication attempts
  - Unusual API usage patterns
  - High error rates
- PII redaction in logs

**Vulnerability Management:**
- Regular dependency updates for extension and Lambda
- Automated security scanning via AWS Inspector
- Penetration testing before production launch
- Bug bounty program for responsible disclosure


## AWS Bedrock Integration

### Prompt Engineering for Explanation Grading

**Prompt Template Structure:**

```
You are an expert programming educator evaluating a student's understanding of code.

**Code Snippet:**
```{programming_language}
{code_snippet}
```

**Student's Explanation ({language}):**
{explanation}

**Evaluation Criteria:**
1. Correctness: Does the student correctly identify what the code does?
2. Completeness: Does the explanation cover key concepts (parameters, return values, logic flow)?
3. Depth: Does the student demonstrate understanding of edge cases, data types, and practical applications?

**Previous Attempt Context:**
{previous_gaps}

**Instructions:**
- Assign a score from 0-100 based on the criteria above
- Provide specific feedback highlighting strengths and gaps
- If score < 70, generate a progressive hint based on attempt number
- Be encouraging and constructive in tone
- For Hindi explanations, evaluate with the same rigor as English

**Response Format (JSON):**
{
  "score": <number 0-100>,
  "feedback": "<detailed feedback>",
  "strengths": ["<strength1>", "<strength2>"],
  "gaps": ["<gap1>", "<gap2>"],
  "hint": {
    "level": <1, 2, or 3>,
    "content": "<progressive hint>",
    "focusAreas": ["<area1>", "<area2>"]
  }
}
```

**Prompt Optimization:**
- Use few-shot examples for consistent scoring
- Include language-specific evaluation guidelines
- Adapt hint detail based on attempt number (20%, 40%, 60%)
- Maintain consistent scoring across English and Hindi


### Bedrock Model Configuration

**Model Selection:** Claude 3.5 Sonnet

**Rationale:**
- Superior multilingual support (English and Hindi)
- Fast inference (<2s for typical explanations)
- Strong reasoning capabilities for nuanced evaluation
- Cost-effective for target scale (₹5/student/month)

**Model Parameters:**
```json
{
  "modelId": "anthropic.claude-3-5-sonnet-20240620-v1:0",
  "temperature": 0.3,
  "maxTokens": 1000,
  "topP": 0.9,
  "stopSequences": []
}
```

**Temperature Rationale:**
- Low temperature (0.3) for consistent, deterministic scoring
- Reduces variability in grading similar explanations
- Maintains fairness across students

**Token Budget:**
- Input: ~500 tokens (code + explanation + prompt)
- Output: ~300 tokens (score + feedback + hint)
- Total: ~800 tokens per request
- Cost: ~₹0.02 per request (based on AWS pricing)

**Fallback Strategy:**
- If Bedrock unavailable: Queue request for retry (3 attempts)
- If all retries fail: Return cached generic feedback
- Alert monitoring system for manual review


## Performance Optimization

### Latency Optimization

**AI Code Detection (<500ms):**
- Local pattern matching (no API calls)
- Heuristic-based detection using:
  - Paste event timing analysis
  - Code formatting patterns
  - Comment style detection
  - Variable naming conventions
- Cached results for repeated code snippets

**Explanation Grading (<2s for 95% of requests):**
- Provisioned concurrency for Lambda (5 warm instances)
- Bedrock request optimization:
  - Batch similar requests when possible
  - Compress prompts to reduce token count
  - Use streaming responses for real-time feedback
- Connection pooling for DynamoDB
- Parallel execution:
  - Plagiarism check and Bedrock grading run concurrently
  - Session save happens asynchronously after response

**DynamoDB Read Latency (<100ms):**
- DAX (DynamoDB Accelerator) for frequently accessed data
- Cache student profiles and recent sessions
- TTL: 5 minutes for profile data, 1 minute for sessions
- Read-through cache pattern


### Scalability Strategy

**Auto-Scaling Configuration:**

**Lambda Functions:**
- Provisioned concurrency: 5-50 instances based on load
- Reserved concurrency: 100 per function
- Auto-scale trigger: 80% utilization
- Scale-up: Add 10 instances per minute
- Scale-down: Remove 5 instances per minute (gradual)

**DynamoDB:**
- On-demand capacity mode for unpredictable traffic
- Auto-scaling for provisioned capacity (if needed):
  - Target utilization: 70%
  - Min capacity: 5 RCU/WCU
  - Max capacity: 1000 RCU/WCU
- Global tables for multi-region expansion (Phase 2)

**API Gateway:**
- Throttling limits:
  - Burst: 5000 requests
  - Rate: 2000 requests/second
- Regional endpoint in ap-south-1 (Mumbai)
- CloudFront distribution for static assets

**Load Testing Targets:**
- 10,000 concurrent students (Phase 1)
- 100,000 concurrent students (Phase 2)
- Peak load: 500 requests/second
- Sustained load: 200 requests/second


### Cost Optimization

**Target Cost:** ₹5 per student per month

**Cost Breakdown (per student):**
- Bedrock (Claude 3.5 Sonnet): ₹2.50
  - Assumption: 50 explanations/month @ ₹0.05 each
- Lambda: ₹0.80
  - Assumption: 200 invocations/month
- DynamoDB: ₹0.50
  - On-demand pricing for variable load
- Transcribe: ₹0.60
  - Assumption: 20 voice inputs/month @ ₹0.03 each
- Comprehend: ₹0.30
  - Plagiarism checks on all explanations
- Amplify: ₹0.20
  - Static hosting and CDN
- KMS: ₹0.10
  - Encryption operations
- **Total: ₹5.00/student/month**

**Optimization Strategies:**

1. **Bedrock Cost Reduction:**
   - Prompt compression to reduce input tokens
   - Cache common feedback patterns
   - Batch requests during off-peak hours (if applicable)

2. **Lambda Cost Reduction:**
   - Use ARM-based Graviton2 processors (20% cheaper)
   - Optimize memory allocation (512MB optimal for most functions)
   - Reduce cold starts with provisioned concurrency

3. **DynamoDB Cost Reduction:**
   - TTL for automatic data expiration (90 days)
   - Compress large text fields before storage
   - Use sparse indexes to reduce storage costs

4. **Transcribe Cost Reduction:**
   - Encourage text input over voice (gamification)
   - Limit voice input duration to 60 seconds
   - Use standard model (not medical/custom)

5. **Data Transfer Cost Reduction:**
   - Use CloudFront for static assets
   - Compress API responses (gzip)
   - Regional deployment to minimize cross-region transfer

**Cost Monitoring:**
- Daily cost reports via CloudWatch
- Alert when per-student cost exceeds ₹6
- Monthly budget review and optimization


## Error Handling

### Error Categories and Responses

**1. Client Errors (4xx):**

**400 Bad Request:**
- Invalid request format
- Missing required fields
- Data validation failures
- Response: Detailed error message with field-level errors

**401 Unauthorized:**
- Invalid or expired token
- Missing authentication header
- Response: Redirect to login flow

**403 Forbidden:**
- Insufficient permissions
- Account suspended
- Response: Clear explanation of restriction

**429 Too Many Requests:**
- Rate limit exceeded
- Response: Retry-After header with wait time

**2. Server Errors (5xx):**

**500 Internal Server Error:**
- Unexpected Lambda errors
- Bedrock API failures
- Response: Generic error message + request ID for support

**503 Service Unavailable:**
- AWS service outages
- Maintenance mode
- Response: Estimated recovery time

**504 Gateway Timeout:**
- Lambda timeout (>30s)
- Bedrock slow response
- Response: Retry suggestion


### Retry Logic

**Exponential Backoff Strategy:**

```typescript
interface RetryConfig {
  maxAttempts: 3;
  initialDelay: 1000; // ms
  maxDelay: 10000; // ms
  backoffMultiplier: 2;
  jitter: true; // Add randomness to prevent thundering herd
}

function calculateDelay(attemptNumber: number): number {
  const delay = Math.min(
    initialDelay * Math.pow(backoffMultiplier, attemptNumber - 1),
    maxDelay
  );
  
  if (jitter) {
    return delay * (0.5 + Math.random() * 0.5); // 50-100% of delay
  }
  
  return delay;
}
```

**Retry Conditions:**
- Network errors: Retry all 3 attempts
- 5xx errors: Retry all 3 attempts
- 429 errors: Retry with Retry-After header value
- 4xx errors (except 429): No retry
- Timeout errors: Retry with increased timeout

**Circuit Breaker Pattern:**
- Open circuit after 5 consecutive failures
- Half-open state after 30 seconds
- Close circuit after 3 successful requests
- Prevents cascading failures


### Graceful Degradation

**Offline Mode:**
- Queue submissions locally (max 50 sessions)
- Allow manual code execution with "pending verification" status
- Sync automatically when connectivity restored
- Display clear offline indicator in UI

**Bedrock Unavailable:**
- Return cached generic feedback
- Allow code execution with warning
- Queue for manual review (educator dashboard)
- Alert monitoring system

**Transcribe Unavailable:**
- Fallback to text-only input
- Display error message with alternative
- Log incident for investigation

**DynamoDB Unavailable:**
- Use local cache for read operations
- Queue write operations for retry
- Display warning about potential data loss
- Escalate to critical alert

**Partial Feature Degradation:**
- Core functionality (code lock/unlock) always available
- Non-critical features (achievements, leaderboard) can fail gracefully
- Clear communication to user about degraded state


## Testing Strategy

### Dual Testing Approach

CodeGuardian will employ both unit testing and property-based testing to ensure comprehensive coverage:

**Unit Tests:**
- Specific examples and edge cases
- Integration points between VS Code extension and AWS services
- Error conditions and failure scenarios
- UI component rendering and interactions
- Authentication and authorization flows

**Property-Based Tests:**
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number

**Testing Balance:**
- Unit tests focus on concrete scenarios and integration
- Property tests verify general correctness across all inputs
- Together they provide comprehensive validation

**Property Test Configuration:**
- Library: fast-check (for TypeScript/JavaScript components)
- Library: Hypothesis (for Python Lambda functions if used)
- Minimum iterations: 100 per test
- Tag format: `Feature: code-guardian, Property {number}: {property_text}`


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Core Detection and Locking Properties

Property 1: AI code detection performance
*For any* code snippet up to 500 lines, the AI_Code_Detector should complete analysis within 500ms
**Validates: Requirements 1.1, 9.1**

Property 2: AI code execution blocking
*For any* code detected as AI-generated, the Code_Execution_Gate should prevent execution until understanding is verified
**Validates: Requirements 1.2**

Property 3: AI code detection notification
*For any* AI-generated code detection, a non-intrusive notification should be displayed prompting explanation
**Validates: Requirements 1.3**

Property 4: Manual code immediate execution
*For any* code typed manually (character by character over time), the AI_Code_Detector should classify it as non-AI and allow immediate execution
**Validates: Requirements 1.4, 4.4**

Property 5: Educational resource distinction
*For any* code pasted from educational resources, the AI_Code_Detector should distinguish it from AI-generated code
**Validates: Requirements 1.5**


### Explanation Collection Properties

Property 6: Voice transcription performance
*For any* voice input, the Voice_Input_Module should convert speech to text within 2 seconds
**Validates: Requirements 2.2**

Property 7: Text explanation length validation
*For any* text explanation, it should be accepted if length is between 50 and 1000 characters, and rejected otherwise
**Validates: Requirements 2.3**

Property 8: Language preference persistence
*For any* session, when a student switches between English and Hindi, the language preference should be maintained throughout that session
**Validates: Requirements 2.4**

Property 9: Real-time transcription feedback
*For any* active voice input, real-time transcription feedback should be provided to the student
**Validates: Requirements 2.6**


### Grading and Scoring Properties

Property 10: Bedrock integration
*For any* submitted explanation, it should be sent to AWS Bedrock (Claude 3.5 Sonnet) for evaluation
**Validates: Requirements 3.1**

Property 11: Score range and performance
*For any* explanation sent to Bedrock, an Understanding_Score between 0 and 100 should be returned within 2 seconds
**Validates: Requirements 3.2, 9.2**

Property 12: Feedback structure
*For any* grading result, it should contain specific feedback with strengths and gaps arrays
**Validates: Requirements 3.5**

Property 13: Plagiarism score reduction
*For any* explanation where plagiarism is detected, the Understanding_Score should be reduced by 50%
**Validates: Requirements 3.6**


### Code Execution Control Properties

Property 14: Unlock on passing score
*For any* Understanding_Score of 70% or higher, the Code_Execution_Gate should unlock and allow code execution
**Validates: Requirements 4.1**

Property 15: Lock on failing score
*For any* Understanding_Score below 70%, the Code_Execution_Gate should remain locked and display the score with feedback
**Validates: Requirements 4.2**

Property 16: Unlock side effects
*For any* code unlock event, a success message should be displayed and the student's progress metrics should be updated
**Validates: Requirements 4.3**

Property 17: Lock state persistence
*For any* locked code block, the locked state should persist across VS Code restarts until understanding is verified
**Validates: Requirements 4.5**


### Retry and Hint Properties

Property 18: Hint provision on failure
*For any* Understanding_Score below 70%, progressive hints should be provided based on the specific gaps identified
**Validates: Requirements 5.1**

Property 19: Retry limit enforcement
*For any* session, a maximum of 3 retry attempts should be allowed
**Validates: Requirements 5.2**

Property 20: Fallback unlock after max retries
*For any* session where all 3 retry attempts are exhausted without reaching 70%, the code should unlock but the session should be marked as "unverified" in metrics
**Validates: Requirements 5.3**

Property 21: Progressive hint detail
*For any* sequence of failed attempts (1, 2, 3), hint detail should increase progressively (20%, 40%, 60%)
**Validates: Requirements 5.4**

Property 22: Attempt count recording
*For any* successful explanation (score >= 70%), the number of attempts taken should be recorded in progress metrics
**Validates: Requirements 5.5**

Property 23: Language-specific hints
*For any* hint generated, the content should be adapted based on the programming language (JavaScript, Python, Java)
**Validates: Requirements 5.6**


### Progress Tracking Properties

Property 24: AI dependency ratio calculation
*For any* set of code metrics (AI lines, total lines), the AI_Dependency_Ratio should be calculated as (AI_code_lines / total_code_lines) × 100
**Validates: Requirements 6.1**

Property 25: Session data persistence
*For any* completed session, the Understanding_Score, timestamp, language, and retry count should be stored in DynamoDB
**Validates: Requirements 6.2**

Property 26: Interview readiness calculation
*For any* set of metrics (AI_Dependency_Ratio, average Understanding_Score, manual coding frequency), the Interview_Readiness_Score should be calculated correctly
**Validates: Requirements 6.3**

Property 27: Language-specific metric tracking
*For any* session, metrics should be tracked separately under the correct programming language (JavaScript, Python, or Java)
**Validates: Requirements 6.5**

Property 28: Achievement notification on improvement
*For any* week where AI_Dependency_Ratio decreases by 10% or more, a congratulatory achievement notification should be displayed
**Validates: Requirements 6.6**


### Dashboard and Visualization Properties

Property 29: Color coding based on trends
*For any* metric displayed in the Progress_Dashboard, color coding should be applied correctly (green for improvement, yellow for stagnation, red for regression)
**Validates: Requirements 7.3**

Property 30: Milestone badge display
*For any* achieved milestone (30% AI dependency, 90% average Understanding_Score), corresponding badges should be displayed in the Progress_Dashboard
**Validates: Requirements 7.5**


### Security and Privacy Properties

Property 31: Data encryption in transit
*For any* data transmission to AWS services (code snippets, explanations), it should be encrypted using TLS 1.3
**Validates: Requirements 8.1**

Property 32: Account deletion compliance
*For any* account deletion request, all associated data should be permanently removed within 24 hours
**Validates: Requirements 8.3**

Property 33: Token-based authentication
*For any* authentication request, a secure token with session expiration should be issued
**Validates: Requirements 8.5**


### Performance Properties

Property 34: Cache read latency
*For any* cached data access, DynamoDB read latency should be below 100ms
**Validates: Requirements 9.5**


### Cost Optimization Properties

Property 35: Request batching
*For any* set of AWS Bedrock API requests that can be batched, they should be combined to reduce invocation costs
**Validates: Requirements 10.2**

Property 36: Data retention TTL
*For any* stored session data, TTL should be set correctly (90 days for detailed logs, 1 year for aggregated metrics)
**Validates: Requirements 10.4**


### Localization and Accessibility Properties

Property 37: Complete UI translation
*For any* UI text element, translations should exist in both English and Hindi
**Validates: Requirements 11.1**

Property 38: Language preference application
*For any* notification or feedback displayed, it should use the student's selected language preference
**Validates: Requirements 11.2**

Property 39: ARIA labels for accessibility
*For any* interactive UI element, descriptive ARIA labels should be provided for screen readers
**Validates: Requirements 11.4**

Property 40: Keyboard navigation support
*For any* feature in the extension, it should be accessible via keyboard without requiring mouse input
**Validates: Requirements 11.5**

Property 41: Color-blind accessible indicators
*For any* color-coded metric, icons or patterns should accompany the color coding for color-blind accessibility
**Validates: Requirements 11.6**


### Gamification Properties

Property 42: Milestone badge awarding
*For any* milestone reached (first 70% score, 7-day streak, 50% AI reduction), a corresponding badge should be awarded
**Validates: Requirements 12.1**

Property 43: Weekly streak calculation
*For any* sequence of active days, the weekly streak counter should be calculated correctly
**Validates: Requirements 12.2**

Property 44: Level progression display
*For any* Interview_Readiness_Score value, the correct level (Beginner, Intermediate, Advanced, Expert) should be displayed
**Validates: Requirements 12.3**

Property 45: Daily challenge generation
*For any* student profile with identified weak areas, appropriate daily challenges should be generated
**Validates: Requirements 12.4**

Property 46: Leaderboard percentile calculation
*For any* set of students (opt-in only), anonymous percentile rankings should be calculated correctly
**Validates: Requirements 12.6**


### VS Code Integration Properties

Property 47: Status bar indicator display
*For any* active CodeGuardian session, a status bar indicator should display the current AI_Dependency_Ratio
**Validates: Requirements 13.2**

Property 48: Keyboard shortcut registration
*For any* common action (explain code, view dashboard), the corresponding keyboard shortcut should be registered and functional
**Validates: Requirements 13.3**

Property 49: Locked code inline decorations
*For any* locked code block, inline decorations should be displayed highlighting the locked region
**Validates: Requirements 13.4**

Property 50: VS Code notification integration
*For any* alert or notification, it should use VS Code's native notification system
**Validates: Requirements 13.5**

Property 51: Terminal execution interception
*For any* code execution attempt in VS Code's integrated terminal, locked code should be intercepted
**Validates: Requirements 13.6**


### Offline Mode Properties

Property 52: Offline submission queuing
*For any* explanation submission while offline, it should be queued locally for later processing
**Validates: Requirements 14.1**

Property 53: Automatic sync on reconnection
*For any* queued submissions when connectivity is restored, they should be automatically synced to AWS services
**Validates: Requirements 14.2**

Property 54: Offline execution with pending status
*For any* session completed while offline, code should execute but be marked as "pending verification"
**Validates: Requirements 14.3**

Property 55: Queue capacity limit
*For any* offline queue, it should accept up to 50 pending sessions before requiring sync
**Validates: Requirements 14.4**

Property 56: Sync prioritization and progress
*For any* sync operation, recent sessions should be prioritized and sync progress should be displayed
**Validates: Requirements 14.5**

Property 57: Offline mode notification
*For any* offline state, a notification should be displayed explaining the limitations
**Validates: Requirements 14.6**


### Educator Features Properties (Phase 2)

Property 58: Admin dashboard access
*For any* educator account, an admin dashboard showing class-wide metrics should be accessible
**Validates: Requirements 15.1**

Property 59: At-risk student identification
*For any* class, students with AI_Dependency_Ratio above 60% should be identified for targeted intervention
**Validates: Requirements 15.3**

Property 60: Report generation with permissions
*For any* educator export request, CSV reports should be generated with anonymized or identified data based on permissions
**Validates: Requirements 15.4**

Property 61: Custom threshold configuration
*For any* educator-set Passing_Threshold value (60-80%), it should be applied to grading for that class
**Validates: Requirements 15.5**

Property 62: SSO integration
*For any* institutional deployment, SSO authentication flow should work correctly with university systems
**Validates: Requirements 15.6**


## Implementation Considerations

### Technology Stack

**VS Code Extension:**
- Language: TypeScript
- Framework: VS Code Extension API
- Testing: Jest + fast-check (property-based testing)
- Build: webpack
- Package Manager: npm

**AWS Lambda Functions:**
- Language: Node.js 18.x (TypeScript compiled)
- Runtime: AWS Lambda with Provisioned Concurrency
- Testing: Jest + AWS SDK mocks
- Deployment: AWS SAM or Serverless Framework

**Web Dashboard:**
- Framework: React 18
- State Management: Redux Toolkit
- UI Library: Material-UI or Chakra UI
- Charts: Recharts or Chart.js
- Hosting: AWS Amplify
- Build: Vite

**Infrastructure as Code:**
- Tool: AWS CDK (TypeScript) or Terraform
- Version Control: Git
- CI/CD: GitHub Actions or AWS CodePipeline


### Development Phases

**Phase 1: Hackathon MVP (AI for Bharat 2026)**
- Core detection and locking (Requirements 1, 4)
- Explanation collection (Requirement 2)
- Bedrock grading (Requirement 3)
- Retry and hints (Requirement 5)
- Basic progress tracking (Requirement 6)
- Minimal dashboard (Requirement 7)
- Security essentials (Requirement 8)
- Performance optimization (Requirement 9)

**Phase 2: Post-Hackathon Extensions**
- Advanced gamification (Requirement 12)
- Offline mode (Requirement 14)
- Educator features (Requirement 15)
- Enhanced accessibility (Requirement 11)
- Cost optimization at scale (Requirement 10)

**Phase 3: Enterprise Scale**
- Multi-region deployment
- Advanced analytics and ML insights
- Integration with university LMS systems
- Mobile app companion
- Advanced plagiarism detection


### Monitoring and Observability

**CloudWatch Metrics:**
- API Gateway request count and latency
- Lambda invocation count, duration, and errors
- DynamoDB read/write capacity and throttles
- Bedrock API call count and latency
- Transcribe job count and duration

**Custom Metrics:**
- AI code detection rate
- Average Understanding_Score
- Pass rate (score >= 70%)
- Retry rate
- Offline queue size
- Cost per student

**Alarms:**
- API Gateway 5xx error rate > 1%
- Lambda error rate > 5%
- DynamoDB throttling events
- Bedrock API failures
- Cost exceeding budget threshold
- High latency (p95 > 2s for grading)

**Logging:**
- Structured JSON logs in CloudWatch
- Request ID tracking across services
- PII redaction in logs
- Log retention: 30 days for debug, 2 years for audit

**Dashboards:**
- Real-time system health dashboard
- Cost analysis dashboard
- Student engagement metrics dashboard
- Performance metrics dashboard


### Deployment Strategy

**Environment Setup:**
- Development: Local VS Code + LocalStack for AWS services
- Staging: Dedicated AWS account with reduced capacity
- Production: Separate AWS account with full capacity

**Deployment Pipeline:**
1. Code commit to GitHub
2. Automated tests (unit + property-based)
3. Build and package extension + Lambda functions
4. Deploy to staging environment
5. Run integration tests
6. Manual approval for production
7. Blue-green deployment to production
8. Smoke tests in production
9. Gradual rollout (10% → 50% → 100%)

**Rollback Strategy:**
- Automated rollback on high error rate
- Manual rollback capability
- Database migration rollback scripts
- Extension version pinning for stability

**Version Management:**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Extension marketplace updates
- Lambda function versioning and aliases
- API versioning for backward compatibility


## Conclusion

This design document provides a comprehensive technical blueprint for the CodeGuardian VS Code extension. The architecture leverages AWS services (Bedrock, Lambda, Transcribe, DynamoDB, Amplify, Comprehend, KMS) to create a scalable, secure, and cost-effective solution for reducing AI dependency among Indian CS students.

Key design decisions:
- **Client-server architecture** with VS Code extension as client and AWS as backend
- **Event-driven processing** with Lambda functions for scalability
- **Bedrock (Claude 3.5 Sonnet)** for intelligent explanation grading
- **DynamoDB** for fast, scalable data storage with encryption
- **Bilingual support** (English and Hindi) throughout the system
- **Offline-first approach** with automatic sync
- **Cost optimization** targeting ₹5/student/month
- **Property-based testing** for comprehensive correctness validation

The design addresses all functional and non-functional requirements from the requirements document, with clear traceability through 62 correctness properties. The phased implementation approach ensures a working MVP for the AI for Bharat 2026 hackathon while providing a roadmap for enterprise-scale deployment.


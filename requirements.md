# Requirements Document: CodeGuardian VS Code Extension

## Introduction

CodeGuardian is a VS Code extension designed to address the critical problem of AI code dependency among Indian CS students (ages 18-22). The extension intercepts AI-generated code, prompts students to demonstrate understanding through explanations, and uses AWS Bedrock (Claude 3.5 Sonnet) to grade their comprehension before allowing code execution. The system supports both English and Hindi to serve students across Tier 1-3 cities, with the goal of reducing AI dependency from 70% to 30% within 30 days and improving technical interview pass rates by 40%.

## Scope for Hackathon Phase (AI for Bharat 2026)

For the AI for Bharat 2026 hackathon, the initial scope focuses on the core learning guardrail loop:

**Hackathon MVP (Phase 1)**:
- AI code detection and interception (Requirement 1)
- Student explanation collection in English + Hindi text/voice (Requirement 2)
- Explanation grading and scoring via AWS Bedrock (Requirement 3)
- Code execution control (Requirement 4)
- Retry mechanism and hint system (Requirement 5)
- Basic progress tracking and minimal dashboard (parts of Requirements 6 & 7)
- Core security and performance requirements (Requirements 8 & 9)

**Post-Hackathon Extensions (Phase 2+)**:
The following requirements are planned as Phase 2+ extensions beyond the hackathon prototype and are included here to show long-term vision:
- Advanced gamification and achievements (Requirement 12)
- Offline mode and sync (Requirement 14)
- Admin and educator features (Requirement 15)
- Large-scale institutional deployment and SSO
- Advanced cost optimization at 100,000+ student scale

This scoping ensures the hackathon prototype is buildable and testable within AWS credits and timeline constraints, while still presenting a clear path to a full Bharat-scale product.

## Glossary

- **CodeGuardian**: The VS Code extension system that monitors, intercepts, and validates student understanding of AI-generated code
- **AI_Code_Detector**: Component that identifies code originating from AI tools (GitHub Copilot, ChatGPT, etc.)
- **Explanation_Grader**: AWS Bedrock-powered service that evaluates student explanations and assigns comprehension scores
- **Code_Execution_Gate**: Mechanism that blocks or allows code execution based on understanding verification
- **Student**: Target user aged 18-22, BE CSE AI/ML student learning JavaScript, Python, or Java
- **AI_Dependency_Ratio**: Percentage of code written by AI tools versus manually written code by the student
- **Understanding_Score**: Numerical score (0-100) assigned by Explanation_Grader to student explanations
- **Passing_Threshold**: Minimum Understanding_Score of 70% required to unlock code execution
- **Progress_Dashboard**: Web interface displaying student metrics, AI dependency trends, and interview readiness
- **Interview_Readiness_Score**: Composite metric indicating student's preparedness for technical interviews
- **Hint_System**: Progressive guidance provided when students fail to meet Passing_Threshold
- **Voice_Input_Module**: Amazon Transcribe-powered component supporting Hindi and English voice explanations
- **Plagiarism_Detector**: Amazon Comprehend-based service identifying copied explanations
- **Session**: Single interaction cycle from code paste to explanation grading
- **Retry_Attempt**: Student's subsequent explanation submission after failing to meet Passing_Threshold (max 3 per Session)

## Requirements

### Requirement 1: AI Code Detection and Interception

**User Story:** As a student, I want the system to detect when I paste AI-generated code, so that I can be prompted to demonstrate my understanding before using it.

#### Acceptance Criteria

1. WHEN a student pastes code into the VS Code editor, THE AI_Code_Detector SHALL analyze the code within 500ms to determine if it originated from AI tools
2. WHEN AI-generated code is detected, THE Code_Execution_Gate SHALL prevent execution of that code until understanding is verified
3. WHEN AI-generated code is detected, THE CodeGuardian SHALL display a non-intrusive notification prompting the student to explain the code
4. WHEN a student types code manually (character by character over time), THE AI_Code_Detector SHALL classify it as non-AI code and allow immediate execution
5. WHEN code is pasted from educational resources (Stack Overflow, documentation), THE AI_Code_Detector SHALL distinguish it from AI-generated code using pattern analysis
6. THE AI_Code_Detector SHALL support JavaScript, Python, and Java code detection with 90% accuracy

### Requirement 2: Student Explanation Collection

**User Story:** As a student, I want to provide explanations in English or Hindi through text or voice, so that I can demonstrate my understanding in my preferred language and format.

#### Acceptance Criteria

1. WHEN the explanation prompt appears, THE CodeGuardian SHALL provide input options for both text and voice in English and Hindi
2. WHEN a student selects voice input, THE Voice_Input_Module SHALL use Amazon Transcribe to convert speech to text within 2 seconds
3. WHEN a student provides a text explanation, THE CodeGuardian SHALL accept explanations between 50 and 1000 characters
4. WHEN a student switches between English and Hindi, THE CodeGuardian SHALL maintain language preference for the current session
5. THE CodeGuardian SHALL display a character counter and estimated speaking time to guide students
6. WHEN voice input is active, THE Voice_Input_Module SHALL provide real-time transcription feedback

### Requirement 3: Explanation Grading and Scoring

**User Story:** As a student, I want my explanation to be graded quickly and fairly, so that I receive immediate feedback on my understanding.

#### Acceptance Criteria

1. WHEN a student submits an explanation, THE Explanation_Grader SHALL send it to AWS Bedrock (Claude 3.5 Sonnet) for evaluation
2. WHEN AWS Bedrock receives an explanation, THE Explanation_Grader SHALL return an Understanding_Score between 0 and 100 within 2 seconds
3. WHEN grading an explanation, THE Explanation_Grader SHALL evaluate correctness, completeness, and depth of understanding
4. WHEN an explanation is in Hindi, THE Explanation_Grader SHALL process it with the same accuracy as English explanations
5. THE Explanation_Grader SHALL provide specific feedback highlighting strengths and gaps in the student's explanation
6. WHEN the Plagiarism_Detector identifies copied content, THE Explanation_Grader SHALL reduce the Understanding_Score by 50%

### Requirement 4: Code Execution Control

**User Story:** As a student, I want code execution to unlock when I demonstrate sufficient understanding, so that I can proceed with my work after proving comprehension.

#### Acceptance Criteria

1. WHEN the Understanding_Score is 70% or higher, THE Code_Execution_Gate SHALL unlock and allow the code to execute
2. WHEN the Understanding_Score is below 70%, THE Code_Execution_Gate SHALL remain locked and display the current score with feedback
3. WHEN code execution is unlocked, THE CodeGuardian SHALL display a success message and update the student's progress metrics
4. WHEN a student manually writes code, THE Code_Execution_Gate SHALL allow immediate execution without requiring explanation
5. THE Code_Execution_Gate SHALL maintain locked state across VS Code restarts until understanding is verified

### Requirement 5: Retry Mechanism and Hint System

**User Story:** As a student, I want to receive hints and retry opportunities when my explanation is insufficient, so that I can learn and improve my understanding.

#### Acceptance Criteria

1. WHEN the Understanding_Score is below 70%, THE Hint_System SHALL provide progressive hints based on the specific gaps identified
2. WHEN a student requests a retry, THE CodeGuardian SHALL allow up to 3 Retry_Attempts per Session
3. WHEN a student exhausts all 3 Retry_Attempts without reaching 70%, THE CodeGuardian SHALL unlock the code but mark the session as "unverified" in metrics
4. WHEN providing hints, THE Hint_System SHALL reveal increasingly specific guidance with each failed attempt (20% detail, 40% detail, 60% detail)
5. WHEN a student achieves 70% on a retry, THE CodeGuardian SHALL record the number of attempts taken in the progress metrics
6. THE Hint_System SHALL adapt hint content based on the programming language (JavaScript, Python, Java)

### Requirement 6: Progress Tracking and Metrics

**User Story:** As a student, I want to track my AI dependency ratio and learning progress over time, so that I can measure my improvement and interview readiness.

#### Acceptance Criteria

1. THE CodeGuardian SHALL calculate AI_Dependency_Ratio weekly as (AI_code_lines / total_code_lines) × 100
2. WHEN a student completes a Session, THE CodeGuardian SHALL store the Understanding_Score, timestamp, language, and retry count in DynamoDB
3. THE CodeGuardian SHALL calculate Interview_Readiness_Score based on AI_Dependency_Ratio, average Understanding_Score, and manual coding frequency
4. WHEN a student opens the Progress_Dashboard, THE CodeGuardian SHALL display weekly trends, language-specific metrics, and improvement suggestions
5. THE CodeGuardian SHALL track metrics separately for JavaScript, Python, and Java to identify language-specific weaknesses
6. WHEN AI_Dependency_Ratio decreases by 10% or more in a week, THE CodeGuardian SHALL display a congratulatory achievement notification

### Requirement 7: Web Dashboard and Visualization

**User Story:** As a student, I want to view my progress through an intuitive web dashboard, so that I can visualize my learning journey and identify areas for improvement.

#### Acceptance Criteria

1. WHEN a student accesses the Progress_Dashboard, THE CodeGuardian SHALL display current AI_Dependency_Ratio, Interview_Readiness_Score, and weekly trends
2. THE Progress_Dashboard SHALL visualize data using charts showing AI vs manual code ratio over time
3. WHEN displaying metrics, THE Progress_Dashboard SHALL use color coding (green for improvement, yellow for stagnation, red for regression)
4. THE Progress_Dashboard SHALL provide language-specific breakdowns for JavaScript, Python, and Java
5. WHEN a student achieves milestones (30% AI dependency, 90% average Understanding_Score), THE Progress_Dashboard SHALL display badges and achievements
6. THE Progress_Dashboard SHALL be accessible via AWS Amplify with responsive design for mobile and desktop

### Requirement 8: Security and Privacy

**User Story:** As a student, I want my code and explanations to be encrypted and private, so that my learning data remains confidential and secure.

#### Acceptance Criteria

1. WHEN transmitting data to AWS services, THE CodeGuardian SHALL encrypt all code snippets and explanations using AWS KMS
2. THE CodeGuardian SHALL store student data in DynamoDB with encryption at rest enabled
3. WHEN a student deletes their account, THE CodeGuardian SHALL permanently remove all associated data within 24 hours
4. THE CodeGuardian SHALL not share student code or explanations with third parties without explicit consent
5. WHEN authenticating students, THE CodeGuardian SHALL use secure token-based authentication with session expiration
6. THE CodeGuardian SHALL comply with data protection regulations applicable to Indian students

### Requirement 9: Performance and Scalability

**User Story:** As a student, I want the system to respond quickly without interrupting my coding workflow, so that learning verification feels seamless.

#### Acceptance Criteria

1. WHEN detecting AI code, THE AI_Code_Detector SHALL complete analysis within 500ms for code snippets up to 500 lines
2. WHEN grading explanations, THE Explanation_Grader SHALL return results within 2 seconds for 95% of requests
3. THE CodeGuardian SHALL support 10,000 concurrent students without degradation in response time
4. WHEN AWS Lambda processes requests, THE CodeGuardian SHALL use provisioned concurrency to eliminate cold starts
5. THE CodeGuardian SHALL cache frequently accessed data to reduce DynamoDB read latency below 100ms
6. WHEN system load exceeds 80% capacity, THE CodeGuardian SHALL auto-scale Lambda functions and DynamoDB throughput

### Requirement 10: Cost Optimization

**User Story:** As a student, I want the service to remain affordable, so that cost does not become a barrier to using the learning tool.

#### Acceptance Criteria

1. THE CodeGuardian SHALL maintain operational cost below ₹5 per student per month using AWS Free Tier and optimization strategies
2. WHEN making AWS Bedrock API calls, THE CodeGuardian SHALL batch requests where possible to reduce invocation costs
3. THE CodeGuardian SHALL use DynamoDB on-demand pricing for unpredictable traffic patterns
4. WHEN storing student data, THE CodeGuardian SHALL implement data retention policies (90 days for detailed logs, 1 year for aggregated metrics)
5. THE CodeGuardian SHALL monitor AWS costs daily and alert administrators when approaching budget thresholds
6. WHEN serving 100,000 students, THE CodeGuardian SHALL maintain total monthly cost below ₹5,00,000

### Requirement 11: Accessibility and Localization

**User Story:** As a student from a Tier 2-3 city, I want to use the tool in Hindi with accessible interfaces, so that language is not a barrier to improving my coding skills.

#### Acceptance Criteria

1. THE CodeGuardian SHALL provide complete UI text in both English and Hindi with language toggle
2. WHEN displaying notifications and feedback, THE CodeGuardian SHALL use the student's selected language preference
3. THE CodeGuardian SHALL comply with WCAG 2.1 Level AA accessibility standards for visual, auditory, and motor accessibility
4. WHEN using screen readers, THE CodeGuardian SHALL provide descriptive labels for all interactive elements
5. THE CodeGuardian SHALL support keyboard navigation for all features without requiring mouse input
6. WHEN displaying color-coded metrics, THE CodeGuardian SHALL also use icons and patterns for color-blind accessibility

### Requirement 12: Gamification and Engagement

**User Story:** As a student, I want to earn achievements and see my progress gamified, so that I stay motivated to reduce AI dependency and improve my skills.

#### Acceptance Criteria

1. WHEN a student reaches milestones (first 70% score, 7-day streak, 50% AI reduction), THE CodeGuardian SHALL award badges
2. THE CodeGuardian SHALL display a weekly streak counter showing consecutive days of active learning
3. WHEN a student's Interview_Readiness_Score increases, THE CodeGuardian SHALL show level progression (Beginner, Intermediate, Advanced, Expert)
4. THE CodeGuardian SHALL provide daily challenges encouraging manual coding practice in weak areas
5. WHEN students achieve goals, THE CodeGuardian SHALL use positive reinforcement without shaming for low scores
6. THE Progress_Dashboard SHALL display a leaderboard showing anonymous percentile rankings (opt-in only)

### Requirement 13: Integration with VS Code

**User Story:** As a student, I want CodeGuardian to integrate seamlessly with VS Code, so that it feels like a natural part of my development environment.

#### Acceptance Criteria

1. THE CodeGuardian SHALL install as a standard VS Code extension from the marketplace
2. WHEN activated, THE CodeGuardian SHALL add a status bar indicator showing current AI_Dependency_Ratio
3. THE CodeGuardian SHALL provide keyboard shortcuts for common actions (explain code: Ctrl+Shift+E, view dashboard: Ctrl+Shift+D)
4. WHEN code is locked, THE CodeGuardian SHALL display inline decorations highlighting the locked code block
5. THE CodeGuardian SHALL integrate with VS Code's notification system for non-intrusive alerts
6. WHEN students use VS Code's integrated terminal, THE CodeGuardian SHALL monitor and intercept code execution attempts

### Requirement 14: Offline Mode and Sync

**User Story:** As a student with intermittent internet connectivity, I want to continue coding offline and sync my progress when reconnected, so that connectivity issues don't block my learning.

#### Acceptance Criteria

1. WHEN internet connectivity is lost, THE CodeGuardian SHALL queue explanation submissions for later processing
2. WHEN connectivity is restored, THE CodeGuardian SHALL automatically sync queued submissions to AWS services
3. WHEN operating offline, THE CodeGuardian SHALL allow manual code execution but mark sessions as "pending verification"
4. THE CodeGuardian SHALL store up to 50 pending sessions locally before requiring sync
5. WHEN syncing, THE CodeGuardian SHALL prioritize recent sessions and display sync progress
6. THE CodeGuardian SHALL notify students when offline mode is active and explain limitations

### Requirement 15: Admin and Educator Features

**User Story:** As an educator at Chitkara University, I want to view aggregated student progress and identify struggling students, so that I can provide targeted support.

#### Acceptance Criteria

1. WHERE educator access is enabled, THE CodeGuardian SHALL provide an admin dashboard showing class-wide metrics
2. WHEN viewing class data, THE CodeGuardian SHALL display average AI_Dependency_Ratio, Interview_Readiness_Score distribution, and language-specific trends
3. THE CodeGuardian SHALL identify students with AI_Dependency_Ratio above 60% for targeted intervention
4. WHEN educators request reports, THE CodeGuardian SHALL generate CSV exports with anonymized or identified data based on permissions
5. THE CodeGuardian SHALL allow educators to set custom Passing_Threshold values (60-80%) for different difficulty levels
6. WHERE institutional deployment is used, THE CodeGuardian SHALL support SSO integration with university authentication systems

## Non-Functional Requirements

### Performance

- **Latency**: AI code detection SHALL complete within 500ms; explanation grading SHALL complete within 2 seconds for 95% of requests
- **Throughput**: System SHALL support 10,000 concurrent users with <5% degradation in response time
- **Scalability**: System SHALL auto-scale to support 100,000 students in Phase 1 deployment

### Reliability

- **Availability**: System SHALL maintain 99.5% uptime during peak hours (9 AM - 11 PM IST)
- **Error Handling**: System SHALL gracefully handle AWS service failures with retry logic (3 attempts with exponential backoff)
- **Data Integrity**: System SHALL ensure zero data loss for student progress and metrics

### Security

- **Encryption**: All data in transit SHALL use TLS 1.3; all data at rest SHALL use AWS KMS encryption
- **Authentication**: System SHALL use secure token-based authentication with 24-hour session expiration
- **Privacy**: System SHALL comply with applicable data protection regulations and provide data deletion within 24 hours of request

### Usability

- **Learning Curve**: Students SHALL be able to complete first explanation session within 5 minutes of installation
- **Accessibility**: System SHALL comply with WCAG 2.1 Level AA standards
- **Language Support**: System SHALL provide complete functionality in English and Hindi with 95% translation accuracy

### Maintainability

- **Code Quality**: Extension code SHALL maintain 80% test coverage with automated testing
- **Logging**: System SHALL log all critical operations with structured logging for debugging
- **Monitoring**: System SHALL provide real-time dashboards for system health, costs, and usage metrics

### Cost

- **Per-Student Cost**: System SHALL maintain operational cost below ₹5 per student per month
- **Total Cost**: System SHALL maintain total monthly cost below ₹5,00,000 for 100,000 students
- **Cost Monitoring**: System SHALL alert administrators when costs exceed 80% of budget

## Technical Constraints

1. **VS Code Compatibility**: Extension MUST support VS Code versions 1.85.0 and above
2. **AWS Services**: System MUST use Amazon Bedrock (Claude 3.5 Sonnet), AWS Lambda, Amazon Transcribe, DynamoDB, AWS Amplify, Amazon Comprehend, and AWS KMS
3. **Programming Languages**: System MUST support JavaScript, Python, and Java code analysis
4. **Browser Support**: Web dashboard MUST support Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
5. **AWS Region**: System MUST deploy in AWS Asia Pacific (Mumbai) region for optimal latency
6. **Free Tier**: System MUST maximize use of AWS Free Tier to minimize costs

## Assumptions and Dependencies

### Assumptions

1. Students have VS Code installed and basic familiarity with the editor
2. Students have internet connectivity for initial setup and periodic syncing
3. Students are enrolled in BE CSE AI/ML programs at participating universities
4. AWS Bedrock (Claude 3.5 Sonnet) is available in Asia Pacific (Mumbai) region
5. Students consent to data collection for progress tracking and improvement

### Dependencies

1. **AWS Bedrock**: Availability and pricing of Claude 3.5 Sonnet model
2. **Amazon Transcribe**: Hindi language support quality and latency
3. **VS Code Extension API**: Stability of code execution interception APIs
4. **University Partnerships**: Collaboration with institutions like Chitkara University for pilot programs
5. **AWS Free Tier**: Continued availability of free tier limits for target services

## Success Metrics and KPIs

### Primary Metrics

1. **AI Dependency Reduction**: Reduce average student AI_Dependency_Ratio from 70% to 30% within 30 days
2. **Interview Pass Rate**: Improve technical interview pass rate by 40% for students using CodeGuardian for 60+ days
3. **Student Retention**: Achieve 80% student retention after 2 weeks of usage
4. **Scale**: Support 100,000 students in Phase 1 deployment

### Secondary Metrics

1. **Understanding Scores**: Achieve average Understanding_Score of 75% or higher across all students
2. **Engagement**: Maintain average of 5+ explanation sessions per student per week
3. **Language Adoption**: Achieve 40% Hindi usage among Tier 2-3 city students
4. **Performance**: Maintain 95th percentile explanation grading latency below 2 seconds
5. **Cost Efficiency**: Maintain per-student monthly cost below ₹5
6. **Accessibility**: Achieve WCAG 2.1 Level AA compliance score of 95% or higher

### Monitoring and Reporting

1. **Weekly Reports**: Generate automated reports showing AI dependency trends, engagement metrics, and cost analysis
2. **Monthly Reviews**: Conduct monthly reviews of interview pass rates and student feedback
3. **Real-Time Dashboards**: Provide real-time monitoring of system health, AWS costs, and user activity
4. **A/B Testing**: Conduct A/B tests on Passing_Threshold values, hint strategies, and gamification features to optimize learning outcomes

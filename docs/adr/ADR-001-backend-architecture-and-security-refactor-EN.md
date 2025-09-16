ADR-001: Backend Architecture and Security Refactor
Status: Accepted

Date: 2025-09-16

1. Context
After completing the initial MVP, I identified two critical, unacceptable flaws during testing. First, my initial synchronous architecture (v7.1) caused frequent request timeouts when calling the time-consuming OpenAI API, making the service highly unreliable. Second, during a security review, I discovered that sensitive Personally Identifiable Information (PII) was hardcoded in the source code and exposed in the public Git history, posing a severe privacy vulnerability. To elevate the project to a professional, open-source-ready standard, I decided that a major refactor covering both reliability and security was necessary.

2. Decision
I decided to execute a comprehensive, two-part refactor of the backend:

Architectural Evolution (v7.1 -> v7.3): I performed an iterative architectural refactor to resolve the timeout issue.

First, I moved to a purely asynchronous model (v7.2) to achieve an immediate response to the webhook and process the AI task in the background.

However, I realized this introduced a new security vulnerability by validating the signature only in the background task.

Ultimately, I settled on a hybrid asynchronous architecture (v7.3). It performs synchronous, real-time signature validation at the webhook entry point, dispatching only legitimate, time-consuming tasks to the background.

Data Security Refactor (v7.4): To eliminate the PII exposure risk, I executed a two-pronged emergency response plan.

Decoupling Data from Code: All PII was moved from the source code to an external config.json file, which is excluded from version control via .gitignore.

Rebuilding Git History: To ensure no trace of PII remained, I performed a complete repository rebuild, purging all past commit history and re-initializing the repository with only the secure, refactored code.

3. Alternatives Considered
On Architecture: I considered using a more complex task queue system like Celery, but opted for FastAPI's built-in BackgroundTasks for the sake of MVP simplicity.

On Security: I considered using tools like git filter-branch to clean the history, but a clean repository rebuild was deemed a simpler and more foolproof solution for a solo-developer project.

4. Consequences
Positive Consequences:

The application resolves the timeout issue via the hybrid asynchronous architecture, enhancing system reliability.

The data leak risk is completely mitigated by externalizing PII and rebuilding the Git history, ensuring project security.

The new architecture is more maintainable and extensible, with the key trade-offs and decision processes documented in this ADR.

Negative Consequences:

The detailed iterative commit history from the project's early stages is permanently deleted. This consolidated ADR now serves as the official historical record for these critical decisions.
# cscs-ci

Agent skill for interacting with CSCS CI infrastructure. This is useful e.g. for
doing CI-fix cycles through CI, or for setting up new CSCS CI pipelines.

This skill exists for a couple of major reasons:

- Agents tend to take a `cicd-ext-mw.cscs.ch...&type=gitlab` status url, go to
  GitLab, and conclude that they can't access the logs due to authorization
  requirements. This informs agents that they can remove the `&type=gitlab`
  parameter and access logs from the `cicd-ext-mw.cscs.ch` logs page instead.
- If I refer to cscs-ci or similar, agents will often try to go looking for a
  `cscs-ci` command and get confused. This clarifies that.
  
Beyond that, this skill also acts as a reference for creating CSCS CI pipelines
and some extra details. However, these are more reference style. The two points
above are where agents typically go wrong.

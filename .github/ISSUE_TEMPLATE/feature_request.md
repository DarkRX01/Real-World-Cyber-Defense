name: Feature Request
description: Suggest an improvement or new feature
title: "Feature: [Brief description]"
labels: ["enhancement", "needs-triage"]

body:
  - type: markdown
    attributes:
      value: |
        Thank you for suggesting an improvement! Describe your idea in detail.

  - type: textarea
    id: description
    attributes:
      label: Description
      description: What is the feature or improvement?
      placeholder: "Describe the feature..."
    validations:
      required: true

  - type: textarea
    id: problem
    attributes:
      label: Problem It Solves
      description: What problem does this address?
      placeholder: "This would help with..."
    validations:
      required: true

  - type: textarea
    id: use-case
    attributes:
      label: Use Case
      description: How would you use this feature?
      placeholder: "I would use it for..."
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      description: Any other approaches?
      placeholder: "Other options could be..."

  - type: textarea
    id: implementation
    attributes:
      label: Possible Implementation
      description: Optional - Any ideas on how to implement?
      placeholder: "This could be done by..."

  - type: checkboxes
    id: checklist
    attributes:
      label: Before Submitting
      options:
        - label: "I have checked existing issues and discussions"
          required: true
        - label: "This feature aligns with the project scope"
          required: true
        - label: "I would be willing to help implement this"
          required: false

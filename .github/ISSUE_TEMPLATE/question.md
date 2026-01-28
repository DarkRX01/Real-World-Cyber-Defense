name: Question
description: Ask a question about the extension
title: "Question: [Brief question]"
labels: ["question"]

body:
  - type: markdown
    attributes:
      value: |
        Have a question? We'd love to help!

  - type: textarea
    id: question
    attributes:
      label: Question
      description: What would you like to know?
      placeholder: "How do I...?"
    validations:
      required: true

  - type: textarea
    id: context
    attributes:
      label: Context
      description: Any additional context?
      placeholder: "I'm trying to..."
      required: true

  - type: dropdown
    id: topic
    attributes:
      label: Topic
      options:
        - "Setup/Installation"
        - "Configuration"
        - "Usage"
        - "API Integration"
        - "Development"
        - "Other"
    validations:
      required: true

  - type: textarea
    id: tried
    attributes:
      label: What Have You Tried?
      description: What steps have you already taken?
      placeholder: "I've tried..."

  - type: checkboxes
    id: checklist
    attributes:
      label: Before Asking
      options:
        - label: "I checked the README and documentation"
          required: true
        - label: "I searched existing issues and discussions"
          required: true

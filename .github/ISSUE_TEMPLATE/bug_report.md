name: Bug Report
description: Report a bug or unexpected behavior
title: "Bug: [Brief description]"
labels: ["bug", "needs-triage"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thank you for reporting a bug! Please provide detailed information to help us fix it.

  - type: dropdown
    id: extension-version
    attributes:
      label: Extension Version
      options:
        - "1.0.0"
        - "Other (please specify in description)"
    validations:
      required: true

  - type: dropdown
    id: chrome-version
    attributes:
      label: Chrome Version
      options:
        - "Latest"
        - "120.x"
        - "119.x"
        - "118.x"
        - "Older"
    validations:
      required: true

  - type: dropdown
    id: os
    attributes:
      label: Operating System
      options:
        - "Windows"
        - "macOS"
        - "Linux"
        - "Other"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: What is the bug? What were you trying to do?
      placeholder: "Describe the issue..."
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: How can we reproduce the bug?
      placeholder: |
        1. Navigate to...
        2. Click on...
        3. See the bug...
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should happen?
      placeholder: "The extension should..."
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happens?
      placeholder: "Instead, it..."
    validations:
      required: true

  - type: textarea
    id: error
    attributes:
      label: Error Message or Console Output
      description: Any error messages or console output? (F12 → Console)
      placeholder: "Paste any errors here..."

  - type: textarea
    id: screenshots
    attributes:
      label: Screenshots
      description: Optional - Add screenshots if helpful

  - type: textarea
    id: context
    attributes:
      label: Additional Context
      description: Any other relevant information?
      placeholder: "e.g., Does it happen in Incognito? In Reader mode? etc."

  - type: checkboxes
    id: checklist
    attributes:
      label: Before Submitting
      options:
        - label: "I have checked existing issues"
          required: true
        - label: "I am using the latest extension version"
          required: true
        - label: "I cleared the extension's threat log"
          required: false
        - label: "I haven't exposed my API key in this report"
          required: true

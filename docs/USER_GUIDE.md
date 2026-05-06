# CareBridge Local User Guide

This guide is for non-technical reviewers and field users.

## Install

1. Download `CareBridgeLocal-Setup-1.0.0.exe` from the repository `release/` folder.
2. Double-click the installer.
3. Open **CareBridge Local** from the Start Menu.

You do not need to install Python, Node.js, Rust, Docker, Ollama, or any developer tools.

## First Launch

1. Open the **Runtime Setup Wizard** at the top of the app.
2. If the reviewer kit includes a `llama.cpp` runtime bundle, import it with **Install Runtime**.
3. Use **Download E4B** for the recommended Gemma profile, or **Download E2B** on lower-memory machines.
4. If you already have a GGUF model file, use **Import local GGUF** instead.
5. Choose **Auto** or **Balanced (E4B)**, then click **Start Runtime**.

The app stores all local data under the user profile, not in a cloud account.

## Try A Demo Case

Use one of these scenarios:

- Pediatric fever: symptoms `fever, vomiting, very sleepy`; risk factors `child`; notes `dry mouth, not drinking well`.
- Pregnancy danger signs: symptoms `bleeding, severe headache`; risk factors `pregnancy`; notes `28 weeks pregnant`.
- Medication uncertainty: symptoms `dizziness`; notes `patient brought an unclear medicine label`.

Workflow:

1. Fill in **Patient label**, **Symptoms**, **Risk factors**, and **Notes**.
2. Click **Create Case**.
3. Click **Run Triage** and review urgency, red flags, missing information, and citations.
4. Ask a follow-up question in **Grounded Chat**.
5. Click **Export Referral Pack** when a handoff is needed.

## Offline Use

After runtime and model setup, the core workflow runs locally. You can import local guideline documents into **Knowledge Import** before going offline.

## Where Data Is Stored

CareBridge Local stores cases, imported documents, models, and exports on the local computer. It does not require a hosted database.

## Troubleshooting

- If the app says it cannot reach `127.0.0.1:8011`, close and reopen CareBridge Local.
- If **Start Runtime** is disabled, install/import a runtime and model first.
- If model download is slow, import a GGUF model file manually.
- If the machine has limited memory, use the E2B compatibility model.

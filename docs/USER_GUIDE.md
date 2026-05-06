# CareBridge Local User Guide

This guide is for non-technical reviewers and field users.

## Install

1. Download `CareBridgeLocal-Setup-1.0.0.exe` from the repository `release/` folder.
2. Double-click the installer.
3. Open **CareBridge Local** from the Start Menu.

You do not need to install Python, Node.js, Rust, Docker, Ollama, or any developer tools.

## First Launch

1. Type a question in **Ask CareBridge** on the first screen.
2. Use the sample questions if you want a quick demo.
3. Expand **Runtime Setup** only when you need to install/import the local Gemma runtime.
4. If the reviewer kit includes a `llama.cpp` runtime bundle, import it with **Install Runtime**.
5. Use **Download E4B** for the recommended Gemma profile, or **Download E2B** on lower-memory machines.
6. If you already have a GGUF model file, use **Import local GGUF** instead.
7. Choose **Auto** or **Balanced (E4B)**, then click **Start Runtime**.

The app stores all local data under the user profile, not in a cloud account.

## Try A Demo Case

Use one of these scenarios:

- Pediatric fever: symptoms `fever, vomiting, very sleepy`; risk factors `child`; notes `dry mouth, not drinking well`.
- Pregnancy danger signs: symptoms `bleeding, severe headache`; risk factors `pregnancy`; notes `28 weeks pregnant`.
- Medication uncertainty: symptoms `dizziness`; notes `patient brought an unclear medicine label`.

Workflow:

1. Ask the question directly on the home screen.
2. Expand **Clinical Case Tools** if you want to save a formal case.
3. Fill in **Patient label**, **Symptoms**, **Risk factors**, and **Notes**.
4. Click **Save Case**, then **Run Triage**.
5. Click **Export Referral** when a handoff is needed.

## Offline Use

After runtime and model setup, the core workflow runs locally. You can import local guideline documents into **Knowledge Import** before going offline.

## Where Data Is Stored

CareBridge Local stores cases, imported documents, models, and exports on the local computer. It does not require a hosted database.

## Troubleshooting

- If the app says it cannot reach `127.0.0.1:8011`, close and reopen CareBridge Local.
- If **Start Runtime** is disabled, install/import a runtime and model first.
- If model download is slow, import a GGUF model file manually.
- If the machine has limited memory, use the E2B compatibility model.

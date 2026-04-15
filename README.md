# Project Magnolia

**Your AI assistant for computational chemistry**

Project Magnolia is like having a smart research assistant who can run scientific software, design molecules, and keep detailed notes — all by chatting with it in plain English.

---

## What can it do?

Magnolia can help you with tasks like:

- **Molecular docking** — predict how a small peptide or drug binds to a protein
- **De novo design** — generate new peptide or protein sequences that might bind better
- **Pocket prediction** — find where on a protein a drug is most likely to stick
- **Run tracking** — remember which method worked best, so you don't have to keep notes by hand

Think of it as a lab notebook that can also press the "run" button on your experiments.

---

## How do I talk to it?

You chat with Magnolia using a program called **OpenCode** (or any compatible AI client). You simply type what you want in normal sentences, for example:

> *"I want to dock this peptide onto my target protein and find the best binding pose."*

> *"Design me 10 new peptides that might bind more tightly."*

> *"What did we learn from the last run?"*

The assistant will figure out the steps, run the software, and tell you the results.

---

## Key ideas (explained simply)

### 1. The Agent
The **agent** is the AI assistant itself — the part you chat with. It reads your request, decides which scientific tools to use, and reports back.

### 2. The Memory System
Magnolia keeps a **project notebook** automatically. It remembers:
- Which experiments you ran
- What scores or results you got
- Mistakes you hit and how they were fixed
- Tips that worked well (for example: "p2rank pocket restraints work better than manual ones")

This notebook lives inside your project folder, so if you move the project to another computer, the memories travel with it.

### 3. The Tools
Scientific software like **HADDOCK3**, **BoltzGen**, and **GROMACS** are stored in a `softwares/` folder. Magnolia knows how to call each one so you don't have to learn dozens of different command-line programs.

---

## Folder layout (the simple version)

```
project_magnolia/
├── opencode_cc_mem/          # The "brain" of the assistant
│   ├── rules/                # Instructions the AI follows
│   ├── mcp-servers/          # Memory and tool connectors
│   └── projects/             # Your actual science projects
│       └── my_project/   # Example: peptide docking project
│           ├── raw_input/    # Your PDB files and sequences
│           ├── runs/         # Results from docking or design
│           └── .magnolia/    # The assistant's notebook for this project
├── softwares/                # Scientific software (HADDOCK3, BoltzGen, etc.)
│   ├── bin/                  # Shortcuts to run the tools
│   ├── boltzgen/             # AI design tool
│   └── manifest.yaml         # List of installed tools
└── README.md                 # This file
```

**You mainly work inside `opencode_cc_mem/projects/<your_project_name>/`.** Everything else is managed by the assistant.

---

## Getting started

1. **Make sure OpenCode (or your AI client) is pointed at this folder.**
2. **Create a new project folder** under `opencode_cc_mem/projects/`, for example:
   ```
   opencode_cc_mem/projects/my_docking_project/
   ```
3. **Put your input files there** (for example: a protein PDB file and a peptide PDB file).
4. **Tell the assistant what you want to do.**

The assistant will:
- Check which tools are installed
- Prepare the run
- Execute it
- Save the results in `runs/`
- Write a summary in the project notebook

---

## Working with high-performance computers (HPC)

In the future, you may want to run big calculations on a university cluster (using **Slurm** or similar queue systems). Magnolia is designed for this:

- It can submit jobs to the cluster for you.
- The project notebook travels with your files, so the assistant can pick up where it left off when the cluster job finishes.
- **Important:** The AI assistant runs on your personal computer; it does not need to run directly on the cluster.

---

## Quick tips

- **You don't need to memorize commands.** Just describe what you want.
- **Check the notebook.** If you want to know what worked last time, ask the assistant or look in `projects/<name>/.magnolia/entries/`.
- **Don't worry about installing software.** The assistant installs tools into the `softwares/` folder automatically when needed.

---

## Need help?

If something goes wrong, just tell the assistant:

> *"That didn't work. Can you check the error and try again?"*

Because of the memory system, it will often know exactly what went wrong and how to fix it.

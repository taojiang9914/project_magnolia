# Project Magnolia

**A quick-learning intern for computational chemistry**

Project Magnolia is like hiring a very bright research intern who reads fast, runs experiments, writes detailed lab notes — and never forgets what you taught them. You work with Magnolia by chatting in plain English, giving it tasks, correcting it when needed, and building up a shared body of knowledge over time.

---

## What is Magnolia, really?

Think of Magnolia as an **intern**, not a magic box.

- It can **install and run** scientific software (docking, design, simulation)
- It can **read your old results** and summarize what happened
- It can **design new experiments** based on what it learned
- It **takes notes automatically** in a project notebook so you don't have to remember every detail
- But like any intern, it works best when you give it **clear instructions**, point it to the right files, and **correct it** when it goes off track

The more you work with it, the better it gets — because it remembers your project's history.

---

## What can it do?

Magnolia can help with tasks like:

- **Molecular docking** — predict how a peptide or drug binds to a protein
- **De novo design** — generate new sequences that might bind better
- **Pocket prediction** — find the best spots on a protein for a drug to stick
- **Run tracking** — keep a lab notebook of which methods worked and which didn't

---

## How do I talk to it?

You chat with Magnolia using a program like **OpenCode**. Just type what you want in normal sentences, the same way you'd explain a task to a student in your lab:

> *"I want to dock this peptide onto my target protein and find the best binding pose. The files are in `projects/my_project/raw_input/`."*

> *"Design me 10 new peptides that might bind more tightly, but start with the the motif since that worked best before."*

> *"What did we learn from the last run? And did we ever try pocket 2?"*

Magnolia will figure out the steps, run the software, and report back. If it misunderstands, just correct it — like you would with a trainee.

---

## Key ideas (explained simply)

### 1. The Intern
Magnolia is the AI agent — the part you chat with. It reads your requests, looks up what it knows, decides which tool to use, and reports back. It is fast and eager, but it needs you to point it to the right folders and tell it what matters.

### 2. The Lab Notebook (Memory System)
Every project has its own notebook at `projects/<name>/.magnolia/`. Magnolia writes down:
- Which experiments you ran
- Scores and results
- Errors you hit and how they were fixed
- Rules that worked (for example: *"p2rank pocket restraints are better than manual restraints for this protein"*)

Because the notebook lives inside your project folder, you can move the project to another computer and the intern still knows everything.

### 3. The Tools
Scientific programs like **HADDOCK3**, **BoltzGen**, and **GROMACS** live in a `softwares/` folder. Magnolia knows how to call them, but it installs them in isolated "fenced yards" so they don't interfere with each other. You don't need to memorize command lines.

---

## Folder layout (the simple version)

```
project_magnolia/
├── opencode_cc_mem/          # The "brain" and training of the intern
│   ├── rules/                # Lab protocols the intern follows
│   ├── mcp-servers/          # Connectors for memory and tools
│   └── projects/             # Your actual science projects
│       └── my_project/   # Example project
│           ├── raw_input/    # Your PDB files and sequences
│           ├── runs/         # Results from experiments
│           └── .magnolia/    # The intern's notebook for this project
├── softwares/                # Scientific software
│   ├── bin/                  # Shortcuts to run tools
│   ├── boltzgen/             # AI design tool
│   └── manifest.yaml         # List of installed tools
├── README.md                 # This file
└── WORKFLOW_GUIDE.md         # How to supervise the intern effectively
```

**You mainly work inside `opencode_cc_mem/projects/<your_project_name>/`.** Everything else is managed by Magnolia.

---

## Getting started

1. **Make sure your AI client (OpenCode) is pointed at this folder.**
2. **Create a new project folder**, for example:
   ```
   opencode_cc_mem/projects/my_docking_project/
   ```
3. **Put your input files there** (for example, a protein PDB and a peptide PDB).
4. **Tell Magnolia what you want**, including where the files are and what you have already tried.

**New to working with AI assistants?** Read [`WORKFLOW_GUIDE.md`](WORKFLOW_GUIDE.md) for a step-by-step example of how to supervise Magnolia effectively — from planning an experiment to analyzing results.

Magnolia will:
- Check which tools are installed
- Suggest a plan
- Run the experiment
- Save results in `runs/`
- Write a note in the project notebook

---

## Working with high-performance computers (HPC)

Eventually you may want to run big calculations on a university cluster (using **Slurm**). Magnolia is designed for this:

- It can submit jobs to the cluster for you.
- The project notebook travels with your files, so when the cluster job finishes, Magnolia can read the results and continue.
- **Important:** Magnolia runs on your personal computer. The cluster just runs the heavy calculations.

---

## Quick tips

- **Be specific.** The intern is smart, but it can't read your mind. Point it to files, mention prior runs, and say what you want changed.
- **Correct it.** If Magnolia is about to do something wrong, say *"Wait — do it this way instead."* Good collaboration means steering.
- **Check the notebook.** Ask *"What did we learn from the last run?"* or look in `projects/<name>/.magnolia/entries/`.
- **Let it install tools.** Magnolia will install software into `softwares/` automatically when needed.

---

## Need help?

If something goes wrong, just tell Magnolia:

> *"That didn't work. Can you check the error and try again?"*

Because of the memory system, it will often know exactly what went wrong and how to fix it.

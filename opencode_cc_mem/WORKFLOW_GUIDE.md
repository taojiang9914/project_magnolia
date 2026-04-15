# How to Work With Project Magnolia

Project Magnolia is like a **quick-learning research intern**, not a search engine or a magic button. The more context and direction you give it, the better it performs. This guide shows you how to supervise Magnolia effectively, using a real workflow pattern.

---

## The Golden Rule

**Bad (vague intern task):**
> *"Dock this peptide."*

**Good (clear intern task):**
> *"I want to dock a 5-residue peptide onto my protein. I already have PDB files in `projects/my_project/raw_input/`. I also have prior docking results in `/old/results/` using manual restraints — I'd like to try a pocket-based protocol and compare the scores."*

The second version gives the intern:
- The **goal**
- The **location of inputs**
- **Prior work** it should read
- A **specific improvement** you want to test

---

## Example Workflow: Supervising an Experiment From Start to Finish

Below is a realistic conversation between a PI and Magnolia. The specific science is anonymized, but the **structure of the interaction** is exactly how to get the best results.

### Step 1: State your goal with context

**You:**
> *"I'd like to install a generative design tool to design peptide binders. I have a directory at `projects/binder_design/` with a receptor structure and some existing docked peptides. I also want to make sure we track what we learn properly in the memory system. What do you think is the best way to manage software dependencies?"*

**Why this works:** You told the intern what you want, where the project lives, and that you care about keeping good notes. It can propose a strategy before touching anything.

**Intern response pattern:** Magnolia discusses the approach first (e.g., isolated environments per tool), then asks if it should proceed.

---

### Step 2: Give permission to act

**You:**
> *"Yes, proceed."*

**Why this works:** The intern now has clear authority to make changes.

**Intern response pattern:** Magnolia installs the tool, creates wrapper scripts, and reports what it did and where things live.

---

### Step 3: Correct mistakes early

**You:**
> *"Wait — I think we should keep all software in a shared `softwares/` directory, not in the base environment. And each tool should have its own fenced yard."*

**Why this works:** You corrected the plan before the intern went too far down the wrong path. Good supervision means catching errors early.

**Intern response pattern:** Magnolia adjusts course, cleans up, and reinstalls following your rule.

---

### Step 4: Point the intern to prior work

**You:**
> *"Now let's get back to the science. I actually already did docking for this project. See `/path/to/old_docking_results/`. Can you look at what was done?"*

**Why this works:** You're surfacing **existing knowledge** the intern wouldn't otherwise know about.

**Intern response pattern:** Magnolia reads reports, configs, and memory files. It synthesizes:
- Which protocol was used
- What scores were achieved
- What the key learnings were

---

### Step 5: Ask for analysis, then use it

**You:**
> *"Can you perform contact analysis on those short peptides?"*

**Why this works:** This is a specific, bounded task with clear inputs.

**Intern response pattern:** Magnolia analyzes contact maps and extracts rules like:
- "Position 1 prefers a positive charge"
- "Position 2 needs an aromatic residue"

---

### Step 6: Let the intern apply analysis to design

**You:**> *"Given those contact patterns, should we constrain our generative design?"*

**Why this works:** You explicitly link the analysis to the next step.

**Intern response pattern:** Magnolia translates the contact rules into a design specification, writes the config file, validates it, and asks if you want to run it.

---

### Step 7: Sequence tasks and verify

**You:**
> *"Run the constrained design first. Then set up physics-based docking to validate the best designs."*

**Why this works:** You sequence two dependent tasks and make validation explicit.

**Intern response pattern:**
1. Runs the design job
2. Reads the output (sequences, scores)
3. Generates PDB files for the top designs
4. Sets up docking runs using the *same proven protocol* from your prior work
5. Starts the most promising one

---

### Step 8: Ask the intern to check its own notebook

**You:**
> *"The memory system seems empty even though we did a lot. Is it working?"*

**Why this works:** You noticed the intern's lab notebook is incomplete and asked it to investigate.

**Intern response pattern:** Magnolia inspects the notebook, explains why auto-capture failed (bash commands bypassed the logging system), proposes a fix (a wrapper that auto-logs every command), implements it, and retroactively writes up the key runs.

---

### Step 9: Make the intern commit its work

**You:**
> *"Commit the changes and push to git while we wait for the docking run to finish."*

**Why this works:** You treat infrastructure improvements as first-class deliverables, just like any other lab work.

---

## Common Mistakes to Avoid

| Mistake | Why It Hurts | Better Alternative |
|---------|-------------|-------------------|
| *"Do docking"* | Intern doesn't know which system, files, or protocol | *"Dock the peptide in `raw_input/peptide.pdb` onto the protein in `raw_input/protein.pdb`. Use the same pocket restraints from my Jan 26 run."* |
| *"Why is it slow?"* | No context on what's running | *"The HADDOCK3 job I started 20 minutes ago seems stuck. PID is 92410. Can you check?"* |
| *"Fix it"* | Intern doesn't know what "it" is | *"The previous BoltzGen run failed with a CUDA error about `libnvrtc`. Can you fix the library path in the wrapper script?"* |
| Asking 5 things at once | Intern may miss one or do them out of order | Break into 2–3 messages, confirm each step |
| Never correcting the intern | Small errors compound over time | *"Actually, Phe is at position 2, not 3. Please fix the memory entry."* |
| Treating it like a search engine | You get shallow answers instead of experiments | Give it files to read and tasks to execute |

---

## Pro Tips for Good Supervision

1. **Point to files.** The intern can read files and directories. Saying *"see `/path/to/results/`"* is extremely helpful.
2. **Reference past runs.** The intern can read old configs and reports. You don't need to re-explain what you did last month.
3. **Say "no" or "wait."** If the intern is about to do something wrong, interrupt it. Good supervision requires steering.
4. **Ask "why?"** If the intern recommends something, ask for its reasoning. It often reveals useful context you hadn't considered.
5. **Use the notebook.** Ask *"What did we learn from the last run?"* or *"Has this error happened before?"*
6. **Build habits together.** The first session may feel slow as you establish folder structures and rules. After that, the intern works faster because it remembers.

---

## Quick-Start Template

Copy and adapt this for your first session with the intern:

> *"I want to [GOAL] for my project in `projects/[PROJECT_NAME]/`. I have [INPUT FILES] in `raw_input/`. I [HAVE / HAVE NOT] done this before. [If yes: see `path/to/prior_results/` for previous runs.] I'd like to [SPECIFIC OUTCOME]. Please look at what we have, suggest an approach, and tell me what you'd do first."*

---

## Remember: Magnolia learns from you

The best results come from treating Magnolia as a trainee who:
- **Works hard** when given clear tasks
- **Remembers everything** you teach it
- **Needs correction** from time to time
- **Gets better** the longer you work together

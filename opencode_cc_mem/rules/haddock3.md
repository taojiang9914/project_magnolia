---
name: haddock3
description: Critical rules, common mistakes, module parameters, and troubleshooting for HADDOCK3 molecular docking.
version: 1.0
last_verified: 2026-03-30
---

# HADDOCK3 Rules

## Mandatory: Self-Contained Run Directories

Every HADDOCK3 run gets its own directory under `runs/` with ALL inputs copied in:

```
runs/YYYY-MM-DD_<name>/
├── config.cfg          # run_dir = "output"
├── receptor.pdb        # COPY (not symlink)
├── ligand.pdb          # COPY (with chain ID)
├── ambig.tbl           # Restraints
└── output/             # Created by HADDOCK3
```

- `run_dir = "output"` (relative, never absolute path)
- All input files in same directory as config.cfg
- Never reference files outside the run directory

## Mandatory: Protein-Ligand Topology

If docking a ligand, `ligand_top_fname` and `ligand_param_fname` MUST appear in **ALL** CNS-based modules:

```
topoaa, rigidbody, flexref, emref, mdref, emscoring, mdscoring
```

Skipping this in any module causes: `missing nonbonded Lennard-Jones parameters`

## Common Mistakes

| Mistake | Correct |
|---------|---------|
| Output files are `.pdb` | Most are `.pdb.gz` (compressed) |
| Looking for `cluster.out` | It's `cluster.out.gz` |
| Looking for `structures.txt` | It's `seletopclusts.txt` |
| Actpass with comma-separated residues | Use SPACE-separated |
| Actpass with 1 line | Must have exactly 2 lines (active, passive) |
| Ligand params only in `[topoaa]` | Must be in ALL CNS modules |
| ACPYPE lowercase atom types | Convert `.par` atom types to UPPERCASE |
| `haddock3-restraints restrain_ligand -n 20` | Use `--max-restraints 20` |

## Essential Commands

```bash
haddock3 config.cfg                        # Launch workflow
haddock3-cfg -m rigidbody                  # View module parameters
haddock3-restraints active_passive_to_ambig actpass1.txt actpass2.txt > ambig.tbl
haddock3-restraints validate_tbl ambig.tbl # Validate restraints
haddock3-score complex.pdb                 # Quick score
haddock3-pp protein.pdb > clean.pdb       # Preprocess PDB
```

## Module Categories

- **Topology**: topoaa (always first)
- **Sampling**: rigidbody, lightdock, gdock
- **Refinement**: flexref, emref, mdref
- **Analysis**: caprieval, seletop, clustfcc, seletopclusts, contactmap

## Scoring Weights

| System | w_vdw | w_elec | w_desolv | w_air |
|--------|-------|--------|----------|-------|
| Protein-protein | 1.0 | 0.2 | 1.0 | 0.01 |
| Protein-DNA | 1.0 | 0.2 | 1.0 | 0.01 |
| Protein-glycan | 1.0 | 0.4 | 1.0 | 0.01 |

## Protein-Ligand Specifics

- Higher sampling: 2000-5000 (small ligand, many poses)
- `inter_rigid = 0.01` for buried sites
- `mdsteps_rigid = 0` and `mdsteps_cool1 = 0` in flexref for small ligands

## Sampling Guidelines

| Scenario | Sampling |
|----------|----------|
| Strong restraints | 1000 |
| Weak restraints | 2000-5000 |
| Ab-initio | 5000-10000+ |
| Ligand | 2000-5000 |

## Quality Red Flags

- Positive HADDOCK score
- No clusters formed (all singletons)
- 100% of output not generated
- All models identical

## Error Resolution

| Error | Fix |
|-------|-----|
| `missing nonbonded Lennard-Jones parameters` | Add ligand_top/param to ALL CNS modules |
| `50% output not generated` in topoaa | Check .par atom types (lowercase → uppercase) |
| `actpass file does not have two lines` | File needs exactly 2 lines |
| `invalid literal for int()` | SPACE-separated, not comma-separated |
| `Could not identify chainID or segID` | Add chain ID at column 22 in PDB |
| Ligand flies away in MD | Set `mdsteps_rigid=0`, `mdsteps_cool1=0` |

## Workflow Template

```toml
run_dir = "output"
molecules = ["mol1.pdb", "mol2.pdb"]
mode = "local"
ncores = 40

[topoaa]

[rigidbody]
ambig_fname = "ambig.tbl"
sampling = 1000

[seletop]
select = 200

[flexref]

[emref]

[clustfcc]

[seletopclusts]

[caprieval]
```

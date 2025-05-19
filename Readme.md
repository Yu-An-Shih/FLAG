# FLAG: Formal and LLM-assisted SVA Generation for Formal Specifications of On-Chip Communication Protocols

## Reproducing the results

### 1. Property Generation & SAT-based Property Check

```
python spec2sva.py -w <info_file> -g <grammar_file> [-o <output_dir>]
```
For example: `python spec2sva.py -w waveforms/AXI/handshake.json -g grammar/complete.json -o results/`

The `<info_file>` consists of the signal information and timing diagrams of the functionality group. This command generates candidate properties according to the `<grammar_file>` and signal information, and performs the SAT-based property check with respect to the timing diagrams. The following files will be generated in `<output_dir>`:
- `templates_*.json`: The property templates in various formats.
- `properties_*.json`: The formally checked properties in various formats.

Please view `spec2sva/main.py` for more execution options.

### 2. LLM-assisted Property Filtering

```
cd LLM_filtering
python run.py
```

The command-line interface for this step is under development and not flexible at this moment. So far, the formally-checked properties, textual description, and target properties and placed under their corresponding directory of the functionality group for each protocol. The results would be generated in the same directory. Please view `LLM_filtering/run.py` for more information.

You may observe some naming convention mismatch between the paper and this repository. We will gradually modify the naming conventions of this repository to match those in the paper.

## Software dependencies

- [Z3] (https://github.com/Z3Prover/z3), version 4.13.3
- [OpenAI Python API] (https://platform.openai.com/docs/api-reference/introduction)

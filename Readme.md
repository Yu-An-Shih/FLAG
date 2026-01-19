# SVAG: Formal and LLM-assisted SVA Generation for Formal Specifications of On-Chip Communication Protocols

## Reproducing the results

### 1. Grammar-based Template Generation & Template-based Property Generation & SAT-based Property Filtering

```
python spec2sva.py all -g <grammar_file> -w <tds_file> [-wd] [-o <output_dir>] [-v]
```
For example: `python spec2sva.py -g grammar/complete.json -w test_cases/AXI/channel_handshake/timing_diagrams.json -o results/`

Our framework first generates a template set based on the user-defined grammar in `<grammar_file>`. Then, the candidate properties are generated and filtered based on the timing diagrams (`<tds_file>`) for the target mechanism. The `-wd` flag indicates that the timing diagrams are provided in WaveDrom format instead of our self-defined JSON format. Note that we only support a subset of WaveDrom syntax for now.

The following files will be generated in `<output_dir>`:
- `sat_filtered_*.json`: The SAT-filtered properties in various formats.
If the verbose option (`-v`) is used, the following intermediate results will also be stored:
- `templates_*.json`: The property templates in various formats.
- `candidates_*.json`: The candidate properties before SAT-based filtering, in various formats.

Please view `spec2sva/main.py` for more execution options.

### 2. LLM-based Property Filtering & LLM-as-a-judge

All LLM agents can be found in the `LLM-based_property_filtering/` directory. Each agent is implemented by Python scripts that (1) creates a batch file to query LLMs via the [OpenAI Batch API](https://platform.openai.com/docs/guides/batch) and (2) parses the model outputs to obtain the results. Please refer to the Python scripts for detailed prompts and configurations.

The grammars used in our experiments are listed under the `grammar/` directory. The corresponding template sets are under the `templates/` directory. The timing diagrams and results for each protocol mechanism can be found under the `test_cases/` directory. Intermediate results produced by each LLM agent are also stored in its corresponding `work/` directory.

## Software dependencies

- [Z3](https://github.com/Z3Prover/z3), version 4.13.3
- [OpenAI Python API](https://platform.openai.com/docs/api-reference/introduction)

# Preparing Servable Archives with Refgenie and Snakemake

[refgenie/refgenieserver1 repository](https://github.com/refgenie/refgenieserver1/) contains all the necessary files to generate and execute a Snakemake workflow that builds and archives servable reference genome assets. The workflow is designed to be run locally or on a cluster, leveraging the flexibility of Snakemake.

By following these instructions, you can efficiently generate and execute a Snakemake workflow for building and archiving servable reference genome assets.

## Snakefile Generation

To enhance flexibility, the Snakefile can be dynamically generated from a Jinja2 template using `refgenie generate` command:

```console
refgenie1 generate snakefile --help

usage: refgenie generate snakefile [-h] --output-path O [--snakefile-template-path S]

Generate a Snakemake file.

options:
  -h, --help                         show this help message and exit
  --output-path O, -o O              Path to save the generated Snakefile.
  --snakefile-template-path S, -s S  Path to the Snakefile template. If not provided, the default template will be used.
```

```console
refgenie1 generate snakefile --output-path generated.smk
```

This script **utilizes the available Refgenie configuration** to generate the Snakefile. The asset-building rules and dependancies between them are derived from the recipes currently managed by Refgenie.

## Usage

To run the workflow, ensure that Snakemake and Refgenie are installed and configured, and that the Snakefile has been generated.

### Input Files

Many recipes require input files (e.g. `fasta` recipe requires an input FASTA file), which need to be available to the asset building software. If needed, refer to [Extra: Downloading recipe input files](#extra-downloading-recipe-input-files) section below for more information on how the download process can be streamlined.

### Configuration

#### PEP Configuration

The workflow expects a [PEP (Portable Encapsulated Project)](https://pep.databio.org/) configuration file in the `./pep` directory. The PEP must contain the following attributes:

- `genome_name`: The name of the genome to prepare the servable archive for.
- `genome_description`: A description of the genome.
- `fasta_file_path`: The path to the FASTA file for the genome.
- `asset_groups`: A list of asset groups to build for the genome.

Additionally, the PEP must define the asset groups to be built for each genome, which can be specified using a subsample table.

Example PEP:

**config.yaml**:

```yaml
pep_version: 2.0.0
sample_table: sample_table.csv
subsample_table: subsample_table.csv

sample_modifiers:
  append:
    fasta_file_path: path
  derive:
    attributes: [fasta_file_path]
    sources:
      path: ${REFGENIE_INPUTS}/{genome_name}.fa
```

A real-life [example of a PEP config](./pep/config.yaml) file

**sample_table.csv**:

```csv
sample_name,genome_name,genome_description
rCRSd,rCRSd,The revised Cambridge reference sequence.
mm10,mm10,The GCA_000001635.5 sequences for alignment pipelines from NCBI.
hg38,hg38,The GCA_000001405.15 GRCh38 no-alt analysis set from NCBI.
```

A real-life [example of PEP sample table](./pep/sample_table.csv) file

**subsample_table.csv**:

```csv
genome_name,asset_group
rCRSd,fasta
rCRSd,bowtie2_index
rCRSd,bwa_index
dm6,fasta
```

A real-life [example of PEP subssample table](./pep/assets.csv) file

### Environment Variables

In addition to the standard environment variables used to configure Refgenie, the workflow requires the following environment variables:

- `REFGENIE_INPUTS`: The path to the directory where the input files for the workflow are stored.
  - make sure files in `$REFGENIE_INPUTS` are named according to the convention used in the PEP
- `TEMPLATE_THREADS`: The default number of threads to use for template generation. This parameter affects the `threads` parameter for asset groups whose recipes do not specify a default number of threads.

### Running the Workflow

Once configured, you can run the workflow using the following command:

```bash
snakemake --jobs <num_cores_if_local/num_parallel_jobs_if_cluster>
```

```bash
snakemake --jobs unlimited --snakefile generated.smk --default-resources slurm_account=<acct> slurm_partition=standard mem_mb=32000 --cores 8 --workflow-profile <path_to_snakemake_dir>
```

Note: `--workflow-profile` needs to point to a directory where snakemake `config.yaml` is located, which in turn points to the executor to be used.

```yaml
executor: slurm
```

### Recipe software dependencies

The recipes very often require specialized bioinformatics software to build the assets which usually isn't available in the your system/head node.

Here are potential ways to manage the software dependencies:

- (recommended) [Bulker Refgenie tutorial](https://bulker.databio.org/en/latest/refgenie_tutorial/)
  - we use [more recent bulker Refgenie manifest](refgenie1_bulker_manifest.yaml)
- [Snakemake: using-environment-modules](https://snakemake.readthedocs.io/en/latest/snakefiles/deployment.html#using-environment-modules)
- [Snakemake: running-jobs-in-containers](https://snakemake.readthedocs.io/en/latest/snakefiles/deployment.html#running-jobs-in-containers)
  - `snakemake --software-deployment-method apptainer`
  - also check `singularity:` directive with `snakemake --use-singularity` flag

## Extra: Using Taskfile

The workflow can also be run using [Taskfile](https://taskfile.dev/#/) for easier management of tasks. To run the workflow using Taskfile, use the following command which uses the tasks defined in [Taskfile.yaml](https://github.com/refgenie/refgenieserver1/blob/master/Taskfile.yaml)

```bash
task archive
```

## Extra: Downloading recipe input files

The `./pep/download_recipe_inputs.py` script can be used to download the input files for the recipes from the sources specified in the `./pep/recipe_inputs_sources.csv` file.

```bash
uv run python download_recipe_inputs.py recipe_inputs_sources.csv <output_dir>
```

## Extra: Report Generation

Snakemake can generate a detailed report of the workflow execution, providing a visual overview and verifying that all steps ran as expected. To generate the report, use the following command:

```bash
snakemake --report refgenie.html
```

# Testing a uenv with ReFrame

CSCS tests uenv with the [cscs-reframe-tests](https://github.com/eth-cscs/cscs-reframe-tests) suite: in the uenv build pipeline after an image is built, in the regular tests of each cluster, and when a cluster is upgraded.
An image takes part when its recipe has an `extra/reframe.yaml` file.
Run the same tests by hand on a freshly built image, before it is deployed: they exercise MPI, GPU and application behavior at a scale that `uenv run` smoke tests do not.

Two things are needed:

- `extra/reframe.yaml` in the recipe: says how to load the uenv, and which tests apply to it.
- tests in `cscs-reframe-tests` that match it. They often exist already; write new ones only for software that has none.

The test suite has its own agent notes, `skills/reframe-alps/SKILL.md` in its repository. Read them after cloning: they cover ReFrame options, Slurm accounts, partitions and reservations. This page covers the uenv side.

## `extra/reframe.yaml`

Stackinator copies the `extra/` directory of the recipe to `meta/extra/` in the image, which is where ReFrame reads the file.

```yaml
default:                # name of the environment: free choice, one entry per environment to test
  features:             # which tests are run
    - cuda
    - mpi
    - openmp
    - osu-micro-benchmarks
  cc: mpicc             # compiler wrappers used by tests that build
  cxx: mpic++
  ftn: mpifort
  views:                # views to load, becomes `#SBATCH --view=`
    - default
  # activation:         # optional: commands run before each test, e.g. for a view of modules
  #   - module load cuda cray-mpich
```

Each top-level entry becomes one ReFrame programming environment, and every selected test is run once in each.
Add a second entry to test a second way of loading the image, for example a `modules` view with `module load` commands in `activation`.

Check the file against the recipe:

- **`views` must name views that exist** in `environments.yaml`. Renaming a view without updating `reframe.yaml` leaves the file pointing at a view that is not there.
- **Start from the `reframe.yaml` of a similar recipe**, as with the rest of the recipe, then correct the views and features.

### Choosing features

A test declares the environments it runs in with `valid_prog_environs`, for example `['+uenv +mpi +cuda']` or `['+pytorch']`.
A feature in `reframe.yaml` is a claim that the environment provides what such tests need. The `uenv` feature is added automatically.

List the features the test suite knows, and the tests behind one of them:

```bash
cd cscs-reframe-tests
grep -rhoE "valid_prog_environs\s*=\s*\[[^]]*\]" checks | grep -oE "\+[A-Za-z0-9_-]+" | sort | uniq -c | sort -rn
grep -rn -- "+osu-micro-benchmarks" checks
```

Common features:

| Feature | The environment provides | Tests it selects (examples) |
|---|---|---|
| `serial`, `openmp` | a compiler (`cc`, `cxx`, `ftn`) | build-and-run checks such as STREAM |
| `mpi` | MPI compiler wrappers and `srun` launch | MPI build-and-run checks |
| `cuda` | the CUDA toolkit (`nvcc`, headers, libraries) | GPU builds, such as gpu_burn |
| `osu-micro-benchmarks` | the OSU benchmark executables in the view | point-to-point and collective latency and bandwidth, on CPU and, with `cuda`, on GPU |
| `nccl-tests` | the NCCL test executables in the view | NCCL all-reduce and send-receive bandwidth |
| `prgenv` | a general programming environment | the wide set of compile-and-run checks. Not for application images |
| `<application>`, `<application>-dev` | the application, or everything needed to build it | the tests of that application, e.g. `pytorch`, `cp2k`, `gromacs`, `arbor-dev` |

- List a feature only when the view provides it: a feature for software that is missing gives failing tests, not skipped ones.
- General features select general tests. Some tests ask only for `+uenv` with `+cuda` or `+mpi`, and are selected for every image with those features although they test other software. Find them in the list of selected tests (below), and leave them out with `-x` when running by hand.
- Features that no test asks for (for example `cray-mpich`, `nccl`) do no harm, and select nothing.

## Setting up

ReFrame is installed on Alps: there is nothing to build.
Run it on a login node. ReFrame submits the Slurm jobs and waits for them, so it does not need an allocation of its own.

```bash
source /capstor/store/cscs/cscs/public/reframe/reframe-stable/$CLUSTER_NAME/rfm-env/bin/activate
git clone https://github.com/eth-cscs/cscs-reframe-tests.git    # the `main` branch
cd cscs-reframe-tests
```

Point `CSCS_RFM_UENV` at the image. It takes the path of a SquashFS file or the label of an image in the uenv repository:

```bash
# an image that was just built: the path of the squashfs file
export CSCS_RFM_UENV=/path/to/store.squashfs
# or an image that was pulled or added to the uenv repository: its label
export CSCS_RFM_UENV=prgenv-gnu/25.11:v1
```

**With a path, ReFrame reads `meta/extra/reframe.yaml` from the directory that holds the SquashFS file**, not from inside the image. A Stackinator build directory has `store.squashfs` but no `meta/` beside it, so extract it:

```bash
img=$SCRATCH/<project>/store.squashfs          # on a shared filesystem, not /dev/shm: compute nodes mount it
unsquashfs -q -d $(dirname $img)/sq $img meta && mv $(dirname $img)/sq/meta $(dirname $img)/meta && rmdir $(dirname $img)/sq
```

Keep one image per directory, as `meta/` belongs to the image beside it.
This copy of `meta/extra/reframe.yaml` can be edited to try other features and views without rebuilding the image: put the result back in the recipe afterwards.

If the file is not found, ReFrame prints `Skipping uenv ..., there was an error reading the metadata`, goes on without the uenv, and finds only tests of the `builtin` environment.

## Running the tests

Three steps: list, dry run, run.

```bash
# select the environments of the uenv, not the `builtin` environment or the CPE
sel="-C config/cscs.py -c checks -R --system $CLUSTER_NAME:normal -p '(?!PrgEnv-.*|builtin)' -S build_locally=0"

# 1. which tests do the features select?
eval reframe $sel -l

# 2. generate the job scripts without submitting, and read them
eval reframe $sel --prefix $SCRATCH/rfm/dry --dry-run
find $SCRATCH/rfm/dry/stage -name 'rfm_job.sh' | xargs grep -H -E '^#SBATCH --(ntasks|ntasks-per-node|time|uenv|view)'

# 3. run
eval reframe $sel --prefix $SCRATCH/rfm/run --keep-stage-files --performance-report -r
```

- **`-S build_locally=0` is required.** Without it, tests that compile do so on the login node, where the image is not mounted, and fail with errors like `make: nvcc: Command not found` although the view provides the tool. With it the build is a job with `--uenv` and `--view`, as in the build pipeline.
- `--system <cluster>:normal` selects the partition as ReFrame knows it. The names are in `config/systems/<cluster>.py`.
- `--prefix` puts the stage and output directories on `$SCRATCH`. Without it they are created in the current directory.
- `-n <pattern>` selects tests by name and `-x <pattern>` leaves tests out. Both take regular expressions.
- `-S <variable>=<value>` sets a variable of the tests, such as the version of the software that a test downloads. The variables are declared with `variable(...)` in the test.
- `--tag='maintenance|production'` reduces the selection to the tests that are run when a uenv is deployed.

**Check the dry run before running.** In each `rfm_job.sh`:

- `#SBATCH --uenv=` is the image and `#SBATCH --view=` is the view from `reframe.yaml`;
- `--ntasks` divided by `--ntasks-per-node` is the number of nodes. Some tests are large: the Megatron-LM tests of the `pytorch` feature use 16 and 32 GPU nodes. Tell the user what will be submitted, and agree before running tests that go beyond the resources they offered.

Expect to wait: the jobs are queued in the `normal` partition like any other, and ReFrame returns when the last one has finished. Run it in the background and do something else.
The `debug` partition (`-J=--partition=debug`) starts sooner, but its QoS limits the number of jobs a user can submit: check with `sacctmgr show qos debug format=name,maxsubmitpu,maxjobspu`, and add `--exec-policy=serial` so that ReFrame submits one job at a time.

## Reading the results

ReFrame prints `[ OK ]` or `[ FAIL ]` for each test, then a summary of the failures with the reason, and the performance report.
With `--keep-stage-files`, the files of each test are in `<prefix>/stage/<cluster>/<partition>/<environment>/<test>/`: the job script `rfm_job.sh`, its output `rfm_job.out` and `rfm_job.err`, and for tests that build, `rfm_build.sh`, `rfm_build.out` and `rfm_build.err`.

A failure is one of:

- **sanity**: the test did not produce the expected output. Read `rfm_job.err`. The image may be broken, or the test may assume something the image does not provide: a missing executable usually means a feature was claimed that the view does not provide.
- **performance**: the test ran and its figure of merit is outside the reference range. Compare with the reference in the test. Environment variables set by the test can override the ones the view sets, so check `rfm_job.sh` before blaming the image.
- **build**: a test that compiles against the uenv failed. Read `rfm_build.err`: these find missing headers, wrappers that do not link, and `pkg-config` files that are not in the view.

A test that needs a failed build is reported as skipped, so one build failure can hide several tests: count the tests that ran in the last line, `Ran 16/21 test case(s) ... 5 skipped`.

To run a test again by hand, `cd` to its stage directory and `sbatch rfm_job.sh`. Copy and edit the script to test a hypothesis, such as unsetting a variable that the view sets, before changing the recipe.

Failures that are not faults of the build are common with an image that has newer software or other settings than the images the tests were written for. Seen with a PyTorch image:

- **The view tunes the environment for something else than the test measures.** Its libfabric settings for NCCL (`FI_CXI_RDZV_THRESHOLD=0` and related) send every MPI message of 256 bytes or more through the rendezvous protocol, so the OSU latency tests measure 11 us where the reference is 2.3 us. Unsetting the variables in a copy of the job script gave the reference figure: the setting is a choice of the recipe, to confirm with the user, not a broken MPI.
- **A test pins an old version of the application.** The Megatron-LM test checks out a commit from before the Transformer Engine in the image, and fails in its sanity check before training starts. A newer version (`-S megatron_release=<commit>`) gets further, and then needs arguments the test does not pass. When a test needs more than a variable to run against the image, stop and report it: the test needs an update by its maintainers, and the image has to be validated another way meanwhile.
- **A test builds source that does not compile with a newer library.** The OSU benchmarks 7.2 that a test downloads do not compile with CUDA 13 (`cudaMemPrefetchAsync` changed), which skips the tests that use them. The OSU executables that the image provides are tested separately and pass.
- **A test measures the node, not the image.** Tests of the system, such as the CXI GPU loopback bandwidth, are selected for every uenv environment on a GPU partition and use none of the image.

Decide for each failure whether the image or the test is wrong.
Fix the image in the recipe. Fix a test in a branch of `cscs-reframe-tests`, and tell the user: the tests are shared by all uenv and clusters, so changes go through a pull request to that repository.
Record the tests that were run, and their results, in the `README.md` of the recipe.

## Writing a test for new software

When no test exists for the software in the image, add one in `checks/apps/<name>/` of `cscs-reframe-tests`, and a feature for it in `reframe.yaml`:

- select environments with the feature, `valid_prog_environs = ['+<name>']`, and systems with `valid_systems = ['+uenv']`, never by the names of clusters or partitions;
- `import uenv` and use `uenv.uarch(self.current_partition)` (`gh200`, `a100`, `zen2`, `zen3`, `mi200`, `mi300`) to set build flags, the Slurm resources and performance references for each node type;
- build on the compute node (`build_locally = False`), where the uenv is mounted;
- use an existing uenv test as the model, e.g. `checks/apps/arbor/arbor-dev.py`.

The [ReFrame tutorial of alps-uenv](https://eth-cscs.github.io/alps-uenv/pkg-reframe/) walks through that example, test by test.

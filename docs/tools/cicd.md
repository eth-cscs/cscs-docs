[](){#ref-cicd}
# Continous Integration / Continuous Deployment (CI/CD)

[](){#ref-cicd-containerized-intro}
## Introduction containerized CI/CD

Containerized CI/CD allows you to build containers and run them at scale on CSCS systems. The basic idea is that you provide a [Dockerfile](https://docs.docker.com/reference/dockerfile/) with build instructions and run the newly created container. Most of the boilerplate work is being taken care by the CI implementation such that you can concentrate on providing build instructions and testing. The important information is provided to you from the CI side for the configuration of your repository.

We support any git provider that supports [webhooks](https://en.wikipedia.org/wiki/Webhook). This includes GitHub, GitLab and Bitbucket. A typical pipeline consists of at least one build job and one test job. The build job makes sure that a new container with your most recent code changes is built. The test step uses the new container as part of an MPI job; e.g., it can run your tests on multiple nodes with GPU support.

Building your software inside a container requires a Dockerfile and a name for the container in the registry where the container will be stored. Testing your software then requires the commands that must be executed to run the tests. No explicit container spawning is required (and also not possible). Your test jobs need to specify the number of nodes and tasks required for the test and the test commands.

Here is an example of a full [helloworld project](https://github.com/finkandreas/containerised_ci_helloworld).

It is also helpful to consult the [GitLab CI yaml](https://docs.gitlab.com/ee/ci/yaml/) reference documentation and the [predefined pipeline variables reference](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html).

[](){#ref-cicd-containerized-tutorial}
### Tutorial Hello World

In this example we are using the [containerized hello world repository](https://github.com/finkandreas/containerised_ci_helloworld). This is a sample Hello World CMake project. The application only echos `Hello from $HOSTNAME`, but this should demonstrate the idea of how to run a program on multiple nodes. The pipeline instructions are inside the file `ci/cscs.yml`. Let's walk through the pipeline bit by bit.
```yaml
include:
  - remote: 'https://gitlab.com/cscs-ci/recipes/-/raw/master/templates/v2/.ci-ext.yml'
```

This block includes a yaml file which contains definitions with default values to build and run containers. Have a look inside this file to see available building blocks.
```yaml
stages:
  - build
  - test
```
Here we define two different stages, named `build` and `test`. The names can be chosen freely.
```yaml
variables:
  PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/helloworld:$CI_COMMIT_SHORT_SHA
```

This block defines variables that will apply to all jobs. See [CI variables](https://confluence.cscs.ch/spaces/KB/pages/868812112/Continuous+Integration+Continuous+Deployment#ContinuousIntegration/ContinuousDeployment-CIvariables).

```yaml
build_job:
  stage: build
  extends: .container-builder-cscs-zen2
  variables:
    DOCKERFILE: ci/docker/Dockerfile.build
```

This adds a job named `build_job` to the stage `build`. This runner expects a Dockerfile as input, which is specified in the variable `DOCKERFILE`. The resulting container name is specified with the variable `PERSIST_IMAGE_NAME`, which has been defined already above, therefore it does not need to be explicitly mentioned in the `variables` block, again. There is further documentation of this runner at gitlab-runner-k8s-container-builder.
!!! todo
    link to runner specs

```yaml
test_job:
  stage: test
  extends: .container-runner-eiger-zen2
  image: $PERSIST_IMAGE_NAME
  script:
    - /opt/helloworld/bin/hello
  variables:
    SLURM_JOB_NUM_NODES: 2
    SLURM_NTASKS: 2
```

This block defines a test job. The job will be executed by the container-runner-eiger-zen2.
!!! todo
    link to runner

This runner will pull the image on the cluster Eiger and run the commands as specified in the `script` tag. In this example we are requesting 2 nodes with 1 task on each node, i.e. 2 tasks total. All [Slurm environment variables](https://slurm.schedmd.com/srun.html#SECTION_INPUT-ENVIRONMENT-VARIABLES) are supported. The commands will be running inside the container specified by the `image` tag.

[](){#ref-cicd-cscs-impl}
## CI at CSCS
### Enable CI for your project

While the procedure to enable CSCS CI for your repository consists of only a few steps outlined below, many of them require features in GitHub, GitLab or Bitbucket. The links in the text contain additional steps which may be needed.
Some of those documents are non-trivial, especially if you do not have considerable background in the repository features. Plan sufficient time for the setup and contact a GitHub/GitLab/Bitbucket professional, if needed.

1. **Register your project with CSCS**: The first step to use containerized CI/CD is to register your Git repository with CSCS. Please open an [Service Desk ticket](https://support.cscs.ch/) for this step. Once your project has been registered you will be provided with a webhook-secret.

1. **Set up CI**: Head to the [CI overview page](https://cicd-ext-mw.cscs.ch/ci/overview), login with your CSCS credentials, and go to the newly registered project.

1. **Add FirecREST tokens**: Expand the `Admin config`, and follow the guide (click on the small black triangle next to Firecrest Consumer Key). Enter all fields for FirecREST, i.e.,
    - Consumer Key
    - Consumer Secret
    - default Slurm account for job submission (what you normally provide in the `--account`/`-A` flag to Slurm)
If you don't already know how to obtain FirecREST credentials, you can find more information on [How to create FirecREST clients on the Developer Portal](https://confluence.cscs.ch/spaces/KB/pages/868816917/How+to+create+FirecREST+clients+on+the+Developer+Portal)
!!! todo
    replace link to mkdocs firecrest docs

1. **(Optional) Private project**: If your Git repository is a private repository make sure to check the `Private repository` box and follow the instructions to add an SSH key to your Git repository.

1. **Add notification token**: On the setup page you will also find the field `Notification token`. The token is live tested, and you will see a green checkmark when the token is valid and can be used by the CI. It is mandatory to add a token so that your Git repository will be notified about the status of the build jobs. You cannot save anything as long as the notification token is invalid. (Click on the small triangle to get further instructions)

1. **Add webhook**: On the setup page you will find the `Setup webhook details` button. If you click on it you will see all the entries which have to be added to a new webhook in your Git repository. Follow the link given there to your repository, and add the webhook with the given entries.

1. **Default trusted users and default CI-enabled branches**: Provide the default list of trusted users and CI-enabled branches. The global configuration will apply to all pipelines that do not overwrite it explicitly.

1. **Pipeline default**: Your first pipeline has the name `default`. Click on `Pipeline default` to see the pipeline setup details. The name can be chosen freely but it cannot contain whitespaces (a short descriptive name). Update the entry point, trusted users and CI-enabled branches.

1. **Submit your changes**

1. **(Optional) Add other pipelines**: Add other pipelines with a different entry point if you need more pipelines.

1. **Add entry point yaml files to Git repository**: Commit the yaml entry point files to your repository. You should get notifications about the build status in your repository if everything is correct. See the [Hello World Tutorial](#ref-cicd-containerized-tutorial) for a simple yaml-file.

#### Clarifications and pitfalls to the above-mentioned steps
!!! info
    This section exemplifies on GitHub, but similar settings are available on GitLab and Bitbucket

The `notification token` setup step is crucial, because this is the number one entrypoint for receiving initial feedback on any errors.
You will not be able to save any changes on the CI setup page, as long as the notification token is invalid. The token is checked live, whether it can be used to do notifications.

Notification tokens on GitHub can be setup using `Classic token` or `Fine-grained token`. We discourage the use of fine-grained tokens. Fine-grained tokens are unsupported, and come with many pitfalls. They can work, but must be enabled at the organization level by an admin, and must be created in the correct organization.
You must choose the correct resource owner, i.e., the organization that the project belongs to. If the organization is not listed, then it has disabled fine-grained tokens at the organization level. It can only be enabled globally on an organization by an admin. As for the repository you can restrict it to only the repository that you want to notify with this token or all repositories. Even if you choose "All repositories", it is still restricted to the organization, and does not grant the access to any repository outside of the resource owner.

Another crucial setup step is the correct webhook setup. The repository provider (GitHub, GitLab, Bitbucket) gives you the ability to see what happened, when the webhook event was sent. If the webhook was not setup correctly, you will receive an HTTP error for the webhook events. The error message can be found in the webhook event response. As an example, here is how you would find it on GitHub: **Settings > Webhooks > `Edit` button of the webhook > `Recent Deliveries` tab > Choose a webhook event from the list > `Response` tab > Check for potential error message**.

A typical error is accepting to defaults of GitHub for new webhooks, where only `Push` events are being sent. When you forget to select `Send me everything`, then some events will not trigger pipelines. Double check your webhook settings.


[](){#ref-cicd-pipeline-triggers}
### Understanding when CI is triggered
[](){#ref-cicd-pipeline-triggers-push}
#### Push events
- Every pipeline can define its own list of CI-enabled branches
- If a pipeline does not define a list of CI-enabled branches, the global list will be used
- If you push changes to a branch every pipeline that has this branch in its list of CI-enabled branches will be triggered
- If the global list and all pipelines have an empty list of CI-enabled branches, then CI will never be triggered on push events

[](){#ref-cicd-pipeline-triggers-pr}
#### Pull requests (Merge requests)
- For simplicity we use PR to mean Pull Request, although some providers call it a Merge request. It is the same thing.
- Every pipeline can define its own list of trusted users.
- If a pipeline does not define a list of trusted users, the global list will be used.
- If a PR is opened/edited and targets a CI-enabled branch, and the source branch is not from a fork, then all pipelines will be started that have the target branch in its list of CI-enabled branches.
- If a PR is opened/edited and targets a CI-enabled branch, but the source branch is from a fork, then a pipeline will be automatically started if and only if the fork is from a user in the pipeline's trusted user list and the target branch is in the pipeline's CI-enabled branches.

[](){#ref-cicd-pipeline-triggers-comment}
#### `cscs-ci run` comment
- You have an open PR
- You want to trigger a specific pipeline
- Write a comment inside the PR with the text
  ```
  cscs-ci run PIPELINE_NAME_1,PIPELINE_NAME_2
  ```
- Special case: You have only one pipeline, then you can skip the pipeline names and write only the comment `cscs-ci run`
- The pipeline will only be triggered, if the commenting user is in the pipeline's trusted users list.
- Only the first line of the comment will be evaluated, i.e. you can add context from line 2 onwards.
- The target branch is ignored, i.e. you can test a pipeline even if the target branch is not in the pipeline's CI-enabled branches.
- Advanced `cscs-ci` run command is possible to inject variables into the pipeline (exposed as environment variables)
    - Triggering a pipeline with additional variables
      ```
      cscs-ci run PIPELINE_NAME;MY_VARIABLE=some_value;ANOTHER_VAR=other_value
      ```
      This will trigger the pipeline PIPELINE_NAME, and in your jobs there will be the environment variables MY_VARIABLE and ANOTHER_VAR available.
    - Disallowed characters for PIPELINE_NAME, variable name and variable value are the characters `,;=` (comma, semicolon, equal), because they serve as separators of the different components.

[](){#ref-cicd-pipeline-triggers-api}
#### API call triggering
- It is possible to trigger a pipeline via an API call
- Create a file named `data.yaml`, with the content
```yaml
ref: main
pipeline: pipeline_name
variables:
  MY_VARIABLE: some_value
  ANOTHER_VAR: other_value
```
Send a POST request to the middleware
```bash
curl -X POST -u 'repository_id:webhook_secret' --data-binary @data.yaml https://cicd-ext-mw.cscs.ch/ci/pipeline/trigger
```
- replace repository_id and webhook_secret with your repository id and the webhook secret.

### Understanding the underlying workflow
Typical users do not need to know the underlying workflow behind the scenes, so you can stop reading here. However, it might put the above-mentioned steps into perspective. It also can give you background for inquiring if and when something in the procedure does not go as expected.

#### Workflow (exemplified on icon-exclaim)
1. (Prerequisite) icon-exclaim will have a webhook set up
1. You make some change in the icon-exclaim repository
1. GitHub sends a webhook event to `cicd-ext-mw.cscs.ch`  (CI middleware)
1. CI middleware fetches your repository from GitHub and pushes a "mirror" to GitLab
1. GitLab sees a change in the repository and starts a pipeline (i.e. it uses the CI yaml as entry point)
1. If the repository uses git submodules, `GIT_SUBMODULE_STRATEGY: recursive` has to be specified (see [GitLab documentation](https://docs.gitlab.com/ee/ci/git_submodules.html#use-git-submodules-in-cicd-jobs))
1. The `container-builder`, which has as input a Dockerfile (specified in the variable `DOCKERFILE`), will take this Dockerfile and execute something similar to `docker build -f $DOCKERFILE .`, where the build context is the whole (recursively) cloned repository

### CI variables

Many variables exist during a pipeline run, they are documented at [Gitlab's predefined variables](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html). Additionally to CI variables available through Gitlab, there are a few CSCS specific pipeline variables:

| Variable                       | Value             | Additional information                                                               |
|--------------------------------|-------------------|--------------------------------------------------------------------------------------|
| `CSCS_REGISTRY`                | jfrog.svc.cscs.ch | CSCS internal registry, preferred registry to store your container images            |
| `CSCS_REGISTRY_PATH`           | jfrog.svc.cscs.ch/docker-ci-ext/<repositorypid> | The prefix path in the CSCS internal container image registry, to which your pipeline has write access. Within this prefix, you can choose any directory structure. Images that are pushed to a path matching **/public/** , can be pulled by anybody within CSCS network |
| `CSCS_CI_MW_URL`               | https://cicd-ext-mw.cscs.ch/ci | The URL of the middleware, the orchestrator software.                   |
| `CSCS_CI_DEFAULT_SLURM_ACCOUNT` | d123             | The project to which accounting will go to. It is set up on the CI setup page in the Admin section. It can be overwritten via SLURM_ACCOUNT for individual jobs. |
| `CSCS_CI_ORIG_CLONE_URL`       | https://github.com/my-org/my-project (public) git@github.com:my-or/my-project (private) | Clone URL for git. This is needed for some implementation details of the gitlab-runner custom executor. This is the clone URL of the registered project, i.e. this is not the clone URL of the mirror project. |

### Example projects
Here are a couple of projects which use this CI setup. Please have a look there for more advanced usage:

- [dcomex-framework](https://github.com/DComEX/dcomex-framework): entry point is `ci/prototype.yml`
- [utopia](https://bitbucket.org/zulianp/utopia/src/development/): two pipelines, with entry points `ci/cscs/mc/gitlab-daint.yml` and `ci/cscs/gpu/gitlab-daint.yml`
- [mars](https://bitbucket.org/zulianp/mars/src/development/): two pipelines, with entry points `ci/gitlab/cscs/gpu/gitlab-daint.yml` and `ci/gitlab/cscs/mc/gitlab-daint.yml`
- [sparse_accumulation](https://github.com/lab-cosmo/sparse_accumulation): entry point is `ci/pipeline.yml`
- [gt4py](https://github.com/GridTools/gt4py): entry point is `ci/cscs-ci.yml`
- [SIRIUS](https://github.com/electronic-structure/SIRIUS): entry point is `ci/cscs-daint.yml`
- [sphericart](https://github.com/lab-cosmo/sphericart): entry point is `ci/pipeline.yml`

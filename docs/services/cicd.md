[](){#ref-cicd}
# Continuous Integration / Continuous Deployment (CI/CD)
!!! info "External references"
    It is helpful to consult the [GitLab CI yaml](https://docs.gitlab.com/ee/ci/yaml/) reference documentation and the [predefined pipeline variables reference](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html).

!!! Tip "Webinar video"
    Watch the latest [webinar video](https://www.youtube.com/watch?v=6cnm32nFw0A) for an overview of CI/CD and its features

[](){#ref-cicd-containerized-intro}
## Introduction containerized CI/CD

Containerized CI/CD allows you to build containers and run them at scale on CSCS systems.
The basic idea is that you provide a [Dockerfile](https://docs.docker.com/reference/dockerfile/) with build instructions and run the newly created container.
Most of the boilerplate work is being taken care by the CI implementation such that you can concentrate on providing build instructions and testing.
The important information is provided to you from the CI side for the configuration of your repository.

We support any git provider that supports [webhooks](https://en.wikipedia.org/wiki/Webhook).
This includes GitHub, GitLab and Bitbucket.
A typical pipeline consists of at least one build job and one test job.
The build job makes sure that a new container with your most recent code changes is built.
The test step uses the new container as part of an MPI job; e.g., it can run your tests on multiple nodes with GPU support.

Building your software inside a container requires a Dockerfile and a name for the container in the registry where the container will be stored.
Testing your software then requires the commands that must be executed to run the tests.
No explicit container spawning is required (and also not possible).
Your test jobs need to specify the number of nodes and tasks required for the test and the test commands.

[](){#ref-cicd-containerized-tutorial}
### Tutorial Hello World
!!! example "Hello World"
    See the [hello world example](https://github.com/finkandreas/containerised_ci_helloworld) on GitHub for a project that demonstrates a containerized end to end CI/CD workflow.

In this example we are using the [containerized hello world repository](https://github.com/finkandreas/containerised_ci_helloworld).
This is a sample Hello World CMake project.
The application only echos `Hello from $HOSTNAME`, but this should demonstrate the idea of how to run a program on multiple nodes.
The pipeline instructions are inside the file `ci/cscs.yml`.
Let's walk through the pipeline bit by bit.
```yaml
include:
  - remote: 'https://gitlab.com/cscs-ci/recipes/-/raw/master/templates/v2/.ci-ext.yml'
```

This block includes a yaml file which contains definitions with default values to build and run containers.
Have a look inside this file to see available building blocks.
```yaml
stages:
  - build
  - test
```
Here we define two different stages, named `build` and `test`.
The names can be chosen freely.
```yaml
variables:
  PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/helloworld:$CI_COMMIT_SHORT_SHA
```

This block defines variables that will apply to all jobs.
See [CI variables](https://confluence.cscs.ch/spaces/KB/pages/868812112/Continuous+Integration+Continuous+Deployment#ContinuousIntegration/ContinuousDeployment-CIvariables).

```yaml
build_job:
  stage: build
  extends: .container-builder-cscs-zen2
  variables:
    DOCKERFILE: ci/docker/Dockerfile.build
```

This adds a job named `build_job` to the stage `build`.
This runner expects a Dockerfile as input, which is specified in the variable `DOCKERFILE`.
The resulting container name is specified with the variable `PERSIST_IMAGE_NAME`, which has been defined already above, therefore it does not need to be explicitly mentioned in the `variables` block, again.
Further refinements can be found at the [reference documentation](#container-builder)

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

This block defines a test job.
The job will be executed by the [.container-runner-eiger-zen2](#container-runner).

This runner will pull the image on the cluster Eiger and run the commands as specified in the `script` tag.
In this example we are requesting 2 nodes with 1 task on each node, i.e. 2 tasks total.
All [Slurm environment variables](https://slurm.schedmd.com/srun.html#SECTION_INPUT-ENVIRONMENT-VARIABLES) are supported.
The commands will be running inside the container specified by the `image` tag.

[](){#ref-cicd-cscs-impl}
## CI at CSCS
### Enable CI for your project

While the procedure to enable CSCS CI for your repository consists of only a few steps outlined below, many of them require features in GitHub, GitLab or Bitbucket.
The links in the text contain additional steps which may be needed.
Some of those documents are non-trivial, especially if you do not have considerable background in the repository features.
Plan sufficient time for the setup and contact a GitHub/GitLab/Bitbucket professional, if needed.

1. **Register your project with CSCS**: The first step to use containerized CI/CD is to register your Git repository with CSCS.
Please open a [Service Desk ticket](https://support.cscs.ch/) and include which repository should be registered, and who should own the registration (by default it would be the requester).
Once your project has been registered you will be provided with a webhook-secret.

1. **Set up CI**: Head to the [CI overview page](https://cicd-ext-mw.cscs.ch/ci/overview), login with your CSCS credentials, and go to the newly registered project.

1. **Add FirecREST tokens**: Expand the `Admin config`, and follow the guide (click on the small black triangle next to Firecrest Consumer Key).
Enter all fields for FirecREST, i.e.,
    * Consumer Key
    * Consumer Secret
    * default Slurm account for job submission (what you normally provide in the `--account`/`-A` flag to Slurm)

    !!! tip "FirecREST credentials"
        If you don't already know how to obtain FirecREST credentials, you can find more information on [CSCS Developer Portal][ref-devportal].
        You must subscribe your application to the FirecREST API of the platform to which you want to submit jobs, e.g.
        `FirecREST-HPC` for the HPC platform.
        If `v2` is available for your platform, then subscribe to `v2` of the API, otherwise `v1` will work too.
        It is not mandatory to subscribe to the `ciext-container-builder` API to use pure CI workflows (this API is only used for building manually container images).

1. **(Optional) Private project**: If your Git repository is a private repository make sure to check the `Private repository` box and follow the instructions to add an SSH key to your Git repository.

1. **Add notification token**: On the setup page you will also find the field `Notification token`.
The token is live tested, and you will see a green checkmark when the token is valid and can be used by the CI.
It is mandatory to add a token so that your Git repository will be notified about the status of the build jobs.
You cannot save anything as long as the notification token is invalid.
(Click on the small triangle to get further instructions)

1. **Add webhook**: On the CI setup page you will find the `Setup webhook details` button (go to the [CI overview](https://cicd-ext-mw.cscs.ch), then the project, and there is a blue button with the text `Setup webhook details`).
If you click on it you will see all the entries which have to be added to a new webhook in your Git repository.
Follow the link given there to your repository, and add the webhook with the given entries.

1. **Default trusted users and default CI-enabled branches**: Provide the default list of trusted users and CI-enabled branches.
The global configuration will apply to all pipelines that do not overwrite it explicitly.

1. **Pipeline default**: Your first pipeline has the name `default`.
Click on `Pipeline default` to see the pipeline setup details.
The name can be chosen freely but it cannot contain whitespace (a short descriptive name).
Update the entry point, trusted users and CI-enabled branches.

1. **Submit your changes**

1. **(Optional) Add other pipelines**: Add other pipelines with a different entry point if you need more pipelines.

1. **Add entry point yaml files to Git repository**: Commit the yaml entry point files to your repository.
You should get notifications about the build status in your repository if everything is correct.
See the [Hello World Tutorial](#ref-cicd-containerized-tutorial) for a simple yaml-file.

#### Clarifications and pitfalls to the above-mentioned steps
!!! info
    This section exemplifies on GitHub, but similar settings are available on GitLab and Bitbucket

The `notification token` setup step is crucial, because this is the number one entrypoint for receiving initial feedback on any errors.
You will not be able to save any changes on the CI setup page, as long as the notification token is invalid.
The token is checked live, whether it can be used to do notifications.

Notification tokens on GitHub can be setup using `Classic token` or `Fine-grained token`.
We discourage the use of fine-grained tokens.
Fine-grained tokens are unsupported, and come with many pitfalls.
They can work, but must be enabled at the organization level by an admin, and must be created in the correct organization.
You must choose the correct resource owner, i.e., the organization that the project belongs to.
If the organization is not listed, then it has disabled fine-grained tokens at the organization level.
It can only be enabled globally on an organization by an admin.
As for the repository you can restrict it to only the repository that you want to notify with this token or all repositories.
Even if you choose "All repositories", it is still restricted to the organization, and does not grant the access to any repository outside of the resource owner.

Another crucial setup step is the correct webhook setup.
The repository provider (GitHub, GitLab, Bitbucket) gives you the ability to see what happened, when the webhook event was sent.
If the webhook was not setup correctly, you will receive an HTTP error for the webhook events.
The error message can be found in the webhook event response.
As an example, here is how you would find it on GitHub: **Settings > Webhooks > `Edit` button of the webhook > `Recent Deliveries` tab > Choose a webhook event from the list > `Response` tab > Check for potential error message**.

A typical error is accepting to defaults of GitHub for new webhooks, where only `Push` events are being sent.
When you forget to select `Send me everything`, then some events will not trigger pipelines.
Double check your webhook settings.


[](){#ref-cicd-pipeline-triggers}
## Understanding when CI is triggered
[](){#ref-cicd-pipeline-triggers-push}
#### Push events
- Every pipeline can define its own list of CI-enabled branches
- If a pipeline does not define a list of CI-enabled branches, the global list will be used
- If you push changes to a branch every pipeline that has this branch in its list of CI-enabled branches will be triggered
- If the global list and all pipelines have an empty list of CI-enabled branches, then CI will never be triggered on push events

[](){#ref-cicd-pipeline-triggers-pr}
#### Pull requests (Merge requests)
- For simplicity we use PR to mean Pull Request, although some providers call it a Merge request.
It is the same thing.
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
Typical users do not need to know the underlying workflow behind the scenes, so you can stop reading here.
However, it might put the above-mentioned steps into perspective.
It also can give you background for inquiring if and when something in the procedure does not go as expected.

#### Workflow (exemplified on a GitHub repository)
1. (Prerequisite) Repository in GitHub will have a webhook set up, with the setup details from the CI setup page
1. You push some change to the GitHub repository
1. GitHub sends a (push) webhook event to `cicd-ext-mw.cscs.ch` (CI middleware)
1. CI middleware fetches your repository from GitHub and pushes a "mirror" to GitLab
1. GitLab receives the change in the "mirror" repository and a pipeline is triggered (i.e. it uses the CI yaml as entry point)
1. If the repository uses git submodules, `GIT_SUBMODULE_STRATEGY: recursive` has to be specified (see [GitLab documentation](https://docs.gitlab.com/ee/ci/git_submodules.html#use-git-submodules-in-cicd-jobs))
1. The [container-builder](#container-builder), which has as input a Dockerfile (specified in the variable `DOCKERFILE`), will take this Dockerfile and execute something similar to `docker build -f $DOCKERFILE .`, where the [build context](#build-context) is the whole (recursively) cloned repository

## Containerized CI - best practices
###  Multi-architecture images

With the introduction of Grace-Hopper nodes, we have now `aarch64` and `x86_64` machines.
This implies that the container images should be built for the correct architecture.
This can be achieved by the following example
```yaml
include:
  - remote: 'https://gitlab.com/cscs-ci/recipes/-/raw/master/templates/v2/.ci-ext.yml'

stages:
  - build
  - make_multiarch
  - run

.build:
  stage: build
  variables:
    DOCKERFILE: path/to/my_dockerfile
    PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/${ARCH}/my_image_name:${CI_COMMIT_SHORT_SHA}
build aarch64:
  extends: [.container-builder-cscs-gh200, .build]
build x86_64:
  extends: [.container-builder-cscs-zen2, .build]

make multiarch:
  extends: .make-multiarch-image
  stage: make_multiarch
  variables:
    PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/my_multiarch_image:${CI_COMMIT_SHORT_SHA}
    PERSIST_IMAGE_NAME_AARCH64: $CSCS_REGISTRY_PATH/aarch64/my_image_name:${CI_COMMIT_SHORT_SHA}
    PERSIST_IMAGE_NAME_X86_64: $CSCS_REGISTRY_PATH/x86_64/my_image_name:${CI_COMMIT_SHORT_SHA}

.run:
  stage: run
  image: $CSCS_REGISTRY_PATH/my_multiarch_image:${CI_COMMIT_SHORT_SHA}
  script:
    - uname -a
run aarch64:
  extends: [.container-runner-daint-gh200, .run]
run x86_64:
  extends: [.container-runner-eiger-mc, .run]
```

We first create two container images which have different names.
Then we combine these two names to a single name, with both architectures.
Finally in the run step we use the multi-architecture image, where the container runtime will pull the correct architecture.

It is *not* mandatory to combine the container images to a multi-architecture image, i.e. a CI setup which consistently uses the correct architecture specific paths can work.
A multi-architecture image is convenient when you plan to distribute it to other users.

### Dependency management
#### Problem

A common observation is that your software has many dependencies that are more or less static, i.e. they can change but do so very rarely.
A common pattern one can observe to work around rebuilding base images unnecessarily is a multi-stage CI setup

1. Build (rarely but manually) a base container with all static dependencies and push it to a public container registry
1. Use the base container and build the software container
1. Test the newly created software container
1. Deploy the software container

This works fine but has the drawback that one has to do a manual step whenever the dependencies change, e.g. when one wants to upgrade to new versions of the dependencies.
Another drawback of this is that it allows to keep the recipe of the base container outside of the repository, which makes it harder to reproduce results, especially when colleagues want to reproduce a build.

#### Solution

A common solution to this problem is that you have a multi stage setup.
Your repository should have (at least) two Dockerfiles, let us call them `Dockerfile.base` and `Dockerfile`.

- `Dockerfile.base`: This dockerfile contains the recipe to build your base-container, it normally derives `FROM` a very basic container, e.g. `docker.io/ubuntu:24.04` or CSCS spack base containers.
Let us call the container image that is built using this recipe `BASE_IMG`.
- `Dockerfile`: This Dockerfile contains the recipe to build your software-container.
It must start with `FROM $BASE_IMG`.

!!! note
    Have a look at the [Spack based images](#spack-based-images) section, to manage software installed in base containers via Spack

The `.container-builder-cscs-*` blocks can be used to solve this problem.
The runner supports the variable `CSCS_REBUILD_POLICY`, which by default is set to `if-not-exists`.

This means that the runner will check the remote registry if the container image specified in `PERSIST_IMAGE_NAME` exists.
A new container image is built only if it does not exist yet.
Note: In case you have one build job, `PERSIST_IMAGE_NAME` can be specified in the `variables:` field of this build job or as a global variable, like in the Hello World example.
In case you have multiple build jobs and you specify the `PERSIST_IMAGE_NAME` variable per build job, you need to specify the exact name of the image to be used in the `image` field of the test job.

CI files would look in the simplest case like this:

=== "CI YAML"
    ```yaml title="ci/cscs.yml"
    include:
      - remote: 'https://gitlab.com/cscs-ci/recipes/-/raw/master/templates/v2/.ci-ext.yml'

    stages:
      - build_base
      - build
      - test

    build base:
      extends: .container-builder-cscs-zen2
      stage: build_base
      variables:
        DOCKERFILE: ci/docker/Dockerfile.base
        PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/base/my_base_container:1.0
        CSCS_REBUILD_POLICY: if-not-exists # default anyway, only here for verbosity

    build software:
      extends: .container-builder-cscs-zen2
      stage: build
      variables:
        DOCKERFILE: ci/docker/Dockerfile
        PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/software/my_software:$CI_COMMIT_SHORT_SHA
        DOCKER_BUILD_ARGS: '["BASE_IMG=$CSCS_REGISTRY_PATH/base/my_base_container:1.0"]'

    test software single node:
      extends: .container-runner-daint-gpu
      image: $CSCS_REGISTRY_PATH/software/my_software:$CI_COMMIT_SHORT_SHA
      script:
        - ./test_suite_1.sh
        - ./test_suite_2.sh
      variables:
        SLURM_JOB_NUM_NODES: 1

    test software multi:
      extends: .container-runner-daint-gpu
      image: $CSCS_REGISTRY_PATH/software/my_software:$CI_COMMIT_SHORT_SHA
      script:
        - ./test_suite_1.sh
        - ./test_suite_2.sh
      variables:
        SLURM_JOB_NUM_NODES: 4
    ```

=== "Dockerfile base image"
    ```Dockerfile title="ci/docker/Dockerfile.base"
    FROM docker.io/finkandreas/spack:0.19.2-cuda11.7.1-ubuntu22.04

    ARG NUM_PROCS

    RUN spack-install-helper daint-gpu \
        petsc \
        trilinos
    ```

=== "Dockerfile application"
    ```Dockerfile title="ci/docker/Dockerfile"
    ARG BASE_IMG
    FROM $BASE_IMG

    ARG NUM_PROCS

    RUN mkdir /build && cd /build && cmake /sourcecode && make -j$NUM_PROCS
    ```

A setup like this would run the very first time and build the container image `$CSCS_REGISTRY_PATH/base/my_base_container:1.0`, followed by the job that builds the container image `$CSCS_REGISTRY_PATH/software/my_software:1.0`.
The next time CI is triggered the `.container-builder-cscs-zen2` would check the remote repository if the target tag (`PERSIST_IMAGE_NAME`) exists, and only build a new container image if it does not exist yet.
Since the tag for the job `build base` is static, i.e. it is the same for every run of CI, it would build the first time it is running, but not for subsequent runs.
In contrast to this is the job `build software`: Here the tag changes with every CI run, since the variable `CI_COMMIT_SHORT_SHA` is different for every run.

##### Manual dependency update
At some point you realise that you have to update some of the dependencies.
You can use a manual update process to update your base-container, where you ensure that you update all necessary image tags.
In our example, this means updating in `ci/cscs.yml` all occurences of `$CSCS_REGISTRY_PATH/base/my_base_container:1.0` to `$CSCS_REGISTRY_PATH/base/my_base_container:2.0` (or any other versioning scheme - for all that matters is that the full name must change).
Of course something in `Dockerfile.base` should change too, otherwise you are building the same artifact, with just a different name.

##### Dynamic dependency update
While manually updating image tags works fine, it has the drawback that it is error-prone.
Take for example the situation where you update the tag in `build base`, but forget to change it in `build software`.
Your pipeline would still run fine, because the dependency of `build software` exists.
Since there is no explicit error for the inconsistencies it is hard to find the error.

Therefore, there is also the possibility to have a dynamic way of naming your container images.
The idea is the same, i.e. we build first a base-container, and use this base-container to build our software-container.

The `build base` and `build software` jobs would look similar to this:
```yaml
build base:
  extends: .container-builder-cscs-zen2
  stage: build_base
  before_script:
    - DOCKER_TAG=`cat ci/docker/Dockerfile.base | sha256sum - | head -c 16`
    - export PERSIST_IMAGE_NAME=$CSCS_REGISTRY_PATH/base/my_base_image:$DOCKER_TAG
    - echo "BASE_IMAGE=$PERSIST_IMAGE_NAME" > build.env
  artifacts:
    reports:
      dotenv: build.env
  variables:
    DOCKERFILE: ci/docker/Dockerfile.base # overwrite with the real path of the Dockerfile

build software:
  extends: .container-builder-cscs-zen2
  stage: build
  variables:
    DOCKERFILE: ci/docker/Dockerfile
    PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/software/my_software:$CI_COMMIT_SHORT_SHA
    DOCKER_BUILD_ARGS: '["BASE_IMG=$BASE_IMAGE"]'
```

Let us walk through the changes in the `build base` job:

- `DOCKER_TAG` is computed at runtime by the sha256sum of the `Dockerfile.base`, i.e. it would change, when you change the content of `Dockerfile.base` (we keep only the first 16 characters, this is random enough to guarantee that we have a unique name).
- We export `PERSIST_IMAGE_NAME` to the dynamic name with `DOCKER_TAG`.
- We write the dynamic name to the file `build.env`
- We tell the CI system to keep the `build.env` as an artifact (see [here](https://docs.gitlab.com/ee/ci/yaml/artifacts_reports.html#artifactsreportsdotenv) the documentation of this)

Note: The dotenv artifacts of a specific job for public projects is available at `https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/<project_id>/<pipeline_id>/-/jobs/<job_id>/artifacts/download?file_type=dotenv`.

Now let us look at the changes in the `build software` job:

- `DOCKER_BUILD_ARGS` is now using `$BASE_IMAGE`.
This variable exists, because we transferred the information via a `dotenv` artifact from `build base` to this job.

In this example the names `BASE_IMG` and `BASE_IMAGE` are chosen to be different, for clarification where the different variables are set and used.
Feel free to use the same names for consistent naming.
The default behaviour is to import all artifacts from all previous jobs.
If you want only specific artifacts in your job, you should have a look at [dependencies](https://docs.gitlab.com/ee/ci/yaml/#dependencies).

There is also a building block in the templates, name `.dynamic-image-name`, which you can use to get rid for most of the boilerplate.
It is important to note that this building block will export the dynamic name under the hardcoded name `BASE_IMAGE` in the `dotenv` file.
The jobs would look something like this:
```yaml
build base:
  extends: [.container-builder-cscs-zen2, .dynamic-image-name]
  stage: build_base
  variables:
    DOCKERFILE: ci/docker/Dockerfile.base
    PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/base/my_base_image
    WATCH_FILECHANGES: 'ci/docker/Dockerfile.base'

build software:
  extends: .container-builder-cscs-zen2
  stage: build
  variables:
    DOCKERFILE: ci/docker/Dockerfile
    PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/software/my_software:$CI_COMMIT_SHORT_SHA
    DOCKER_BUILD_ARGS: '["BASE_IMG=$BASE_IMAGE"]'
```

`build base` is using additionally the building block `.dynamic-image-name`, while `build software` is unchanged.
Have a look at the definition of the block `.dynamic-image-name` in the file [.ci-ext.yml](https://gitlab.com/cscs-ci/recipes/-/blob/master/templates/v2/.ci-ext.yml) for further notes.

### Image cleanup
Images pushed to [CSCS_REGISTRY_PATH](#ci-variables) are cleaned daily according to the following rules:

* No deletion if total storage usage < 300GB
* No deletion of images newer than 30 days
* First cleanup excluding folders `base`, `baseimg`, `baseimage`, `deploy`, `deployment`
    * Delete images that have been unused for more than 30 days (usage means that the image has been downloaded)
* Second cleanup if storage usage is still > 300GB
    * Delete images in the above mentioned excluded folders if the image has been unused for more than 365 days

### Third party registries
While it is recommended to work with the CSCS provided registry at [CSCS_REGISTRY_PATH](#ci-variables), due to fastest network connection, it is also possible to work with third party registries like dockerhub.com or quay.io.
When you work with third party registries, then you have to provide login credentials for the CI jobs.

There are two possible ways to push images to third party registries (it is assumed that you have stored the variable `DOCKERHUB_ACCESS_TOKEN` at the CI setup page):

The first approach will push both, CSCS registry and third party registry `dockerhub.com`
```yaml
my_job:
  extends: .container-builder-cscs-zen2
  stage: my_stage
  variables:
    DOCKERFILE: path/to/Dockerfile
    PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/my_image:${CI_COMMIT_SHORT_SHA}
    SECONDARY_IMAGE_NAME: docker.io/your_dockerhub_username/my_image:${CI_COMMIT_SHORT_SHA}
    SECONDARY_IMAGE_USERNAME: your_dockerhub_username
    SECONDARY_IMAGE_PASSWORD: $DOCKERHUB_ACCESS_TOKEN
```

The second approach will only push to the third party registry `dockerhub.com`:
```yaml
my_job:
  extends: .container-builder-cscs-zen2
  stage: my_stage
  variables:
    DOCKERFILE: path/to/Dockerfile
    PERSIST_IMAGE_NAME: docker.io/your_dockerhub_username/my_image:${CI_COMMIT_SHORT_SHA}
    CUSTOM_REGISTRY_USERNAME: your_dockerhub_username
    CUSTOM_REGISTRY_PASSWORD: $DOCKERHUB_ACCESS_TOKEN
```

#### Clone image from CSCS registry
CI has access to the CSCS registry while a job is running.
However you cannot download images from the CSCS registry directly, because you do not have valid credentials to access the images.
If the image has not been pushed to a third party registry like hinted above, and one still wants to inspect the image, one can instruct manually CI to copy the image to a third party registry.
Create a yaml file with the content
```yaml title="copy_image.yaml"
username: <repository-id>
password: <webhook-secret>
from_image: $CSCS_REGISTRY_PATH/my_cool_image:1.0
to_image: docker.io/your_dockerhub_username/my_cool_image_cloned:latest
registry_credentials:
  username: your_registry_username
  password: your_registry_password
```

* `from_image`: The image that you want to copy out of CSCS registry.
It must begin with `$CSCS_REGISTRY_PATH`
* `to_image`: The path where the image should be copied
* `registry_credentials`: The credentials which allow to login to the registry specified in `to_image`.
Many registries allow you to create access tokens, which should be preferred to your password.

To trigger the copy POST a request to https://cicd-ext-mw.cscs.ch/ci/image/clone (e.g. with `curl`)
```console
$ curl --data-binary @copy_image.yaml https://cicd-ext-mw.cscs.ch/ci/image/clone
```
The call might take some time, depending on image size.

### Spack based images
#### Introduction
[Spack](https://spack.io/) is a package management tool designed to support multiple versions and configurations of software on a wide variety of platforms and environments.
It was designed for administrators in large supercomputing centres, where many users and application teams share common installations of software on clusters.
It can also be used by users to install software environments exactly for their needs.

We provide Docker images with preinstalled Spack, its configuration for the hardware available at CSCS, and helper scripts that simplify using Spack in a Dockerfile.

#### Install helper script
In the image, we provide a `spack-install-helper` script that helps build a list of packages for a desired architecture.
The script can be used as follows:
```console
$ spack-install-helper --target <target-arch> [--add-repo <repo>] [--only-dependencies <spec>] <spec> [<spec>...]
```

* `--target` (mandatory) specifying the target architecture.
  Possible values are `alps-zen2`, `alps-a100`, `alps-gh200`, `alps-mi200`, `alps-mi300a`
* `--add-repo` (optional) adds an additional custom Spack repository`
* `--only-dependencies` (optional) install only dependencies of the spec.
  It is useful if you want to install a package manually, e.g. for debugging purposes, or together with `--add-repo` for developing spack's `package.py`
* `spec` are any specs that can be passed to the `spack install` command

#### Building Docker images
It is good practice to keep Docker images as small as possible, with only the software needed and nothing more.
To support this philosophy, we create our image in a [multistage build](https://docs.docker.com/build/building/multi-stage/).
In the first stage, Spack is used to install the software stack we need.
In the second stage, the software installed in the first stage is copied (without build dependencies and Spack).
After that, we can add to the image anything we need.
We can, for example, build our software, prepare tests, ...

##### Docker images naming scheme
We provide two different images that can be used in the first and second stages of the multistage build.
The image `spack-build` is used in the first stage and has Spack installed.
The image `spack-runtime`  is the same, but without spack, only with scripts that make the software installed with spack available.

Both images are available with different versions of installed software, this is encoded in the docker tag.
The tag of the `spack-build` image has the following scheme `spack<version>-<os><version>-<arch>[version]`, e.g. `spack-build:spack0.21.0-ubuntu22.04-cuda12.4.1` is an image based on `ubuntu-22.04` with `cuda-12.4.1` and `spack-0.21.0`.
The tag of the `spack-runtime` image has the same scheme, but without `spack<version>-`, as spack is not installed in this image, e.g. `spack-runtime:ubuntu22.04-cuda12.4.1`.
It is strongly recommended to always use both images with the same OS and arch for the first and the second stage.

We provide images based on `Ubuntu 22.04 LTS`  for three different architectures:

* CPU (x86_64)
* CUDA (`x86_64+A100` and `arm64+GH200`)
* ROCm (`x86_64+MI250`)

##### Docker registry
We provide these images in two docker registries:

* JFrog hosted at CSCS (jfrog.svc.cscs.ch)
    * `FROM $CSCS_REGISTRY/docker-ci-ext/base-containers/public/spack-build:<tag>`
    * `FROM $CSCS_REGISTRY/docker-ci-ext/base-containers/public/spack-runtime:<tag>`
    * Available only on the CSCS network
    * Recommended for CI/CD workflows at CSCS
* [GitHub Container Registry](https://github.com/orgs/eth-cscs/packages)
    * `FROM ghcr.io/eth-cscs/docker-ci-ext/base-containers/spack-build:<tag>`
    * `FROM ghcr.io/eth-cscs/docker-ci-ext/base-containers/spack-runtime:<tag>`
    * Available from everywhere
    * Recommended for manual workflows

##### Example Dockerfile
Use this Dockerfile template.
Adjust the `spack-install-helper` command as needed, especially the target architecture and list of packages.
Add any commands after `fix_spack_install` or drop all of them if you need only the software installed by spack.

```Dockerfile title="Dockerfile"
# use spack to install the software stack
FROM $CSCS_REGISTRY/docker-ci-ext/base-containers/public/spack-build:spack0.21.0-ubuntu22.04-cuda12.4.1 as builder

# number or processes used for building the spack software stack
ARG NUM_PROCS

RUN spack-install-helper --target alps-gh200 \
    "git" "cmake" "valgrind" "python@3.11" "vim +python +perl +lua"

# end of builder container, now we are ready to copy necessary files

# copy only relevant parts to the final container
FROM $CSCS_REGISTRY/docker-ci-ext/base-containers/public/spack-runtime:ubuntu22.04-cuda12.4.1

# it is important to keep the paths, otherwise your installation is broken
# all these paths are created with the above `spack-install-helper` invocation
COPY --from=builder /opt/spack-environment /opt/spack-environment
COPY --from=builder /opt/software /opt/software
COPY --from=builder /opt/._view /opt/._view
COPY --from=builder /etc/profile.d/z10_spack_environment.sh /etc/profile.d/z10_spack_environment.sh

# Some boilerplate to get all paths correctly - fix_spack_install is part of the base image
# and makes sure that all important things are being correctly setup
RUN fix_spack_install

# Finally install software that is needed, e.g. compilers
# It is also possible to build compilers via spack and let all dependencies be handled by spack
RUN apt-get -yqq update && apt-get -yqq upgrade \
 && apt-get -yqq install build-essential gfortran \
 && rm -rf /var/lib/apt/lists/*
```

### Manual container build
It is possible to use CI's mechanisms to build a container image manually providing a `Dockerfile`, or even a full build context with a `Dockerfile`.
For reproducibility one should aim to use a code versioning system like `git`, but for debugging a manual API call might not pollute the code history so much.

To use the API endpoint you need to create API credentials (one time setup) using the developer portal.
Please follow [this guide][ref-devportal].
To be able to use manual API container builds you must subscribe your application to the `ciext-container-builder` API.

After your application is created the tab `APIs` will appear at the top of the developer portal, which allows you to inspect the API for `ciext-container-builder`.
The section `Documents` is very helpful as it contains the endpoint documentation for `/container/build POST`.
Refer to the documentation there for all parameters.

The endpoint can work in two different modes:

1. Send just a Dockerfile
1. Send a full build context as a tar.gz-archive and tell the API where the Dockerfile inside the tarball is.

!!! info "Create access token"
    To send any request to the API endpoint, we first need to create an access token, which can be done with the Consumer Key and Consumer secret.
    ```console
    $ ACCESS_TOKEN="$(curl  -u <your-consumer-key>:<your-consumer-secret> --silent -X POST https://auth.cscs.ch/auth/realms/firecrest-clients/protocol/openid-connect/token -d "grant_type=client_credentials" | jq -r '.access_token')"
    ```
    The token is stored in the variable ACCESS_TOKEN.
    This token has only a short validity, so you need to create a fresh access token, whenever the current one becomes invalid (about 5 minutes validity).

!!! info "Build from Dockerfile"
    ```console
    $ curl -H "Authorization: Bearer $ACCESS_TOKEN" --data-binary @path/to/Dockerfile "https://api.cscs.ch/ciext/v1/container/build?arch=x86_64"
    ```
    It is mandatory to specify for which architecture you want to build the container.
    Valid choices are:

    * `x86_64` - Correct for all nodes that are not Grace-Hopper
    * `aarch64` - ARM architecture - Correct for Grace-Hopper

    The API call above sends the Dockerfile to the server, and the server will reply with a link, where you can see the build log.
    The final container image will be pushed to JFrog, a CSCS internal container registry.
    Once the container image is built, it can be pulled from any CSCS machine.

    If you want to push the image to your Docker Hub account, you need to create a Docker Hub access token with write permissions, and then use the API call (similarly for other OCI registry providers)
    ```
    $ curl -H "Authorization: Bearer $ACCESS_TOKEN" -H "X-Registry-Username <your-dockerhub-username>" -H "X-Registry-Password: <your-dockerhub-token>" --data-binary @path/to/Dockerfile "https://api.cscs.ch/ciext/v1/container/build?arch=x86_64&image=docker.io/<your-dockerhub-username>/my_image_name:latest"
    ```

!!! info "Build with code"
    If you are using `COPY` or `ADD` statements in your Dockerfile, you will need to send the build context too.
    To send a full archive the easiest is via the API call
    ```console
    $ tar -C path/to/build-context -czf - . | curl -H "Authorization: Bearer $ACCESS_TOKEN" --data-binary @- "https://api.cscs.ch/ciext/v1/container/build?arch=x86_64&dockerfile=relative/path/to/Dockerfile"
    ```
    This is similar to
    ```console
    $ docker build -f relative/path/to/Dockerfile .
    ```

## CSCS CI specifics

### Restart CI jobs
This section applies for public projects.
Public projects get as notification a link to the pipeline in the Gitlab mirror repository.
Since a user does not have any special permissions to the mirror repository, it is not possible to restart jobs through the Gitlab UI.
However, it is possible to see an alternative view of your pipeline result in a CSCS-provided pipeline overview.
Private projects will always get as notification a link to the CSCS pipeline overview, since the mirror repository is private and the pipeline results are not visible publicly.

To view the CSCS pipeline overview for a public project and restart / cancel jobs, follow these steps:

* Copy the web link of the CSCS CI status of your project and remove the from the link the `type=gitlab`.
* Alternativily, assemble the link yourself, it has the form `https://cicd-ext-mw.cscs.ch/ci/pipeline/results/<repository_id>/<project_id>/<pipeline_nb>` (the IDs can be found on the Gitlab page of your mirror project).
* Click on `Login to restart jobs` at the bottom right and login with your CSCS credentials
* Click `Cancel running` or `Restart jobs` or cancel individual jobs (button next to job's name)
* Everybody that has at least *Manager* access can restart / cancel jobs (access level is managed on the CI setup page in the Admin section)

### Common pitfalls
The CI service uses GitLab to run the pipelines, with the familiar GitLab YAML configuration.
However, some features described in the official documentation will not work as expected.

Below are known differences:

* `CI_PIPELINE_SOURCE` always has the value `trigger`, i.e. it is never `push` or `merge_request`, or any other value mentioned in the GitLab documentation.
* `rules: changes` will not work, as you never run a branch or a merge request pipeline
* `only / except` and `rules` can restrict jobs to specific branches, but remember that a pipeline is only triggered if it matches the rules defined on your repository's setup page.
* Trigger jobs for child pipelines must use `trigger:forward:pipeline_variables: true`, i.e.
  ```yaml
  my trigger job:
    trigger:
      include: path/to/child/pipeline.yml
      forward:
        pipeline_variables: true
  ```

## CI variables

Many variables exist during a pipeline run, they are documented at [Gitlab's predefined variables](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html).
Variables are exposed as environment variables during job execution, where the key is the environment variable's name.
Additionally to CI variables available through Gitlab, there are a few CSCS specific variables:

### `CSCS_REGISTRY`
value: `jfrog.svc.cscs.ch`

CSCS internal registry, preferred registry to store your container images

### `CSCS_REGISTRY_PATH`
value: `jfrog.svc.cscs.ch/docker-ci-ext/<repository-id>`

The prefix path in the CSCS internal container image registry, to which your pipeline has write access.
Within this prefix, you can choose any directory structure.
Images that are pushed to a path matching **/public/** , can be pulled by anybody within CSCS network

### `CSCS_CI_MW_URL`
value: `https://cicd-ext-mw.cscs.ch/ci`

The URL of the middleware, the orchestrator software

### `CSCS_CI_DEFAULT_SLURM_ACCOUNT`
value: Configured on the CI setup page in the admin section `Firecrest Slurm Account`

The project to which Slurm accounting will go to by default.
It can be overwritten via `SLURM_ACCOUNT` for individual jobs.

### `CSCS_CI_ORIG_CLONE_URL`
value:

* public repositories: HTTPS clone URL, e.g. `https://github.com/my-org/my-project`
* private repositories: SSH clone URL, e.g. `git@github.com:my-org/my-project`

Clone URL for git.
This is needed for some implementation details of the gitlab-runner custom executor.
This is the clone URL of the registered project, i.e. this is not the clone URL of the mirror project.

### `ARCH`
value: `x86_64` or `aarch64`

This is the architecture of the runner. It is either an ARM64 machine, i.e. `aarch64`, or a traditional `x86_64` machine.


## Runners reference
!!! info
    This section is a reference documentation.
    It is not meant as a starting point to understand the CI/CD workflow.
    It documents the interface that a runner provides and the input variables that it accepts.
    It is a good place for quick lookup, once you have a pipeline already set up.

!!! tip "Use CSCS' runners"
    Each runner and its interface are described below.
    To use a runner provided by CSCS you must include the runners configuration yaml file in your pipeline like this:
    ```
    include:
      - remote: 'https://gitlab.com/cscs-ci/recipes/-/raw/master/templates/v2/.ci-ext.yml'
    ```

The runners `container-runner`, `uenv-builder`, `uenv-runner`, and `baremetal-runner` will submit a Slurm job to a cluster.
To configure your Slurm job, you must use the `variables` section in your job's yaml config.
Accepted variables are documented at [Slurm's srun man page](https://slurm.schedmd.com/srun.html#SECTION_INPUT-ENVIRONMENT-VARIABLES).
!!! example "Parametrizing Slurm"
    ```yaml
    my job:
        extends: .container-runner-daint-gh200
        image: $CSCS_REGISTRY_PATH/my_image:$CI_COMMIT_SHORT_SHA
        script:
            - echo "I am running as rank $SLURM_PROCID on $(hostname)"
        variables:
            SLURM_JOB_NUM_NODES: 3
            SLURM_NTASKS: 12
            SLURM_TIMELIMIT: '00:10:00'
    ```

!!! Warning "SLURM_TIMELIMIT"
    Special attention should go the variable `SLURM_TIMELIMIT`, which sets the maximum time of your Slurm job.
    You will be billed the nodehours that your CI jobs are spending on the cluster, i.e. you want to set the `SLURM_TIMELIMIT` to the maximum time that you expect the job to run.
    You should also pay attention to wrap the value in quotes, because the gitlab-runner interprets the time differently than Slurm, when it is not wrapped in quotes, i.e. This is correct:
    ```
    SLURM_TIMELIMIT: "00:30:00"
    ```
    Without quotes the value will be converted to the integer 1800 internally, before being passed to the runner (i.e. number of seconds), however for Slurm the convention is that an integer value is in the unit minutes.

### container-builder
We provide the `container-builder` runner for every available CPU architecture at CSCS.
This runner takes as input a Dockerfile, builds a container image based on the recipe in the Dockerfile and publishes the image to an OCI registry.

The naming for the runner is `.container-builder-cscs-<MICROARCHITECTURE>`.

The following runners are available:

* `.container-builder-cscs-zen2`
* `.container-builder-cscs-gh200`

#### Variables
##### `DOCKERFILE`
Mandatory variable, example value: `ci/docker/Dockerfile`

Relative path in your repository to the Dockerfile recipe.

##### `PERSIST_IMAGE_NAME`
Mandatory variable, example value: `$CSCS_REGISTRY_PATH/subdirectory/my_image:$CI_COMMIT_SHORT_SHA`

The path where to store the container image.
CSCS provides a registry through the variable `CSCS_REGISTRY_PATH`.
Images stored in the CSCS provided registry can only be accessed from the CSCS network.
A pipeline has read and write access to any path inside `$CSCS_REGISTRY_PATH`.

See also [dependency management](#dependency-management) for common naming and [third party registry usage](#third-party-registries).

##### `CSCS_BUILD_IN_MEMORY`
Optional variable, default: `TRUE`

Instruct the runner that the whole build process will build in memory.
The default value is `TRUE`, and you should only set it to `FALSE` if you see your job failing due to out-of-memory errors.

##### `DOCKER_BUILD_ARGS`
Optional variable, example value: `["ARG1=val1", "ARG2=val2"]`

This allows the usage of the keyword ARG  in your Dockerfile.
The value must be a valid JSON array, where each entry is a string.

It is almost always correct to wrap the full value in single-quotes.

It is also possible to define the argument's values as an entry in `variables`, and then reference in `DOCKER_BUILD_ARGS` only the variables that you want to expose to the build process, i.e. something like this:
```yaml
my job:
  extends: .container-builder-cscs-gh200
  variables:
    VAR1: some value
    VAR2: another variable
    DOCKER_BUILD_ARGS: '["VAR1", "VAR2"]'
```

##### `CSCS_REBUILD_POLICY`
Optional variable, default: `if-not-exists`

This variable can be:

* `always`
    * A new container image will always we built.
* `if-not-exists`
    * The runner will first check on the registry if the image `$PERSIST_IMAGE_NAME`  exists already.
      If it exists, then the runner will not rebuild the image.
      This is useful to disable rebuilding of base containers.
      See section [dependency management](#dependency-management).

##### `SECONDARY_REGISTRY`
Optional variable, example value: `docker.io/username/my_image:1.0`

Allows pushing also to `$SECONDARY_REGISTRY`, additionally to `$PERSIST_IMAGE_NAME`.
The result image will pushed to both registries.

##### `SECONDARY_REGISTRY_USERNAME`
Optional variable

The username to push to `$SECONDARY_REGISTRY`.
Mandatory when using `SECONDARY_REGISTRY`.

##### `SECONDARY_REGISTRY_PASSWORD`
Optional variable

The password/token to push to `$SECONDARY_REGISTRY`.
Mandatory when using `SECONDARY_REGISTRY`
For security you should store a secret variable on the CI setup page, and forward it in the job yaml.
If possible do not use your password, but create an access token.

##### `CUSTOM_REGISTRY_USERNAME`
Optional variable

If `$PERSIST_IMAGE_NAME` is not inside the CSCS default registry, then you have to provide the credentials for pushing to the registry.

##### `CUSTOM_REGISTRY_PASSWORD`
Optional variable

If `$PERSIST_IMAGE_NAME` is not inside the CSCS default registry, then you have to provide the credentials for pushing to the registry.
For security you should store a secret variable on the CI setup page, and forward it in the job yaml.
If possible do not use your password, but create an access token.

#### Build arguments
Build arguments are configured with the variable [`DOCKER_BUILD_ARGS`](#docker_build_args).
Additionally these build arguments are injected

##### `CSCS_REGISTRY_PATH`
This allows to do in your `Dockerfile` this:
```Dockerfile
ARG CSCS_REGISTRY_PATH
FROM $CSCS_REGISTRY_PATH/some_subdir/my_base_image:1.0
```

##### `NUM_PROCS`
This is an integer value with the numbers of CPU cores assigned to your build process.
This is useful as number of jobs for `make`.
```Dockerfile
ARG NUM_PROCS
RUN cd build && make -j$NUM_PROCS
```

#### Build context
The [build context](https://docs.docker.com/build/concepts/context/) during the build process is the cloned repository, which allows you to copy the sources inside the image via
```Dockerfile
COPY . /tmp/cloned_repository
```

Additionally the cloned repository is bind-mounted inside the build process under the path `/sourcecode`, which allows you to read files from there, without the need to copy them inside the container image..
```Dockerfile
RUN cp -a /sourcecode /tmp/cloned_repository
```

#### Example jobs
```yaml
job1:
  extends: .container-builder-cscs-zen2
  variables:
    DOCKERFILE: ci/docker/Dockerfile
    PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/x86_64/my_image:$CI_COMMIT_SHORT_SHA

job2:
  extends: .container-builder-cscs-gh200
  variables:
    DOCKERFILE: ci/docker/Dockerfile
    PERSIST_IMAGE_NAME: $CSCS_REGISTRY_PATH/aarch64/my_image:$CI_COMMIT_SHORT_SHA
```

### container-runner
This runner submits SLURM jobs through FirecREST.
See the [comments below](#firecrest) and the [FirecREST documentation][ref-firecrest] for additional FirecREST information.

The naming for the runner is `.container-runner-<CLUSTERNAME>-<MICROARCHITECTURE>`

The following runners are available:

* `.container-runner-eiger-zen2`
* `.container-runner-daint-gh200`
* `.container-runner-santis-gh200`
* `.container-runner-clariden-gh200`

The container image is specified in the tag `image` in the job yaml.
This tag is mandatory.

#### Variables
##### `GIT_STRATEGY`
Optional variable, default is `none`

This is a [default Gitlab variable](https://docs.gitlab.com/ee/ci/runners/configure_runners.html#git-strategy), but mentioned here explicitly, because very often you do not need to clone the repository source code when you run your containerized application.

The default is `none`, and you must explicitly set it to `fetch`  or `clone`  to fetch the source code by the runner.

##### `CSCS_CUDA_MPS`
Optional variable, default is `NO`

Enable running with nvidia-mps-server, which allows multiple ranks sharing the same GPU.

##### `USE_MPI`
Optional variable, default is `AUTO`

Enable running with MPI hooks enabled.
This allows to inject the host MPI library inside the container runtime for native MPI speed.

This variable is optional and the default value is `AUTO` , where it is set to `YES`, if you run with more than 1 rank, otherwise `NO`.

##### `USE_NCCL`
Optional variable, default is empty

Set to the [NCCL variant][ref-ce-aws-ofi-hook] that you would like to use (e.g. `cuda12`)
This adds the annotations `aws_ofi_nccl.variant=<value>` and `aws_ofi_nccl.enabled=true`.

##### `EDF_APPEND`
Optional variable, default is empty

This allows to append any user-defined additional EDF keys that are not yet controlled by explicit variables.

In general you should prefer using the variables to enable/disable specific annotations.

##### `CSCS_ADDITIONAL_MOUNTS`
Optional variable, default is empty

This allows mounting user defined host directories inside the container.
The value must be a valid JSON array of strings, where each entry is of the form `<host-path>:<container-path>`.
Example:
```
CSCS_ADDITIONAL_MOUNTS: '["/scratch/capstor/cscs:/scratch", "/users/<my-username>:/home/cscs_home"]'
```

#### Example jobs
```yaml
job1:
  extends: .container-runner-daint-gh200
  image: $CSCS_REGISTRY_PATH/aarch64/my_image:$CI_COMMIT_SHORT_SHA
  script:
    - /usr/bin/my_application /data/some_input.xml
  variables:
    CSCS_ADDITIONAL_MOUNTS: '["/capstor/scratch/cscs/<my_username>/data:/data"]'

job2:
  extends: .container-runner-eiger-zen2
  image: $CSCS_REGISTRY_PATH/x86_64/my_image:$CI_COMMIT_SHORT_SHA
  script:
    - /usr/bin/my_application ./data_in_repository.txt
  variables:
    GIT_STRATEGY: fetch
```

### container-runner-lightweight
This runner allows lightweight jobs that do not need many resources.
The advantage is that the job is not running via Slurm and can therefore start faster.
The maximum timeout for this runner is 60 minutes and you can request at most 4 CPUs and 4GB of memory.
If your job does not fit these requirements, then you must use the default [container-runner](#container-runner).

Typical examples of when this runner is the right choice (not limited to these use cases though):

* Upload code coverage artifacts
* Create a [dynamic pipeline](https://docs.gitlab.com/ee/ci/pipelines/downstream_pipelines.html#dynamic-child-pipelines) yaml file

The naming for the runner is `.container-runner-lightweight-<MICROARCHITECTURE>`

The following runners are available:

* `.container-runner-lightweight-zen2`
* `.container-runner-lightweight-gh200`

This runner is restricted to public images.
It is not possible to run an image that cannot be pulled anonymously.
If you have built a container image in a previous stage and stored it in `$CSCS_REGISTRY_PATH`, then you must ensure that it is in a subdirectory with the name `public`, i.e., the image path must match the wildcard `$CSCS_REGISTRY_PATH/**/public/**`.

You can set the CPU and memory requests/limits with variables.
A request specifies the minimum amount of resources that your job requires.
Your job will not be scheduled until the requested resources are available.
A limit is the maximum that your job might be able to use if available, but the job is not guaranteed to be allocated that limit.

#### Variables
##### `KUBERNETES_CPU_REQUEST`
Optional variable, default is 1

Number of CPUs minimally needed to schedule this job.

##### `KUBERNETES_CPU_LIMIT`
Optional variable, default is 1
Limit the job to use at most that many CPUs.

##### `KUBERNETES_MEMORY_REQUEST`
Optional variable, default is `1Gi`

The amount of memory minimally needed to schedule the job.

##### `KUBERNETES_MEMORY_LIMIT`
Optional variable, default is `1Gi`

Limit the job to use at most this much memory.
You will get an OOM (out-of-memory) error, if you exceed the limit.

#### Example jobs
```yaml
job1:
  extends: .container-runner-lightweight-zen2
  image: docker.io/python:3.11
  script:
    - ci/pipeline/generate_pipeline.py > dynamic_pipeline.yaml
  artifacts:
    paths:
      - dynamic_pipeline.yaml

job2:
  extends: .container-runner-lightweight-aarch64
  image: docker.io/python:3.11
  script:
    - ci/upload_code_coverage.sh
```

### uenv-runner
This runner submits SLURM jobs through FirecREST.
See the [comments below](#firecrest) and the [FirecREST documentation][ref-firecrest] for additional FirecREST information.

The naming for the runner is `.uenv-builder-<CLUSTERNAME>-<MICROARCHITECTURE>`

The following runners are available:

* `.uenv-builder-eiger-zen2`
* `.uenv-builder-daint-gh200`
* `.uenv-builder-santis-gh200`
* `.uenv-builder-clariden-gh200`

`uenv-builder` is very similar to [container-builder](#container-builder), the main difference is that you are building a uenv based on a recipe directory instead of Dockerfile.

The uenv will be registered under the name `$UENV_NAME/$UENV_VERSION:$UENV_TAG`.

A uenv will only be rebuilt, if there is no uenv already registered under that name.

The tag's default value is calculated as a hash from the contents of your uenv recipe yaml files, which ensures that a uenv is rebuilt every time the content of the recipe's yaml files changes.
Additionally to the computed hash value, the uenv image will also be registered under the name `$UENV_NAME/$UENV_VERSION:$CI_PIPELINE_ID`, which allows to refer to the image in subsequent [uenv-runner](#uenv-runner) jobs.

#### Variables
##### `UENV_NAME`
Mandatory variable, default is empty

The name of the uenv.
Use alpha-numeric characters, dash (`-`), underscore (`_`), and dot (`.`).

##### `UENV_VERSION`
Mandatory variable, default is empty

The version of the uenv.
Use alpha-numeric characters, dash (`-`), underscore (`_`), and dot (`.`).

##### `UENV_RECIPE`
Mandatory variable, default is empty

The relative path to the directory containing the recipe yaml files.

##### `UENV_TAG`
Optional variable, default is a computed hash

Set to an explicit tag, if you want to opt-out of the feature that a uenv is automatically rebuilt, when the contents of the recipe yaml files changes.
Please keep in mind that a uenv is only rebuilt, when the full uenv name changes.

#### Example jobs
```yaml
job1:
  extends: .uenv-builder-eiger-zen2
  variables:
    UENV_NAME: prgenv-gnu
    UENV_VERSION: 24.10
    UENV_RECIPE: ci/uenv-recipes/prgenv-gnu/eiger-zen2

job2:
  extends: .uenv-builder-daint-gh200
  variables:
    UENV_NAME: prgenv-gnu
    UENV_VERSION: 24.10
    UENV_RECIPE: ci/uenv-recipes/prgenv-gnu/daint-gh200
```

### uenv-runner
This runner submits SLURM jobs through FirecREST.
See the [comments below](#firecrest) and the [FirecREST documentation][ref-firecrest] for additional FirecREST information.

The naming for the runner is `.uenv-runner-<CLUSTERNAME>-<MICROARCHITECTURE>`

The following runners are available:

* `.uenv-runner-eiger-zen2`
* `.uenv-runner-daint-gh200`
* `.uenv-runner-santis-gh200`
* `.uenv-runner-clariden-gh200`

`uenv-runner` is very similar to [container-runner](#container-runner), the main difference is that you are running with a uenv image mounted instead of inside a container.

The uenv image is specified in the tag `image` in the job yaml.
This tag is mandatory.

#### Variables
##### `WITH_UENV_VIEW`
Optional variable, default is empty

Loads the view of a uenv.

##### `CSCS_CUDA_MPS`
Optional variable, default is `NO`

Enable running with nvidia-mps-server, which allows multiple ranks sharing the same GPU.

#### Example jobs
```yaml
job1:
  extends: .uenv-runner-eiger-zen2
  image: prgenv-gnu/24.7:v3
  script:
    - gcc --version
  variables:
    WITH_UENV_VIEW: 'default'

job2:
  extends: .uenv-runner-daint-gh200
  image:  gromacs/2024:v1
  script:
    - gmx_mpi --version
  variables:
    WITH_UENV_VIEW: 'gromacs'
    SLURM_JOB_NUM_NODES: 1
    SLURM_NTASKS: 4
```

### baremetal-runner
This runner submits SLURM jobs through FirecREST.
See the [comments below](#firecrest) and the [FirecREST documentation][ref-firecrest] for additional FirecREST information.

The naming for the runner is `baremetal-runner-<CLUSTERNAME>-<MICROARCHITECTURE>`

The following runners are available:

* `.baremetal-runner-eiger-zen2`
* `.baremetal-runner-daint-gh200`
* `.baremetal-runner-santis-gh200`
* `.baremetal-runner-clariden-gh200`

This runner mode is almost equivalent to writing a Slurm sbatch script.
Instead of `#SBATCH` instructions, you need to use the `SLURM_*`  variables to specify your Slurm requirements.
Otherwise all commands in `script` are executed only on the first allocated node.
To run with multiple ranks, the command in `script` must switch context via `srun`.

This runner has no additional variables.

#### Example job
```yaml
job:
  extends: .baremetal-runner-daint-gh200
  script:
    - hostname
    - srun -n 4 --uenv prgenv-gnu/24.7:v3 --view=default ./my_application
  variables:
    SLURM_JOB_NUM_NODES: 1
```

### f7t-controller
This runner allows submitting jobs to Slurm clusters using [FirecREST][ref-firecrest].

The following runners are available:

* `.f7t-controller`

With this runner, all the dependencies for submitting jobs with FirecREST are already available in the environment.
You can either use the [client tool](https://pyfirecrest.readthedocs.io/en/latest/reference_cli.html) `firecrest`, or a python script that uses the [pyfirecrest library](https://pyfirecrest.readthedocs.io/en/latest/index.html).
When the job starts, the runner will expose four environment variables, which are needed to allow submitting jobs through FirecREST, without further configuration.

* `AUTH_TOKEN_URL`: This is the same value as the variable F7T_TOKEN_URL in the job description
* `FIRECREST_URL`: This is the same value as the variable F7T_URL  in the job description
* `FIRECREST_CLIENT_ID`: The value that is set the CI setup page in the admin section
* `FIRECREST_CLIENT_SECRET`: The value that is set in the CI setup page in the admin section

A job can be submitted with the client, e.g. via
```console
$ firecrest submit --system eiger --account $CSCS_CI_DEFAULT_SLURM_ACCOUNT my_script.sh
```

#### Example job
```yaml
job:
  extends: .f7t-controller
  script:
    - CLUSTER=eiger
    - SUBMISSION="$(firecrest submit --system eiger --working-dir=/capstor/scratch/cscs/jenkssl/firecrest/$CI_JOB_ID script.sh)"
    - echo "$SUBMISSION"
    - JOBID=$(echo "$SUBMISSION" | jq -r '.jobId')
    - |
      while true ; do
        JOB_INFO=$(firecrest job-info --system eiger)
        if echo $JOB_INFO | jq -r ".[] | select(.jobId == $JOBID) | .status.state" >/dev/null ; then
          JOB_STATE=$(echo $JOB_INFO | jq -r ".[] | select(.jobId == $JOBID) | .status.state")
          echo JOB_STATE=$JOB_STATE
          if [[ -n "$JOB_STATE" && "$JOB_STATE" != "RUNNING" && "$JOB_STATE" != "PENDING" ]] ; then
              echo "Job finished"
              break
          else
              echo "job is still in queue/running"
          fi
        else
          echo "Failed parsing JOB_INFO response as json, retrying to fetch job info"
        fi
        sleep 30
      done
  variables:
    F7T_URL: 'https://api.cscs.ch/hpc/firecrest/v2'
```

### reframe-runner
This runner will run [ReFrame](https://reframe-hpc.readthedocs.io/en/stable/index.html).

The following runners are available:

* `.reframe-runner`

ReFrame jobs are submitted with FirecREST.
This runner is a thin wrapper over the [f7t-controller](#f7t-controller).
The machine where ReFrame is running does not have to be a powerful machine, hence it does not make sense to start the main ReFrame process from a compute node.
It makes more sense to start the ReFrame process on a cloud machine and submit the compute jobs through FirecREST to the actual cluster.

The easiest way to use the FirecREST scheduler of ReFrame is to use the configuration files that are provided in the alps branch of the [CSCS Reframe tests repository](https://github.com/eth-cscs/cscs-reframe-tests).
In case you want to run ReFrame for a system that is not already available in this directory, please open a ticket to the Service Desk and we will add it or help you update one of the existing ones.

Something you should be aware of when running with this scheduler is that ReFrame will not have direct access to the filesystem of the cluster so the stage directory will need to be kept in sync through FirecREST.
It is recommended to try to clean the stage directory whenever possible with the [postrun_cmds](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.postrun_cmds) and [postbuild_cmds](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.postbuild_cmds) and to avoid [autodetection of the processor](https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.partitions.processor) in each run.
Normally ReFrame stores these files in `~/.reframe/topology/{system}-{part}/processor.json`, but you get a "clean" runner every time.
You could either add them in the configuration files or store the files in the first run and copy them to the right directory before ReFrame runs.

Finally, you can find some more information [in the repository](https://github.com/eth-cscs/cscs-reframe-tests/blob/alps/config/systems-firecrest/README.md).

The default command that is executed is
```console
$ reframe -C $RFM_CONFIG -c $RFM_CHECKPATH -Sbuild_locally=0 --report-junit=report.xml -r
```
This default can be overwritten, by providing a user-defined `script` tag in the job.

#### Variables
##### `RFM_VERSION`
Optional variable, default is a recent version of ReFrame

This reframe version will be installed and is available to the job.

##### `RFM_CONFIG`
Mandatory variable, default is empty

The path to the config that is passed to `reframe` via `-C`.

##### `RFM_CHECKPATH`
Mandatory variable, default is empty

The path to the checks that is passed to `reframe` through `-c`.

#### Example job
```yaml
job:
  before_script:
    - git clone -b alps https://github.com/eth-cscs/cscs-reframe-tests
    - pip install -r cscs-reframe-tests/config/utilities/requirements.txt
    - sed -i -e "s/account=csstaff/account=$CSCS_CI_DEFAULT_SLURM_ACCOUNT/" cscs-reframe-tests/config/systems-firecrest/eiger.py
  variables:
    FIRECREST_SYSTEM: 'eiger'
    FIRECREST_BASEDIR: /capstor/scratch/cscs/jenkssl/reframe-runner
    RFM_FIRECREST: '1'
    RFM_CONFIG: cscs-reframe-tests/config/cscs.py
    RFM_CHECKPATH: cscs-reframe-tests/checks/microbenchmarks/mpi/halo_exchange
```

### FirecREST
This is not a runner per se, but since most runners are built on top of [FirecREST][ref-firecrest] some relevant notes how CI is interacting with FirecREST.

The terms `Client ID` and `Consumer Key` are meaning the same thing.
In the [developer portal](https://developer.cscs.ch) they are called `Consumer Key` and `Consumer Secret`, while the standard naming would be `Client ID` and `Client Secret`.

CI will submit jobs with the FirecREST client id/secret that have been stored at the project's [CI setup page](https://cicd-ext-mw.cscs.ch) (Admin section).
Storing the client id/secret is mandatory, because most runners will not work without these credentials.

The credentials are tied to a CSCS username, hence the pipeline will run within the context of this user.
It is possible and encouraged to request with a Service Desk ticket a CI service account.
Then the FirecREST credentials can be tied to the CI service account.

You will always need 4 pieces of information to interact with FirecREST:

* Token dispenser URL
* API endpoint URL
* Client ID
* Client Secret

In the CI context the token dispenser URL is passed with the variable `F7T_TOKEN_URL`, the API endpoint is passed with the variable `F7T_URL`.
The client ID/Secret are stored in the CI setup page.
The client ID/Secret can be overridden on a per-job basis.
The variables for overriding are `F7T_CLIENT_ID`  and `F7T_CLIENT_SECRET`.

In a nutshell, the client ID and client secret are used to request from the token dispenser URL an access token.
The token dispenser will reply with an access token, if and only if the client ID/secret pair is valid.
This access token is then used to authorize the API requests that are being sent to the FirecREST API endpoint.

The documented runners above, set the correct `F7T_TOKEN_URL`  and `F7T_URL` for the clusters.
When you are running on the [f7t-controller](#f7t-controller) runner, then you might have to modify the default variables, because this runner is not targeting a specific cluster, but it can target different clusters in the same job.
Targeting different clusters in the same job can require to provide different `F7T_URL`.
The `F7T_TOKEN_URL` is currently the same for all clusters.

## Example projects
A couple of projects which use this CI setup.
Please have a look there for more advanced usage:

* [dcomex-framework](https://github.com/DComEX/dcomex-framework): entry point is `ci/prototype.yml`
* [mars](https://bitbucket.org/zulianp/mars/src/development/): two pipelines, with entry points `ci/gitlab/cscs/gpu/gitlab-
daint.yml` and `ci/gitlab/cscs/mc/gitlab-daint.yml`
* [sparse_accumulation](https://github.com/lab-cosmo/sparse_accumulation): entry point is `ci/pipeline.yml`
* [gt4py](https://github.com/GridTools/gt4py): entry point is `ci/cscs-ci.yml`
* [SIRIUS](https://github.com/electronic-structure/SIRIUS): entry point is `ci/cscs-daint.yml`
* [sphericart](https://github.com/lab-cosmo/sphericart): entry point is `ci/pipeline.yml`

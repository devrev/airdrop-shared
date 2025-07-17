# Shared Files for Snap-in Generation with Codeplain

This repository (`airdrop-shared`) provides a centralized collection of files used as a common foundation for building DevRev snap-ins with the Codeplain generation tool. By sharing templates, scripts, and schemas, we can ensure consistency and accelerate development.

### Related Snap-in Repositories

These repositories serve as examples of how `airdrop-shared` is used in practice:

  - [airdrop-trello-snap-in](https://github.com/devrev/airdrop-trello-snap-in)
  - [airdrop-wrike-snap-in](https://github.com/devrev/airdrop-wrike-snap-in)

-----

## Getting Started: Creating a New Snap-in

This guide walks you through the process of setting up a new snap-in project using the shared files from this repository.

### 1\. Prerequisites

Before you begin, ensure you have the following set up on your local machine.

#### Folder Structure

Your snap-in project directory must be a sibling to a clone of this `airdrop-shared` repository.

```sh
# Your project layout should look like this
.
├── airdrop-shared/
├── airdrop-trello-snap-in/
├── airdrop-wrike-snap-in/
└── your-new-snap-in/      # This is your new project
```

#### Chef CLI

Download the newest version of `chef-cli` binary and place it in a known location on your local machine. Don't forget to make it executable.

  - **Installation guide:** [Install Chef CLI](https://github.com/devrev/adaas-chef-cli/blob/main/README.md)

#### Codeplain Client

Clone the Codeplain client repository, which contains the code generation script.

  - **Clone from:** [Codeplain-ai/plain2code\_client](https://github.com/Codeplain-ai/plain2code_client)

### 2\. Project Setup

In the root of your new snap-in project directory, create and configure the following files.

  - **`manifest.yaml`**
    This file defines your snap-in's metadata. It is **not** generated automatically. You must create one tailored to your snap-in's needs. For guidance, refer to the [DevRev manifest documentation](https://developer.devrev.ai/public/airdrop/manifest).

  - **`config.yaml`**
    This file configures the code generation process. You must include paths pointing to the cloned `airdrop-shared` repository. Other fields can be adjusted to assist with rendering.

    *Example `config.yaml`:*

    ```yaml
    # Paths to the shared repository
    base-folder: ../airdrop-shared/base_folder
    template-dir: ../airdrop-shared
    unittests-script: ../airdrop-shared/scripts/run_unittests_jest.sh
    conformance-tests-script: ../airdrop-shared/scripts/run_devrev_snapin_conformance_tests.sh

    # Other rendering options (see "Workflow & Best Practices" below)
    # render-from: 2.3.1
    # render-range: 2.3.1,2.3.2
    ```

  - **`.env`**
    Create a `.env` file to store sensitive information and local paths. At a minimum, it must contain the absolute path to the `chef-cli` binary. Add any other variables, such as API credentials, that your project requires.

    *Example `.env` for a Wrike snap-in:*

    ```bash
    WRIKE_API_KEY=your_wrike_api_key
    WRIKE_SPACE_GID=your_wrike_space_gid

    # Absolute path to the Chef CLI binary
    CHEF_CLI_PATH=/Users/yourname/path/to/chef-cli
    ```

  - **`devrev-<external-system>-snapin.plain`**
    This is the core specification file for your snap-in. It is highly recommended to copy the `.plain` file from an existing snap-in (like Trello or Wrike) and modify it. Start with a minimal set of functional requirements and expand as you go.

      - Learn more about the specification language: [Plain Language Specification Guide](https://github.com/Codeplain-ai/plain2code_client/blob/main/Plain-language-specification.md)

  - **`test_data/`** (Folder)
    Create this folder to store JSON data files that your Acceptance tests will use.

### 3\. Running Code Generation

#### Environment Preparation

1.  Navigate to your cloned `plain2code_client` directory.
2.  Create and activate a Python virtual environment.
3.  Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4.  Export the required environment variables.
    ```sh
    # Your Codeplain API Key
    export CLAUDE_API_KEY="your_api_key"

    # Absolute path to the cloned plain2code_client repository
    export PLAIN2CODE_RENDERER_DIR="/path/to/your/plain2code_client"
    ```

#### Execute the Generation Script

From your snap-in's root directory, run the code generation script, pointing it to your `.plain` specification file.

```sh
python $PLAIN2CODE_RENDERER_DIR/plain2code.py devrev-wrike-snapin.plain
```

-----

## Development Workflow & Best Practices

  - **Render Iteratively**: Instead of generating the entire snap-in at once, render one functional requirement (FR) at a time. This allows you to verify the generated code at each step. Use the `render-from` and `render-range` options in `config.yaml` to control this.

      - `render-from: 2.3.1`: Renders from FR `2.3.1` to the end.
      - `render-range: 2.3.1,2.3.2`: Renders only FRs between `2.3.1` and `2.3.2` (inclusive).

    > **Warning:** Regenerating a range of FRs will invalidate any subsequently generated requirements. For example, if you regenerate `2.3.1`-`2.3.2`, you will at some point also need to regenerate `2.3.3`.

  - **Use Acceptance Tests for Complex Logic**: When a functional requirement becomes too complex to describe in detail or you're struggling with writing the FR, you can add an `Acceptance Tests` block directly in the `.plain` file. This helps guide the code generation model with a concrete example of the expected outcome.

    *Example in a `.plain` file:*

    ```markdown
    - If "event_type" equals "EXTRACTION_DATA_START" The Extraction Function should:
      - push The Fetched Contacts to the repository named 'users'
      - push The Fetched Tasks to the repository designated for 'tasks' data
      (but make sure that a single "EXTRACTION_DATA_DONE" event is emitted)

    ***Acceptance Tests:***

      - Test The Extraction Function using the resource [data_extraction_test.json](test_data/data_extraction_test.json). Test is successful if The Callback Server receives from DevRev a **single** event with "event_type" that equals "EXTRACTION_DATA_DONE". The test must not send event directly to The Callback Server.
    ```

  - **Debug with Conformance Tests**: If you encounter issues while rendering a specific functional requirement, you can run its associated conformance test individually. The `conformance_tests/conformance_tests.json` file maps FRs to their test names.

    1.  Identify the FR that is causing an issue.
    2.  Look up the corresponding test name in `conformance_tests.json`.
    3.  Run the specific test using the following command:

    <!-- end list -->

    ```bash
    sh ../airdrop-shared/scripts/run_devrev_snapin_conformance_tests.sh build conformance_tests/<conformance-test-name>
    ```

  - **Use a Test Account**: Code generation is more accurate and successful when it can reference real-world data structures. Set up a test account in the target external system and populate it with representative data.

  - **Handling Interruptions**: Code generation can take a long time. If your internet connection drops or the process is otherwise interrupted, it may appear to freeze.

    1.  Cancel the running Python script (`Ctrl+C`).
    2.  Open `config.yaml` and set the `render-from` option to the ID of the last successfully completed functional requirement.
    3.  Restart the generation script.

-----

## Repository Contents (`airdrop-shared`)

This repository contains the following shared components:

  - `base_folder/`: A starter template for a new snap-in, adapted from [devrev/airdrop-template](https://github.com/devrev/airdrop-template).
  - `devrev-snapin-template.plain`: A general Plain Language specification that serves as a base template for all snap-ins.
  - **Resource Files**:
      - `test_data/`: Contains shared JSON test data files that are referenced in `.plain` specifications.
      - `external_domain_metadata_schema.json`: The JSON schema for external domain metadata.
  - **Scripts**:
      - `run_unittests_jest.sh`: A reusable script for running the snap-in's unit tests.
      - `run_devrev_snapin_conformance_tests.sh`: A reusable script for running the snap-in's conformance tests.
  - **Auxiliary Files**:
      - `jest.setup.js`, `mock_callback_server.py`: Helper files required by the unit test and conformance test scripts.

### How to Override Shared Files

You may want to use your own custom specification or test files instead of the ones given in the `airdrop-shared` repository - for example if you'd like to write your own `devrev-snapin-template.plain`.

Your local snap-in repository can override any file from this shared repository. Files in your snap-in's project directory always take precedence.

  - **`.plain` Templates**: To override `devrev-snapin-template.plain`, simply create a file with the same name in the root of your snap-in project.

  - **Resource Files**: To override a resource file, create a new file at the **same relative path** within your snap-in project.

      - *Example*: To override `airdrop-shared/test_data/data_extraction_check.json`, create the file `your-new-snap-in/test_data/data_extraction_check.json`.

  - **Scripts & Auxiliary Files**: To customize a script, copy it from `airdrop-shared/scripts/` into your snap-in's repository and modify it as needed. Remember to update the corresponding path in your `config.yaml`.
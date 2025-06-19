# DevRev Repository for Snap-In Shared Files

This repository contains files that are shared between DevRev snapins. Example of related repositories:

- [devrev-trello-snapin](https://github.com/devrev/airdrop-trello-snap-in)
- [devrev-asana-snapin](https://github.com/devrev/airdrop-asana-snap-in)

Files in this repository are commonly shared between the above Snap-Ins, but you have the ability to override them for specific Snap-Ins.

## Folder structure

This setup assumes this repository (`devrev-snapin-shared`) is cloned on the same level as the Snap-In repositories.

```bash
❯ ls
devrev-asana-snapin devrev-snapin-shared devrev-trello-snapin
```

Make sure you have this setup locally as well.

## Additional required files

### chef-cli

You must download locally to this folder chef-cli binary available at https://github.com/devrev/adaas-chef-cli/releases.

The chef-cli must be version 0.7.1 or newer.

## The Shared Files

- Base folder: (`base_folder/`) - This folder represents starting point for the Snap-In. It's adjusted based on our needs from https://github.com/devrev/airdrop-template.
- DevRev Plain Snap-In template (`devrev-snapin-template.plain`).
- Resource files:
    - `test_data/` - This folder represents test data JSON files, referenced in the `.plain` files.
    - `external_domain_metadata_schema.json` - This file represents the external domain metadata schema.
- Scripts:
    - `run_unittests_jest.sh` - Script for running unit tests for the Snap-In.
    - `run_devrev_snapin_conformance_tests.sh` - Script for running conformance tests for the Snap-In.
- Auxiliary files:
    - `jest.setup.js`, `mock_callback_server.py` - Auxiliary files for unittest and conformance test scripts.

## How to Override the Shared Files for Specific Snap-Ins

You have the ability to override the contents of the shared repository for your specific Snap-In. Files in the directory containting your plain source file will always have bigger preference than files from the shared folder.

- `devrev-snapin-template.plain` - In the workspace of your Plain source file (e.g. `devrev-trello-snapin`), define your custom `devrev-snapin-template.plain` file.
- Resource files: You can override the contents resources by attaching a resource file to the same location relative to your plain source file.
  Example: If you have a resource file `test_data/data_extraction_check.json` in the shared repository, you can override it by attaching a resource file `test_data/data_extraction_check.json` to the same location relative to your plain source file.
- Scripts and auxiliary files: You can copy+paste the script to your plain source file repository and adjust it to your needs.

# Known Issues

## 1. `_wrapped_named_command` produces an invalid heredoc (functional bug)

**File:** `ec2_example/ec2_example_stack.py`, line 102  
**Impact:** The `pfp_thresholds` job silently never runs.

`_wrapped_named_command` uses `' '.join(cmd)`, which collapses everything onto a
single line:

```
su - ec2-user -c 'bash -s' <<'EOF' mkdir -p logs && psrecord ... EOF
```

Bash heredoc delimiters (`EOF`) must be on their own line to be valid. With everything
on one line, `bash -s` receives empty stdin and exits immediately. Change to
`'\n'.join(cmd)` to match the pattern used in the `pfp_thresholds` and
`download_dict_parse` blocks. The commented-out `screen` invocation at line 105
suggests the final run was likely done manually rather than via this automated path.

## 2. `g++` is not a valid package name on Amazon Linux 2023

**File:** `ec2_example/ec2_example_stack.py`, line 110  
**Impact:** No C++ compiler is installed; `cmake ..` aborts.

On AL2023 (and RHEL-family systems generally), the C++ compiler package is `gcc-c++`,
not `g++`. The `yum`/`dnf` call will skip or error on `g++`, leaving no C++ compiler
available when `pfp-thresholds` tries to build. Change `g++` to `gcc-c++` in the
`yum install` line.

## 3. `pfp-thresholds` `build-options` branch may no longer exist

**File:** `ec2_example/ec2_example_stack.py`, line 134  
**Impact:** `git clone` fails; nothing builds.

The clone is pinned to a specific feature branch on an external repo:

```
git clone -b build-options https://github.com/mohsenzakeri/pfp-thresholds.git
```

Feature branches are routinely deleted after merging. Verify the branch still exists
before deploying. Consider pinning to a specific commit hash or tag for reproducibility.

## 4. `max_price` is a float but CDK expects a string

**File:** `config.json` / `ec2_example/ec2_example_stack.py`, line 80  
**Impact:** Spot instance may fail to launch.

`spot_price` values in `config.json` are JSON numbers (e.g. `3.0`), but
`LaunchTemplateSpotOptions.max_price` is typed `Optional[str]` in CDK. Passing a
Python `float` may serialize incorrectly depending on CDK/CloudFormation version.
Store spot prices as strings in `config.json` (e.g. `"3.0"`) or cast explicitly:
`str(instance_config['large']['spot_price'])`.

## 5. `x2iedn.24xlarge` availability and spot price in `eu-north-1` should be verified

**File:** `config.json`  
**Impact:** Instance may never launch.

Two things to confirm before deploying:

- **Regional availability:** The `x2iedn` family is available in only a small number of
  AWS regions. Verify that `x2iedn.24xlarge` is actually offered in `eu-north-1`
  (Stockholm).
- **Spot bid:** The configured max of $3.00/hr is modest for an instance with an
  on-demand price of ~$20/hr. If the current spot market price exceeds the bid, the
  instance will never launch rather than producing an explicit error. Check current spot
  prices before deploying.

## 6. CDK version is pinned to an exact old release

**File:** `requirements.txt`  
**Impact:** Low — existing pinned version still works, but misses security/bug fixes.

`aws-cdk-lib==2.198.0` was already several months old at time of writing. Consider
relaxing to `>=2.198.0,<3.0.0` and keeping the installed version current.

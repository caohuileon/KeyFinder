# KeyFinder
This tool is find and replace keywords in mapping files for your repo.

# Setup
Since it is a small tool, so no need to make it into package to install.
## Git clone code to your machine
```
git@github.west.isilon.com:lcao1/KeyFinder.git
cd code/KeyFinder/: python3 findKey.py -h
```
# Instructions
Followed detail usage.
## Command
```
python3 findKey.py -k [keywords] -p path -b branch --replace=True
```
* keywords: Can be IP address or other keywords. Such as: ["10.1.25.6,head1 TEST SUITE DESCRIPTION"], use
comma to split multi keywords. Type: List String, Positional
* path: Target walk path, can be directory path or file path. Type: String, Positional
* branch: Target repo branch you want to walk in, it will checkout and work on this branch. Type: String, optional, 
default: current repo branch.
* --replace: Replace keywords according to replace_schema.json. Type: Bool, optional, default: False

Note: It support blur search keywords like: 10.2.\*, USER_STRING_*, but only support start with/end with * blur search,
not support middle * blur search.

Eg: # python3 findKey.py -k "10.25.68.*,Tests for synciq_packet_fragmentation check" 
-p /repo/Code/OneFS/onefs/isilon/test-qa/tests/healthcheck/test_checks --replace=True

## Result
Running result will generate result.json file in code/KeyFinder/
```
root@remotedev-lcao1-02:/repo/Scripts/Tools/KeyFinder/KeyFinder [master *%] # cat result.json
{
  "10.25.68.*": [
    {
      "10.25.68.30": [
        "/repo/Code/OneFS/onefs/isilon/test-qa/tests/healthcheck/test_checks/networking/test_mixed_external_interfaces.py"
      ]
    },
    {
      "10.25.68.41": [
        "/repo/Code/OneFS/onefs/isilon/test-qa/tests/healthcheck/test_checks/networking/test_mixed_external_interfaces.py",
        "/repo/Code/OneFS/onefs/isilon/test-qa/tests/healthcheck/test_checks/siq/test_synciq_packet_fragmentation.py"
      ]
    },
    {
      "10.25.68.42": [
        "/repo/Code/OneFS/onefs/isilon/test-qa/tests/healthcheck/test_checks/networking/test_mixed_external_interfaces.py",
        "/repo/Code/OneFS/onefs/isilon/test-qa/tests/healthcheck/test_checks/siq/test_synciq_packet_fragmentation.py"
      ]
    },
    {
      "10.25.68.50": [
        "/repo/Code/OneFS/onefs/isilon/test-qa/tests/healthcheck/test_checks/networking/test_mixed_external_interfaces.py"
      ]
    },
    {
      "10.25.68.51": [
        "/repo/Code/OneFS/onefs/isilon/test-qa/tests/healthcheck/test_checks/networking/test_mixed_external_interfaces.py"
      ]
    }
  ],
  "Tests for synciq_packet_fragmentation check": [
    {
      "Tests for synciq_packet_fragmentation check": [
        "/repo/Code/OneFS/onefs/isilon/test-qa/tests/healthcheck/test_checks/siq/test_synciq_packet_fragmentation.py"
      ]
    }
  ]
```
## replace_schema.json
Replace will follow replace_schema.json file content.
```
{
  "rep_file_type": [".py"],
  "rep_files": ["/repo/Code/OneFS/onefs/isilon/test-qa/tests/healthcheck/test_checks"],
  "rep_data": [
    {"10.25.68.42": "10.11.22.33"},
    {"Tests for synciq_packet_fragmentation check": "test replace"}
  ]
}
```
* rep_file_type: Define target file types you want to replace in. Default is result file all types, if rep_file_type is 
not empty it will only replace target types files. Type: List, such as: [".py", ".list", ".cpp"]
* rep_files: Define specify target file/directory you want to replace in. If it is empty, will default replace target 
walk path files/directories otherwise it will only replace here listed files or directory files. Type: List, such as: 
["/repo/Code/OneFS/onefs/isilon/test-qa/tests", 
"/repo/Code/OneFS/onefs/isilon/test-qa/tests/webui/e2e/tests/18_external_network_test/networks_config.js"]
* rep_data: Define target replace data. Type: List and Dict.
```
[
  {Old: Replace}, 
  {Old: Replace}, 
  ...
]
```
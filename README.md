# cclyon_py_tools
CCLyon python tools

`launch_command.py -pc 5 command ...` requests five CPUs using
one hardware thread per physical core on Slurm. Put launcher options before the
command. The option passes `--hint=nomultithread` to `sbatch` and runs the workload
through a single-task `srun` with the same hint. The affinity mask is printed in
the workload log. Set the application's own thread count to five as well.

`--physical-cores 5` is the long form of `-pc 5`. Use either `-mc` or `-pc`,
not both.

Use `-debug` to generate the script and print the submission command without
submitting it. Without `-pc`, the existing allocation/execution
behavior is unchanged. This option does not apply to CERN HTCondor or the
launcher's `-interactive` mode, which executes directly in the current shell.
Whether sibling threads can be allocated to other jobs depends on the cluster's
Slurm configuration; this option does not request an exclusive node.

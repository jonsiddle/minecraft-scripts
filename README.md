# What's this?

Scripts to manage minecraft server and backups of the running server

# How does it work?

In normal use, it consists of two long-running scripts.

The `runmc` script is trivial and runs the `bedrock_server` within a GNU
`screen` session so that we can inject commands and monitor its output.

The `mcbak` script does the heavy lifting. It runs a loop which periodically:

+ Prepares for backup by telling the server to disable writing to the world
  files. Any further changes are held (much like a filesystem journal).
+ Queries the server for the valid backup details (you must truncate the files
  to the specified number of bytes; I assume because they continue to be
  appended to).
+ Uses this information to take a backup.
+ Resumes normal operation by telling the server it can write to the world files
  again.

# Where do the backups go?

The latest backup of the world files is stored in a directory.

All backups are stored in a [`bup`](https://github.com/bup/bup) repository. This
means they are versioned and stored extremely efficiently.

# How do I run it?

+ Run tmux
+ Split pane (ctrl-b ")
+ In one tmux pane, run `runmc`
+ In the other run `mcbak`

`runmc` will start a screen session named `minecraft`, sets the log file to a
known location (`mclog`) and run `bedrock_server` within that.

`mcbak` loops forever. Every interval (by default 10 minutes), it:

# Notes

You don't *have* to use `tmux`, but it's a convenient way to be able to run this
and see both scripts at the same time. You could just start both processes in
the background using your method of choice.

In part, I used `tmux` for this part to avoid nested `screen`s.

The `bup` store can get so large that it becomes unusably slow. I only saw this
after running for *years* with the interval set to 10 minutes, so you probably
won't run into this if your interval is set to longer.

However, once it's wedged it's *really* wedged.

There is a third script - `reducebup` which aggressively prunes the `bup`
repository to retain only one version per day, except for the latest x days.

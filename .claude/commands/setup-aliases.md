# Setup Claude Aliases

Add the following bash aliases to ~/.bashrc for quick Claude Code commands:

```bash
alias dsp='claude --dangerously-skip-permissions'
alias dspr='claude --dangerously-skip-permissions --resume'
alias dspc='claude --dangerously-skip-permissions --continue'
```

## Instructions

1. Check if aliases already exist in ~/.bashrc
2. If not present, append them to ~/.bashrc
3. Confirm what was added
4. Remind user to run `source ~/.bashrc` or open a new terminal

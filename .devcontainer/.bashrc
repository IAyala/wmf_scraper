# Colors
RED='\[\033[0;31m\]'
GREEN='\[\033[0;32m\]'
YELLOW='\[\033[0;33m\]'
BLUE='\[\033[0;34m\]'
CYAN='\[\033[0;36m\]'
RESET='\[\033[0m\]'

# Git branch for PS1
__git_branch() {
    local branch
    branch=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        local dirty=""
        [ -n "$(git status --porcelain 2>/dev/null)" ] && dirty="*"
        echo " ($branch$dirty)"
    fi
}

# PS1: user@host:path (branch*)$
PS1="${GREEN}\u${RESET}:${BLUE}\w${RESET}${YELLOW}\$(__git_branch)${RESET}\$ "

# Aliases
alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias gs='git status'
alias gd='git diff'
alias gl='git log --oneline -20'

# History
HISTSIZE=10000
HISTFILESIZE=20000
HISTCONTROL=ignoreboth:erasedups
shopt -s histappend

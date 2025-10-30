def has_flag(cmd, *flags):
    return any(f in cmd.flags for f in flags)
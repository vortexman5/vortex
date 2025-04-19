# Admin Mode

Admin mode is a special configuration that bypasses security restrictions for advanced users who need unrestricted agent capabilities. This mode is intended for personal use only and should be used with extreme caution.

## What is Admin Mode?

Admin mode disables the security checks that normally prevent potentially risky operations. When enabled:

- Security analyzers (like the Invariant analyzer) will not block any actions
- Confirmation prompts for potentially dangerous operations are bypassed
- The agent has unrestricted access to execute commands and modify files

## When to Use Admin Mode

Admin mode should only be used in the following scenarios:
- Personal development environments where you need full system access
- Testing advanced agent capabilities without security interruptions
- Debugging security-related issues
- Environments where you fully trust the LLM and understand the risks

## Security Implications

**WARNING: Admin mode removes critical security safeguards. Use at your own risk.**

When admin mode is enabled:
- The agent can execute any command without restrictions
- System files can be modified or deleted
- Network operations are unrestricted
- Potentially harmful code can be executed

## How to Enable Admin Mode

1. **Create a dedicated admin configuration file**:
   ```bash
   cp config.template.toml config.admin.toml
   ```

2. **Edit the configuration file** to enable admin mode:
   ```toml
   [security]
   # Enable admin mode with unrestricted capabilities
   admin_mode = true
   
   # Use the invariant security analyzer (will be bypassed in admin mode)
   security_analyzer = "invariant"
   
   # Disable confirmation mode for convenience
   confirmation_mode = false
   ```

3. **Start OpenHands with the admin configuration**:
   ```bash
   # For CLI mode
   python -m openhands.cli --config config.admin.toml
   
   # For server mode
   python -m openhands.server --config config.admin.toml
   ```

4. **Verify admin mode is active**:
   When admin mode is enabled, you'll see a log message: "Admin mode enabled: Bypassing security checks" when the agent performs actions.

## Best Practices for Admin Mode

1. **Never use admin mode in production environments**
2. **Never share your admin configuration file** with others
3. **Create a separate workspace directory** for admin mode sessions
4. **Regularly backup important files** before using admin mode
5. **Monitor agent actions closely** when admin mode is enabled
6. **Disable admin mode** when it's no longer needed

## Technical Implementation

Admin mode works by modifying the behavior of the security analyzers:

1. The `SecurityConfig` class includes an `admin_mode` flag (default: False)
2. When admin mode is enabled, the `SecurityAnalyzer` base class bypasses all security checks
3. The `InvariantAnalyzer` specifically checks for admin mode and allows all actions to proceed
4. The security configuration is passed through the class hierarchy to ensure consistent behavior

## Example Use Cases

### Development and Testing

```bash
# Start a CLI session with admin mode for development
python -m openhands.cli --config config.admin.toml

# Ask the agent to perform tasks that would normally be restricted
> Please modify the system configuration file at /etc/hosts
```

### Advanced System Administration

```bash
# Start a server with admin mode for system administration
python -m openhands.server --config config.admin.toml

# Connect to the web interface and ask the agent to:
> Install and configure a firewall on this system
```

### Debugging Security Issues

```bash
# Use admin mode to debug security-related problems
python -m openhands.cli --config config.admin.toml

# Ask the agent to analyze security logs
> Please analyze the security logs in /var/log/auth.log and identify any suspicious activity
```
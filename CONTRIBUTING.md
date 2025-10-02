# Contributing to Network Logging

Thank you for considering contributing! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, mtr version)
- **Relevant log excerpts** (please redact private IPs if needed)

### Suggesting Enhancements

Feature requests are welcome! Please:
- Check existing issues first to avoid duplicates
- Clearly describe the feature and its use case
- Explain why it would be useful to most users

### Pull Requests

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow existing code style
   - Add docstrings to new functions
   - Update config.example.json if adding new config options
   - Test thoroughly

3. **Update documentation:**
   - Update README.md if needed
   - Add entry to CHANGELOG.md
   - Document any new config options

4. **Commit with clear messages:**
   ```bash
   git commit -m "Add feature: brief description"
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a Pull Request on GitHub.

## 📝 Code Style Guidelines

### Python Style
- Follow PEP 8 where practical
- Use meaningful variable names
- Add docstrings to all public functions
- Include type hints for function parameters where helpful

### Example Function:
```python
def ping(host: str, timeout: int = 4) -> Optional[float]:
    """
    Ping a host and return RTT in seconds.
    
    Args:
        host: IP address or hostname to ping
        timeout: Timeout in seconds
        
    Returns:
        Round-trip time in seconds, or None if ping failed
    """
    # Implementation...
```

### Configuration
- All magic numbers should be configurable via config.json
- Provide sensible defaults
- Document new config options in config.example.json with `_*_help` keys

### Testing
- Test on Linux if possible (primary platform)
- Verify changes don't break existing functionality
- Test with different network conditions if relevant

## 🏗️ Project Structure

```
network-logging/
├── netLogging.py          # Main monitoring script
├── analyze_netlog.py      # Analysis and reporting
├── discover_isp_hops.py   # ISP hop discovery utility
├── probe_tcp_hosts.py     # TCP connectivity testing
├── config.json            # User configuration (not in git)
├── config.example.json    # Example config with documentation
├── start_netlogging.sh    # Cron wrapper script
├── README.md              # Main documentation
├── CHANGELOG.md           # Version history
├── LICENSE                # MIT License
├── requirements.txt       # Python dependencies (minimal)
├── .gitignore            # Git ignore rules
└── logs/                  # Log directory (not in git)
    ├── netlog.csv        # Main CSV log
    └── mtr_*.log         # MTR trace logs
```

## 🎯 Priority Areas

Help is especially appreciated in these areas:

1. **Windows Compatibility**
   - Adapting network commands for Windows
   - Testing on Windows environments

2. **macOS Testing**
   - Verify compatibility with macOS network tools
   - Document any macOS-specific setup steps

3. **Enhanced Analysis**
   - More sophisticated outage pattern detection
   - Visualization options (graphs, charts)
   - Export formats (HTML, PDF)

4. **Documentation**
   - More usage examples
   - Video tutorials
   - Troubleshooting guides

5. **Testing**
   - Unit tests for core functions
   - Integration tests
   - Mock network conditions for testing

## ❓ Questions?

- Open a GitHub issue for questions
- Check existing issues and discussions
- Review README.md thoroughly first

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making Network Logging better! 🚀

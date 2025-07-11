# Universal Emoji Removal Script

A comprehensive tool that finds and removes all emojis from text files in **any repository**. Works with Python, JavaScript, Java, C++, Go, Rust, and any other project type.

## Universal Usage

### For any repository:
```bash
# Preview what would be removed (safe)
python remove_emojis.py --preview

# Actually remove emojis
python remove_emojis.py --remove

# Process different repository
python remove_emojis.py --root /path/to/any/repo --preview

# Check specific file in any language
python remove_emojis.py --file src/main.py --preview
python remove_emojis.py --file README.md --remove
```

## Why You'll Need This Again

**Emojis creep in everywhere:**
- Copy-pasting from documentation that has emojis
- IDE autocomplete suggesting emoji unicode
- Markdown files with emoji shortcuts
- Comments with casual emojis
- Documentation templates with emojis
- Error messages with status emojis
- Commit messages that accidentally include emojis

**This script prevents emoji violations across your entire codebase.**

## Comprehensive Language Support

The script automatically detects and processes:

### Documentation
- `.md`, `.txt`, `.rst`, `.adoc`, `.asciidoc`

### Programming Languages
- **Python**: `.py`
- **JavaScript/TypeScript**: `.js`, `.ts`, `.jsx`, `.tsx`
- **Java**: `.java`
- **C/C++**: `.c`, `.cpp`, `.h`, `.hpp`
- **C#**: `.cs`
- **PHP**: `.php`
- **Ruby**: `.rb`
- **Go**: `.go`
- **Rust**: `.rs`
- **Swift**: `.swift`
- **Kotlin**: `.kt`
- **Scala**: `.scala`

### Configuration Files
- `.yaml`, `.yml`, `.json`, `.toml`, `.ini`, `.cfg`, `.conf`
- `.xml`, `.html`, `.htm`, `.css`, `.scss`, `.sass`, `.less`

### Scripts
- `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1`, `.bat`, `.cmd`

### Other Text Files
- `.sql`, `.r`, `.m`, `.pl`, `.lua`, `.vim`, `.tex`, `.bib`

## Smart Repository Detection

**Automatically skips:**
- **Version Control**: `.git`, `.svn`, `.hg`, `.bzr`
- **Dependencies**: `node_modules`, `vendor`, `.bundle`
- **Python Artifacts**: `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.tox`, `venv`, `.venv`
- **Build Directories**: `build`, `dist`, `target`, `bin`, `obj`, `out`, `.next`, `.nuxt`
- **IDE Directories**: `.vscode`, `.idea`, `.vs`
- **Cache Directories**: `.cache`, `.tmp`, `tmp`, `temp`
- **Coverage/Test Outputs**: `.coverage`, `coverage`, `.nyc_output`, `htmlcov`
- **Language Specific**: `.cargo`, `.gradle`, `.m2`, `.ivy2`, `.sbt`

**Binary File Detection**: Automatically skips binary files by checking for null bytes.

## Real-World Examples

### Python Projects
```bash
cd my-python-project
python /path/to/remove_emojis.py --preview
```

### JavaScript/Node.js Projects  
```bash
cd my-react-app
python /path/to/remove_emojis.py --remove
```

### Multi-language Repositories
```bash
cd my-microservices-repo
python /path/to/remove_emojis.py --preview
# Finds emojis in Python, Java, JavaScript, YAML configs, etc.
```

### Documentation Sites
```bash
cd my-docs-site
python /path/to/remove_emojis.py --file README.md --preview
```

### Any Git Repository
```bash
# Copy script to your tools directory
cp remove_emojis.py ~/bin/
chmod +x ~/bin/remove_emojis.py

# Use anywhere
cd /any/repository
remove_emojis.py --preview
```

## Sample Output

```
============================================================
EMOJI SCAN REPORT
============================================================
Scanning repository at: /path/to/repo
  Processed 247 files...

Found emojis in 3 files:
------------------------------------------------------------

src/components/Button.tsx
   5 emojis found:
   - '🚀' at position 423
   - '✅' at position 1205
   - '❌' at position 1284

README.md
   12 emojis found:
   - '🎯' at position 89
   - '📚' at position 156
   ... and 10 more

docs/api.md
   3 emojis found:
   - '📝' at position 34
   - '🔧' at position 445
   - '💡' at position 892

============================================================
SUMMARY:
  Files with emojis: 3
  Total emojis: 20
  Unique emojis: 8

Most common emojis:
  '📚': 4 times
  '🚀': 3 times
  '✅': 3 times

To remove these emojis, run:
  python remove_emojis.py --remove
============================================================
```

## Installation for Universal Use

### Make globally available:
```bash
# Copy to your PATH
cp remove_emojis.py ~/bin/emoji-clean
chmod +x ~/bin/emoji-clean

# Or create alias
echo 'alias emoji-clean="python /path/to/remove_emojis.py"' >> ~/.bashrc
```

### Use in any repository:
```bash
cd /any/project
emoji-clean --preview
emoji-clean --remove
```

## Integration with Git Hooks

### Pre-commit hook to prevent emoji commits:
```bash
#!/bin/sh
# .git/hooks/pre-commit
if python /path/to/remove_emojis.py --preview | grep -q "Found emojis"; then
    echo "ERROR: Emojis found in staged files!"
    python /path/to/remove_emojis.py --preview
    echo "Run: python /path/to/remove_emojis.py --remove"
    exit 1
fi
```

### CI/CD Integration:
```yaml
# .github/workflows/emoji-check.yml
name: Emoji Check
on: [push, pull_request]
jobs:
  emoji-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check for emojis
        run: |
          python remove_emojis.py --preview
          if python remove_emojis.py --preview | grep -q "Found emojis"; then
            echo "❌ Emojis found in repository!"
            exit 1
          fi
```

## Why This Matters

**Professional Code Standards:**
- Clean, readable code without visual distractions
- Consistent text encoding across all platforms
- Terminal compatibility (not all terminals render emojis well)
- Accessibility (screen readers handle text better than emojis)
- International compatibility (emoji meanings vary by culture)

**The script guarantees emoji-free repositories across any technology stack.** 
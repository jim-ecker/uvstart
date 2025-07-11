#!/usr/bin/env python3
"""
Universal Emoji Removal Script

Finds and removes all emojis from text files in any repository.
Supports preview mode and actual removal.

Usage:
    python remove_emojis.py --preview    # Show what would be removed
    python remove_emojis.py --remove     # Actually remove emojis
    python remove_emojis.py --file path  # Process specific file
    python remove_emojis.py --root /path/to/repo  # Process different repository
"""

import re
import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Set


class EmojiRemover:
    def __init__(self):
        # Comprehensive Unicode emoji ranges
        self.emoji_patterns = [
            # Emoticons and symbols
            r'[\U0001F600-\U0001F64F]',  # emoticons
            r'[\U0001F300-\U0001F5FF]',  # symbols & pictographs
            r'[\U0001F680-\U0001F6FF]',  # transport & map symbols
            r'[\U0001F1E0-\U0001F1FF]',  # flags (iOS)
            r'[\U00002702-\U000027B0]',  # dingbats
            r'[\U000024C2-\U0001F251]',  # enclosed characters
            r'[\U0001F900-\U0001F9FF]',  # supplemental symbols
            r'[\U0001FA70-\U0001FAFF]',  # symbols and pictographs extended-A
            # Additional ranges
            r'[\U00002600-\U000026FF]',  # miscellaneous symbols
            r'[\U0001F170-\U0001F189]',  # enclosed alphanumeric supplement
            # Common single emojis that might be missed
            r'[⚡⭐✅❌⚠️💡🔧🔍📁📋🔀💻🚀🧪🎯🎨🏥📖📦🛠️🤝📄]',
        ]
        
        # Combine all patterns
        self.emoji_regex = re.compile('|'.join(self.emoji_patterns))
        
        # File extensions to process (comprehensive list for any repo type)
        self.text_extensions = {
            # Documentation
            '.md', '.txt', '.rst', '.adoc', '.asciidoc',
            # Code files
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            # Config files
            '.yaml', '.yml', '.json', '.toml', '.ini', '.cfg', '.conf',
            '.xml', '.html', '.htm', '.css', '.scss', '.sass', '.less',
            # Shell scripts
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
            # Other text files
            '.sql', '.r', '.m', '.pl', '.lua', '.vim', '.tex', '.bib'
        }
        
        # Directories to skip (universal patterns)
        self.skip_dirs = {
            # Version control
            '.git', '.svn', '.hg', '.bzr',
            # Dependencies
            'node_modules', 'vendor', '.bundle',
            # Python
            '__pycache__', '.pytest_cache', '.mypy_cache', '.tox', 'venv', '.venv', '.virtualenv',
            # Build/output directories
            'build', 'dist', 'target', 'bin', 'obj', 'out', '.next', '.nuxt',
            # IDE/Editor directories
            '.vscode', '.idea', '.vs', '.sublime-project', '.sublime-workspace',
            # Cache directories
            '.cache', '.tmp', 'tmp', 'temp', '.temp',
            # Coverage/test outputs
            '.coverage', 'coverage', '.nyc_output', 'htmlcov',
            # Language specific
            '.cargo', '.gradle', '.m2', '.ivy2', '.sbt'
        }
        
        # Files to skip (this script and common files that might contain emoji patterns)
        self.skip_files = {
            'remove_emojis.py', 'emoji_remover.py', 'clean_emojis.py',
            # Common files that might have emoji references
            'package-lock.json', 'yarn.lock', 'Pipfile.lock', 'poetry.lock',
            'Cargo.lock', 'go.sum', 'composer.lock'
        }

    def find_emojis_in_text(self, text: str) -> List[Tuple[str, int, int]]:
        """Find all emojis in text and return list of (emoji, start, end) tuples"""
        matches = []
        for match in self.emoji_regex.finditer(text):
            matches.append((match.group(), match.start(), match.end()))
        return matches

    def remove_emojis_from_text(self, text: str) -> str:
        """Remove all emojis from text"""
        return self.emoji_regex.sub('', text)

    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Skip if file name is in skip list
        if file_path.name in self.skip_files:
            return False
            
        # Skip binary files by checking for null bytes in first 1024 bytes
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:
                    return False
        except (PermissionError, OSError):
            return False
            
        # Check if it's a text file (either by extension or if no extension but readable)
        if file_path.suffix.lower() in self.text_extensions:
            return True
            
        # For files without extensions, try to read as text
        if not file_path.suffix:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(100)  # Try to read first 100 chars
                return True
            except (UnicodeDecodeError, PermissionError):
                return False
            
        # Skip if any parent directory is in skip list
        for part in file_path.parts:
            if part in self.skip_dirs:
                return False
                
        return False

    def find_files_with_emojis(self, root_dir: Path) -> List[Tuple[Path, List[Tuple[str, int, int]]]]:
        """Find all files containing emojis"""
        files_with_emojis = []
        processed_count = 0
        
        print(f"Scanning repository at: {root_dir}")
        
        for file_path in root_dir.rglob('*'):
            if not file_path.is_file():
                continue
                
            if not self.should_process_file(file_path):
                continue
                
            processed_count += 1
            if processed_count % 100 == 0:
                print(f"  Processed {processed_count} files...")
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                emojis = self.find_emojis_in_text(content)
                if emojis:
                    files_with_emojis.append((file_path, emojis))
                    
            except (UnicodeDecodeError, PermissionError) as e:
                # Silently skip files we can't read
                continue
                
        print(f"  Total files processed: {processed_count}")
        return files_with_emojis

    def preview_changes(self, root_dir: Path) -> None:
        """Show what emojis would be removed"""
        print("=" * 60)
        print("EMOJI SCAN REPORT")
        print("=" * 60)
        
        files_with_emojis = self.find_files_with_emojis(root_dir)
        
        if not files_with_emojis:
            print("\nCLEAN: No emojis found in repository!")
            return
            
        print(f"\nFound emojis in {len(files_with_emojis)} files:")
        print("-" * 60)
        
        total_emojis = 0
        emoji_counts = {}
        
        for file_path, emojis in files_with_emojis:
            try:
                rel_path = file_path.relative_to(root_dir)
            except ValueError:
                rel_path = file_path
                
            print(f"\n{rel_path}")
            print(f"   {len(emojis)} emojis found:")
            
            for emoji, start, end in emojis[:10]:  # Show first 10 to avoid spam
                print(f"   - '{emoji}' at position {start}")
                
            if len(emojis) > 10:
                print(f"   ... and {len(emojis) - 10} more")
                
            total_emojis += len(emojis)
            for emoji, _, _ in emojis:
                emoji_counts[emoji] = emoji_counts.get(emoji, 0) + 1
                
        print("\n" + "=" * 60)
        print(f"SUMMARY:")
        print(f"  Files with emojis: {len(files_with_emojis)}")
        print(f"  Total emojis: {total_emojis}")
        print(f"  Unique emojis: {len(emoji_counts)}")
        
        if emoji_counts:
            print(f"\nMost common emojis:")
            sorted_emojis = sorted(emoji_counts.items(), key=lambda x: x[1], reverse=True)
            for emoji, count in sorted_emojis[:10]:
                print(f"  '{emoji}': {count} times")
            
        print(f"\nTo remove these emojis, run:")
        print(f"  python {os.path.basename(sys.argv[0])} --remove")
        print("=" * 60)

    def remove_emojis(self, root_dir: Path) -> None:
        """Actually remove emojis from files"""
        print("=" * 60)
        print("EMOJI REMOVAL")
        print("=" * 60)
        
        files_with_emojis = self.find_files_with_emojis(root_dir)
        
        if not files_with_emojis:
            print("\nCLEAN: No emojis found in repository!")
            return
            
        print(f"\nRemoving emojis from {len(files_with_emojis)} files...")
        print("-" * 60)
        
        files_modified = 0
        total_emojis_removed = 0
        
        for file_path, emojis in files_with_emojis:
            try:
                rel_path = file_path.relative_to(root_dir)
            except ValueError:
                rel_path = file_path
            
            try:
                # Read original content
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                    
                # Remove emojis
                cleaned_content = self.remove_emojis_from_text(original_content)
                
                # Write back if changed
                if cleaned_content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    
                    print(f"CLEANED: {rel_path} - removed {len(emojis)} emojis")
                    files_modified += 1
                    total_emojis_removed += len(emojis)
                    
            except Exception as e:
                print(f"ERROR: Error processing {rel_path}: {e}")
                
        print("\n" + "=" * 60)
        print(f"COMPLETED:")
        print(f"  Files modified: {files_modified}")
        print(f"  Total emojis removed: {total_emojis_removed}")
        print("=" * 60)

    def process_single_file(self, file_path: Path, remove: bool = False) -> None:
        """Process a single file"""
        if not file_path.exists():
            print(f"ERROR: File not found: {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            emojis = self.find_emojis_in_text(content)
            
            print("=" * 60)
            print(f"FILE: {file_path}")
            print("=" * 60)
            
            if not emojis:
                print("CLEAN: No emojis found")
                return
                
            print(f"Found {len(emojis)} emojis:")
            
            for emoji, start, end in emojis:
                print(f"  - '{emoji}' at position {start}")
                
            if remove:
                cleaned_content = self.remove_emojis_from_text(content)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                print(f"\nCLEANED: Removed {len(emojis)} emojis")
            else:
                print(f"\nTo remove these emojis, add --remove flag")
                
        except Exception as e:
            print(f"ERROR: Error processing {file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Find and remove emojis from text files in any repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --preview              # Show what emojis would be removed
  %(prog)s --remove               # Actually remove emojis
  %(prog)s --file README.md       # Check specific file
  %(prog)s --file README.md --remove  # Remove emojis from specific file
  %(prog)s --root /path/to/repo --preview  # Scan different repository
        """
    )
    
    parser.add_argument('--preview', action='store_true', 
                       help='Preview what emojis would be removed (default)')
    parser.add_argument('--remove', action='store_true',
                       help='Actually remove emojis from files')
    parser.add_argument('--file', type=Path,
                       help='Process specific file instead of entire repository')
    parser.add_argument('--root', type=Path, default=Path('.'),
                       help='Root directory to scan (default: current directory)')
    
    args = parser.parse_args()
    
    # Default to preview if no action specified
    if not args.remove and not args.preview:
        args.preview = True
        
    # Validate root directory
    if not args.root.exists():
        print(f"ERROR: Directory not found: {args.root}")
        return 1
        
    if not args.root.is_dir():
        print(f"ERROR: Not a directory: {args.root}")
        return 1
        
    emoji_remover = EmojiRemover()
    
    if args.file:
        # Process single file
        emoji_remover.process_single_file(args.file, remove=args.remove)
    else:
        # Process entire repository
        if args.preview:
            emoji_remover.preview_changes(args.root)
        elif args.remove:
            emoji_remover.remove_emojis(args.root)
    
    return 0


if __name__ == '__main__':
    sys.exit(main()) 
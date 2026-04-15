"""
Build script for C3 Time-Machine distribution
Creates a single-file Windows executable with all dependencies
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Import version info
try:
    from version import VERSION_INFO
except ImportError:
    VERSION_INFO = {
        'version': '1.0.0',
        'author': 'Utwej Sai Nalluri',
        'name': 'C3 Time-Machine',
        'description': 'Retroactive meeting audio capture utility',
        'company': 'Utwej Sai Nalluri',
        'copyright': 'Copyright © 2026 Utwej Sai Nalluri',
    }


def check_dependencies():
    """Check if required packages are installed"""
    print("=" * 60)
    print("Checking dependencies...")
    print("=" * 60)

    required = ['PyQt6', 'sounddevice', 'numpy', 'pyinstaller', 'Pillow']
    missing = []

    for package in required:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT FOUND")
            missing.append(package)

    if missing:
        print("\n⚠ Missing packages detected!")
        print(f"Install with: pip install {' '.join(missing)}")
        return False

    print("✓ All dependencies satisfied\n")
    return True


def generate_icon():
    """Generate application icon"""
    print("=" * 60)
    print("Generating application icon...")
    print("=" * 60)

    if Path("c3_icon.ico").exists():
        print("✓ Icon already exists: c3_icon.ico\n")
        return True

    try:
        result = subprocess.run(
            [sys.executable, "generate_icon.py"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print("✗ Icon generation failed")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"✗ Error generating icon: {e}")
        print("Continuing without custom icon...\n")
        return False


def create_version_file():
    """Create version file for PyInstaller"""
    print("=" * 60)
    print("Creating version info file...")
    print("=" * 60)

    version_template = f"""
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({VERSION_INFO['version'].replace('.', ', ')}, 0),
    prodvers=({VERSION_INFO['version'].replace('.', ', ')}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{VERSION_INFO['company']}'),
        StringStruct(u'FileDescription', u'{VERSION_INFO['description']}'),
        StringStruct(u'FileVersion', u'{VERSION_INFO['version']}'),
        StringStruct(u'InternalName', u'C3TimeMachine'),
        StringStruct(u'LegalCopyright', u'{VERSION_INFO['copyright']}'),
        StringStruct(u'OriginalFilename', u'C3TimeMachine.exe'),
        StringStruct(u'ProductName', u'{VERSION_INFO['name']}'),
        StringStruct(u'ProductVersion', u'{VERSION_INFO['version']}'),
        StringStruct(u'Developer', u'{VERSION_INFO['author']}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

    version_file = Path("version_info.txt")
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(version_template)

    print(f"✓ Created: {version_file}\n")
    return True


def create_manifest():
    """Create Windows manifest for standard user execution"""
    print("=" * 60)
    print("Creating Windows manifest...")
    print("=" * 60)

    manifest_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="*"
    name="C3.TimeMachine"
    type="win32"
  />
  <description>C3 Time-Machine - Retroactive Meeting Audio Capture</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 10 and Windows 11 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
    </application>
  </compatibility>
</assembly>
"""

    manifest_file = Path("c3_manifest.xml")
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write(manifest_content)

    print(f"✓ Created: {manifest_file}")
    print("  - Execution level: asInvoker (no UAC prompt)\n")
    return True


def build_executable():
    """Build the executable using PyInstaller"""
    print("=" * 60)
    print("Building executable with PyInstaller...")
    print("=" * 60)

    # Check if icon exists
    icon_arg = ""
    if Path("c3_icon.ico").exists():
        icon_arg = "--icon=c3_icon.ico"
        print("✓ Using custom icon")

    # Check if manifest exists
    manifest_arg = ""
    if Path("c3_manifest.xml").exists():
        manifest_arg = "--manifest=c3_manifest.xml"
        print("✓ Using custom manifest")

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single file
        "--noconsole",                  # No console window
        "--name=C3TimeMachine",         # Executable name
        "--add-data=config;config",     # Bundle config folder
        "--add-data=recordings;recordings",  # Bundle recordings folder
        "--hidden-import=sounddevice",  # Ensure sounddevice is included
        "--hidden-import=numpy",        # Ensure numpy is included
        "--hidden-import=PyQt6",        # Ensure PyQt6 is included
        "--collect-all=sounddevice",    # Collect all sounddevice files
    ]

    # Add version info
    if Path("version_info.txt").exists():
        cmd.append("--version-file=version_info.txt")
        print("✓ Using version info")

    # Add icon
    if icon_arg:
        cmd.append(icon_arg)

    # Add manifest
    if manifest_arg:
        cmd.append(manifest_arg)

    # Entry point
    cmd.append("c3tm/main.py")

    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True)

        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✓ BUILD SUCCESSFUL!")
            print("=" * 60)
            return True
        else:
            print("\n✗ Build failed")
            return False

    except subprocess.CalledProcessError as e:
        print(f"\n✗ PyInstaller error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


def post_build_setup():
    """Setup post-build artifacts"""
    print("\n" + "=" * 60)
    print("Post-build setup...")
    print("=" * 60)

    dist_dir = Path("dist")
    exe_file = dist_dir / "C3TimeMachine.exe"

    if not exe_file.exists():
        print("✗ Executable not found in dist/")
        return False

    # Calculate file size
    file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
    print(f"✓ Executable created: {exe_file}")
    print(f"  Size: {file_size:.2f} MB")

    # Copy icon to dist if it exists
    if Path("c3_icon.ico").exists():
        shutil.copy("c3_icon.ico", dist_dir / "c3_icon.ico")
        print("✓ Copied icon to dist/")

    # Create config and recordings folders in dist
    (dist_dir / "config").mkdir(exist_ok=True)
    (dist_dir / "recordings").mkdir(exist_ok=True)

    # Copy default config
    default_config = Path("config/default_config.json")
    if default_config.exists():
        shutil.copy(default_config, dist_dir / "config" / "default_config.json")
        print("✓ Copied default config")

    print("\n" + "=" * 60)
    print("DISTRIBUTION READY!")
    print("=" * 60)
    print(f"\nExecutable location: {exe_file.absolute()}")
    print("\nTo distribute:")
    print("  1. Copy the entire 'dist/' folder")
    print("  2. Rename it to 'C3TimeMachine'")
    print("  3. Zip it or share the folder")
    print("\nUsers can run: C3TimeMachine.exe")
    print("No Python installation required!")

    return True


def clean_build_artifacts():
    """Clean up build artifacts"""
    print("\n" + "=" * 60)
    print("Cleaning up build artifacts...")
    print("=" * 60)

    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = ["*.spec"]

    for dir_name in dirs_to_remove:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"✓ Removed: {dir_name}/")

    for pattern in files_to_remove:
        import glob
        for file in glob.glob(pattern):
            Path(file).unlink()
            print(f"✓ Removed: {file}")

    print()


def main():
    """Main build process"""
    print("\n" + "=" * 60)
    print("C3 TIME-MACHINE - BUILD SCRIPT")
    print("=" * 60)
    print(f"Version: {VERSION_INFO['version']}")
    print(f"Author: {VERSION_INFO['author']}")
    print("=" * 60 + "\n")

    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n✗ Build aborted - missing dependencies")
        return 1

    # Step 2: Generate icon
    generate_icon()  # Non-critical, continue even if it fails

    # Step 3: Create version file
    if not create_version_file():
        print("\n✗ Build aborted - version file creation failed")
        return 1

    # Step 4: Create manifest
    if not create_manifest():
        print("\n✗ Build aborted - manifest creation failed")
        return 1

    # Step 5: Build executable
    if not build_executable():
        print("\n✗ Build failed")
        return 1

    # Step 6: Post-build setup
    if not post_build_setup():
        print("\n✗ Post-build setup failed")
        return 1

    # Step 7: Clean up
    clean_build_artifacts()

    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)
    print("\nYour distributable application is ready in the 'dist/' folder.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

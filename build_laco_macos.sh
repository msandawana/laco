#!/bin/bash
echo "Building LACO Membership System..."
python3 -m pip install pyinstaller Pillow --quiet
rm -rf build dist __pycache__
python3 -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "LACO_Membership" \
  --add-data "laco_database.py:." \
  laco_app.py
echo ""
if [ -d "dist/LACO_Membership.app" ]; then
  echo "SUCCESS: dist/LACO_Membership.app"
  echo "Run with: open dist/LACO_Membership.app"
else
  echo "Build failed - check errors above"
fi

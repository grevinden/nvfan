#!/bin/sh
set -eu

cd "$(dirname "$0")"

DEB_NAME="nvfan_1.0.0_amd64.deb"
STAGING="nvfan.deb-staging"

# 1. Build binary if missing
if [ ! -f nvfan ]; then
    echo "Binary not found, building..."
    ./build.sh
fi

# 2. Clean previous staging
rm -rf "$STAGING" "$DEB_NAME"

# 3. Create DEB directory structure
mkdir -p "$STAGING/usr/local/bin"
mkdir -p "$STAGING/etc/systemd/system"
mkdir -p "$STAGING/DEBIAN"

# 4. Copy files
cp nvfan "$STAGING/usr/local/bin/nvfan"
chmod 755 "$STAGING/usr/local/bin/nvfan"

cp nvfan.service "$STAGING/etc/systemd/system/nvfan.service"

cp debian/control "$STAGING/DEBIAN/control"
cp debian/postinst "$STAGING/DEBIAN/postinst"
cp debian/prerm "$STAGING/DEBIAN/prerm"
chmod 755 "$STAGING/DEBIAN/postinst" "$STAGING/DEBIAN/prerm"

# 5. Build package
dpkg-deb --build --root-owner-group "$STAGING" "$DEB_NAME"

# 6. Cleanup staging
rm -rf "$STAGING"

echo ""
echo "Built: $(ls -lh "$DEB_NAME" | awk '{print $5}') $DEB_NAME"

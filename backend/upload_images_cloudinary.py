"""
Script pentru upload imagini la Cloudinary (production storage)
Rulează după setup Cloudinary account
"""

import os
import sys
from pathlib import Path
from decouple import config

try:
    import cloudinary
    import cloudinary.uploader
except ImportError:
    print("❌ Cloudinary nu e instalat!")
    print("Rulează: pip install cloudinary")
    sys.exit(1)

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from database import SessionLocal
from models import Symbol

# ==============================================
# CONFIGURARE CLOUDINARY
# ==============================================
cloud_name = config('CLOUDINARY_CLOUD_NAME', default='')
api_key = config('CLOUDINARY_API_KEY', default='')
api_secret = config('CLOUDINARY_API_SECRET', default='')

if not all([cloud_name, api_key, api_secret]):
    print("❌ Cloudinary credentials lipsesc!")
    print("Setează CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET în .env")
    sys.exit(1)

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
    secure=True
)

print(f"✅ Cloudinary configurat: {cloud_name}")

# ==============================================
# UPLOAD IMAGINI
# ==============================================
db = SessionLocal()

images_dir = Path("data/images")
if not images_dir.exists():
    print(f"❌ Folderul {images_dir} nu există!")
    sys.exit(1)

print(f"\n📂 Scanare folder: {images_dir}")
print("=" * 60)

uploaded_count = 0
skipped_count = 0
error_count = 0

# Găsește toate imaginile
image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))

if not image_files:
    print("⚠️  Nu s-au găsit imagini în folder!")
    sys.exit(0)

print(f"📊 Găsite {len(image_files)} imagini\n")

for img_path in image_files:
    # Extrage numele simbolului din numele fișierului
    symbol_name = img_path.stem.replace('_', ' ').title()
    
    # Caută simbolul în DB (case-insensitive, partial match)
    symbol = db.query(Symbol).filter(
        Symbol.name.ilike(f"%{symbol_name}%")
    ).first()
    
    if not symbol:
        # Încearcă fără spații
        symbol = db.query(Symbol).filter(
            Symbol.name.ilike(f"%{img_path.stem}%")
        ).first()
    
    if symbol:
        try:
            # Upload la Cloudinary
            print(f"📤 Upload: {img_path.name} → {symbol.name}... ", end='', flush=True)
            
            result = cloudinary.uploader.upload(
                str(img_path),
                folder="aac-symbols",
                public_id=f"symbol_{symbol.id}",
                overwrite=True,
                resource_type="image",
                transformation=[
                    {'width': 512, 'height': 512, 'crop': 'limit'},
                    {'quality': 'auto:good'}
                ]
            )
            
            # Update DB cu URL-ul Cloudinary
            old_url = symbol.image_url
            symbol.image_url = result['secure_url']
            db.commit()
            
            print(f"✅")
            print(f"   Vechi: {old_url}")
            print(f"   Nou:   {symbol.image_url}")
            print()
            
            uploaded_count += 1
            
        except Exception as e:
            print(f"❌\n   Eroare: {e}\n")
            error_count += 1
            db.rollback()
    else:
        print(f"⊘ Skip: {img_path.name} (nu s-a găsit simbolul '{symbol_name}' în DB)")
        skipped_count += 1

db.close()

# ==============================================
# RAPORT FINAL
# ==============================================
print("\n" + "=" * 60)
print("📊 RAPORT FINAL")
print("=" * 60)
print(f"✅ Uploadate cu succes: {uploaded_count}")
print(f"⊘ Sărite (nu există în DB): {skipped_count}")
print(f"❌ Erori: {error_count}")
print(f"📁 Total procesate: {len(image_files)}")
print("=" * 60)

if uploaded_count > 0:
    print("\n🎉 Upload complet!")
    print(f"✅ {uploaded_count} imagini sunt acum pe Cloudinary")
    print("🔗 Vezi-le în dashboard: https://cloudinary.com/console/media_library")
else:
    print("\n⚠️  Nicio imagine nu a fost uploadată")
    print("Verifică că imaginile corespund cu simbolurile din baza de date")

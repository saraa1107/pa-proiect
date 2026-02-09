# ========================================
# DEPLOYMENT SCRIPTS - AAC System
# ========================================
# Scripturi pentru deploy backend + frontend

Write-Host "🚀 AAC DEPLOYMENT HELPER" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# ========================================
# MENIU
# ========================================
Write-Host "Selectează acțiunea:" -ForegroundColor Yellow
Write-Host "1. Deploy Backend (Render)" -ForegroundColor White
Write-Host "2. Deploy Frontend (Netlify)" -ForegroundColor White
Write-Host "3. Build Frontend Local" -ForegroundColor White
Write-Host "4. Test Backend Local" -ForegroundColor White
Write-Host "5. Upload Imagini Cloudinary" -ForegroundColor White
Write-Host "6. Setup Environment (.env)" -ForegroundColor White
Write-Host "7. Push to GitHub" -ForegroundColor White
Write-Host "0. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Alegere (0-7)"

switch ($choice) {
    "1" {
        # ========================================
        # DEPLOY BACKEND
        # ========================================
        Write-Host ""
        Write-Host "📦 DEPLOY BACKEND PE RENDER" -ForegroundColor Cyan
        Write-Host "============================" -ForegroundColor Cyan
        Write-Host ""
        
        Write-Host "Pasul 1: Verificare fișiere..." -ForegroundColor Yellow
        
        if (Test-Path "backend/requirements_production.txt") {
            Write-Host "✅ requirements_production.txt găsit" -ForegroundColor Green
        } else {
            Write-Host "❌ requirements_production.txt lipsește!" -ForegroundColor Red
            exit 1
        }
        
        if (Test-Path "render.yaml") {
            Write-Host "✅ render.yaml găsit" -ForegroundColor Green
        } else {
            Write-Host "❌ render.yaml lipsește!" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "Pasul 2: Push la GitHub..." -ForegroundColor Yellow
        git add .
        git commit -m "Ready for Render deployment"
        git push
        
        Write-Host ""
        Write-Host "✅ Push complet!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Pasul 3: Deploy pe Render" -ForegroundColor Yellow
        Write-Host "1. Deschide https://render.com/" -ForegroundColor White
        Write-Host "2. New → Blueprint" -ForegroundColor White
        Write-Host "3. Conectează repository-ul" -ForegroundColor White
        Write-Host "4. Click 'Apply'" -ForegroundColor White
        Write-Host ""
        Write-Host "⏱️  Așteptare: ~5-10 minute pentru build" -ForegroundColor Yellow
    }
    
    "2" {
        # ========================================
        # DEPLOY FRONTEND
        # ========================================
        Write-Host ""
        Write-Host "🎨 DEPLOY FRONTEND PE NETLIFY" -ForegroundColor Cyan
        Write-Host "==============================" -ForegroundColor Cyan
        Write-Host ""
        
        Write-Host "Pasul 1: Build Flutter Web..." -ForegroundColor Yellow
        cd frontend
        
        Write-Host "Running: flutter pub get" -ForegroundColor Gray
        flutter pub get
        
        Write-Host "Running: flutter build web --release" -ForegroundColor Gray
        flutter build web --release --web-renderer html
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Build complet!" -ForegroundColor Green
        } else {
            Write-Host "❌ Build eșuat!" -ForegroundColor Red
            cd ..
            exit 1
        }
        
        cd ..
        
        Write-Host ""
        Write-Host "Pasul 2: Deploy pe Netlify" -ForegroundColor Yellow
        
        $hasNetlifyCLI = Get-Command netlify -ErrorAction SilentlyContinue
        
        if ($hasNetlifyCLI) {
            Write-Host "Netlify CLI găsit - deploying..." -ForegroundColor Green
            cd frontend
            netlify deploy --prod --dir=build/web
            cd ..
        } else {
            Write-Host "⚠️  Netlify CLI nu e instalat" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Opțiunea 1: Install CLI" -ForegroundColor White
            Write-Host "  npm install -g netlify-cli" -ForegroundColor Gray
            Write-Host "  netlify login" -ForegroundColor Gray
            Write-Host "  cd frontend" -ForegroundColor Gray
            Write-Host "  netlify deploy --prod --dir=build/web" -ForegroundColor Gray
            Write-Host ""
            Write-Host "Opțiunea 2: Deploy via Website" -ForegroundColor White
            Write-Host "  1. https://app.netlify.com/" -ForegroundColor Gray
            Write-Host "  2. New site from Git" -ForegroundColor Gray
            Write-Host "  3. Selectează repository" -ForegroundColor Gray
            Write-Host "  4. Deploy!" -ForegroundColor Gray
            Write-Host ""
        }
    }
    
    "3" {
        # ========================================
        # BUILD FRONTEND LOCAL
        # ========================================
        Write-Host ""
        Write-Host "🔨 BUILD FRONTEND LOCAL" -ForegroundColor Cyan
        Write-Host "=======================" -ForegroundColor Cyan
        Write-Host ""
        
        cd frontend
        
        Write-Host "Step 1: Clean..." -ForegroundColor Yellow
        flutter clean
        
        Write-Host "Step 2: Get dependencies..." -ForegroundColor Yellow
        flutter pub get
        
        Write-Host "Step 3: Build for web..." -ForegroundColor Yellow
        flutter build web --release --web-renderer html
        
        cd ..
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Build complet!" -ForegroundColor Green
            Write-Host "📁 Output: frontend/build/web/" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Pentru a testa local:" -ForegroundColor Yellow
            Write-Host "  cd frontend/build/web" -ForegroundColor Gray
            Write-Host "  python -m http.server 3000" -ForegroundColor Gray
            Write-Host "  Deschide: http://localhost:3000" -ForegroundColor Gray
        } else {
            Write-Host ""
            Write-Host "❌ Build eșuat!" -ForegroundColor Red
            exit 1
        }
    }
    
    "4" {
        # ========================================
        # TEST BACKEND LOCAL
        # ========================================
        Write-Host ""
        Write-Host "🧪 TEST BACKEND LOCAL" -ForegroundColor Cyan
        Write-Host "=====================" -ForegroundColor Cyan
        Write-Host ""
        
        cd backend
        
        Write-Host "Starting backend server..." -ForegroundColor Yellow
        Write-Host "Access: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
        Write-Host ""
        
        python run.py
        
        cd ..
    }
    
    "5" {
        # ========================================
        # UPLOAD CLOUDINARY
        # ========================================
        Write-Host ""
        Write-Host "☁️  UPLOAD IMAGINI CLOUDINARY" -ForegroundColor Cyan
        Write-Host "=============================" -ForegroundColor Cyan
        Write-Host ""
        
        if (-not (Test-Path "backend/.env")) {
            Write-Host "❌ Fișierul .env lipsește!" -ForegroundColor Red
            Write-Host "Rulează opțiunea 6 pentru setup" -ForegroundColor Yellow
            exit 1
        }
        
        cd backend
        
        Write-Host "Verificare credentials Cloudinary..." -ForegroundColor Yellow
        python -c "from decouple import config; print('✅' if config('CLOUDINARY_CLOUD_NAME', default='') else '❌ Cloudinary not configured')"
        
        Write-Host ""
        Write-Host "Starting upload..." -ForegroundColor Yellow
        python upload_images_cloudinary.py
        
        cd ..
    }
    
    "6" {
        # ========================================
        # SETUP ENVIRONMENT
        # ========================================
        Write-Host ""
        Write-Host "⚙️  SETUP ENVIRONMENT" -ForegroundColor Cyan
        Write-Host "====================" -ForegroundColor Cyan
        Write-Host ""
        
        if (Test-Path "backend/.env") {
            Write-Host "⚠️  Fișierul .env există deja" -ForegroundColor Yellow
            $overwrite = Read-Host "Vrei să-l suprascrii? (y/n)"
            if ($overwrite -ne "y") {
                Write-Host "Operație anulată" -ForegroundColor Gray
                exit 0
            }
        }
        
        Write-Host "Copiez .env.example → .env..." -ForegroundColor Yellow
        Copy-Item "backend/.env.example" "backend/.env"
        
        Write-Host "✅ Fișier .env creat!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "1. Deschide backend/.env în editor" -ForegroundColor White
        Write-Host "2. Completează valorile:" -ForegroundColor White
        Write-Host "   - DATABASE_URL (dacă ai PostgreSQL local)" -ForegroundColor Gray
        Write-Host "   - SECRET_KEY (generează unul nou)" -ForegroundColor Gray
        Write-Host "   - CLOUDINARY_* (dacă vrei upload imagini)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Pentru a genera SECRET_KEY:" -ForegroundColor Yellow
        Write-Host "  python -c `"import secrets; print(secrets.token_urlsafe(32))`"" -ForegroundColor Gray
    }
    
    "7" {
        # ========================================
        # PUSH TO GITHUB
        # ========================================
        Write-Host ""
        Write-Host "📤 PUSH TO GITHUB" -ForegroundColor Cyan
        Write-Host "=================" -ForegroundColor Cyan
        Write-Host ""
        
        Write-Host "Commit message:" -ForegroundColor Yellow
        $message = Read-Host ">"
        
        if ([string]::IsNullOrWhiteSpace($message)) {
            $message = "Update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        }
        
        Write-Host ""
        Write-Host "Adding files..." -ForegroundColor Yellow
        git add .
        
        Write-Host "Committing..." -ForegroundColor Yellow
        git commit -m $message
        
        Write-Host "Pushing..." -ForegroundColor Yellow
        git push
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Push complet!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "❌ Push eșuat!" -ForegroundColor Red
            Write-Host ""
            Write-Host "Cauze posibile:" -ForegroundColor Yellow
            Write-Host "- Nu ai configurat remote: git remote add origin <URL>" -ForegroundColor Gray
            Write-Host "- Nu ai autentificare: git config --global credential.helper wincred" -ForegroundColor Gray
        }
    }
    
    "0" {
        Write-Host "Bye! 👋" -ForegroundColor Cyan
        exit 0
    }
    
    default {
        Write-Host "❌ Opțiune invalidă!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Gata!" -ForegroundColor Green
Write-Host ""

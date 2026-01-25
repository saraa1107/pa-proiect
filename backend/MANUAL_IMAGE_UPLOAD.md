# Ghid pentru încărcarea imaginilor reale

## Opțiunea 1: Încărcare manuală (RECOMANDAT)

### Pasul 1: Găsește imagini reale
Poți folosi:
- **Unsplash**: https://unsplash.com (imagini gratuite, de calitate)
- **Pexels**: https://www.pexels.com (imagini gratuite)
- **Pixabay**: https://pixabay.com (imagini gratuite)
- Sau orice altă sursă de imagini

### Pasul 2: Descarcă imaginile
1. Caută imaginea potrivită (ex: pentru "Fericit" caută "happy person smiling")
2. Descarcă imaginea pe computer
3. Asigură-te că este în format JPG sau PNG

### Pasul 3: Încarcă imaginea folosind API-ul

#### Folosind Postman sau un client HTTP:

**Endpoint**: `POST http://localhost:8000/api/symbols/uploadimage`

**Body**: `form-data`
- `file`: selectează fișierul tău
- `symbol_id`: ID-ul simbolului (ex: 5 pentru "Fericit")
- `image_name`: (opțional) nume personalizat

#### Folosind Python:

```python
import requests

url = "http://localhost:8000/api/symbols/uploadimage"
files = {'file': open('fericit.jpg', 'rb')}
data = {'symbol_id': 5}  # ID-ul simbolului "Fericit"
response = requests.post(url, files=files, data=data)
print(response.json())
```

#### Folosind cURL:

```bash
curl -X POST "http://localhost:8000/api/symbols/uploadimage" \
  -F "file=@fericit.jpg" \
  -F "symbol_id=5"
```

### Pasul 4: Verifică ID-urile simbolurilor

Poți verifica ID-urile simbolurilor accesând:
- `GET http://localhost:8000/api/symbols` - toate simbolurile
- `GET http://localhost:8000/api/symbols/{id}` - un simbol specific
- `http://localhost:8000/docs` - documentație interactivă

## Opțiunea 2: Descărcare automată (necesită API keys)

Dacă ai API keys pentru Unsplash sau Pexels, poți folosi scriptul `download_images.py`:

1. Editează `download_images.py` și adaugă API keys
2. Rulează: `python download_images.py`

## Opțiunea 3: Folosind URL-uri de pe internet

Dacă ai URL-uri directe către imagini:

**Endpoint**: `POST http://localhost:8000/api/symbols/addimage`

**Body** (JSON):
```json
{
  "image_url": "https://example.com/fericit.jpg",
  "symbol_id": 5
}
```

## Exemple de imagini necesare

Pentru fiecare simbol, ai nevoie de o imagine clară care reprezintă:
- **Acțiuni**: persoane care fac acțiunea (ex: persoană care mănâncă, bea, doarme)
- **Alimente**: obiectul real (ex: pâine, apă, măr)
- **Emoții**: expresii faciale (ex: față fericită, tristă, supărată)
- **Persoane**: persoane reale sau ilustrații clare
- **Locații**: locurile reale (ex: casă, școală, parc)
- **Obiecte**: obiectele reale (ex: masă, scaun, jucărie)

## Sfaturi

1. **Calitate**: Folosește imagini clare, minim 200x200 pixeli
2. **Fond**: Preferă fundaluri simple sau transparente
3. **Claritate**: Imaginea trebuie să fie ușor de recunoscut
4. **Format**: JPG sau PNG funcționează cel mai bine

## Verificare

După ce încarci imaginile:
1. Reîncarcă aplicația frontend
2. Verifică dacă imaginile apar corect
3. Testează că fiecare simbol are imaginea potrivită

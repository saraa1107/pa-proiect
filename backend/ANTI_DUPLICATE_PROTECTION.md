# Protecție Anti-Duplicate - Documentație

## Problema
Baza de date conținea duplicate de categorii și simboluri, făcând interfața de utilizare confuză și greu de folosit.

## Soluție Implementată

### 1. Constrângeri la Nivel de Bază de Date ✅

**Locație:** `backend/models.py`

Adăugate constrângeri UNIQUE pentru:
- **Category**: `(name, child_id)` - previne duplicate de categorii cu același nume pentru același copil
- **Symbol**: `(name, category_id, child_id)` - previne duplicate de simboluri
- **FavoriteSymbol**: `(child_id, symbol_id)` - previne adăugarea aceluiași simbol de mai multe ori la favorite

```python
class Category(Base):
    __table_args__ = (
        UniqueConstraint('name', 'child_id', name='uq_category_name_child'),
    )

class Symbol(Base):
    __table_args__ = (
        UniqueConstraint('name', 'category_id', 'child_id', name='uq_symbol_name_category_child'),
    )
```

**Limitare:** SQLite tratează fiecare NULL ca o valoare unică, deci pentru categorii/simboluri globale (child_id = NULL), constrângerea nu funcționează complet.

### 2. Verificări în Backend ✅

**Locație:** `backend/services.py`

#### CategoryService.create()
```python
def create(db: Session, category: CategoryCreate) -> Category:
    # Evită duplicatele pe combinația (name, child_id)
    query = db.query(Category).filter(Category.name == category.name)
    
    if category.child_id is None:
        query = query.filter(Category.child_id.is_(None))
    else:
        query = query.filter(Category.child_id == category.child_id)
    
    existing = query.first()
    if existing:
        return existing  # Returnează categoria existentă în loc să creeze duplicat
    
    # Creează doar dacă nu există
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    return db_category
```

#### SymbolService.create()
Logică similară - verifică `(name, category_id, child_id)` înainte de a crea.

### 3. Filtrare Inteligentă la Returnare ✅

**Locație:** `backend/services.py`

#### CategoryService.get_all_for_child()
```python
def get_all_for_child(db: Session, child_id: int) -> List[Category]:
    # 1. Preia categoriile personalizate ale copilului
    child_categories = db.query(Category).filter(Category.child_id == child_id).all()
    
    # 2. Preia categoriile globale
    global_categories = db.query(Category).filter(Category.child_id.is_(None)).all()
    
    # 3. Creează set cu numele categoriilor personalizate
    child_category_names = {cat.name for cat in child_categories}
    
    # 4. Adaugă doar categoriile globale care NU au versiune personalizată
    for global_cat in global_categories:
        if global_cat.name not in child_category_names:
            child_categories.append(global_cat)
    
    return child_categories
```

**Rezultat:** Fiecare copil vede fie versiunea personalizată a categoriei, fie versiunea globală - **niciodată ambele**.

### 4. Scripturi de Curățare ✅

Createte pentru a elimina duplicatele existente:

- **clean_duplicates.py** - șterge categorii și simboluri duplicate
- **fix_orphan_symbols.py** - șterge simboluri care referă categorii inexistente
- **check_maria_categories.py** - verifică starea categoriilor pentru debugging

## Cum Funcționează în Practică

### Scenariul 1: Creare Categorie Nouă
1. Frontend trimite request de creare
2. Backend verifică dacă există deja `(name, child_id)`
3. Dacă există → returnează categoria existentă
4. Dacă nu există → creează categoria nouă
5. Baza de date verifică constrângerea UNIQUE
6. **Rezultat:** Nu se creează niciun duplicat

### Scenariul 2: Afișare Categorii pentru Copil
1. Frontend cere categoriile pentru copilul Maria (ID: 17)
2. Backend rulează `get_all_for_child(17)`
3. Găsește 6 categorii personalizate pentru Maria
4. Găsește 6 categorii globale
5. **Filtrează:** Pentru fiecare categorie globală, verifică dacă Maria are o versiune personalizată
6. **Returnează:** Doar 6 categorii (versiunile personalizate)
7. Frontend afișează cele 6 categorii unice

### Scenariul 3: Încercare Manuală de Duplicat (SQL Direct)
1. Cineva încearcă să insereze direct în baza de date
2. Baza de date verifică constrângerea UNIQUE
3. Pentru valori non-NULL → **REJECT** cu eroare
4. Pentru valori NULL → se creează dar backend va folosi doar prima găsită

## Migrare Aplicată

Script: `migrate_add_unique_constraints.py`

```bash
python migrate_add_unique_constraints.py
```

Adaugă index-uri UNIQUE pe:
- `categories(name, child_id)`
- `symbols(name, category_id, child_id)`
- `favorite_symbols(child_id, symbol_id)`

## Rezultate

✅ **Înainte:** Maria avea 42 categorii (duplicate multiple)
✅ **După:** Maria are 12 categorii (6 personalizate + 6 globale vizibile ca 6 unice)
✅ **Acum:** Maria are 6 categorii (doar versiunile personalizate)

## Testare

Rulează:
```bash
python test_unique_constraints.py
```

Verifică:
- ✅ Nu se pot crea duplicate pentru copii specifici
- ✅ Categorii cu același nume pot exista pentru copii diferiți
- ✅ Constrângerile de bază de date sunt active

## Mentenanță Viitoare

Dacă apar din nou duplicate:

1. **Diagnostic:**
   ```bash
   python check_maria_categories.py
   python check_child_duplicates.py
   ```

2. **Curățare:**
   ```bash
   python clean_duplicates.py
   python fix_orphan_symbols.py
   ```

3. **Verificare:**
   - Repornește backend-ul
   - Reîncarcă aplicația Flutter (Ctrl+Shift+R)
   - Verifică că duplicatele au dispărut

## Prevenție

**Cele 3 straturi de protecție împiedică duplicatele:**
1. Baza de date (UNIQUE constraints)
2. Backend (verificări la creare)
3. Frontend (de-duplicare la afișare)

**Duplicatele nu mai pot apărea** decât dacă:
- Cineva modifică manual baza de date cu SQL direct ȘI
- Rulează multiple INSERT-uri cu NULL child_id ȘI
- Ocolește complet backend-ul

**Probabilitate:** Aproape zero în utilizare normală.

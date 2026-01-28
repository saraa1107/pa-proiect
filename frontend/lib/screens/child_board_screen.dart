import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:image_picker/image_picker.dart';
import 'package:animate_do/animate_do.dart';
import '../theme/app_theme.dart';
import 'dart:typed_data';
import 'dart:html' as html;
import '../models/category.dart';
import '../models/child.dart';
import '../models/symbol.dart';
import '../providers/auth_provider.dart';
import '../providers/sentence_provider.dart';
import '../services/api_service.dart';
import '../services/tts_service.dart';
import '../widgets/sentence_bar.dart';
import '../widgets/search_bar.dart';
import '../widgets/category_grid.dart';
import '../widgets/symbol_grid.dart';

const int _kFavoritesCategoryId = -1;
const String _kPlaceholderImage = 'http://localhost:8000/images/casa.jpg';

class ChildBoardScreen extends StatefulWidget {
  final Child child;

  const ChildBoardScreen({super.key, required this.child});

  @override
  State<ChildBoardScreen> createState() => _ChildBoardScreenState();
}

class _ChildBoardScreenState extends State<ChildBoardScreen> {
  final TTSService _tts = TTSService();
  bool _isPlayingSentence = false;
  List<Category> _categories = [];
  List<Symbol> _allSymbols = []; // lista completă (pentru filtrare/căutare)
  List<Symbol> _symbols = [];
  Set<int> _favoriteIds = {};
  int? _selectedCategoryId; // null = Toate, _kFavoritesCategoryId = Favorite
  bool _loading = true;
  bool _reorderMode = false;
  String? _error;
  String _searchQuery = '';

  String? get _token => context.read<AuthProvider>().token;

  Future<void> _loadCategories() async {
    final t = _token;
    if (t == null) return;
    try {
      final list = await ApiService.getChildCategories(t, widget.child.id);
      
      // De-dup după id pentru a evita repetări vizuale
      final seen = <int>{};
      final unique = <Category>[];
      for (final c in list) {
        if (seen.add(c.id)) unique.add(c);
      }
      
      setState(() => _categories = unique);
    } catch (_) {}
  }

  Future<void> _loadFavorites() async {
    final t = _token;
    if (t == null) return;
    try {
      final list = await ApiService.getChildFavorites(t, widget.child.id);
      setState(() {
        _favoriteIds = list.map((s) => s.id).toSet();
      });
    } catch (_) {}
  }

  Future<void> _loadSymbols() async {
    final t = _token;
    if (t == null) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      List<Symbol> list;
      if (_selectedCategoryId == _kFavoritesCategoryId) {
        list = await ApiService.getChildFavorites(t, widget.child.id);
      } else {
        list = await ApiService.getChildSymbols(
          t,
          widget.child.id,
          categoryId: _selectedCategoryId,
        );
      }

      // De-dup după id și (name, category_id) pentru a evita repetări vizuale
      final seenIds = <int>{};
      final seenKeys = <String>{}; // key = "name_categoryId"
      final unique = <Symbol>[];
      for (final s in list) {
        final key = '${s.name}_${s.categoryId}';
        if (seenIds.add(s.id) && seenKeys.add(key)) {
          unique.add(s);
        }
      }

      setState(() {
        _allSymbols = unique;
        if (_searchQuery.isEmpty) {
          _symbols = List<Symbol>.from(_allSymbols);
        } else {
          final q = _searchQuery.toLowerCase();
          _symbols = _allSymbols
              .where((s) =>
                  s.name.toLowerCase().contains(q) ||
                  s.text.toLowerCase().contains(q))
              .toList();
        }
        _loading = false;
      });
      _loadFavorites();
    } catch (e) {
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await _loadCategories();
      // Selectează prima categorie dacă există
      if (_categories.isNotEmpty) {
        setState(() => _selectedCategoryId = _categories.first.id);
      }
      await _loadSymbols();
    });
  }

  void _selectCategory(int? id) {
    setState(() => _selectedCategoryId = id);
    _loadSymbols();
  }

  Future<void> _toggleFavorite(Symbol s) async {
    final t = _token;
    if (t == null) return;
    try {
      if (_favoriteIds.contains(s.id)) {
        await ApiService.removeChildFavorite(t, widget.child.id, s.id);
        setState(() => _favoriteIds.remove(s.id));
      } else {
        await ApiService.addChildFavorite(t, widget.child.id, s.id);
        setState(() => _favoriteIds.add(s.id));
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _addCategory() async {
    final nameController = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Categorie nouă'),
        content: TextField(
          controller: nameController,
          decoration: const InputDecoration(labelText: 'Nume', hintText: 'Ex: Emoții'),
          autofocus: true,
          onSubmitted: (_) => Navigator.of(ctx).pop(true),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('Anulare')),
          FilledButton(onPressed: () => Navigator.of(ctx).pop(true), child: const Text('Adaugă')),
        ],
      ),
    );
    if (ok != true || nameController.text.trim().isEmpty) return;
    final t = _token;
    if (t == null) return;
    try {
      await ApiService.createChildCategory(t, widget.child.id, nameController.text.trim());
      if (!mounted) return;
      await _loadCategories();
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Categorie adăugată')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _deleteCategory(Category category) async {
    final t = _token;
    if (t == null) return;

    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Șterge categorie'),
        content: Text(
          'Ești sigur că vrei să ștergi categoria "${category.name}" '
          'și toate cuvintele ei pentru acest copil?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Anulare'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Șterge'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      await ApiService.deleteChildCategory(t, widget.child.id, category.id);
      if (!mounted) return;
      setState(() {
        _categories.removeWhere((c) => c.id == category.id);
        if (_selectedCategoryId == category.id) {
          _selectedCategoryId = null;
        }
      });
      await _loadSymbols();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Categoria "${category.name}" a fost ștearsă.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _addSymbol() async {
    if (_categories.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Adaugă mai întâi o categorie')),
      );
      return;
    }
    Category? chosen = _categories.first;
    final nameController = TextEditingController();
    final textController = TextEditingController();
    Uint8List? selectedImageBytes;
    String? selectedImageFileName;

    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModal) {
          return AlertDialog(
            title: const Text('Cuvânt nou'),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  DropdownButtonFormField<Category>(
                    value: chosen,
                    decoration: const InputDecoration(labelText: 'Categorie'),
                    items: _categories
                        .map((c) => DropdownMenuItem(value: c, child: Text(c.name)))
                        .toList(),
                    onChanged: (c) => setModal(() => chosen = c),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: nameController,
                    decoration: const InputDecoration(labelText: 'Nume', hintText: 'Ex: Fericit'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: textController,
                    decoration: const InputDecoration(labelText: 'Text vorbit', hintText: 'Ex: Sunt fericit'),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    onPressed: () async {
                      // Pentru web, folosim html.FileUploadInputElement
                      final uploadInput = html.FileUploadInputElement();
                      uploadInput.accept = 'image/*';
                      uploadInput.click();
                      
                      uploadInput.onChange.listen((e) async {
                        final files = uploadInput.files;
                        if (files != null && files.isNotEmpty) {
                          final file = files[0];
                          final reader = html.FileReader();
                          reader.readAsArrayBuffer(file);
                          reader.onLoadEnd.listen((e) {
                            setModal(() {
                              selectedImageBytes = reader.result as Uint8List;
                              selectedImageFileName = file.name;
                            });
                          });
                        }
                      });
                    },
                    icon: const Icon(Icons.image),
                    label: Text(selectedImageFileName != null ? 'Imagine: $selectedImageFileName' : 'Selectează imagine'),
                  ),
                  if (selectedImageBytes != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.memory(selectedImageBytes!, height: 100, fit: BoxFit.cover),
                      ),
                    ),
                ],
              ),
            ),
            actions: [
              TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('Anulare')),
              FilledButton(onPressed: () => Navigator.of(ctx).pop(true), child: const Text('Adaugă')),
            ],
          );
        },
      ),
    );
    if (ok != true || chosen == null || nameController.text.trim().isEmpty) return;
    final cat = chosen!;
    final t = _token;
    if (t == null) return;
    try {
      if (selectedImageBytes != null && selectedImageFileName != null) {
        // Creează cu imagine din calculator
        await ApiService.createChildSymbolWithImage(
          t,
          widget.child.id,
          name: nameController.text.trim(),
          text: textController.text.trim().isEmpty ? nameController.text.trim() : textController.text.trim(),
          categoryId: cat.id,
          imageBytes: selectedImageBytes!,
          fileName: selectedImageFileName!,
        );
      } else {
        // Creează fără imagine (vor folosi placeholder)
        await ApiService.createChildSymbol(
          t,
          widget.child.id,
          name: nameController.text.trim(),
          text: textController.text.trim().isEmpty ? nameController.text.trim() : textController.text.trim(),
          categoryId: cat.id,
          imageUrl: _kPlaceholderImage,
        );
      }
      if (!mounted) return;
      await _loadSymbols();
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Cuvânt adăugat')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _deleteSymbol(Symbol s) async {
    final t = _token;
    if (t == null) return;

    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Șterge cuvânt'),
        content: Text('Ești sigur că vrei să ștergi cuvântul "${s.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Anulare'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Șterge'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      await ApiService.deleteChildSymbol(t, widget.child.id, s.id);
      if (!mounted) return;
      setState(() {
        _allSymbols.removeWhere((sym) => sym.id == s.id);
        _symbols.removeWhere((sym) => sym.id == s.id);
        _favoriteIds.remove(s.id);
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Cuvântul "${s.name}" a fost șters.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _saveReorder(List<Symbol> ordered) async {
    final t = _token;
    if (t == null) return;
    try {
      final items = <Map<String, int>>[];
      for (var i = 0; i < ordered.length; i++) {
        items.add({'symbol_id': ordered[i].id, 'display_order': i});
      }
      await ApiService.reorderChildSymbols(t, widget.child.id, items);
      setState(() {
        _symbols = ordered;
        _reorderMode = false;
      });
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Ordine salvată')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final favCategory = Category(
      id: _kFavoritesCategoryId,
      name: 'Favorite',
      createdAt: DateTime.now(),
      color: '#E91E63',
    );

    return Scaffold(
      appBar: AppBar(
        title: Text('Tabla AAC – ${widget.child.name}'),
        actions: [
          if (_selectedCategoryId != _kFavoritesCategoryId)
            IconButton(
              icon: Icon(_reorderMode ? Icons.check : Icons.sort),
              tooltip: _reorderMode ? 'Salvează ordinea' : 'Reordonează',
              onPressed: () {
                if (_reorderMode) {
                  _saveReorder(List<Symbol>.from(_symbols));
                } else {
                  // când intrăm în modul de reordonare, curățăm căutarea
                  setState(() {
                    _reorderMode = true;
                    _searchQuery = '';
                    _symbols = List<Symbol>.from(_allSymbols);
                  });
                }
              },
            ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.add),
            tooltip: 'Adaugă',
            onSelected: (v) {
              if (v == 'category') _addCategory();
              if (v == 'symbol') _addSymbol();
            },
            itemBuilder: (_) => [
              const PopupMenuItem(value: 'category', child: Text('Categorie')),
              const PopupMenuItem(value: 'symbol', child: Text('Cuvânt')),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // Bară de propoziție – la fel ca pe tabla de bază
          SlideInUp(
            duration: AppTheme.animationDurationNormal,
            child: Consumer<SentenceProvider>(
              builder: (context, sentenceProvider, _) {
                return SentenceBar(
                  symbols: sentenceProvider.sentence,
                  onSpeak: () async {
                    if (sentenceProvider.sentence.isEmpty) return;
                    setState(() => _isPlayingSentence = true);
                    try {
                      final texts =
                          sentenceProvider.sentence.map((s) => s.text).toList();
                      await _tts.speakSequence(texts);
                    } finally {
                      if (mounted) {
                        setState(() => _isPlayingSentence = false);
                      }
                    }
                  },
                  onClear: () {
                    sentenceProvider.clear();
                  },
                  isPlaying: _isPlayingSentence,
                );
              },
            ),
          ),

          // Bară de căutare – filtrare locală în tabla copilului
          FadeInDown(
            duration: AppTheme.animationDurationNormal,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: SearchBarWidget(
                onSearch: (query) {
                  setState(() {
                    _searchQuery = query;
                    if (query.isEmpty) {
                      _symbols = List<Symbol>.from(_allSymbols);
                    } else {
                      final q = query.toLowerCase();
                      _symbols = _allSymbols
                          .where((s) =>
                              s.name.toLowerCase().contains(q) ||
                              s.text.toLowerCase().contains(q))
                          .toList();
                    }
                  });
                },
              ),
            ),
          ),

          // Selector de categorii, inclusiv Favorite, cu culori ca pe tabla de bază
          FadeIn(
            duration: AppTheme.animationDurationNormal,
            delay: const Duration(milliseconds: 300),
            child: CategoryGrid(
              categories: [favCategory, ..._categories],
              selectedCategory: _selectedCategoryId == null
                  ? null
                  : ([favCategory, ..._categories]
                          .firstWhere(
                            (c) => c.id == _selectedCategoryId,
                            orElse: () => favCategory,
                          )),
              onCategorySelected: (category) {
                if (category?.id == _kFavoritesCategoryId) {
                  _selectCategory(_kFavoritesCategoryId);
                } else {
                  _selectCategory(category?.id);
                }
              },
              onCategoryLongPress: (category) {
                if (category.id != _kFavoritesCategoryId) {
                  _deleteCategory(category);
                }
              },
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _error != null
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(24.0),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.red)),
                              const SizedBox(height: 16),
                              FilledButton(onPressed: _loadSymbols, child: const Text('Reîncearcă')),
                            ],
                          ),
                        ),
                      )
                    : _symbols.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.tag_faces, size: 64, color: Colors.grey[400]),
                                const SizedBox(height: 12),
                                const Text('Niciun cuvânt aici. Adaugă categorii și cuvinte.'),
                              ],
                            ),
                          )
                        : _reorderMode
                            ? ReorderableListView.builder(
                                padding: const EdgeInsets.all(8),
                                itemCount: _symbols.length,
                                onReorder: (oldIndex, newIndex) {
                                  setState(() {
                                    final s = _symbols.removeAt(oldIndex);
                                    if (newIndex > oldIndex) newIndex--;
                                    _symbols.insert(newIndex, s);
                                  });
                                },
                                itemBuilder: (ctx, i) {
                                  final s = _symbols[i];
                                  return ListTile(
                                    key: ValueKey(s.id),
                                    leading: SizedBox(
                                      width: 56,
                                      height: 56,
                                      child: CachedNetworkImage(
                                        imageUrl: s.imageUrl,
                                        placeholder: (_, __) => const Center(
                                          child: CircularProgressIndicator(strokeWidth: 2),
                                        ),
                                        errorWidget: (_, __, ___) =>
                                            const Icon(Icons.image_not_supported),
                                        fit: BoxFit.contain,
                                      ),
                                    ),
                                    title: Text(s.name),
                                    trailing: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        IconButton(
                                          icon: Icon(
                                            _favoriteIds.contains(s.id)
                                                ? Icons.favorite
                                                : Icons.favorite_border,
                                          ),
                                          color: _favoriteIds.contains(s.id)
                                              ? Colors.red
                                              : null,
                                          onPressed: () => _toggleFavorite(s),
                                        ),
                                        const Icon(Icons.drag_handle),
                                      ],
                                    ),
                                  );
                                },
                              )
                            : SymbolGrid(
                                symbols: _symbols,
                                favoriteIds: _favoriteIds,
                                onSymbolTap: (s) async {
                                  await _tts.speak(s.text);
                                },
                                onSymbolDoubleTap: (s) {
                                  context.read<SentenceProvider>().addSymbol(s);
                                },
                                onToggleFavorite: (s) => _toggleFavorite(s),
                                onSymbolLongPress: (s) => _deleteSymbol(s),
                              ),
          ),
        ],
      ),
    );
  }
}

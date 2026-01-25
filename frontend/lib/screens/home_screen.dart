import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/category_provider.dart';
import '../providers/symbol_provider.dart';
import '../widgets/category_grid.dart';
import '../widgets/symbol_grid.dart';
import '../widgets/search_bar.dart';
import '../services/tts_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TTSService _ttsService = TTSService();

  @override
  void initState() {
    super.initState();
    // Încarcă datele la inițializare
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CategoryProvider>().loadCategories();
      context.read<SymbolProvider>().loadSymbols();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AAC Communication System'),
        centerTitle: true,
        elevation: 2,
      ),
      body: Column(
        children: [
          // Bară de căutare
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: SearchBarWidget(
              onSearch: (query) {
                if (query.isEmpty) {
                  context.read<SymbolProvider>().clearSearch();
                  context.read<CategoryProvider>().clearSelection();
                  context.read<SymbolProvider>().loadSymbols();
                } else {
                  context.read<SymbolProvider>().searchSymbols(query);
                }
              },
            ),
          ),

          // Selector de categorii
          Consumer<CategoryProvider>(
            builder: (context, categoryProvider, _) {
              if (categoryProvider.isLoading) {
                return const Center(child: CircularProgressIndicator());
              }

              if (categoryProvider.error != null) {
                return Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(
                    'Eroare: ${categoryProvider.error}',
                    style: const TextStyle(color: Colors.red),
                  ),
                );
              }

              return CategoryGrid(
                categories: categoryProvider.categories,
                selectedCategory: categoryProvider.selectedCategory,
                onCategorySelected: (category) {
                  categoryProvider.selectCategory(category);
                  context.read<SymbolProvider>().loadSymbols(
                    categoryId: category?.id,
                  );
                },
              );
            },
          ),

          const Divider(),

          // Grid de simboluri
          Expanded(
            child: Consumer<SymbolProvider>(
              builder: (context, symbolProvider, _) {
                if (symbolProvider.isLoading) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (symbolProvider.error != null) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Eroare: ${symbolProvider.error}',
                            style: const TextStyle(color: Colors.red),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: () {
                              symbolProvider.loadSymbols();
                            },
                            child: const Text('Reîncearcă'),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                if (symbolProvider.symbols.isEmpty) {
                  return const Center(
                    child: Text(
                      'Nu există simboluri disponibile',
                      style: TextStyle(fontSize: 16),
                    ),
                  );
                }

                return SymbolGrid(
                  symbols: symbolProvider.symbols,
                  onSymbolTap: (symbol) async {
                    // Generează și redă audio
                    await _ttsService.speak(symbol.text);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}


